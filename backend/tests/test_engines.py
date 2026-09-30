"""Unit tests for the scoring engines (pure functions, no database)."""

from __future__ import annotations

from datetime import date

import pytest

from app.constants import DEMAND_WEIGHTS
from app.services import course_intelligence, demand_engine, forecasting, gap_engine
from app.services.recommendation_engine import build_recommendation, suggest_capacity
from app.services.skill_extraction import extract_skill_names, extract_skills
from app.services.skill_normalization import normalize_term


# --- Normalisation ---------------------------------------------------------

@pytest.mark.parametrize("surface,expected", [
    ("Python 3", "Python"),
    ("python developer", "Python"),
    ("Amazon Web Services", "AWS"),
    ("AWS Cloud", "AWS"),
    ("k8s", "Kubernetes"),
    ("cyber security", "Cybersecurity"),
    ("devsecops", "Cloud Security"),
])
def test_normalize_known_aliases(surface, expected):
    canon, conf = normalize_term(surface)
    assert canon == expected
    assert 0 < conf <= 1


def test_normalize_unknown_returns_none():
    canon, conf = normalize_term("xyzzy quux nonskill")
    assert canon is None
    assert conf == 0.0


# --- Extraction ------------------------------------------------------------

def test_extraction_finds_multiple_skills():
    text = ("We need a Python developer with machine learning and AWS experience. "
            "Knowledge of Kubernetes and cyber security is a plus.")
    found = set(extract_skill_names(text))
    assert {"Python", "Machine Learning", "AWS", "Kubernetes", "Cybersecurity"} <= found


def test_extraction_boundary_punctuation():
    # Trailing period must not block the match.
    found = set(extract_skill_names("Experience with devsecops."))
    assert "Cloud Security" in found


def test_extraction_confidence_sorted():
    results = extract_skills("python and sql and docker")
    confs = [r["confidence"] for r in results]
    assert confs == sorted(confs, reverse=True)


# --- Demand ----------------------------------------------------------------

def test_demand_index_full_components_is_100():
    comps = {k: 100.0 for k in DEMAND_WEIGHTS}
    assert demand_engine.demand_index(comps) == pytest.approx(100.0)


def test_demand_explanation_contributions_sum_to_index():
    comps = {"job_volume": 80, "job_growth": 40, "employer_signal": 60,
             "salary_premium": 30, "industry_growth": 50, "emerging_signal": 70}
    exp = demand_engine.explain_demand(comps)
    assert exp["index"] == pytest.approx(sum(exp["contributions"].values()), abs=0.11)


# --- Emergence -------------------------------------------------------------

@pytest.mark.parametrize("growth,label", [
    (0.50, "Emerging"), (0.15, "Growing"), (0.0, "Stable"), (-0.30, "Declining"),
])
def test_emergence_labels(growth, label):
    assert demand_engine.emergence_label(growth) == label


# --- Supply + gap ----------------------------------------------------------

def test_gap_is_demand_minus_supply_clamped():
    assert gap_engine.gap_score(80, 30) == 50
    assert gap_engine.gap_score(20, 90) == 0  # clamped, never negative


@pytest.mark.parametrize("score,label", [
    (70, "Critical"), (45, "High"), (25, "Moderate"), (5, "Balanced"),
])
def test_gap_labels(score, label):
    assert gap_engine.gap_label(score) == label


def test_no_supply_gives_low_supply_index():
    comps = gap_engine.supply_components(
        seats=0, seats_lo=0, seats_hi=1000, completion_rate=0,
        placement_rate=0, pipeline=0, pipeline_lo=0, pipeline_hi=1000)
    assert gap_engine.supply_index(comps) == pytest.approx(0.0)


# --- Forecasting -----------------------------------------------------------

def test_forecast_horizon_and_milestones():
    fc = forecasting.forecast([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], horizon=12)
    assert len(fc["points"]) == 12
    assert fc["milestones"]["12m"]["upper"] >= fc["milestones"]["12m"]["point"]
    assert fc["milestones"]["12m"]["lower"] <= fc["milestones"]["12m"]["point"]


def test_forecast_uptrend_predicts_growth():
    fc = forecasting.forecast([2, 4, 6, 8, 10, 12], horizon=6)
    assert fc["points"][-1] > 12  # continues upward


# --- Recommendation --------------------------------------------------------

def _base_ctx(**over):
    ctx = dict(
        skill_name="Cloud Security", skill_category="Security",
        related_skills=["AWS", "Cybersecurity"], demand_index=88.0, supply_index=20.0,
        gap_score=68.0, gap_label="Critical", emergence_label="Emerging",
        emergence_score=85.0, growth_rate=0.4, job_postings_count=120,
        employer_count=8, cross_industry=4, avg_salary=90000, seats=0, enrolled=0,
        placement_rate=0.0, has_course=False, course_names=[],
        missing_modern_skills=[], district_scale=0.9, district_name="Pune")
    ctx.update(over)
    return ctx


def test_recommendation_create_course_for_uncovered_critical_gap():
    rec = build_recommendation(_base_ctx())
    assert rec["action"] == "CREATE_COURSE"
    assert rec["suggested_capacity"] > 0
    assert rec["evidence"]["rationale"]


def test_recommendation_expand_when_course_exists():
    rec = build_recommendation(_base_ctx(has_course=True, seats=60, placement_rate=0.6))
    assert rec["action"] == "EXPAND_COURSE"


def test_recommendation_reduce_for_declining_oversupply():
    rec = build_recommendation(_base_ctx(
        emergence_label="Declining", growth_rate=-0.2, demand_index=20,
        supply_index=70, gap_score=0, gap_label="Balanced", has_course=True, seats=200))
    assert rec["action"] == "REDUCE_CAPACITY"


def test_recommendation_none_when_balanced():
    rec = build_recommendation(_base_ctx(
        gap_label="Balanced", gap_score=10, emergence_label="Stable",
        demand_index=40, supply_index=35, has_course=True, seats=50, placement_rate=0.7))
    assert rec is None


def test_suggested_capacity_bounds_and_rounding():
    cap = suggest_capacity(90, 70, 0.9)
    assert 50 <= cap <= 400
    assert cap % 25 == 0


# --- Course intelligence ---------------------------------------------------

def test_stale_low_demand_course_flagged():
    result = course_intelligence.analyse_course(
        avg_skill_demand=30, placement_rate=0.3, enrolled=20, capacity=100,
        last_updated=date(2022, 1, 1), today=date(2026, 9, 30),
        missing_skills=["React", "Docker"], mostly_declining=True)
    assert result["obsolescence_risk"] in ("High", "Moderate")
    assert result["recommendation"] in ("RETIRE_OR_REDUCE", "UPDATE_CURRICULUM", "REVIEW")


def test_fresh_high_demand_course_kept():
    result = course_intelligence.analyse_course(
        avg_skill_demand=85, placement_rate=0.85, enrolled=95, capacity=100,
        last_updated=date(2026, 6, 1), today=date(2026, 9, 30),
        missing_skills=[], mostly_declining=False)
    assert result["recommendation"] == "KEEP"
