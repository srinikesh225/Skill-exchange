"use client";

import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import {
  useApi,
  DistrictSummary,
  SkillMetricDetail,
  TrendResult,
} from "@/lib/api";
import { fmtInt, fmtPct, fmtSalaryINR } from "@/lib/format";
import {
  EmptyState,
  ErrorState,
  GapBadge,
  KpiCard,
  Meter,
  PageHeader,
  SectionHeader,
  Spinner,
} from "@/components/ui";
import { TrendForecastChart } from "@/components/charts";

const COMPONENT_LABELS: Record<string, string> = {
  job_volume: "Job posting volume",
  job_growth: "Job posting growth",
  employer_signal: "Employer demand signal",
  salary_premium: "Salary premium",
  industry_growth: "Industry growth",
  emerging_signal: "Emerging-skill signal",
  capacity: "Training capacity",
  completion: "Completion rate",
  placement: "Placement rate",
  pipeline: "Learner pipeline",
};

export default function SkillExplorerPage() {
  return (
    <Suspense fallback={<Spinner />}>
      <SkillExplorer />
    </Suspense>
  );
}

function SkillExplorer() {
  const params = useParams();
  const skillId = params.id as string;
  const search = useSearchParams();

  const { data: skill, error } = useApi<{
    id: number;
    canonical_name: string;
    category: string;
    description: string;
    related_skills: string[];
    national_demand: number;
    national_gap: number;
    top_districts: { district_id: number; district: string; demand_index: number; gap_score: number; gap_label: string; growth_pct: number }[];
  }>(`/api/skills/${skillId}`);
  const { data: districts } = useApi<DistrictSummary[]>("/api/districts");

  const [districtId, setDistrictId] = useState<string>("");

  // Default district: URL param, else the top-demand district for this skill.
  useEffect(() => {
    const fromUrl = search.get("district");
    if (fromUrl) setDistrictId(fromUrl);
    else if (skill?.top_districts?.length) setDistrictId(String(skill.top_districts[0].district_id));
  }, [search, skill]);

  const metricPath = districtId ? `/api/skills/${skillId}/metric?district_id=${districtId}` : null;
  const trendPath = districtId ? `/api/skills/${skillId}/trend?district_id=${districtId}` : null;
  const { data: metric } = useApi<SkillMetricDetail>(metricPath);
  const { data: trend } = useApi<TrendResult>(trendPath);

  if (error) return <ErrorState message={error} />;
  if (!skill) return <Spinner label="Loading skill…" />;

  return (
    <div>
      <Link href="/skills" className="text-sm text-muted hover:text-ink inline-flex items-center gap-1 mb-3">
        <ArrowLeft size={14} /> All skills
      </Link>

      <PageHeader
        title={skill.canonical_name}
        subtitle={`${skill.category} · national demand ${skill.national_demand.toFixed(0)} · national gap ${skill.national_gap.toFixed(0)}`}
        right={
          <select
            value={districtId}
            onChange={(e) => setDistrictId(e.target.value)}
            className="py-2 px-3 rounded-md border border-border bg-surface text-sm min-w-[220px]"
          >
            <option value="">Select a district…</option>
            {(districts ?? [])
              .slice()
              .sort((a, b) => a.name.localeCompare(b.name))
              .map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} — {d.state}
                </option>
              ))}
          </select>
        }
      />

      {!metric ? (
        <EmptyState message="Select a district to see this skill's demand, supply and gap." />
      ) : (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <KpiCard label="Demand index" value={metric.demand.index.toFixed(0)} />
            <KpiCard label="Supply index" value={metric.supply.index.toFixed(0)} />
            <KpiCard
              label="Skill gap"
              value={metric.gap_score.toFixed(0)}
              hint={metric.gap_label}
              accent="var(--critical)"
            />
            <KpiCard label="12-month growth" value={fmtPct(metric.growth_pct)} accent="var(--primary)" />
          </div>

          <div className="grid lg:grid-cols-2 gap-4 mb-6">
            <div className="card p-4">
              <SectionHeader title="Demand score breakdown" hint="Weighted 0–100 components" />
              <ComponentBreakdown
                components={metric.demand.components}
                weights={metric.demand.weights}
                contributions={metric.demand.contributions}
                index={metric.demand.index}
              />
            </div>
            <div className="card p-4">
              <SectionHeader title="Supply score breakdown" />
              <ComponentBreakdown
                components={metric.supply.components}
                weights={metric.supply.weights}
                index={metric.supply.index}
              />
            </div>
          </div>

          <div className="card p-4 mb-6">
            <SectionHeader
              title="Demand trend & 12-month forecast"
              hint={trend ? trend.forecast.method : ""}
            />
            {!trend ? (
              <Spinner />
            ) : (
              <>
                <TrendForecastChart
                  months={trend.months}
                  counts={trend.counts}
                  forecast={trend.forecast}
                />
                <div className="grid grid-cols-3 gap-3 mt-3">
                  {(["3m", "6m", "12m"] as const).map((k) => {
                    const m = trend.forecast.milestones[k];
                    return (
                      <div key={k} className="bg-surface-2 rounded-md p-3 text-center">
                        <div className="text-xs text-subtle uppercase">{k} forecast</div>
                        <div className="num text-lg font-semibold">
                          {m ? m.point.toFixed(0) : "—"}
                        </div>
                        <div className="text-xs text-subtle">
                          {m ? `range ${m.lower.toFixed(0)}–${m.upper.toFixed(0)}` : ""}
                        </div>
                      </div>
                    );
                  })}
                </div>
                <p className="text-xs text-subtle mt-2">
                  Forecasts are estimates with uncertainty, not guaranteed outcomes.
                </p>
              </>
            )}
          </div>

          <div className="grid lg:grid-cols-3 gap-4">
            <div className="card p-4">
              <SectionHeader title="Top industries" />
              {metric.top_industries.length === 0 ? (
                <EmptyState message="No postings." />
              ) : (
                metric.top_industries.map((i) => (
                  <div key={i.industry} className="flex justify-between text-sm py-1">
                    <span>{i.industry}</span>
                    <span className="num text-muted">{fmtInt(i.postings)}</span>
                  </div>
                ))
              )}
            </div>
            <div className="card p-4">
              <SectionHeader title="Top occupations" />
              {metric.top_occupations.length === 0 ? (
                <EmptyState message="No postings." />
              ) : (
                metric.top_occupations.map((o) => (
                  <div key={o.title} className="flex justify-between text-sm py-1">
                    <span className="truncate mr-2">{o.title}</span>
                    <span className="num text-muted shrink-0">{fmtInt(o.postings)}</span>
                  </div>
                ))
              )}
            </div>
            <div className="card p-4">
              <SectionHeader title="Context" />
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted">Job postings</span>
                  <span className="num">{fmtInt(metric.job_postings_count)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Training seats</span>
                  <span className="num">{fmtInt(metric.training_seats)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Avg salary</span>
                  <span className="num">{fmtSalaryINR(metric.avg_salary)}</span>
                </div>
              </div>
              {skill.related_skills.length > 0 && (
                <>
                  <div className="label mt-4 mb-2">Related skills</div>
                  <div className="flex flex-wrap gap-1.5">
                    {skill.related_skills.map((r) => (
                      <span key={r} className="chip bg-surface-2 border border-border">
                        {r}
                      </span>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </>
      )}

      {/* Top districts for this skill */}
      <div className="card p-4 mt-6">
        <SectionHeader title={`Where ${skill.canonical_name} is most in demand`} />
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="th">District</th>
                <th className="th text-right">Demand</th>
                <th className="th text-right">Gap</th>
                <th className="th text-right">Growth</th>
              </tr>
            </thead>
            <tbody>
              {skill.top_districts.map((t) => (
                <tr key={t.district_id} className="hover:bg-surface-2">
                  <td className="td">
                    <button
                      onClick={() => setDistrictId(String(t.district_id))}
                      className="hover:text-primary font-medium"
                    >
                      {t.district}
                    </button>
                  </td>
                  <td className="td text-right num">{t.demand_index.toFixed(0)}</td>
                  <td className="td text-right">
                    <GapBadge label={t.gap_label} score={t.gap_score} />
                  </td>
                  <td className="td text-right num">{fmtPct(t.growth_pct)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function ComponentBreakdown({
  components,
  weights,
  contributions,
  index,
}: {
  components: Record<string, number>;
  weights: Record<string, number>;
  contributions?: Record<string, number>;
  index: number;
}) {
  return (
    <div>
      <div className="space-y-3">
        {Object.entries(components).map(([key, val]) => (
          <div key={key}>
            <div className="flex justify-between text-sm mb-1">
              <span>
                {COMPONENT_LABELS[key] ?? key}
                <span className="text-subtle text-xs ml-1">
                  ×{(weights[key] ?? 0).toFixed(2)}
                </span>
              </span>
              <span className="num">
                {val.toFixed(0)}
                {contributions && (
                  <span className="text-subtle"> → {contributions[key]?.toFixed(1)}</span>
                )}
              </span>
            </div>
            <Meter value={val} />
          </div>
        ))}
      </div>
      <div className="flex justify-between items-baseline border-t border-border mt-3 pt-3">
        <span className="label">Composite index</span>
        <span className="num text-2xl font-semibold">{index.toFixed(0)}</span>
      </div>
    </div>
  );
}
