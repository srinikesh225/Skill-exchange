"""Synthetic demo-data generator.

Produces an internally-consistent dataset: a district's economy drives its
industry mix, which drives skill demand and salary, while training supply
deliberately lags for newer skills (low supply_maturity). The gap/recommendation
engines then DISCOVER shortages from this data — nothing is hard-coded per
district. All output is clearly-labelled synthetic demo data.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from sqlalchemy import delete, insert
from sqlalchemy.orm import Session

from app.config import get_settings
from app.data.districts import DISTRICTS
from app.data.taxonomy import SKILLS
from app.models import (
    Course,
    DemandPoint,
    District,
    EmployerSignal,
    JobPosting,
    Skill,
    TrainingProvider,
    course_skill,
)
from app.services.skill_extraction import extract_skill_names

TODAY = date(2026, 9, 30)

ARCHETYPE_INDUSTRY_WEIGHTS: dict[str, dict[str, float]] = {
    "IT_HUB": {"IT & Software": 0.30, "Cloud & Data": 0.22, "Cybersecurity": 0.12,
               "Fintech & BFSI": 0.14, "Retail & E-commerce": 0.10, "Telecom": 0.06,
               "Healthcare & Pharma": 0.06},
    "EMERGING_TECH": {"IT & Software": 0.24, "Cloud & Data": 0.14, "Fintech & BFSI": 0.12,
                      "Retail & E-commerce": 0.14, "Telecom": 0.08, "Healthcare & Pharma": 0.10,
                      "Manufacturing": 0.10, "Cybersecurity": 0.08},
    "MANUFACTURING": {"Manufacturing": 0.30, "Automotive": 0.20, "Energy & Utilities": 0.14,
                      "Construction": 0.12, "Logistics": 0.12, "IT & Software": 0.06,
                      "Retail & E-commerce": 0.06},
    "MIXED": {"IT & Software": 0.14, "Manufacturing": 0.14, "Retail & E-commerce": 0.14,
              "Healthcare & Pharma": 0.12, "Fintech & BFSI": 0.10, "Construction": 0.10,
              "Logistics": 0.10, "AgriTech": 0.08, "Cloud & Data": 0.08},
    "AGRI_SERVICES": {"AgriTech": 0.22, "Construction": 0.16, "Healthcare & Pharma": 0.14,
                      "Retail & E-commerce": 0.14, "Logistics": 0.12, "Manufacturing": 0.10,
                      "Energy & Utilities": 0.06, "IT & Software": 0.06},
}

HIGH_VALUE_CATEGORIES = {"Data & AI", "Cloud", "Security", "DevOps"}
MID_VALUE_CATEGORIES = {"Programming", "Web Development", "Data", "Engineering",
                        "Embedded & Hardware", "Green Skills"}

_EXPERIENCE = ["Entry", "Mid", "Senior"]
_BASE_SALARY = {"Entry": 22000, "Mid": 55000, "Senior": 105000}  # INR / month

_COMPANY_STEMS = ["Nova", "Meridian", "Axis", "Summit", "Orbit", "Vertex", "Pinnacle",
                  "Catalyst", "Beacon", "Harbor", "Forge", "Kinetic", "Lumen", "Strata"]
_COMPANY_SUFFIX = {"IT & Software": "Technologies", "Cloud & Data": "Data Systems",
                   "Cybersecurity": "Security Labs", "Fintech & BFSI": "Financial Services",
                   "Manufacturing": "Industries", "Automotive": "Motors",
                   "Healthcare & Pharma": "Healthcare", "Retail & E-commerce": "Retail",
                   "Telecom": "Communications", "Energy & Utilities": "Energy",
                   "Construction": "Infra", "AgriTech": "AgriTech", "Logistics": "Logistics"}


def _months_window(n: int = 12) -> list[str]:
    months: list[str] = []
    y, m = TODAY.year, TODAY.month
    for _ in range(n):
        months.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    return list(reversed(months))


def _weighted_sample(rng: random.Random, items: list, weights: list[float], k: int) -> list:
    """Sample up to k distinct items by weight (without replacement)."""
    chosen: list = []
    pool = list(zip(items, weights))
    for _ in range(min(k, len(pool))):
        total = sum(w for _, w in pool)
        if total <= 0:
            break
        r = rng.uniform(0, total)
        acc = 0.0
        for idx, (it, w) in enumerate(pool):
            acc += w
            if acc >= r:
                chosen.append(it)
                pool.pop(idx)
                break
    return chosen


def _salary_tier(category: str) -> float:
    if category in HIGH_VALUE_CATEGORIES:
        return 1.5
    if category in MID_VALUE_CATEGORIES:
        return 1.15
    return 0.85


def _district_scale(tech: float, archetype: str) -> float:
    base = 0.6 + tech * 0.6
    if archetype == "IT_HUB":
        base += 0.25
    return min(1.6, base)


def generate(db: Session, verbose: bool = True) -> dict:
    settings = get_settings()
    rng = random.Random(settings.demo_seed)
    months = _months_window(12)

    # --- Clean slate --------------------------------------------------------
    for model in (course_skill, DemandPoint, EmployerSignal, JobPosting, Course,
                  TrainingProvider):
        db.execute(delete(model))
    db.execute(delete(Skill))
    db.execute(delete(District))
    db.commit()

    # --- Skills -------------------------------------------------------------
    skill_rows = []
    for s in SKILLS:
        skill_rows.append(Skill(
            canonical_name=s["name"], category=s["category"],
            description=s.get("description", ""), aliases=s.get("aliases", []),
            related_skills=s.get("related", []), emerging_flag=s.get("trend", 1.0) >= 1.04,
        ))
    db.add_all(skill_rows)
    db.commit()
    skill_by_name = {sk.canonical_name: sk for sk in db.query(Skill).all()}
    meta_by_name = {s["name"]: s for s in SKILLS}

    # --- Districts ----------------------------------------------------------
    district_objs = []
    for (name, state, lat, lon, archetype, tech) in DISTRICTS:
        pop = int(rng.uniform(0.6, 3.5) * 1_000_000 * (0.7 + tech))
        working = int(pop * rng.uniform(0.45, 0.55))
        youth = int(pop * rng.uniform(0.18, 0.24))
        d = District(
            name=name, state=state, latitude=lat, longitude=lon,
            population=pop, working_population=working, youth_population=youth,
            unemployment_rate=round(rng.uniform(3.0, 12.0), 1),
            lfpr=round(rng.uniform(46.0, 64.0), 1),
            wpr=round(rng.uniform(40.0, 58.0), 1),
            training_capacity=int(working * rng.uniform(0.002, 0.006)),
        )
        d._archetype = archetype  # type: ignore[attr-defined]  (transient)
        d._tech = tech            # type: ignore[attr-defined]
        district_objs.append(d)
    db.add_all(district_objs)
    db.commit()

    districts = db.query(District).all()
    # Re-attach transient attrs by name (query returns fresh objects).
    arch_by_name = {row[0]: (row[4], row[5]) for row in DISTRICTS}

    posting_rows: list[dict] = []
    demand_counts: dict[tuple[int, int, str], int] = {}
    employer_rows: list[dict] = []
    course_link_rows: list[dict] = []
    course_rows: list[Course] = []
    provider_rows: list[TrainingProvider] = []

    all_skill_names = [s["name"] for s in SKILLS]

    for d in districts:
        archetype, tech = arch_by_name[d.name]
        ind_weights = ARCHETYPE_INDUSTRY_WEIGHTS[archetype]
        industries = list(ind_weights.keys())
        iw = list(ind_weights.values())

        # Precompute per-skill affinity in this district.
        affinity: dict[str, float] = {}
        for s in SKILLS:
            match = sum(ind_weights.get(ind, 0.0) for ind in s["industries"])
            affinity[s["name"]] = s["base_popularity"] * (0.15 + match)

        # --- Training providers ---
        n_providers = rng.randint(2, 5)
        for i in range(n_providers):
            provider_rows.append(TrainingProvider(
                name=f"{d.name} {rng.choice(['ITI', 'Polytechnic', 'Skill Centre', 'Community College'])} {i+1}",
                provider_type=rng.choice(["ITI", "Polytechnic", "Private", "PPP"]),
                district_id=d.id,
            ))

        # --- Job postings across 12 months, trend applied per skill ---
        scale = _district_scale(tech, archetype)
        total_jobs = int(settings.demo_jobs_per_district * scale)
        per_month = max(1, total_jobs // 12)

        for m_idx, month in enumerate(months):
            for _ in range(per_month + rng.randint(-3, 4)):
                industry = rng.choices(industries, weights=iw, k=1)[0]
                cand = [s for s in SKILLS if industry in s["industries"]]
                if not cand:
                    cand = SKILLS
                weights = [affinity[s["name"]] * (s["trend"] ** m_idx) for s in cand]
                k = rng.randint(3, 6)
                picked = _weighted_sample(rng, cand, weights, k)
                if not picked:
                    continue
                primary = picked[0]
                exp = rng.choices(_EXPERIENCE, weights=[0.4, 0.42, 0.18], k=1)[0]
                tier = max(_salary_tier(s["category"]) for s in picked)
                base = _BASE_SALARY[exp]
                smin = int(base * tier * rng.uniform(0.85, 1.0))
                smax = int(base * tier * rng.uniform(1.1, 1.35))
                day = rng.randint(1, 28)
                posted = date(int(month[:4]), int(month[5:]), day)
                skill_list = [s["name"] for s in picked]
                description = _build_description(primary, picked, industry, d.name, exp)
                # Prove extraction: recover skills from the text (dictionary layer).
                extracted = extract_skill_names(description, use_semantic=False)
                skills_final = extracted or skill_list
                company = f"{rng.choice(_COMPANY_STEMS)} {_COMPANY_SUFFIX.get(industry, 'Group')}"

                posting_rows.append({
                    "title": f"{primary['name']} {_role_word(primary['category'])}",
                    "company": company, "industry": industry, "district_id": d.id,
                    "state": d.state, "date_posted": posted, "salary_min": smin,
                    "salary_max": smax, "experience_level": exp,
                    "description": description, "source": "synthetic", "skills": skills_final,
                })
                for nm in skills_final:
                    sid = skill_by_name[nm].id
                    key = (d.id, sid, month)
                    demand_counts[key] = demand_counts.get(key, 0) + 1

        # --- Employer signals for the most-relevant skills ---
        top_skills = sorted(all_skill_names, key=lambda n: affinity[n], reverse=True)[:16]
        for nm in top_skills:
            s = meta_by_name[nm]
            n_sig = rng.randint(1, 3)
            for _ in range(n_sig):
                # Signal tracks affinity + trend momentum + noise.
                momentum = (s["trend"] ** 11 - 1)
                score = 100 * min(1.0, affinity[nm] * 1.3) * (0.7 + momentum) + rng.uniform(-8, 8)
                employer_rows.append({
                    "district_id": d.id, "skill_id": skill_by_name[nm].id,
                    "industry": rng.choice(s["industries"]),
                    "demand_score": round(max(5.0, min(100.0, score)), 1),
                    "survey_date": TODAY - timedelta(days=rng.randint(5, 150)),
                    "confidence": round(rng.uniform(0.55, 0.95), 2),
                })

        # --- Courses: supply concentrated on ESTABLISHED, locally-relevant skills.
        n_courses = rng.randint(4, 6) + int(scale * 3)
        course_weights = [meta_by_name[n]["supply_maturity"] * (0.4 + affinity[n]) for n in all_skill_names]
        anchors = _weighted_sample(rng, all_skill_names, course_weights, n_courses)
        for anchor in anchors:
            s = meta_by_name[anchor]
            related = [r for r in s.get("related", []) if r in skill_by_name]
            covered = [anchor] + rng.sample(related, min(len(related), rng.randint(0, 2)))
            capacity = int(rng.choice([30, 45, 60, 90, 120, 180, 240]) * (0.6 + scale / 2))
            enrolled = int(capacity * rng.uniform(0.4, 0.95))
            # Placement correlates with skill momentum (modern skills place better).
            momentum = s["trend"] ** 11
            placement = min(0.92, max(0.2, 0.35 + (momentum - 1) * 1.2 + rng.uniform(-0.1, 0.1)))
            completion = round(rng.uniform(0.55, 0.95), 2)
            # Foundational/declining courses updated long ago -> obsolescence signal.
            stale_years = 3 if s["trend"] < 0.99 else (2 if s["trend"] < 1.02 else 0)
            last_up = TODAY - timedelta(days=rng.randint(30, 300) + stale_years * 365)
            c = Course(
                name=f"{anchor} Programme", provider=f"{d.name} Skill Centre",
                district_id=d.id, duration_weeks=rng.choice([8, 12, 16, 24]),
                capacity=capacity, enrolled=enrolled, completion_rate=completion,
                placement_rate=round(placement, 2),
                placement_count=int(enrolled * completion * placement),
                equipment_required=_equipment(s["category"]),
                trainer_requirements=_trainer(s["category"]),
                last_updated=last_up,
            )
            c._covered = covered  # type: ignore[attr-defined]
            course_rows.append(c)

    # --- Bulk persist -------------------------------------------------------
    if verbose:
        print(f"  postings={len(posting_rows)}  employer_signals={len(employer_rows)}")
    db.add_all(provider_rows)
    _chunked_insert(db, JobPosting, posting_rows)
    _chunked_insert(db, EmployerSignal, employer_rows)

    demand_rows = [{"district_id": k[0], "skill_id": k[1], "month": k[2], "job_count": v}
                   for k, v in demand_counts.items()]
    _chunked_insert(db, DemandPoint, demand_rows)

    db.add_all(course_rows)
    db.commit()
    # Link courses to skills (many-to-many).
    for c in course_rows:
        for nm in c._covered:  # type: ignore[attr-defined]
            course_link_rows.append({"course_id": c.id, "skill_id": skill_by_name[nm].id})
    _chunked_insert_table(db, course_skill, course_link_rows)
    db.commit()

    return {
        "districts": len(districts), "skills": len(skill_rows),
        "job_postings": len(posting_rows), "employer_signals": len(employer_rows),
        "courses": len(course_rows), "demand_points": len(demand_rows),
        "months": months,
    }


# --- helpers ---------------------------------------------------------------

def _chunked_insert(db: Session, model, rows: list[dict], size: int = 2000) -> None:
    for i in range(0, len(rows), size):
        db.execute(insert(model), rows[i:i + size])
    db.commit()


def _chunked_insert_table(db: Session, table, rows: list[dict], size: int = 2000) -> None:
    for i in range(0, len(rows), size):
        db.execute(insert(table), rows[i:i + size])
    db.commit()


def _role_word(category: str) -> str:
    return {
        "Programming": "Developer", "Web Development": "Engineer", "Cloud": "Engineer",
        "DevOps": "Engineer", "Data & AI": "Engineer", "Data": "Analyst",
        "Security": "Analyst", "Embedded & Hardware": "Engineer", "Engineering": "Engineer",
        "Skilled Trades": "Technician", "Green Skills": "Technician", "Healthcare": "Associate",
        "Business": "Specialist", "Foundational": "Associate",
    }.get(category, "Specialist")


def _build_description(primary: dict, picked: list[dict], industry: str, district: str, exp: str) -> str:
    skills_text = ", ".join(rng_alias(s) for s in picked)
    return (
        f"We are hiring a {exp.lower()}-level {primary['name']} {_role_word(primary['category'])} "
        f"in the {industry} sector, based in {district}. "
        f"The role requires hands-on experience with {skills_text}. "
        f"Responsibilities include building and maintaining {primary['name'].lower()} solutions "
        f"and collaborating with cross-functional teams. "
        f"Familiarity with {', '.join(s['name'] for s in picked[:2])} is essential."
    )


def rng_alias(s: dict) -> str:
    """Use the canonical name or an alias so extraction has to normalise.

    Uses a stable per-name checksum (not built-in hash(), which is salted per
    process) to keep dataset generation reproducible.
    """
    aliases = s.get("aliases", [])
    if aliases and sum(ord(ch) for ch in s["name"]) % 2 == 0:
        return aliases[0]
    return s["name"]


def _equipment(category: str) -> str:
    return {
        "Embedded & Hardware": "Microcontroller kits, oscilloscopes, sensor modules",
        "Engineering": "CAD workstations, CNC simulator access",
        "Skilled Trades": "Welding bays, safety equipment, workshop tools",
        "Green Skills": "Solar test rigs, EV diagnostic tools",
        "Healthcare": "Clinical skills lab, phlebotomy kits",
        "Data & AI": "GPU compute access, cloud credits",
        "Cloud": "Cloud sandbox accounts",
    }.get(category, "Standard computer lab")


def _trainer(category: str) -> str:
    return {
        "Data & AI": "Trainers with applied ML/AI industry experience",
        "Security": "Certified security professionals (e.g. CEH/OSCP-equivalent)",
        "Cloud": "Cloud-certified practitioners",
        "Skilled Trades": "Master craftspersons with assessment certification",
    }.get(category, "Qualified subject-matter trainers")
