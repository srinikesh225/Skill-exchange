from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Recommendation(Base):
    """A district-level training action derived from the gap + supply engines.

    `evidence` holds the machine-readable facts behind the recommendation so the
    UI can render a full 'Why?' explanation. Nothing here is hand-authored per
    district — it is produced by the recommendation engine from the data.
    """

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)

    action: Mapped[str] = mapped_column(String(40), index=True)  # CREATE_COURSE, EXPAND_COURSE, ...
    priority: Mapped[str] = mapped_column(String(20), default="Medium")  # Critical/High/Medium/Low
    priority_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Proposed programme (for CREATE / EXPAND / UPDATE)
    suggested_course: Mapped[str] = mapped_column(String(200), default="")
    suggested_capacity: Mapped[int] = mapped_column(Integer, default=0)
    target_skills: Mapped[list] = mapped_column(JSON, default=list)

    headline: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)


class CourseAlignment(Base):
    """Materialised course-intelligence: how well an existing course matches
    current labour-market demand, plus obsolescence risk."""

    __tablename__ = "course_alignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True, unique=True)
    alignment_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    obsolescence_risk: Mapped[str] = mapped_column(String(20), default="Low")
    components: Mapped[dict] = mapped_column(JSON, default=dict)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list)
    recommendation: Mapped[str] = mapped_column(String(40), default="KEEP")
