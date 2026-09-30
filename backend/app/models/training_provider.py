from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TrainingProvider(Base):
    """An organisation delivering training in a district (ITI, polytechnic, etc.).
    Names are synthetic and clearly labelled demo data."""

    __tablename__ = "training_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    provider_type: Mapped[str] = mapped_column(String(80), default="ITI")
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), index=True)
