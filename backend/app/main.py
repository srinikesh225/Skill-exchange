"""SkillPulse India — FastAPI application entry point.

    uvicorn app.main:app --reload

Serves the district labour-market intelligence API. All figures are synthetic
demo data (see GET /api/meta).
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import (
    analytics,
    courses,
    districts,
    meta,
    recommendations,
    skills,
)
from app.config import get_settings
from app.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("skillpulse")

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Ensure tables exist; data is loaded via scripts/generate_demo_data.py.
    init_db()
    logger.info("SkillPulse India API started (v%s)", __version__)
    yield


app = FastAPI(
    title="SkillPulse India API",
    description=(
        "District-level Labour Market Intelligence & Skill Planning System. "
        "Data → NLP → Statistics → Gap Engine → Recommendation → Visualization. "
        "All figures are synthetic demo data."
    ),
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(districts.router)
app.include_router(skills.router)
app.include_router(courses.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
app.include_router(meta.router)


@app.get("/api/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {"app": "SkillPulse India API", "docs": "/docs", "health": "/api/health"}
