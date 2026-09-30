"""Skill normalisation.

Maps surface forms in job text ("Python 3", "AWS Cloud", "Amazon Web Services")
onto canonical taxonomy skills using an alias dictionary plus fuzzy matching.
This is the deterministic backbone of the extraction pipeline — no LLM required.
"""

from __future__ import annotations

import re
from functools import lru_cache

from rapidfuzz import fuzz

from app.data.taxonomy import SKILLS


def _norm(text: str) -> str:
    """Lowercase and collapse punctuation for stable matching.

    Keeps intra-word '.' and '/' (so 'node.js' and 'ci/cd' survive) but strips
    them at word boundaries (so a sentence-ending 'devsecops.' still matches).
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#./ ]", " ", text)
    # Drop '.' or '/' that is not sitting between two alphanumerics.
    text = re.sub(r"(?<![a-z0-9])[./]", " ", text)
    text = re.sub(r"[./](?![a-z0-9])", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


@lru_cache(maxsize=1)
def _alias_index() -> dict[str, str]:
    """Map every alias and canonical name (normalised) -> canonical name."""
    index: dict[str, str] = {}
    for s in SKILLS:
        canon = s["name"]
        index[_norm(canon)] = canon
        for alias in s.get("aliases", []):
            index[_norm(alias)] = canon
    return index


@lru_cache(maxsize=1)
def _canonical_forms() -> list[tuple[str, str]]:
    """(normalised surface, canonical) pairs for fuzzy fallback matching."""
    return [(surface, canon) for surface, canon in _alias_index().items()]


def normalize_term(term: str, fuzzy_threshold: int = 88) -> tuple[str | None, float]:
    """Return (canonical_skill, confidence 0-1) for a single surface term.

    Exact alias hit -> high confidence. Otherwise a fuzzy token-set ratio is used
    and accepted only above `fuzzy_threshold`.
    """
    key = _norm(term)
    if not key:
        return None, 0.0
    exact = _alias_index().get(key)
    if exact:
        return exact, 0.97

    best_canon: str | None = None
    best_score = 0.0
    for surface, canon in _canonical_forms():
        score = fuzz.token_set_ratio(key, surface)
        if score > best_score:
            best_score, best_canon = score, canon
    if best_canon and best_score >= fuzzy_threshold:
        # Map 88..100 -> 0.70..0.95 confidence band.
        conf = 0.70 + (best_score - fuzzy_threshold) / (100 - fuzzy_threshold) * 0.25
        return best_canon, round(conf, 3)
    return None, 0.0


def all_aliases() -> dict[str, str]:
    """Expose the alias dictionary (used by extraction and docs)."""
    return dict(_alias_index())
