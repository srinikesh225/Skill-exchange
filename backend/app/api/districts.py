from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import _common
from app.database import get_db
from app.models import District, Recommendation, SkillMetric

router = APIRouter(prefix="/api/districts", tags=["districts"])


@router.get("")
def list_districts(db: Session = Depends(get_db)) -> list[dict]:
    """All districts with headline intelligence — powers the map + directory."""
    districts = db.query(District).order_by(District.name).all()
    metrics = _common.all_metrics_by_district(db)
    recs = _common.rec_counts_by_district(db)
    names = _common.skill_name_map(db)
    return [
        _common.district_summary_dict(d, metrics.get(d.id, []), recs.get(d.id, {}), names)
        for d in districts
    ]


@router.get("/{district_id}")
def get_district(district_id: int, db: Session = Depends(get_db)) -> dict:
    d = db.get(District, district_id)
    if not d:
        raise HTTPException(404, "District not found")
    metrics = db.query(SkillMetric).filter(SkillMetric.district_id == district_id).all()
    recs = _common.rec_counts_by_district(db).get(district_id, {})
    names = _common.skill_name_map(db)
    summary = _common.district_summary_dict(d, metrics, recs, names)
    summary.update({
        "population": d.population, "working_population": d.working_population,
        "youth_population": d.youth_population, "unemployment_rate": d.unemployment_rate,
        "lfpr": d.lfpr, "wpr": d.wpr, "training_capacity": d.training_capacity,
        "industries": _common.industry_distribution(db, district_id),
        "top_occupations": _common.top_occupations(db, district_id),
        "skill_count": len(metrics),
    })
    return summary


@router.get("/{district_id}/skills")
def district_skills(district_id: int, db: Session = Depends(get_db)) -> list[dict]:
    if not db.get(District, district_id):
        raise HTTPException(404, "District not found")
    names = _common.skill_name_map(db)
    metrics = db.query(SkillMetric).filter(SkillMetric.district_id == district_id).all()
    return [_metric_dict(m, names) for m in sorted(metrics, key=lambda m: m.demand_index, reverse=True)]


@router.get("/{district_id}/gaps")
def district_gaps(
    district_id: int,
    min_label: str | None = Query(None, description="Filter: Critical/High/Moderate"),
    db: Session = Depends(get_db),
) -> list[dict]:
    if not db.get(District, district_id):
        raise HTTPException(404, "District not found")
    names = _common.skill_name_map(db)
    metrics = db.query(SkillMetric).filter(SkillMetric.district_id == district_id).all()
    metrics = sorted(metrics, key=lambda m: m.gap_score, reverse=True)
    if min_label:
        order = {"Balanced": 0, "Moderate": 1, "High": 2, "Critical": 3}
        threshold = order.get(min_label, 0)
        metrics = [m for m in metrics if order.get(m.gap_label, 0) >= threshold]
    return [_metric_dict(m, names) for m in metrics]


@router.get("/{district_id}/recommendations")
def district_recommendations(district_id: int, db: Session = Depends(get_db)) -> list[dict]:
    if not db.get(District, district_id):
        raise HTTPException(404, "District not found")
    names = _common.skill_name_map(db)
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.district_id == district_id)
        .order_by(Recommendation.priority_score.desc())
        .all()
    )
    return [_rec_dict(r, names) for r in recs]


def _metric_dict(m: SkillMetric, names: dict[int, str]) -> dict:
    return {
        "skill_id": m.skill_id, "skill": names.get(m.skill_id, ""),
        "demand_index": m.demand_index, "demand_components": m.demand_components,
        "supply_index": m.supply_index, "supply_components": m.supply_components,
        "gap_score": m.gap_score, "gap_label": m.gap_label,
        "growth_rate": m.growth_rate, "growth_pct": round(m.growth_rate * 100, 1),
        "emergence_score": m.emergence_score, "emergence_label": m.emergence_label,
        "job_postings_count": m.job_postings_count, "training_seats": m.training_seats,
        "avg_salary": m.avg_salary,
    }


def _rec_dict(r: Recommendation, names: dict[int, str]) -> dict:
    return {
        "id": r.id, "skill_id": r.skill_id, "skill": names.get(r.skill_id, ""),
        "action": r.action, "priority": r.priority, "priority_score": r.priority_score,
        "suggested_course": r.suggested_course, "suggested_capacity": r.suggested_capacity,
        "target_skills": r.target_skills, "headline": r.headline, "evidence": r.evidence,
    }
