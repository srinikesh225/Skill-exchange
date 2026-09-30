from __future__ import annotations

from datetime import date

from sqlalchemy import JSON, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class JobPosting(Base):
    """A single job advertisement. `skills` holds the canonical skills extracted
    from the description by the skill-extraction pipeline (not hand-labelled)."""

    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    company: Mapped[str] = mapped_column(String(200))
    industry: Mapped[str] = mapped_column(String(120), index=True)
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), index=True)
    state: Mapped[str] = mapped_column(String(120), index=True)
    date_posted: Mapped[date] = mapped_column(Date, index=True)
    salary_min: Mapped[int] = mapped_column(Integer, default=0)  # INR / month
    salary_max: Mapped[int] = mapped_column(Integer, default=0)
    experience_level: Mapped[str] = mapped_column(String(40), default="Mid")
    description: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(80), default="synthetic")
    # Extracted canonical skill names, e.g. ["Python", "Machine Learning"].
    skills: Mapped[list] = mapped_column(JSON, default=list)
