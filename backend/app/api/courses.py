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
    page: int | None = Query(None, ge=1, description="If set, return a paginated envelope"),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Backward compatible: with no `page`, returns the full array (existing
    behaviour the frontend relies on). With `page`, returns a paginated envelope
    {items, page, page_size, total, total_pages}."""
    q = db.query(Course)
    if district_id is not None:
        q = q.filter(Course.district_id == district_id)
    courses = q.all()
    align = _alignment_map(db, [c.id for c in courses])
    dnames = {d.id: d.name for d in db.query(District).all()}
    out = [_course_dict(c, align.get(c.id), dnames.get(c.district_id, "")) for c in courses]
    if risk:
        out = [c for c in out if c["obsolescence_risk"] == risk]
    # `id` is a deterministic tiebreaker: alignment_score has many ties, and the
    # DB gives no guaranteed row order, so without it two pages could duplicate
    # or skip a tied course. Does not change any computed value.
    out.sort(key=lambda c: (c["alignment_score"] if c["alignment_score"] is not None else 999, c["id"]))

    if page is None:
        return out  # unchanged legacy shape
    total = len(out)
    start = (page - 1) * page_size
    return {
        "items": out[start:start + page_size],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
    }


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
