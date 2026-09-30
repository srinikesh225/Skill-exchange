"""Demand + emergence engines.

Demand Index (0-100) = weighted blend of six components, each normalised 0-100:
    0.35 job volume + 0.20 job growth + 0.15 employer signal
  + 0.10 salary premium + 0.10 industry growth + 0.10 emerging signal

Emergence Score (0-100) = 0.40 growth + 0.25 recency + 0.20 cross-industry
  + 0.15 employer signal, with a data-derived label.

Weights live in app.constants and are asserted to sum to 1.0.
"""

from __future__ import annotations

from app.constants import DEMAND_WEIGHTS, EMERGENCE_LABELS, EMERGENCE_WEIGHTS
from app.services.scaling import (
    growth_to_score,
    log_scale,
    minmax_scale,
    round_components,
    weighted,
)


def emergence_components(
    growth_rate: float,
    recency_ratio: float,
    cross_industry_ratio: float,
    employer_signal: float,
) -> dict[str, float]:
    """All inputs -> 0-100 components for the emergence score."""
    return {
        "growth": growth_to_score(growth_rate),
        "recency": minmax_scale(recency_ratio, 0.0, 1.0),
        "cross_industry": minmax_scale(cross_industry_ratio, 0.0, 1.0),
        "employer_signal": employer_signal,  # already 0-100
    }


def emergence_score(components: dict[str, float]) -> float:
    return weighted(components, EMERGENCE_WEIGHTS)


def emergence_label(growth_rate: float) -> str:
    for threshold, label in EMERGENCE_LABELS:
        if growth_rate >= threshold:
            return label
    return "Declining"


def demand_components(
    *,
    job_volume: int,
    volume_lo: float,
    volume_hi: float,
    growth_rate: float,
    employer_signal: float,
    salary_premium: float,
    premium_lo: float,
    premium_hi: float,
    industry_growth: float,
    emerging_signal: float,
) -> dict[str, float]:
    """Assemble the six demand components on a common 0-100 scale."""
    return {
        "job_volume": log_scale(job_volume, volume_lo, volume_hi),
        "job_growth": growth_to_score(growth_rate),
        "employer_signal": employer_signal,
        "salary_premium": minmax_scale(salary_premium, premium_lo, premium_hi),
        "industry_growth": industry_growth,
        "emerging_signal": emerging_signal,
    }


def demand_index(components: dict[str, float]) -> float:
    return weighted(components, DEMAND_WEIGHTS)


def explain_demand(components: dict[str, float]) -> dict:
    """Return a UI-friendly breakdown: each component's value and its weighted
    contribution to the final index."""
    rounded = round_components(components)
    contributions = {
        k: round(components.get(k, 0.0) * w, 1) for k, w in DEMAND_WEIGHTS.items()
    }
    return {
        "components": rounded,
        "weights": DEMAND_WEIGHTS,
        "contributions": contributions,
        "index": round(demand_index(components), 1),
    }
