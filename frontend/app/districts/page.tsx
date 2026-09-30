"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { useApi, DistrictSummary } from "@/lib/api";
import { fmtInt } from "@/lib/format";
import { ErrorState, GapBadge, PageHeader, Spinner } from "@/components/ui";

type SortKey = "overall_gap" | "employment_demand" | "training_supply" | "critical_gaps" | "name";

export default function DistrictsPage() {
  const { data, loading, error } = useApi<DistrictSummary[]>("/api/districts");
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<SortKey>("overall_gap");

  const rows = useMemo(() => {
    if (!data) return [];
    const filtered = data.filter(
      (d) =>
        d.name.toLowerCase().includes(q.toLowerCase()) ||
        d.state.toLowerCase().includes(q.toLowerCase())
    );
    return filtered.sort((a, b) => {
      if (sort === "name") return a.name.localeCompare(b.name);
      return (b[sort] as number) - (a[sort] as number);
    });
  }, [data, q, sort]);

  if (error) return <ErrorState message={error} />;

  return (
    <div>
      <PageHeader
        title="Districts"
        subtitle="Every district ranked by its labour-market skill-gap intelligence."
      />

      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className="relative flex-1 min-w-[220px]">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search district or state…"
            className="w-full pl-9 pr-3 py-2 rounded-md border border-border bg-surface text-sm"
          />
        </div>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortKey)}
          className="py-2 px-3 rounded-md border border-border bg-surface text-sm"
        >
          <option value="overall_gap">Sort: Overall gap</option>
          <option value="employment_demand">Sort: Demand</option>
          <option value="training_supply">Sort: Supply</option>
          <option value="critical_gaps">Sort: Critical gaps</option>
          <option value="name">Sort: Name</option>
        </select>
      </div>

      {loading || !data ? (
        <Spinner />
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="th">District</th>
                <th className="th">State</th>
                <th className="th text-right">Gap</th>
                <th className="th text-right">Demand</th>
                <th className="th text-right">Supply</th>
                <th className="th text-right">Critical</th>
                <th className="th text-right">Emerging</th>
                <th className="th text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((d) => (
                <tr key={d.id} className="hover:bg-surface-2">
                  <td className="td">
                    <Link href={`/districts/${d.id}`} className="font-medium hover:text-primary">
                      {d.name}
                    </Link>
                  </td>
                  <td className="td text-muted">{d.state}</td>
                  <td className="td text-right">
                    <GapBadge
                      label={
                        d.overall_gap >= 60 ? "Critical" : d.overall_gap >= 40 ? "High" : d.overall_gap >= 20 ? "Moderate" : "Balanced"
                      }
                      score={d.overall_gap}
                    />
                  </td>
                  <td className="td text-right num">{d.employment_demand.toFixed(0)}</td>
                  <td className="td text-right num">{d.training_supply.toFixed(0)}</td>
                  <td className="td text-right num">{d.critical_gaps}</td>
                  <td className="td text-right num">{d.emerging_count}</td>
                  <td className="td text-right num">{fmtInt(d.recommendation_count)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
