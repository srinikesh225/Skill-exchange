from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DemandPoint(Base):
    """Monthly demand time series: number of postings mentioning a skill in a
    district in a given month. The raw signal behind trends and forecasts."""

    __tablename__ = "demand_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)
    month: Mapped[str] = mapped_column(String(7), index=True)  # "YYYY-MM"
    job_count: Mapped[int] = mapped_column(Integer, default=0)


class SkillMetric(Base):
    """Materialised per-(district, skill) intelligence, computed by the engines.

    Storing the component breakdown as JSON keeps every score explainable: the UI
    can show exactly how the number was composed.
    """

    __tablename__ = "skill_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)

    # Demand
    demand_index: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    demand_components: Mapped[dict] = mapped_column(JSON, default=dict)
    job_postings_count: Mapped[int] = mapped_column(Integer, default=0)

    # Growth / emergence
    growth_rate: Mapped[float] = mapped_column(Float, default=0.0)  # fraction
    emergence_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    emergence_label: Mapped[str] = mapped_column(String(20), default="Stable")

    # Supply
    supply_index: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    supply_components: Mapped[dict] = mapped_column(JSON, default=dict)
    training_seats: Mapped[int] = mapped_column(Integer, default=0)

    # Gap
    gap_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    gap_label: Mapped[str] = mapped_column(String(20), default="Balanced")

    # Salary context (synthetic), INR/month
    avg_salary: Mapped[int] = mapped_column(Integer, default=0)
