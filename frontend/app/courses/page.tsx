"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useApi, CourseRow, DistrictSummary } from "@/lib/api";
import { COURSE_REC_LABELS } from "@/lib/format";
import { ErrorState, PageHeader, SectionHeader, Spinner } from "@/components/ui";

function riskColor(risk: string | null): string {
  if (risk === "High") return "var(--critical)";
  if (risk === "Moderate") return "var(--moderate)";
  return "var(--balanced)";
}

export default function CoursesPage() {
  const { data, loading, error } = useApi<CourseRow[]>("/api/courses");
  const { data: districts } = useApi<DistrictSummary[]>("/api/districts");
  const [district, setDistrict] = useState("All");
  const [risk, setRisk] = useState("All");

  const rows = useMemo(() => {
    if (!data) return [];
    return data
      .filter((c) => district === "All" || c.district === district)
      .filter((c) => risk === "All" || c.obsolescence_risk === risk);
  }, [data, district, risk]);

  if (error) return <ErrorState message={error} />;

  const atRisk = (data ?? []).filter((c) => c.obsolescence_risk === "High").length;

  return (
    <div>
      <PageHeader
        title="Course intelligence"
        subtitle="Existing training programmes scored against current labour-market demand. Low alignment is flagged for review — courses are never auto-deleted."
      />

      <div className="grid sm:grid-cols-3 gap-4 mb-4">
        <div className="card p-4">
          <div className="label">Courses analysed</div>
          <div className="num text-2xl font-semibold mt-1">{data?.length ?? "—"}</div>
        </div>
        <div className="card p-4">
          <div className="label">High obsolescence risk</div>
          <div className="num text-2xl font-semibold mt-1" style={{ color: "var(--critical)" }}>
            {atRisk}
          </div>
        </div>
        <div className="card p-4">
          <div className="label">Sorted by</div>
          <div className="text-sm mt-1">Lowest alignment first (most at risk)</div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 mb-4">
        <select
          value={district}
          onChange={(e) => setDistrict(e.target.value)}
          className="py-2 px-3 rounded-md border border-border bg-surface text-sm min-w-[200px]"
        >
          <option value="All">All districts</option>
          {(districts ?? [])
            .slice()
            .sort((a, b) => a.name.localeCompare(b.name))
            .map((d) => (
              <option key={d.id} value={d.name}>
                {d.name}
              </option>
            ))}
        </select>
        <select
          value={risk}
          onChange={(e) => setRisk(e.target.value)}
          className="py-2 px-3 rounded-md border border-border bg-surface text-sm"
        >
          <option value="All">All risk levels</option>
          <option value="High">High risk</option>
          <option value="Moderate">Moderate risk</option>
          <option value="Low">Low risk</option>
        </select>
        <span className="text-sm text-muted">{rows.length} shown</span>
      </div>

      {loading || !data ? (
        <Spinner />
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="th">Course</th>
                <th className="th">District</th>
                <th className="th text-right">Alignment</th>
                <th className="th">Risk</th>
                <th className="th text-right">Placement</th>
                <th className="th text-right">Utilisation</th>
                <th className="th">Suggested action</th>
              </tr>
            </thead>
            <tbody>
              {rows.slice(0, 300).map((c) => (
                <tr key={c.id} className="hover:bg-surface-2">
                  <td className="td">
                    <Link href={`/courses/${c.id}`} className="font-medium hover:text-primary">
                      {c.name}
                    </Link>
                  </td>
                  <td className="td text-muted">{c.district}</td>
                  <td className="td text-right num">{c.alignment_score?.toFixed(0) ?? "—"}</td>
                  <td className="td">
                    <span className="chip" style={{ color: riskColor(c.obsolescence_risk) }}>
                      <span
                        className="h-1.5 w-1.5 rounded-full"
                        style={{ background: riskColor(c.obsolescence_risk) }}
                      />
                      {c.obsolescence_risk ?? "—"}
                    </span>
                  </td>
                  <td className="td text-right num">{(c.placement_rate * 100).toFixed(0)}%</td>
                  <td className="td text-right num">{c.utilisation_pct.toFixed(0)}%</td>
                  <td className="td text-sm">{COURSE_REC_LABELS[c.recommendation ?? ""] ?? c.recommendation}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length > 300 && (
            <div className="p-3 text-xs text-subtle">Showing first 300 — filter by district to narrow.</div>
          )}
        </div>
      )}
    </div>
  );
}
