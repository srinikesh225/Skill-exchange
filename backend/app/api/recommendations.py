from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import District, Recommendation, Skill

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("")
def list_recommendations(
    action: str | None = Query(None),
    priority: str | None = Query(None),
    district_id: int | None = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
) -> list[dict]:
    q = db.query(Recommendation)
    if action:
        q = q.filter(Recommendation.action == action)
    if priority:
        q = q.filter(Recommendation.priority == priority)
    if district_id is not None:
        q = q.filter(Recommendation.district_id == district_id)
    recs = q.order_by(Recommendation.priority_score.desc()).limit(limit).all()
    dnames = {d.id: d.name for d in db.query(District).all()}
    snames = {s.id: s.canonical_name for s in db.query(Skill).all()}
    return [
        {
            "id": r.id, "district_id": r.district_id,
            "district": dnames.get(r.district_id, ""),
            "skill_id": r.skill_id, "skill": snames.get(r.skill_id, ""),
            "action": r.action, "priority": r.priority, "priority_score": r.priority_score,
            "suggested_course": r.suggested_course, "suggested_capacity": r.suggested_capacity,
            "target_skills": r.target_skills, "headline": r.headline, "evidence": r.evidence,
        }
        for r in recs
    ]
