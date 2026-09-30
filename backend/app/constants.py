"""Central, documented, tunable constants for every scoring engine.

Keeping these here (not scattered in code) makes the models transparent and
configurable — a reviewer can read exactly how each score is composed, and an
operator can retune weights without touching business logic.

Every weighted formula's weights sum to 1.0 (asserted at import time).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# DEMAND ENGINE
# Demand Score (0-100) = weighted blend of six components, each normalised 0-100.
# ---------------------------------------------------------------------------
DEMAND_WEIGHTS: dict[str, float] = {
    "job_volume": 0.35,       # how many postings mention the skill
    "job_growth": 0.20,       # change in posting volume vs previous period
    "employer_signal": 0.15,  # employer survey demand
    "salary_premium": 0.10,   # salary uplift associated with the skill
    "industry_growth": 0.10,  # growth of industries that request the skill
    "emerging_signal": 0.10,  # emergence score contribution
}

# ---------------------------------------------------------------------------
# EMERGENCE ENGINE
# Emergence Score (0-100) classifies a skill's trajectory.
# ---------------------------------------------------------------------------
EMERGENCE_WEIGHTS: dict[str, float] = {
    "growth": 0.40,             # period-over-period demand growth
    "recency": 0.25,            # concentration of activity in recent months
    "cross_industry": 0.20,     # breadth of industries adopting the skill
    "employer_signal": 0.15,    # employer survey pull
}

# Emergence label thresholds applied to the growth rate (fraction, e.g. 0.30 = +30%).
EMERGENCE_LABELS: list[tuple[float, str]] = [
    (0.25, "Emerging"),
    (0.08, "Growing"),
    (-0.05, "Stable"),
    (float("-inf"), "Declining"),
]

# ---------------------------------------------------------------------------
# SUPPLY ENGINE
# Supply Index (0-100) = blend of local training capacity and pipeline quality.
# ---------------------------------------------------------------------------
SUPPLY_WEIGHTS: dict[str, float] = {
    "capacity": 0.50,          # seats available relative to demand
    "completion": 0.20,        # course completion rate
    "placement": 0.20,         # placement rate of related programmes
    "pipeline": 0.10,          # existing skilled learner pipeline
}

# ---------------------------------------------------------------------------
# GAP ENGINE
# Gap Score = Demand Index - Supply Index, clamped to 0-100, then classified.
# ---------------------------------------------------------------------------
GAP_THRESHOLDS: list[tuple[float, str]] = [
    (60.0, "Critical"),
    (40.0, "High"),
    (20.0, "Moderate"),
    (0.0, "Balanced"),
]

# ---------------------------------------------------------------------------
# COURSE ALIGNMENT ENGINE
# Alignment Score (0-100): how well an existing course matches current demand.
# ---------------------------------------------------------------------------
ALIGNMENT_WEIGHTS: dict[str, float] = {
    "skill_demand": 0.45,      # weighted demand of the skills the course covers
    "placement": 0.25,         # placement rate
    "utilisation": 0.15,       # capacity utilisation (enrolled / capacity)
    "freshness": 0.15,         # how recently the curriculum was updated
}

# Obsolescence risk thresholds applied to alignment score.
OBSOLESCENCE_THRESHOLDS: list[tuple[float, str]] = [
    (65.0, "Low"),        # alignment >= 65  -> low obsolescence risk
    (45.0, "Moderate"),
    (0.0, "High"),
]

# ---------------------------------------------------------------------------
# SKILL EXTRACTION
# ---------------------------------------------------------------------------
# Below this cosine similarity a TF-IDF match to the taxonomy is discarded.
EXTRACTION_SIMILARITY_THRESHOLD = 0.30
# Confidence assigned to an exact alias/dictionary hit.
EXTRACTION_EXACT_CONFIDENCE = 0.97

# ---------------------------------------------------------------------------
# Validate weight sets sum to ~1.0 so a bad edit fails loudly at import.
# ---------------------------------------------------------------------------
for _name, _weights in {
    "DEMAND_WEIGHTS": DEMAND_WEIGHTS,
    "EMERGENCE_WEIGHTS": EMERGENCE_WEIGHTS,
    "SUPPLY_WEIGHTS": SUPPLY_WEIGHTS,
    "ALIGNMENT_WEIGHTS": ALIGNMENT_WEIGHTS,
}.items():
    _total = sum(_weights.values())
    assert abs(_total - 1.0) < 1e-9, f"{_name} must sum to 1.0, got {_total}"
