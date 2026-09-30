from __future__ import annotations

from collections import Counter, defaultdict

import numpy as np
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api import _common
from app.database import get_db
from app.models import DemandPoint, District, JobPosting, Skill, SkillMetric
from app.services import demand_engine, gap_engine
from app.services.forecasting import forecast
from app.services.skill_extraction import extract_skills

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("")
def list_skills(db: Session = Depends(get_db)) -> list[dict]:
    """Skills with national-average demand/gap (averaged across districts)."""
    agg: dict[int, list[SkillMetric]] = defaultdict(list)
    for m in db.query(SkillMetric).all():
        agg[m.skill_id].append(m)
    out = []
    for s in db.query(Skill).order_by(Skill.canonical_name).all():
        ms = agg.get(s.id, [])
        demand = round(float(np.mean([m.demand_index for m in ms])), 1) if ms else 0.0
        gap = round(float(np.mean([m.gap_score for m in ms])), 1) if ms else 0.0
        growth = round(float(np.mean([m.growth_rate for m in ms])) * 100, 1) if ms else 0.0
        labels = Counter(m.emergence_label for m in ms)
        out.append({
            "id": s.id, "canonical_name": s.canonical_name, "category": s.category,
            "aliases": s.aliases, "related_skills": s.related_skills,
            "national_demand": demand, "national_gap": gap, "national_growth_pct": growth,
            "dominant_label": labels.most_common(1)[0][0] if labels else "Stable",
            "districts_present": len(ms),
        })
    return out


@router.get("/extract")
def extract_demo(
    text: str = Query(..., description="Free text (e.g. a job description) to analyse"),
    db: Session = Depends(get_db),
) -> dict:
    """Live demonstration of the skill-extraction pipeline on arbitrary text."""
    results = extract_skills(text)
    return {"input": text, "skills": results, "count": len(results)}


@router.post("/extract")
def extract_demo_post(payload: dict = Body(...)) -> dict:
    text = payload.get("text", "")
    results = extract_skills(text)
    return {"input": text, "skills": results, "count": len(results)}


@router.get("/{skill_id}")
def get_skill(skill_id: int, db: Session = Depends(get_db)) -> dict:
    s = db.get(Skill, skill_id)
    if not s:
        raise HTTPException(404, "Skill not found")
    metrics = db.query(SkillMetric).filter(SkillMetric.skill_id == skill_id).all()
    dnames = {d.id: d.name for d in db.query(District).all()}
    top_districts = sorted(metrics, key=lambda m: m.demand_index, reverse=True)[:8]
    return {
        "id": s.id, "canonical_name": s.canonical_name, "category": s.category,
        "description": s.description, "aliases": s.aliases, "related_skills": s.related_skills,
        "national_demand": round(float(np.mean([m.demand_index for m in metrics])), 1) if metrics else 0,
        "national_gap": round(float(np.mean([m.gap_score for m in metrics])), 1) if metrics else 0,
        "top_districts": [
            {"district_id": m.district_id, "district": dnames.get(m.district_id, ""),
             "demand_index": m.demand_index, "gap_score": m.gap_score,
             "gap_label": m.gap_label, "growth_pct": round(m.growth_rate * 100, 1)}
            for m in top_districts
        ],
    }


@router.get("/{skill_id}/trend")
def skill_trend(
    skill_id: int,
    district_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> dict:
    if not db.get(Skill, skill_id):
        raise HTTPException(404, "Skill not found")
    q = db.query(DemandPoint.month, func.sum(DemandPoint.job_count)).filter(
        DemandPoint.skill_id == skill_id
    )
    if district_id is not None:
        q = q.filter(DemandPoint.district_id == district_id)
    rows = q.group_by(DemandPoint.month).order_by(DemandPoint.month).all()
    months = [r[0] for r in rows]
    counts = [int(r[1]) for r in rows]
    fc = forecast(counts, horizon=12)
    return {
        "skill_id": skill_id, "district_id": district_id,
        "months": months, "counts": counts, "forecast": fc,
    }


@router.get("/{skill_id}/metric")
def skill_metric_detail(
    skill_id: int,
    district_id: int = Query(..., description="District to explain the skill for"),
    db: Session = Depends(get_db),
) -> dict:
    s = db.get(Skill, skill_id)
    if not s:
        raise HTTPException(404, "Skill not found")
    m = (
        db.query(SkillMetric)
        .filter(SkillMetric.skill_id == skill_id, SkillMetric.district_id == district_id)
        .first()
    )
    if not m:
        raise HTTPException(404, "No metric for this district/skill pair")

    # Top industries/occupations requesting this skill in the district.
    postings = db.query(JobPosting).filter(JobPosting.district_id == district_id).all()
    industries: Counter = Counter()
    occupations: Counter = Counter()
    for jp in postings:
        if s.canonical_name in jp.skills:
            industries[jp.industry] += 1
            occupations[jp.title] += 1

    return {
        "skill_id": skill_id, "skill": s.canonical_name, "category": s.category,
        "district_id": district_id,
        "demand": demand_engine.explain_demand(m.demand_components),
        "supply": gap_engine.explain_supply(m.supply_components),
        "gap_score": m.gap_score, "gap_label": m.gap_label,
        "growth_pct": round(m.growth_rate * 100, 1),
        "emergence_score": m.emergence_score, "emergence_label": m.emergence_label,
        "job_postings_count": m.job_postings_count, "training_seats": m.training_seats,
        "avg_salary": m.avg_salary, "related_skills": s.related_skills,
        "top_industries": [{"industry": k, "postings": v} for k, v in industries.most_common(5)],
        "top_occupations": [{"title": k, "postings": v} for k, v in occupations.most_common(5)],
    }
