from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Course, CourseAlignment, District

router = APIRouter(prefix="/api/courses", tags=["courses"])


def _alignment_map(db: Session, course_ids: list[int] | None = None) -> dict[int, CourseAlignment]:
    q = db.query(CourseAlignment)
    if course_ids is not None:
        q = q.filter(CourseAlignment.course_id.in_(course_ids))
    return {a.course_id: a for a in q.all()}


def _course_dict(c: Course, a: CourseAlignment | None, dname: str) -> dict:
    return {
        "id": c.id, "name": c.name, "provider": c.provider,
        "district_id": c.district_id, "district": dname,
        "duration_weeks": c.duration_weeks, "capacity": c.capacity,
        "enrolled": c.enrolled,
        "utilisation_pct": round(c.enrolled / c.capacity * 100, 1) if c.capacity else 0,
        "completion_rate": c.completion_rate, "placement_rate": c.placement_rate,
        "placement_count": c.placement_count, "last_updated": c.last_updated.isoformat(),
        "skills": [s.canonical_name for s in c.skills],
        "alignment_score": a.alignment_score if a else None,
        "obsolescence_risk": a.obsolescence_risk if a else None,
        "recommendation": a.recommendation if a else None,
        "missing_skills": a.missing_skills if a else [],
        "alignment_components": a.components if a else {},
    }


@router.get("")
def list_courses(
    district_id: int | None = Query(None),
    risk: str | None = Query(None, description="Filter by obsolescence risk: Low/Moderate/High"),
    db: Session = Depends(get_db),
) -> list[dict]:
    q = db.query(Course)
    if district_id is not None:
        q = q.filter(Course.district_id == district_id)
    courses = q.all()
    align = _alignment_map(db, [c.id for c in courses])
    dnames = {d.id: d.name for d in db.query(District).all()}
    out = [_course_dict(c, align.get(c.id), dnames.get(c.district_id, "")) for c in courses]
    if risk:
        out = [c for c in out if c["obsolescence_risk"] == risk]
    out.sort(key=lambda c: (c["alignment_score"] if c["alignment_score"] is not None else 999))
    return out


@router.get("/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)) -> dict:
    c = db.get(Course, course_id)
    if not c:
        raise HTTPException(404, "Course not found")
    a = db.query(CourseAlignment).filter(CourseAlignment.course_id == course_id).first()
    d = db.get(District, c.district_id)
    result = _course_dict(c, a, d.name if d else "")
    result.update({
        "equipment_required": c.equipment_required,
        "trainer_requirements": c.trainer_requirements,
    })
    return result


@router.get("/{course_id}/alignment")
def course_alignment(course_id: int, db: Session = Depends(get_db)) -> dict:
    a = db.query(CourseAlignment).filter(CourseAlignment.course_id == course_id).first()
    if not a:
        raise HTTPException(404, "No alignment computed for this course")
    c = db.get(Course, course_id)
    return {
        "course_id": course_id, "course_name": c.name if c else "",
        "alignment_score": a.alignment_score, "components": a.components,
        "obsolescence_risk": a.obsolescence_risk, "missing_skills": a.missing_skills,
        "recommendation": a.recommendation,
        "covered_skills": [s.canonical_name for s in c.skills] if c else [],
    }
