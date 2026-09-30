"""District-level roll-ups from per-(district, skill) metrics.

Aggregates many SkillMetric rows into the headline numbers shown on the map and
the district dashboard. Demand-weighting keeps high-demand skills influential in
the overall gap so the score reflects what actually matters in that district.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DistrictSummary:
    overall_gap: float
    employment_demand: float
    training_supply: float
    emerging_count: int
    critical_gaps: int
    high_gaps: int
    oversupplied: int


def summarise(metrics: list) -> DistrictSummary:
    """`metrics` is a list of objects/dicts with demand_index, supply_index,
    gap_score, gap_label, emergence_label, supply/demand fields."""
    if not metrics:
        return DistrictSummary(0, 0, 0, 0, 0, 0, 0)

    def g(m, k):
        return m[k] if isinstance(m, dict) else getattr(m, k)

    demands = [g(m, "demand_index") for m in metrics]
    supplies = [g(m, "supply_index") for m in metrics]
    gaps = [g(m, "gap_score") for m in metrics]

    total_demand = sum(demands) or 1.0
    # Demand-weighted overall gap: a gap in a high-demand skill counts more.
    overall_gap = sum(gp * d for gp, d in zip(gaps, demands)) / total_demand

    emerging = sum(1 for m in metrics if g(m, "emergence_label") in ("Emerging", "Growing"))
    critical = sum(1 for m in metrics if g(m, "gap_label") == "Critical")
    high = sum(1 for m in metrics if g(m, "gap_label") == "High")
    oversupplied = sum(
        1 for m in metrics
        if g(m, "supply_index") - g(m, "demand_index") >= 15
    )

    return DistrictSummary(
        overall_gap=round(overall_gap, 1),
        employment_demand=round(sum(demands) / len(demands), 1),
        training_supply=round(sum(supplies) / len(supplies), 1),
        emerging_count=emerging,
        critical_gaps=critical,
        high_gaps=high,
        oversupplied=oversupplied,
    )
