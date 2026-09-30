"use client";

import Link from "next/link";
import { useApi, Overview } from "@/lib/api";
import { fmtInt, fmtPct, ACTION_LABELS } from "@/lib/format";
import {
  EmergenceBadge,
  ErrorState,
  KpiCard,
  PageHeader,
  SectionHeader,
  Spinner,
} from "@/components/ui";

export default function DashboardPage() {
  const { data, loading, error } = useApi<Overview>("/api/analytics/overview");
  if (error) return <ErrorState message={error} />;
  if (loading || !data) return <Spinner label="Loading national overview…" />;

  return (
    <div>
      <PageHeader
        title="National overview"
        subtitle="Aggregate labour-market intelligence across all districts in the demo dataset."
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KpiCard label="National Avg Gap" value={data.national_avg_gap.toFixed(0)} accent="var(--high)" />
        <KpiCard label="Avg Demand" value={data.national_avg_demand.toFixed(0)} />
        <KpiCard label="Avg Supply" value={data.national_avg_supply.toFixed(0)} />
        <KpiCard label="Job signals" value={fmtInt(data.totals.job_postings)} hint="synthetic" />
      </div>

      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        <div className="card p-4">
          <SectionHeader title="Top emerging skills (national)" />
          <div className="space-y-2">
            {data.top_emerging_skills.map((s) => (
              <Link
                key={s.skill_id}
                href={`/skills/${s.skill_id}`}
                className="flex items-center justify-between text-sm hover:text-primary"
              >
                <span>{s.skill}</span>
                <span className="flex items-center gap-3">
                  <span className="num text-subtle">demand {s.national_demand.toFixed(0)}</span>
                  <span className="num" style={{ color: "var(--balanced)" }}>
                    {fmtPct(s.growth_pct)}
                  </span>
                </span>
              </Link>
            ))}
          </div>
        </div>

        <div className="card p-4">
          <SectionHeader title="Highest-gap districts" />
          <div className="space-y-2">
            {data.top_gap_districts.map((d) => (
              <Link
                key={d.district_id}
                href={`/districts/${d.district_id}`}
                className="flex items-center justify-between text-sm hover:text-primary"
              >
                <span>
                  {d.district} <span className="text-subtle">· {d.state}</span>
                </span>
                <span className="num" style={{ color: "var(--critical)" }}>
                  {d.overall_gap.toFixed(0)}
                </span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-[1fr_1.4fr] gap-4">
        <div className="card p-4">
          <SectionHeader title="Recommended actions" hint="Across all districts" />
          <div className="space-y-2">
            {Object.entries(data.action_distribution)
              .sort((a, b) => b[1] - a[1])
              .map(([action, count]) => (
                <div key={action} className="flex items-center justify-between text-sm">
                  <span>{ACTION_LABELS[action] ?? action}</span>
                  <span className="num font-medium">{fmtInt(count)}</span>
                </div>
              ))}
          </div>
          <Link href="/recommendations" className="btn btn-outline w-full justify-center mt-4 text-sm">
            Browse all recommendations
          </Link>
        </div>

        <div className="card p-4">
          <SectionHeader title="States by average skill gap" />
          <div className="overflow-x-auto max-h-[380px]">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="th">State</th>
                  <th className="th text-right">Districts</th>
                  <th className="th text-right">Avg gap</th>
                </tr>
              </thead>
              <tbody>
                {data.states.map((s) => (
                  <tr key={s.state} className="hover:bg-surface-2">
                    <td className="td">{s.state}</td>
                    <td className="td text-right num">{s.districts}</td>
                    <td className="td text-right num">{s.avg_gap.toFixed(0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
