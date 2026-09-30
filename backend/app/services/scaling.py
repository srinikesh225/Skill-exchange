"""Small, dependency-light numeric helpers shared by the engines.

Kept explicit and readable so the scoring is auditable.
"""

from __future__ import annotations

import math


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def minmax_scale(value: float, lo: float, hi: float) -> float:
    """Scale `value` from [lo, hi] into [0, 100]. Degenerate range -> 0."""
    if hi <= lo:
        return 0.0
    return clamp((value - lo) / (hi - lo) * 100.0)


def log_scale(value: float, lo: float, hi: float) -> float:
    """Log-then-minmax: compresses heavy-tailed counts (job volumes, seats)."""
    v = math.log1p(max(0.0, value))
    return minmax_scale(v, math.log1p(max(0.0, lo)), math.log1p(max(0.0, hi)))


def growth_to_score(rate: float, lo: float = -0.20, hi: float = 0.60) -> float:
    """Map a growth *fraction* (e.g. 0.30 = +30%) onto 0-100."""
    return minmax_scale(rate, lo, hi)


def weighted(components: dict[str, float], weights: dict[str, float]) -> float:
    """Weighted sum of already-0-100 components. Missing keys treated as 0."""
    return clamp(sum(components.get(k, 0.0) * w for k, w in weights.items()))


def round_components(components: dict[str, float], ndigits: int = 1) -> dict[str, float]:
    return {k: round(v, ndigits) for k, v in components.items()}
