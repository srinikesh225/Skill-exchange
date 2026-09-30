from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EmployerSignal(Base):
    """A demand signal from an employer survey / industry consultation for a
    (district, skill) pair. Synthetic demo data."""

    __tablename__ = "employer_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)
    industry: Mapped[str] = mapped_column(String(120))
    demand_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    survey_date: Mapped[date] = mapped_column(Date)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1
