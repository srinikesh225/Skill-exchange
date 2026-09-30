"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { ArrowLeft, HelpCircle } from "lucide-react";
import {
  useApi,
  DistrictDetail,
  Recommendation,
  SkillMetricRow,
} from "@/lib/api";
import {
  fmtInt,
  fmtPct,
  fmtSalaryINR,
  ACTION_LABELS,
} from "@/lib/format";
import {
  ActionBadge,
  EmergenceBadge,
  EmptyState,
  ErrorState,
  GapBadge,
  KpiCard,
  PageHeader,
  PriorityBadge,
  SectionHeader,
  Spinner,
} from "@/components/ui";
import {
  DemandSupplyChart,
  GapBarChart,
  IndustryBarChart,
} from "@/components/charts";
import { WhyPanel } from "@/components/WhyPanel";

export default function DistrictPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: d, loading, error } = useApi<DistrictDetail>(`/api/districts/${id}`);
  const { data: skills } = useApi<SkillMetricRow[]>(`/api/districts/${id}/skills`);
  const { data: recs } = useApi<Recommendation[]>(`/api/districts/${id}/recommendations`);
  const [why, setWhy] = useState<Recommendation | null>(null);

  if (error) return <ErrorState message={error} />;
  if (loading || !d) return <Spinner label="Loading district intelligence…" />;

  const topDemand = [...(skills ?? [])].sort((a, b) => b.demand_index - a.demand_index).slice(0, 8);
  const demandSupply = topDemand.map((s) => ({
    skill: s.skill,
    demand: s.demand_index,
    supply: s.supply_index,
  }));
  const topGaps = [...(skills ?? [])].sort((a, b) => b.gap_score - a.gap_score).slice(0, 8);
  const gapData = topGaps.map((s) => ({ skill: s.skill, gap: s.gap_score, label: s.gap_label }));
  const emerging = [...(skills ?? [])]
    .filter((s) => ["Emerging", "Growing"].includes(s.emergence_label))
    .sort((a, b) => b.emergence_score - a.emergence_score)
    .slice(0, 8);
  const oversupplied = [...(skills ?? [])]
    .filter((s) => s.supply_index - s.demand_index >= 15)
    .sort((a, b) => b.supply_index - b.demand_index - (a.supply_index - a.demand_index))
    .slice(0, 6);

  return (
    <div>
      <Link href="/districts" className="text-sm text-muted hover:text-ink inline-flex items-center gap-1 mb-3">
        <ArrowLeft size={14} /> All districts
      </Link>

      <PageHeader
        title={d.name}
        subtitle={`${d.state} · ${d.skill_count} skills analysed`}
        right={
          <Link href={`/compare?ids=${d.id}`} className="btn btn-outline text-sm">
            Compare with another district
          </Link>
        }
      />

      {/* Demographics (synthetic) */}
      <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-muted mb-5">
        <span>Population <b className="num text-ink">{fmtInt(d.population)}</b></span>
        <span>Working-age <b className="num text-ink">{fmtInt(d.working_population)}</b></span>
        <span>LFPR <b className="num text-ink">{d.lfpr}%</b></span>
        <span>WPR <b className="num text-ink">{d.wpr}%</b></span>
        <span>Unemployment <b className="num text-ink">{d.unemployment_rate}%</b></span>
        <span>Training capacity <b className="num text-ink">{fmtInt(d.training_capacity)}</b></span>
        <span className="text-subtle text-xs self-center">(synthetic demo values)</span>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KpiCard label="Skill Gap Index" value={d.overall_gap.toFixed(0)} accent="var(--critical)" hint={`${d.critical_gaps} critical · ${d.high_gaps} high`} />
        <KpiCard label="Employment Demand" value={d.employment_demand.toFixed(0)} hint="demand-weighted, 0–100" />
        <KpiCard label="Training Supply" value={d.training_supply.toFixed(0)} hint="capacity + outcomes, 0–100" />
        <KpiCard label="Emerging Skills" value={d.emerging_count} hint="growing / emerging" accent="var(--primary)" />
      </div>

      {/* Charts */}
      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        <div className="card p-4">
          <SectionHeader title="Demand vs training supply" hint="Top skills by demand" />
          <DemandSupplyChart data={demandSupply} />
        </div>
        <div className="card p-4">
          <SectionHeader title="Largest skill gaps" hint="Demand not met by supply" />
          <GapBarChart data={gapData} />
        </div>
      </div>

      {/* Recommendations */}
      <div className="card p-4 mb-6">
        <SectionHeader
          title="Recommended training actions"
          hint={recs ? `${recs.length} generated` : ""}
        />
        {!recs ? (
          <Spinner />
        ) : recs.length === 0 ? (
          <EmptyState message="No actions warranted for this district." />
        ) : (
          <div className="space-y-2">
            {recs.slice(0, 8).map((r) => (
              <div
                key={r.id}
                className="flex items-center gap-3 border border-border rounded-md p-3 hover:bg-surface-2 transition-colors"
              >
                <div className="flex items-center gap-2 shrink-0 w-40">
                  <PriorityBadge priority={r.priority} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{r.headline}</div>
                  <div className="text-xs text-muted mt-0.5">
                    {ACTION_LABELS[r.action] ?? r.action} · gap {r.evidence.gap_score.toFixed(0)} ·{" "}
                    {fmtInt(r.evidence.job_postings)} postings · {r.evidence.employers} employers
                  </div>
                </div>
                <button onClick={() => setWhy(r)} className="btn btn-outline text-sm shrink-0">
                  <HelpCircle size={15} /> Why?
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Emerging + oversupplied + industries */}
      <div className="grid lg:grid-cols-3 gap-4 mb-6">
        <div className="card p-4">
          <SectionHeader title="Emerging skills" />
          {emerging.length === 0 ? (
            <EmptyState message="None detected." />
          ) : (
            <div className="space-y-2">
              {emerging.map((s) => (
                <Link
                  key={s.skill_id}
                  href={`/skills/${s.skill_id}?district=${d.id}`}
                  className="flex items-center justify-between text-sm hover:text-primary"
                >
                  <span>{s.skill}</span>
                  <span className="flex items-center gap-2">
                    <span className="num" style={{ color: "var(--balanced)" }}>
                      {fmtPct(s.growth_pct)}
                    </span>
                    <EmergenceBadge label={s.emergence_label} />
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="card p-4">
          <SectionHeader title="Potentially oversupplied" hint="Supply exceeds demand" />
          {oversupplied.length === 0 ? (
            <EmptyState message="No clear oversupply." />
          ) : (
            <div className="space-y-2">
              {oversupplied.map((s) => (
                <div key={s.skill_id} className="flex items-center justify-between text-sm">
                  <span>{s.skill}</span>
                  <span className="num text-muted">
                    D {s.demand_index.toFixed(0)} · S {s.supply_index.toFixed(0)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card p-4">
          <SectionHeader title="Hiring by industry" />
          <IndustryBarChart data={d.industries.slice(0, 7)} />
        </div>
      </div>

      {/* Full skills table */}
      <div className="card p-4">
        <SectionHeader title="All skills in this district" hint="Click a skill to explore" />
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="th">Skill</th>
                <th className="th text-right">Demand</th>
                <th className="th text-right">Supply</th>
                <th className="th text-right">Gap</th>
                <th className="th">Trend</th>
                <th className="th text-right">Growth</th>
                <th className="th text-right">Postings</th>
                <th className="th text-right">Avg salary</th>
              </tr>
            </thead>
            <tbody>
              {[...(skills ?? [])]
                .sort((a, b) => b.gap_score - a.gap_score)
                .map((s) => (
                  <tr key={s.skill_id} className="hover:bg-surface-2">
                    <td className="td">
                      <Link href={`/skills/${s.skill_id}?district=${d.id}`} className="hover:text-primary font-medium">
                        {s.skill}
                      </Link>
                    </td>
                    <td className="td text-right num">{s.demand_index.toFixed(0)}</td>
                    <td className="td text-right num">{s.supply_index.toFixed(0)}</td>
                    <td className="td text-right">
                      <GapBadge label={s.gap_label} score={s.gap_score} />
                    </td>
                    <td className="td"><EmergenceBadge label={s.emergence_label} /></td>
                    <td className="td text-right num">{fmtPct(s.growth_pct)}</td>
                    <td className="td text-right num">{fmtInt(s.job_postings_count)}</td>
                    <td className="td text-right num">{fmtSalaryINR(s.avg_salary)}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      <WhyPanel rec={why} onClose={() => setWhy(null)} />
    </div>
  );
}
