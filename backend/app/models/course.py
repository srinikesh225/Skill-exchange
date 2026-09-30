from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Many-to-many: a course teaches several skills.
course_skill = Table(
    "course_skill",
    Base.metadata,
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id"), primary_key=True),
)


class Course(Base):
    """An existing training programme offered in a district."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    provider: Mapped[str] = mapped_column(String(200))
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), index=True)
    duration_weeks: Mapped[int] = mapped_column(Integer, default=12)
    capacity: Mapped[int] = mapped_column(Integer, default=0)       # annual seats
    enrolled: Mapped[int] = mapped_column(Integer, default=0)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0)   # 0-1
    placement_rate: Mapped[float] = mapped_column(Float, default=0.0)    # 0-1
    placement_count: Mapped[int] = mapped_column(Integer, default=0)
    equipment_required: Mapped[str] = mapped_column(String(300), default="")
    trainer_requirements: Mapped[str] = mapped_column(String(300), default="")
    last_updated: Mapped[date] = mapped_column(Date)

    skills: Mapped[list["Skill"]] = relationship(  # noqa: F821
        secondary=course_skill, lazy="selectin"
    )
