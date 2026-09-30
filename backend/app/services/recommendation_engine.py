"""District recommendation engine.

Turns (district, skill) intelligence into an explainable training action. Uses
transparent rules over the computed demand/supply/gap/emergence signals plus
existing course coverage. No per-district action is hard-coded — every result is
derived from the data and ships with the evidence behind it.

Actions: CREATE_COURSE, EXPAND_COURSE, UPDATE_COURSE, REDUCE_CAPACITY,
UPSKILL_TRAINERS, INVEST_EQUIPMENT, MONITOR.
"""

from __future__ import annotations

from app.services.scaling import clamp

_EQUIPMENT_CATEGORIES = {"Embedded & Hardware", "Engineering", "Skilled Trades", "Green Skills", "Healthcare"}

_PRIORITY_BANDS = [(70.0, "Critical"), (50.0, "High"), (30.0, "Medium"), (0.0, "Low")]


def priority_label(score: float) -> str:
    for threshold, label in _PRIORITY_BANDS:
        if score >= threshold:
            return label
    return "Low"


def priority_score(demand_index: float, gap_score: float, emergence_score: float) -> float:
    return clamp(0.5 * gap_score + 0.3 * demand_index + 0.2 * emergence_score)


def suggested_course_title(skill_name: str, action: str) -> str:
    special = {
        "Generative AI": "Applied Generative AI Engineering",
        "Cloud Security": "Cloud Security & DevSecOps",
        "Data Engineering": "Modern Data Engineering",
        "Cybersecurity": "Cybersecurity Operations (SOC) Programme",
        "Solar PV Installation": "Rooftop Solar Installation & Maintenance",
        "EV Servicing": "Electric Vehicle Servicing & Battery Systems",
    }
    if action == "UPDATE_COURSE":
        return f"Updated curriculum: add {skill_name} module"
    return special.get(skill_name, f"Applied {skill_name}")


def suggest_capacity(demand_index: float, gap_score: float, district_scale: float) -> int:
    """district_scale in ~[0.4, 1.0] reflects district size/economy.
    Rounds to the nearest 25 seats, bounded 50-400."""
    raw = (demand_index / 100) * (0.5 + gap_score / 100) * 400 * district_scale
    seats = int(round(raw / 25.0) * 25)
    return int(clamp(seats, 50, 400))


