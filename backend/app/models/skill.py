from __future__ import annotations

from sqlalchemy import JSON, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Skill(Base):
    """A canonical skill in the taxonomy (loosely ESCO-style)."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    # Aliases + related skills stored as JSON lists (portable across SQLite/PG).
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    related_skills: Mapped[list] = mapped_column(JSON, default=list)
    # Seed hint only; the emergence *label* is derived from data by the engine.
    emerging_flag: Mapped[bool] = mapped_column(Boolean, default=False)
