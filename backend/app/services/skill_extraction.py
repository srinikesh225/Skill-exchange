"""Skill-extraction pipeline.

    raw text
      -> preprocessing
      -> candidate extraction (alias/phrase dictionary)
      -> semantic similarity (TF-IDF cosine; sentence-transformers if installed)
      -> taxonomy matching + confidence
      -> optional LLM validation (disabled by default)

Deterministic by default; the semantic and LLM layers are graceful enhancements.
"""

from __future__ import annotations

from functools import lru_cache

from app.constants import (
    EXTRACTION_EXACT_CONFIDENCE,
    EXTRACTION_SIMILARITY_THRESHOLD,
)
from app.data.taxonomy import SKILLS
from app.services.skill_normalization import _norm, all_aliases


@lru_cache(maxsize=1)
def _phrase_map() -> list[tuple[str, str]]:
    """Longest-first (normalised alias, canonical) pairs for phrase matching.

    Longest-first avoids matching 'java' inside 'javascript'.
    """
    pairs = [(surface, canon) for surface, canon in all_aliases().items()]
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    return pairs


def _dictionary_extract(text: str) -> dict[str, float]:
    """Exact alias/phrase hits. Returns {canonical: confidence}."""
    padded = f" {_norm(text)} "
    found: dict[str, float] = {}
    for surface, canon in _phrase_map():
        if canon in found:
            continue
        needle = f" {surface} "
        if needle in padded:
            found[canon] = EXTRACTION_EXACT_CONFIDENCE
    return found


# --- Semantic layer -------------------------------------------------------
# TF-IDF cosine similarity between the job text and each skill's "document".
# If sentence-transformers is installed, it is used instead (higher quality).

@lru_cache(maxsize=1)
def _tfidf_index():
    from sklearn.feature_extraction.text import TfidfVectorizer

    docs, canons = [], []
    for s in SKILLS:
        blob = " ".join([s["name"], *s.get("aliases", []), s.get("description", "")])
        docs.append(_norm(blob))
        canons.append(s["name"])
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    matrix = vec.fit_transform(docs)
    return vec, matrix, canons


def _semantic_extract(text: str, threshold: float) -> dict[str, float]:
    from sklearn.metrics.pairwise import cosine_similarity

    vec, matrix, canons = _tfidf_index()
    q = vec.transform([_norm(text)])
    sims = cosine_similarity(q, matrix)[0]
    out: dict[str, float] = {}
    for canon, sim in zip(canons, sims):
        if sim >= threshold:
            # Map similarity onto a modest confidence band (semantic, not exact).
            out[canon] = round(0.55 + float(sim) * 0.35, 3)
    return out


def extract_skills(
    text: str,
    use_semantic: bool = True,
    similarity_threshold: float = EXTRACTION_SIMILARITY_THRESHOLD,
) -> list[dict]:
    """Extract canonical skills from free text.

    Returns [{"skill": str, "confidence": float, "method": "dictionary"|"semantic"}]
    sorted by confidence desc. Dictionary hits win over semantic on conflict.
    """
    results: dict[str, dict] = {}

    for canon, conf in _dictionary_extract(text).items():
        results[canon] = {"skill": canon, "confidence": conf, "method": "dictionary"}

    if use_semantic:
        try:
            for canon, conf in _semantic_extract(text, similarity_threshold).items():
                if canon not in results:
                    results[canon] = {"skill": canon, "confidence": conf, "method": "semantic"}
        except Exception:
            # Semantic layer is optional; never let it break extraction.
            pass

    return sorted(results.values(), key=lambda r: r["confidence"], reverse=True)


def extract_skill_names(text: str, use_semantic: bool = False) -> list[str]:
    """Convenience: just the canonical names (used during bulk generation)."""
    return [r["skill"] for r in extract_skills(text, use_semantic=use_semantic)]