def build_recommendation(ctx: dict) -> dict | None:
    """ctx keys:
      skill_name, skill_category, related_skills (list)
      demand_index, supply_index, gap_score, gap_label
      emergence_label, emergence_score, growth_rate
      job_postings_count, employer_count, cross_industry, avg_salary
      seats, enrolled, placement_rate (0-1), has_course, course_names (list),
      missing_modern_skills (list), district_scale, district_name
    Returns a recommendation dict, or None when nothing is warranted.
    """
    gap = ctx["gap_score"]
    demand = ctx["demand_index"]
    supply = ctx["supply_index"]
    label = ctx["gap_label"]
    emergence = ctx["emergence_label"]
    seats = ctx.get("seats", 0)
    has_course = ctx.get("has_course", False)
    placement = ctx.get("placement_rate", 0.0)

    action: str | None = None
    rationale: list[str] = []

    # 1) Oversupply of a declining / low-demand skill -> reduce.
    if emergence == "Declining" and supply - demand >= 15 and seats > 0:
        action = "REDUCE_CAPACITY"
        rationale = [
            f"Demand is {emergence.lower()} (growth {ctx['growth_rate']*100:+.0f}%)",
            f"Training supply ({supply:.0f}) exceeds demand ({demand:.0f})",
            f"{seats} seats currently allocated could be redirected",
        ]
    # 2) High/critical gap with no local training -> create.
    elif label in ("Critical", "High") and not has_course:
        action = "CREATE_COURSE"
        rationale = [
            f"{label} skill gap ({gap:.0f}) with no local training programme",
            f"{ctx['job_postings_count']} relevant postings and {ctx['employer_count']} employers signalling demand",
            f"Demand index {demand:.0f} vs supply {supply:.0f}",
        ]
    # 3) High/critical gap, course exists but under-capacity -> expand.
    elif label in ("Critical", "High") and has_course:
        action = "EXPAND_COURSE"
        rationale = [
            f"{label} skill gap ({gap:.0f}) despite existing provision",
            f"Only {seats} seats against demand index {demand:.0f}",
            f"{ctx['employer_count']} employers requesting the skill",
        ]
    # 4) Emerging/growing skill whose existing course misses modern content.
    elif emergence in ("Emerging", "Growing") and has_course and ctx.get("missing_modern_skills"):
        action = "UPDATE_COURSE"
        rationale = [
            f"{emergence} skill (growth {ctx['growth_rate']*100:+.0f}%)",
            f"Existing course omits in-demand topics: {', '.join(ctx['missing_modern_skills'][:4])}",
        ]
    # 5) Supply exists but ineffective (low placement) on a real gap -> upskill.
    elif label in ("Moderate", "High") and has_course and placement < 0.45:
        action = "UPSKILL_TRAINERS"
        rationale = [
            f"Placement rate is low ({placement*100:.0f}%) despite a {label.lower()} gap",
            "Trainer capability / curriculum quality likely limiting outcomes",
        ]
    # 6) Otherwise monitor.
    elif label == "Moderate":
        action = "MONITOR"
        rationale = [f"Moderate gap ({gap:.0f}); watch demand trajectory"]
    else:
        return None

    pscore = priority_score(demand, gap, ctx["emergence_score"])
    target_skills = [ctx["skill_name"], *ctx.get("related_skills", [])][:6]

    equipment_note = None
    if action in ("CREATE_COURSE", "EXPAND_COURSE") and ctx["skill_category"] in _EQUIPMENT_CATEGORIES:
        equipment_note = "Hands-on programme: budget for lab equipment and certified trainers."

    course_title = (
        suggested_course_title(ctx["skill_name"], action)
        if action in ("CREATE_COURSE", "EXPAND_COURSE", "UPDATE_COURSE")
        else ""
    )
    capacity = (
        suggest_capacity(demand, gap, ctx.get("district_scale", 0.6))
        if action in ("CREATE_COURSE", "EXPAND_COURSE")
        else 0
    )

    headline = _headline(action, ctx["skill_name"], ctx["district_name"], course_title, capacity)

    return {
        "action": action,
        "priority": priority_label(pscore),
        "priority_score": round(pscore, 1),
        "suggested_course": course_title,
        "suggested_capacity": capacity,
        "target_skills": target_skills,
        "headline": headline,
        "evidence": {
            "demand_index": round(demand, 1),
            "supply_index": round(supply, 1),
            "gap_score": round(gap, 1),
            "gap_label": label,
            "emergence_label": emergence,
            "growth_rate_pct": round(ctx["growth_rate"] * 100, 1),
            "job_postings": ctx["job_postings_count"],
            "employers": ctx["employer_count"],
            "cross_industry": ctx["cross_industry"],
            "training_seats": seats,
            "placement_rate_pct": round(placement * 100, 1),
            "avg_salary": ctx.get("avg_salary", 0),
            "rationale": rationale,
            "equipment_note": equipment_note,
            "existing_courses": ctx.get("course_names", []),
        },
    }


def _headline(action: str, skill: str, district: str, course: str, capacity: int) -> str:
    if action == "CREATE_COURSE":
        return f'Launch "{course}" in {district} ({capacity} seats)'
    if action == "EXPAND_COURSE":
        return f"Expand {skill} training in {district} to ~{capacity} seats"
    if action == "UPDATE_COURSE":
        return f"Update {skill}-related curriculum in {district}"
    if action == "REDUCE_CAPACITY":
        return f"Redirect surplus {skill} training capacity in {district}"
    if action == "UPSKILL_TRAINERS":
        return f"Upskill trainers for {skill} programmes in {district}"
    if action == "INVEST_EQUIPMENT":
        return f"Invest in {skill} lab equipment in {district}"
    return f"Monitor {skill} demand in {district}"
