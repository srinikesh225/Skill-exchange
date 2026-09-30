"""Shared query helpers for the API routers.

Centralises the roll-ups so districts/analytics/compare stay consistent.
"""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import District, JobPosting, Recommendation, Skill, SkillMetric
from app.services.district_scoring import summarise


def skill_name_map(db: Session) -> dict[int, str]:
    return {s.id: s.canonical_name for s in db.query(Skill).all()}


def all_metrics_by_district(db: Session) -> dict[int, list[SkillMetric]]:
    grouped: dict[int, list[SkillMetric]] = defaultdict(list)
    for m in db.query(SkillMetric).all():
        grouped[m.district_id].append(m)
    return grouped


def rec_counts_by_district(db: Session) -> dict[int, dict]:
    """Per-district recommendation totals and per-action breakdown."""
    out: dict[int, dict] = defaultdict(lambda: {"total": 0, "actions": defaultdict(int)})
    rows = (
        db.query(Recommendation.district_id, Recommendation.action, func.count())
        .group_by(Recommendation.district_id, Recommendation.action)
        .all()
    )
    for did, action, n in rows:
        out[did]["total"] += n
        out[did]["actions"][action] += n
    return out


def district_summary_dict(d: District, metrics: list[SkillMetric], recinfo: dict, names: dict[int, str]) -> dict:
    s = summarise(metrics)
    top_emerging = sorted(
        [m for m in metrics if m.emergence_label in ("Emerging", "Growing")],
        key=lambda m: m.emergence_score, reverse=True,
    )[:5]
    top_gaps = sorted(metrics, key=lambda m: m.gap_score, reverse=True)[:5]
    oversupplied = sorted(
        [m for m in metrics if m.supply_index - m.demand_index >= 15],
        key=lambda m: m.supply_index - m.demand_index, reverse=True,
    )[:5]
    return {
        "id": d.id, "name": d.name, "state": d.state,
        "latitude": d.latitude, "longitude": d.longitude,
        "overall_gap": s.overall_gap, "employment_demand": s.employment_demand,
        "training_supply": s.training_supply, "emerging_count": s.emerging_count,
        "critical_gaps": s.critical_gaps, "high_gaps": s.high_gaps,
        "oversupplied": s.oversupplied,
        "recommendation_count": recinfo.get("total", 0),
        "action_summary": dict(recinfo.get("actions", {})),
        "top_emerging": [
            {"skill": names[m.skill_id], "emergence_score": m.emergence_score,
             "growth_pct": round(m.growth_rate * 100, 1), "label": m.emergence_label}
            for m in top_emerging
        ],
        "top_gaps": [
            {"skill": names[m.skill_id], "gap_score": m.gap_score, "gap_label": m.gap_label,
             "demand_index": m.demand_index, "supply_index": m.supply_index}
            for m in top_gaps
        ],
        "oversupplied_skills": [
            {"skill": names[m.skill_id], "demand_index": m.demand_index,
             "supply_index": m.supply_index}
            for m in oversupplied
        ],
    }


def industry_distribution(db: Session, district_id: int) -> list[dict]:
    rows = (
        db.query(JobPosting.industry, func.count())
        .filter(JobPosting.district_id == district_id)
        .group_by(JobPosting.industry)
        .order_by(func.count().desc())
        .all()
    )
    return [{"industry": ind, "postings": n} for ind, n in rows]


def top_occupations(db: Session, district_id: int, limit: int = 6) -> list[dict]:
    rows = (
        db.query(JobPosting.title, func.count())
        .filter(JobPosting.district_id == district_id)
        .group_by(JobPosting.title)
        .order_by(func.count().desc())
        .limit(limit)
        .all()
    )
    return [{"title": t, "postings": n} for t, n in rows]
