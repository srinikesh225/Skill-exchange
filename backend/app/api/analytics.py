from __future__ import annotations

from collections import defaultdict

import numpy as np
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api import _common
from app.database import get_db
from app.models import (
    Course,
    District,
    EmployerSignal,
    JobPosting,
    Recommendation,
    Skill,
    SkillMetric,
)
from app.services.district_scoring import summarise
from app.services.forecasting import forecast
from app.models import DemandPoint

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def national_overview(db: Session = Depends(get_db)) -> dict:
    metrics = _common.all_metrics_by_district(db)
    names = _common.skill_name_map(db)
    districts = db.query(District).all()

    summaries = []
    for d in districts:
        s = summarise(metrics.get(d.id, []))
        summaries.append((d, s))

    overall_gaps = [s.overall_gap for _, s in summaries]
    demands = [s.employment_demand for _, s in summaries]
    supplies = [s.training_supply for _, s in summaries]

    # National emerging skills (avg emergence across districts, emerging/growing only)
    by_skill: dict[int, list] = defaultdict(list)
    for ms in metrics.values():
        for m in ms:
            by_skill[m.skill_id].append(m)
    emerging = []
    for sid, ms in by_skill.items():
        growth = float(np.mean([m.growth_rate for m in ms]))
        em = float(np.mean([m.emergence_score for m in ms]))
        demand = float(np.mean([m.demand_index for m in ms]))
        if growth > 0.08:
            emerging.append({"skill": names[sid], "skill_id": sid,
                             "emergence_score": round(em, 1),
                             "growth_pct": round(growth * 100, 1),
                             "national_demand": round(demand, 1)})
    emerging.sort(key=lambda x: x["emergence_score"], reverse=True)

    # Action distribution
    action_rows = db.query(Recommendation.action, func.count()).group_by(Recommendation.action).all()
    actions = {a: n for a, n in action_rows}

    # Highest-gap and most-oversupplied districts
    ranked = sorted(summaries, key=lambda t: t[1].overall_gap, reverse=True)
    top_gap_districts = [
        {"district_id": d.id, "district": d.name, "state": d.state,
         "overall_gap": s.overall_gap, "critical_gaps": s.critical_gaps}
        for d, s in ranked[:8]
    ]

    # State-level roll-up
    state_gaps: dict[str, list] = defaultdict(list)
    for d, s in summaries:
        state_gaps[d.state].append(s.overall_gap)
    states = sorted(
        [{"state": st, "avg_gap": round(float(np.mean(v)), 1), "districts": len(v)}
         for st, v in state_gaps.items()],
        key=lambda x: x["avg_gap"], reverse=True,
    )

    return {
        "totals": {
            "districts": len(districts),
            "skills": db.query(func.count(Skill.id)).scalar(),
            "job_postings": db.query(func.count(JobPosting.id)).scalar(),
            "courses": db.query(func.count(Course.id)).scalar(),
            "employer_signals": db.query(func.count(EmployerSignal.id)).scalar(),
            "recommendations": db.query(func.count(Recommendation.id)).scalar(),
        },
        "national_avg_gap": round(float(np.mean(overall_gaps)), 1) if overall_gaps else 0,
        "national_avg_demand": round(float(np.mean(demands)), 1) if demands else 0,
        "national_avg_supply": round(float(np.mean(supplies)), 1) if supplies else 0,
        "action_distribution": actions,
        "top_emerging_skills": emerging[:10],
        "top_gap_districts": top_gap_districts,
        "states": states,
    }


@router.get("/emerging-skills")
def emerging_skills(db: Session = Depends(get_db)) -> list[dict]:
    names = _common.skill_name_map(db)
    by_skill: dict[int, list] = defaultdict(list)
    for m in db.query(SkillMetric).all():
        by_skill[m.skill_id].append(m)
    out = []
    for sid, ms in by_skill.items():
        growth = float(np.mean([m.growth_rate for m in ms]))
        em = float(np.mean([m.emergence_score for m in ms]))
        demand = float(np.mean([m.demand_index for m in ms]))
        out.append({
            "skill_id": sid, "skill": names[sid],
            "emergence_score": round(em, 1), "growth_pct": round(growth * 100, 1),
            "national_demand": round(demand, 1),
        })
    out.sort(key=lambda x: x["emergence_score"], reverse=True)
    return out


@router.get("/forecast")
def analytics_forecast(
    skill_id: int = Query(...),
    district_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> dict:
    q = db.query(DemandPoint.month, func.sum(DemandPoint.job_count)).filter(
        DemandPoint.skill_id == skill_id
    )
    if district_id is not None:
        q = q.filter(DemandPoint.district_id == district_id)
    rows = q.group_by(DemandPoint.month).order_by(DemandPoint.month).all()
    counts = [int(r[1]) for r in rows]
    return {"skill_id": skill_id, "district_id": district_id,
            "months": [r[0] for r in rows], "counts": counts,
            "forecast": forecast(counts, horizon=12)}


@router.get("/compare")
def compare_districts(
    ids: str = Query(..., description="Comma-separated district ids, e.g. 1,2,3"),
    db: Session = Depends(get_db),
) -> dict:
    try:
        id_list = [int(x) for x in ids.split(",") if x.strip()]
    except ValueError:
        id_list = []
    names = _common.skill_name_map(db)
    result = []
    for did in id_list:
        d = db.get(District, did)
        if not d:
            continue
        metrics = db.query(SkillMetric).filter(SkillMetric.district_id == did).all()
        s = summarise(metrics)
        recinfo = _common.rec_counts_by_district(db).get(did, {})
        top_gaps = sorted(metrics, key=lambda m: m.gap_score, reverse=True)[:5]
        top_emerging = sorted(
            [m for m in metrics if m.emergence_label in ("Emerging", "Growing")],
            key=lambda m: m.emergence_score, reverse=True)[:5]
        result.append({
            "district_id": d.id, "district": d.name, "state": d.state,
            "overall_gap": s.overall_gap, "employment_demand": s.employment_demand,
            "training_supply": s.training_supply, "emerging_count": s.emerging_count,
            "critical_gaps": s.critical_gaps, "high_gaps": s.high_gaps,
            "training_capacity": d.training_capacity,
            "recommendation_count": recinfo.get("total", 0),
            "top_gaps": [{"skill": names[m.skill_id], "gap_score": m.gap_score,
                          "gap_label": m.gap_label} for m in top_gaps],
            "top_emerging": [{"skill": names[m.skill_id], "growth_pct": round(m.growth_rate * 100, 1)}
                             for m in top_emerging],
        })
    return {"districts": result}
