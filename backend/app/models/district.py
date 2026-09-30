from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class District(Base):
    """An Indian district. Names and coordinates are real geographic facts.

    All labour-market metrics (population, LFPR, WPR, unemployment, capacity) are
    SYNTHETIC demo values, generated deterministically and clearly labelled as
    such throughout the UI. They are not official statistics.
    """

    __tablename__ = "districts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    state: Mapped[str] = mapped_column(String(120), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    # Synthetic demo demographics
    population: Mapped[int] = mapped_column(Integer, default=0)
    working_population: Mapped[int] = mapped_column(Integer, default=0)
    youth_population: Mapped[int] = mapped_column(Integer, default=0)
    unemployment_rate: Mapped[float] = mapped_column(Float, default=0.0)  # %
    lfpr: Mapped[float] = mapped_column(Float, default=0.0)  # labour force participation rate %
    wpr: Mapped[float] = mapped_column(Float, default=0.0)  # worker population ratio %
    training_capacity: Mapped[int] = mapped_column(Integer, default=0)  # total annual seats
