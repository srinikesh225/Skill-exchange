from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.constants import (
    ALIGNMENT_WEIGHTS,
    DEMAND_WEIGHTS,
    EMERGENCE_WEIGHTS,
    GAP_THRESHOLDS,
    SUPPLY_WEIGHTS,
)
from app.database import get_db
from app.models import (
    Course,
    DemandPoint,
    District,
    EmployerSignal,
    JobPosting,
    Recommendation,
    Skill,
)

router = APIRouter(prefix="/api/meta", tags=["meta"])

DISCLAIMER = (
    "Demo dataset — synthetic data for prototype demonstration. "
    "Figures are generated for illustration and are NOT official government "
    "statistics. Recommendations are decision-support outputs and require human "
    "validation before any policy action."
)


@router.get("")
def meta(db: Session = Depends(get_db)) -> dict:
    months = sorted({r[0] for r in db.query(DemandPoint.month).distinct().all()})
    return {
        "app": "SkillPulse India",
        "subtitle": "District-level Labour Market Intelligence for Smarter Skill Development",
        "data_kind": "synthetic-demo",
        "disclaimer": DISCLAIMER,
        "coverage_months": months,
        "last_updated": months[-1] if months else None,
        "provenance": {
            "job_postings": db.query(func.count(JobPosting.id)).scalar(),
            "employer_signals": db.query(func.count(EmployerSignal.id)).scalar(),
            "courses": db.query(func.count(Course.id)).scalar(),
            "districts": db.query(func.count(District.id)).scalar(),
            "skills": db.query(func.count(Skill.id)).scalar(),
            "recommendations": db.query(func.count(Recommendation.id)).scalar(),
        },
        "methodology": {
            "demand_weights": DEMAND_WEIGHTS,
            "emergence_weights": EMERGENCE_WEIGHTS,
            "supply_weights": SUPPLY_WEIGHTS,
            "alignment_weights": ALIGNMENT_WEIGHTS,
            "gap_thresholds": [{"min": t, "label": l} for t, l in GAP_THRESHOLDS],
        },
    }
