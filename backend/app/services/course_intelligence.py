"""Course intelligence: how well an existing course matches current demand.

Alignment Score (0-100) = 0.45 skill-demand + 0.25 placement
  + 0.15 utilisation + 0.15 freshness.

Obsolescence risk is derived from the alignment score. Courses are never
auto-deleted — low alignment is flagged for human review with a suggested action.
"""

from __future__ import annotations

from datetime import date

from app.constants import ALIGNMENT_WEIGHTS, OBSOLESCENCE_THRESHOLDS
from app.services.scaling import clamp, round_components, weighted


def freshness_score(last_updated: date, today: date) -> float:
    months = max(0, (today.year - last_updated.year) * 12 + (today.month - last_updated.month))
    # 0 months -> 100, 36+ months -> 0
    return clamp(100.0 - months * (100.0 / 36.0))


def alignment_components(
    *,
    avg_skill_demand: float,   # 0-100
    placement_rate: float,     # 0-1
    enrolled: int,
    capacity: int,
    last_updated: date,
    today: date,
) -> dict[str, float]:
    utilisation = (enrolled / capacity * 100.0) if capacity else 0.0
    return {
        "skill_demand": clamp(avg_skill_demand),
        "placement": clamp(placement_rate * 100.0),
        "utilisation": clamp(utilisation),
        "freshness": freshness_score(last_updated, today),
    }


def alignment_score(components: dict[str, float]) -> float:
    return weighted(components, ALIGNMENT_WEIGHTS)


def obsolescence_risk(score: float) -> str:
    for threshold, label in OBSOLESCENCE_THRESHOLDS:
        if score >= threshold:
            return label
    return "High"


def course_recommendation(score: float, missing_skills: list[str], mostly_declining: bool) -> str:
    if score < 45 and mostly_declining:
        return "RETIRE_OR_REDUCE"
    if score < 65 and missing_skills:
        return "UPDATE_CURRICULUM"
    if score < 55:
        return "REVIEW"
    return "KEEP"


def analyse_course(
    *,
    avg_skill_demand: float,
    placement_rate: float,
    enrolled: int,
    capacity: int,
    last_updated: date,
    today: date,
    missing_skills: list[str],
    mostly_declining: bool,
) -> dict:
    comps = alignment_components(
        avg_skill_demand=avg_skill_demand,
        placement_rate=placement_rate,
        enrolled=enrolled,
        capacity=capacity,
        last_updated=last_updated,
        today=today,
    )
    score = alignment_score(comps)
    return {
        "alignment_score": round(score, 1),
        "components": round_components(comps),
        "obsolescence_risk": obsolescence_risk(score),
        "missing_skills": missing_skills,
        "recommendation": course_recommendation(score, missing_skills, mostly_declining),
    }
