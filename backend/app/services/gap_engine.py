"""Supply + gap engines — the heart of the platform.

Supply Index (0-100) = 0.50 capacity + 0.20 completion + 0.20 placement
  + 0.10 pipeline.

Gap Score = clamp(Demand Index - Supply Index, 0, 100), classified as
  Balanced / Moderate / High / Critical via configurable thresholds.
"""

from __future__ import annotations

from app.constants import GAP_THRESHOLDS, SUPPLY_WEIGHTS
from app.services.scaling import clamp, log_scale, round_components, weighted


def supply_components(
    *,
    seats: int,
    seats_lo: float,
    seats_hi: float,
    completion_rate: float,   # 0-1
    placement_rate: float,    # 0-1
    pipeline: int,            # enrolled learners
    pipeline_lo: float,
    pipeline_hi: float,
) -> dict[str, float]:
    return {
        "capacity": log_scale(seats, seats_lo, seats_hi),
        "completion": clamp(completion_rate * 100.0),
        "placement": clamp(placement_rate * 100.0),
        "pipeline": log_scale(pipeline, pipeline_lo, pipeline_hi),
    }


def supply_index(components: dict[str, float]) -> float:
    return weighted(components, SUPPLY_WEIGHTS)


def gap_score(demand: float, supply: float) -> float:
    return clamp(demand - supply, 0.0, 100.0)


def gap_label(score: float) -> str:
    for threshold, label in GAP_THRESHOLDS:
        if score >= threshold:
            return label
    return "Balanced"


def explain_supply(components: dict[str, float]) -> dict:
    return {
        "components": round_components(components),
        "weights": SUPPLY_WEIGHTS,
        "index": round(supply_index(components), 1),
    }
