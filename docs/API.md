# API Reference

Base URL: `http://127.0.0.1:8000`. Interactive OpenAPI docs: **`/docs`**.
All responses are JSON. All figures are synthetic demo data.

## Meta / health

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Liveness check. |
| GET | `/api/meta` | Provenance: counts, coverage months, disclaimer, **methodology weights**. |

## Districts

| Method | Path | Description |
|---|---|---|
| GET | `/api/districts` | All districts + headline intelligence (powers the map). |
| GET | `/api/districts/{id}` | District detail: demographics, industries, occupations, summary. |
| GET | `/api/districts/{id}/skills` | All skill metrics for the district. |
| GET | `/api/districts/{id}/gaps?min_label=` | Gaps sorted desc; optional min severity filter. |
| GET | `/api/districts/{id}/recommendations` | Recommendations sorted by priority. |

## Skills

| Method | Path | Description |
|---|---|---|
| GET | `/api/skills` | All skills with national-average demand/gap/growth. |
| GET | `/api/skills/{id}` | Skill detail + top districts by demand. |
| GET | `/api/skills/{id}/trend?district_id=` | Monthly series + 12-month forecast. |
| GET | `/api/skills/{id}/metric?district_id=` | Full demand/supply breakdown for a (skill, district). |
| GET/POST | `/api/skills/extract` | **Live skill extraction** on arbitrary text (`?text=` or `{text}`). |

## Courses

| Method | Path | Description |
|---|---|---|
| GET | `/api/courses?district_id=&risk=` | Courses + alignment; filter by district / obsolescence risk. |
| GET | `/api/courses/{id}` | Course detail + alignment components + missing skills. |
| GET | `/api/courses/{id}/alignment` | Alignment record only. |

## Recommendations

| Method | Path | Description |
|---|---|---|
| GET | `/api/recommendations?action=&priority=&district_id=&limit=` | Filterable global list. |

## Analytics

| Method | Path | Description |
|---|---|---|
| GET | `/api/analytics/overview` | National totals, avg gap, top emerging, top-gap districts, states. |
| GET | `/api/analytics/emerging-skills` | National emerging-skill ranking. |
| GET | `/api/analytics/forecast?skill_id=&district_id=` | Forecast for a skill (optionally per district). |
| GET | `/api/analytics/compare?ids=1,2,3` | Side-by-side district comparison. |

---

## Example: recommendation with evidence

`GET /api/districts/2/recommendations` →

```json
[
  {
    "action": "CREATE_COURSE",
    "priority": "Critical",
    "priority_score": 71.2,
    "suggested_course": "Applied Azure",
    "suggested_capacity": 350,
    "target_skills": ["Azure", "Docker", "Kubernetes"],
    "headline": "Launch \"Applied Azure\" in Hyderabad (350 seats)",
    "evidence": {
      "demand_index": 71.1, "supply_index": 0.0, "gap_score": 71.1,
      "gap_label": "Critical", "emergence_label": "Emerging",
      "growth_rate_pct": 116.7, "job_postings": 30, "employers": 2,
      "cross_industry": 3, "training_seats": 0, "placement_rate_pct": 0.0,
      "avg_salary": 95522,
      "rationale": [
        "Critical skill gap (71) with no local training programme",
        "30 relevant postings and 2 employers signalling demand",
        "Demand index 71 vs supply 0"
      ],
      "equipment_note": null,
      "existing_courses": []
    }
  }
]
```

## Example: live skill extraction

`GET /api/skills/extract?text=Python developer with AWS and devsecops` →

```json
{
  "input": "Python developer with AWS and devsecops",
  "count": 3,
  "skills": [
    {"skill": "Python", "confidence": 0.97, "method": "dictionary"},
    {"skill": "AWS", "confidence": 0.97, "method": "dictionary"},
    {"skill": "Cloud Security", "confidence": 0.97, "method": "dictionary"}
  ]
}
```

## Security notes

- CORS is restricted to configured origins (`CORS_ORIGINS`).
- Only `GET`/`POST` are allowed; the API is read-only over the dataset.
- SQLAlchemy parameterised queries (no string-built SQL) → SQL-injection safe.
- No secrets are committed; `.env.example` documents configuration.
- The optional LLM layer reads its key from the environment only.
