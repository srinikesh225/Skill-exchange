"""API smoke tests using FastAPI's TestClient against the generated demo DB.

Run `python scripts/generate_demo_data.py` first so the database is populated.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import District

client = TestClient(app)


@pytest.fixture(scope="module")
def sample_district_id() -> int:
    db = SessionLocal()
    try:
        d = db.query(District).first()
        if not d:
            pytest.skip("No demo data; run scripts/generate_demo_data.py first")
        return d.id
    finally:
        db.close()


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_meta_declares_synthetic():
    r = client.get("/api/meta")
    assert r.status_code == 200
    body = r.json()
    assert body["data_kind"] == "synthetic-demo"
    assert "synthetic" in body["disclaimer"].lower()
    # Methodology weights are exposed for transparency.
    assert abs(sum(body["methodology"]["demand_weights"].values()) - 1.0) < 1e-9


def test_districts_list_has_intelligence(sample_district_id):
    r = client.get("/api/districts")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 100
    first = data[0]
    for key in ("overall_gap", "top_gaps", "top_emerging", "latitude", "longitude"):
        assert key in first


def test_district_detail_and_gaps(sample_district_id):
    r = client.get(f"/api/districts/{sample_district_id}")
    assert r.status_code == 200
    assert "industries" in r.json()

    g = client.get(f"/api/districts/{sample_district_id}/gaps")
    assert g.status_code == 200
    gaps = g.json()
    # Gaps sorted descending.
    scores = [x["gap_score"] for x in gaps]
    assert scores == sorted(scores, reverse=True)


def test_recommendations_have_evidence(sample_district_id):
    r = client.get(f"/api/districts/{sample_district_id}/recommendations")
    assert r.status_code == 200
    recs = r.json()
    if recs:
        assert "evidence" in recs[0]
        assert "rationale" in recs[0]["evidence"]


def test_skill_extraction_endpoint():
    r = client.get("/api/skills/extract", params={"text": "python and aws and docker"})
    assert r.status_code == 200
    skills = {s["skill"] for s in r.json()["skills"]}
    assert {"Python", "AWS", "Docker"} <= skills


def test_analytics_overview():
    r = client.get("/api/analytics/overview")
    assert r.status_code == 200
    body = r.json()
    assert body["totals"]["districts"] >= 100
    assert "action_distribution" in body


def test_compare_two_districts():
    r = client.get("/api/districts")
    ids = [d["id"] for d in r.json()[:2]]
    c = client.get("/api/analytics/compare", params={"ids": ",".join(map(str, ids))})
    assert c.status_code == 200
    assert len(c.json()["districts"]) == 2


def test_404_for_missing_district():
    r = client.get("/api/districts/999999")
    assert r.status_code == 404
