"""Analytical pipeline: raw signals -> computed intelligence.

Reads job postings, employer signals, demand time-series and courses; aggregates
them; then runs the emergence, demand, supply, gap, recommendation and
course-alignment engines. Results are materialised into SkillMetric,
Recommendation and CourseAlignment. Re-runnable and idempotent.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.data.districts import DISTRICTS
from app.data.taxonomy import INDUSTRIES, SKILLS
from app.models import (
    Course,
    CourseAlignment,
    DemandPoint,
    District,
    EmployerSignal,
    JobPosting,
    Recommendation,
    Skill,
    SkillMetric,
)
from app.services import course_intelligence, demand_engine, gap_engine
from app.services.recommendation_engine import build_recommendation
from app.services.scaling import clamp, growth_to_score

TOTAL_INDUSTRIES = len(INDUSTRIES)
_TECH_BY_DISTRICT = {row[0]: row[5] for row in DISTRICTS}


def compute(db: Session, verbose: bool = True) -> dict:
    # Clear derived tables
    for model in (Recommendation, CourseAlignment, SkillMetric):
        db.execute(delete(model))
    db.commit()

    skills = db.query(Skill).all()
    districts = db.query(District).all()
    skill_meta = {s["name"]: s for s in SKILLS}
    skill_by_id = {s.id: s for s in skills}
    name_to_id = {s.canonical_name: s.id for s in skills}

    months = _months(db)

    # --- Aggregate postings -------------------------------------------------
    agg_count: dict[tuple[int, int], int] = defaultdict(int)
    agg_salary: dict[tuple[int, int], list[int]] = defaultdict(list)
    agg_industries: dict[tuple[int, int], set[str]] = defaultdict(set)
    district_salaries: dict[int, list[int]] = defaultdict(list)

    for jp in db.query(JobPosting).yield_per(2000):
        mid_salary = (jp.salary_min + jp.salary_max) // 2
        district_salaries[jp.district_id].append(mid_salary)
        for nm in jp.skills:
            sid = name_to_id.get(nm)
            if sid is None:
                continue
            key = (jp.district_id, sid)
            agg_count[key] += 1
            agg_salary[key].append(mid_salary)
            agg_industries[key].add(jp.industry)

    # Monthly series
    series: dict[tuple[int, int], dict[str, int]] = defaultdict(dict)
    for dp in db.query(DemandPoint).yield_per(5000):
        series[(dp.district_id, dp.skill_id)][dp.month] = dp.job_count

    # Employer signals
    emp_scores: dict[tuple[int, int], list[float]] = defaultdict(list)
    for es in db.query(EmployerSignal).yield_per(2000):
        emp_scores[(es.district_id, es.skill_id)].append(es.demand_score)

    # Courses -> supply per (district, skill)
    sup_seats: dict[tuple[int, int], int] = defaultdict(int)
    sup_enrolled: dict[tuple[int, int], int] = defaultdict(int)
    sup_completion: dict[tuple[int, int], list[float]] = defaultdict(list)
    sup_placement: dict[tuple[int, int], list[float]] = defaultdict(list)
    sup_courses: dict[tuple[int, int], list[str]] = defaultdict(list)
    district_covered: dict[int, set[int]] = defaultdict(set)
    courses = db.query(Course).all()
    for c in courses:
        for sk in c.skills:
            key = (c.district_id, sk.id)
            sup_seats[key] += c.capacity
            sup_enrolled[key] += c.enrolled
            sup_completion[key].append(c.completion_rate)
            sup_placement[key].append(c.placement_rate)
            sup_courses[key].append(c.name)
            district_covered[c.district_id].add(sk.id)

    # --- Global normalisation ranges ---------------------------------------
    counts = list(agg_count.values()) or [1]
    vol_hi = float(max(counts))
    seats_hi = float(max(sup_seats.values())) if sup_seats else 1.0
    pipe_hi = float(max(sup_enrolled.values())) if sup_enrolled else 1.0
    district_median = {d: (float(np.median(v)) if v else 1.0) for d, v in district_salaries.items()}
    # Salary premium range from data (p10..p90 to limit outliers)
    premiums = []
    for key, sals in agg_salary.items():
        med = district_median.get(key[0], 1.0) or 1.0
        premiums.append((sum(sals) / len(sals)) / med)
    prem_lo = float(np.percentile(premiums, 10)) if premiums else 0.8
    prem_hi = float(np.percentile(premiums, 90)) if premiums else 1.6

    # Per-skill 12-month industry momentum -> 0-100
    industry_growth_score = {
        s["name"]: growth_to_score(s["trend"] ** 12 - 1.0) for s in SKILLS
    }

    # --- Per (district, skill) metrics -------------------------------------
    metric_rows: list[SkillMetric] = []
    metric_ctx: dict[tuple[int, int], dict] = {}
    district_demand: dict[int, dict[int, float]] = defaultdict(dict)

    universe: set[tuple[int, int]] = set(agg_count) | set(sup_seats)

    for (did, sid) in universe:
        smeta = skill_meta[skill_by_id[sid].canonical_name]
        ser = series.get((did, sid), {})
        vals = [ser.get(m, 0) for m in months]
        count = sum(vals)
        recent3, prior3 = sum(vals[-3:]), sum(vals[:3])
        # Denominator smoothing stops low-volume skills from exploding to +300%
        # off a baseline of 0-1 postings; a volume-confidence damper further
        # tempers growth for thinly-observed skills.
        raw_growth = (recent3 - prior3) / (prior3 + 4.0)
        confidence = min(1.0, count / 8.0)
        growth = clamp(raw_growth * confidence, -0.9, 1.5)
        recency = (recent3 / count) if count else 0.0
        cross_ratio = len(agg_industries.get((did, sid), set())) / TOTAL_INDUSTRIES
        emp = emp_scores.get((did, sid), [])
        emp_signal = float(np.mean(emp)) if emp else 0.0

        em_comps = demand_engine.emergence_components(growth, recency, cross_ratio, emp_signal)
        em_score = demand_engine.emergence_score(em_comps)
        em_label = demand_engine.emergence_label(growth)

        sals = agg_salary.get((did, sid), [])
        avg_salary = int(np.mean(sals)) if sals else 0
        premium = (avg_salary / district_median.get(did, 1.0)) if avg_salary else 0.0

        dem_comps = demand_engine.demand_components(
            job_volume=count, volume_lo=0.0, volume_hi=vol_hi,
            growth_rate=growth, employer_signal=emp_signal,
            salary_premium=premium, premium_lo=prem_lo, premium_hi=prem_hi,
            industry_growth=industry_growth_score[smeta["name"]],
            emerging_signal=em_score,
        )
        dem_index = demand_engine.demand_index(dem_comps)

        seats = sup_seats.get((did, sid), 0)
        enrolled = sup_enrolled.get((did, sid), 0)
        comp_list = sup_completion.get((did, sid), [])
        plac_list = sup_placement.get((did, sid), [])
        sup_comps = gap_engine.supply_components(
            seats=seats, seats_lo=0.0, seats_hi=seats_hi,
            completion_rate=float(np.mean(comp_list)) if comp_list else 0.0,
            placement_rate=float(np.mean(plac_list)) if plac_list else 0.0,
            pipeline=enrolled, pipeline_lo=0.0, pipeline_hi=pipe_hi,
        )
        sup_index = gap_engine.supply_index(sup_comps)

        gap = gap_engine.gap_score(dem_index, sup_index)
        glabel = gap_engine.gap_label(gap)

        metric_rows.append(SkillMetric(
            district_id=did, skill_id=sid, demand_index=round(dem_index, 1),
            demand_components={k: round(v, 1) for k, v in dem_comps.items()},
            job_postings_count=count, growth_rate=round(growth, 4),
            emergence_score=round(em_score, 1), emergence_label=em_label,
            supply_index=round(sup_index, 1),
            supply_components={k: round(v, 1) for k, v in sup_comps.items()},
            training_seats=seats, gap_score=round(gap, 1), gap_label=glabel,
            avg_salary=avg_salary,
        ))
        district_demand[did][sid] = dem_index
        metric_ctx[(did, sid)] = {
            "skill_name": skill_by_id[sid].canonical_name,
            "skill_category": skill_by_id[sid].category,
            "related_skills": smeta.get("related", []),
            "demand_index": dem_index, "supply_index": sup_index,
            "gap_score": gap, "gap_label": glabel, "emergence_label": em_label,
            "emergence_score": em_score, "growth_rate": growth,
            "job_postings_count": count, "employer_count": len(emp),
            "cross_industry": len(agg_industries.get((did, sid), set())),
            "avg_salary": avg_salary, "seats": seats, "enrolled": enrolled,
            "placement_rate": float(np.mean(plac_list)) if plac_list else 0.0,
            "has_course": seats > 0, "course_names": sup_courses.get((did, sid), []),
        }

    db.add_all(metric_rows)
    db.commit()
    if verbose:
        print(f"  skill_metrics={len(metric_rows)}")

    # --- Recommendations ----------------------------------------------------
    district_name_by_id = {d.id: d.name for d in districts}
    rec_rows: list[Recommendation] = []
    for (did, sid), ctx in metric_ctx.items():
        dname = district_name_by_id.get(did, str(did))
        tech = _TECH_BY_DISTRICT.get(dname, 0.5)
        ctx["district_scale"] = clamp(0.4 + tech * 0.6, 0.4, 1.0)
        ctx["district_name"] = dname
        # Modern related skills that are in-demand locally but uncovered.
        missing = []
        for rel in ctx["related_skills"]:
            rid = name_to_id.get(rel)
            if rid and district_demand[did].get(rid, 0) >= 55 and rid not in district_covered[did]:
                missing.append(rel)
        ctx["missing_modern_skills"] = missing
        rec = build_recommendation(ctx)
        if rec:
            rec_rows.append(Recommendation(
                district_id=did, skill_id=sid, action=rec["action"],
                priority=rec["priority"], priority_score=rec["priority_score"],
                suggested_course=rec["suggested_course"],
                suggested_capacity=rec["suggested_capacity"],
                target_skills=rec["target_skills"], headline=rec["headline"],
                evidence=rec["evidence"],
            ))
    db.add_all(rec_rows)
    db.commit()
    if verbose:
        print(f"  recommendations={len(rec_rows)}")

    # --- Course alignment ---------------------------------------------------
    align_rows: list[CourseAlignment] = []
    from app.services.generator import TODAY
    for c in courses:
        sids = [sk.id for sk in c.skills]
        if not sids:
            continue
        demands = [district_demand[c.district_id].get(s, 0.0) for s in sids]
        avg_demand = float(np.mean(demands)) if demands else 0.0
        # Missing: high-demand related skills not covered by this course.
        covered_names = {sk.canonical_name for sk in c.skills}
        related_pool: set[str] = set()
        for sk in c.skills:
            related_pool.update(skill_meta[sk.canonical_name].get("related", []))
        missing = []
        for rel in related_pool:
            rid = name_to_id.get(rel)
            if rid and rel not in covered_names and district_demand[c.district_id].get(rid, 0) >= 60:
                missing.append(rel)
        mostly_declining = sum(
            1 for sk in c.skills if skill_meta[sk.canonical_name]["trend"] < 1.0
        ) >= max(1, len(sids) / 2)
        result = course_intelligence.analyse_course(
            avg_skill_demand=avg_demand, placement_rate=c.placement_rate,
            enrolled=c.enrolled, capacity=c.capacity, last_updated=c.last_updated,
            today=TODAY, missing_skills=missing[:5], mostly_declining=mostly_declining,
        )
        align_rows.append(CourseAlignment(
            course_id=c.id, alignment_score=result["alignment_score"],
            obsolescence_risk=result["obsolescence_risk"], components=result["components"],
            missing_skills=result["missing_skills"], recommendation=result["recommendation"],
        ))
    db.add_all(align_rows)
    db.commit()
    if verbose:
        print(f"  course_alignments={len(align_rows)}")

    return {
        "skill_metrics": len(metric_rows),
        "recommendations": len(rec_rows),
        "course_alignments": len(align_rows),
    }


def _months(db: Session) -> list[str]:
    rows = db.query(DemandPoint.month).distinct().all()
    return sorted({r[0] for r in rows})
