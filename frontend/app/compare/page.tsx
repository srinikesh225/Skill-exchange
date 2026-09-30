"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { Plus, X } from "lucide-react";
import { apiGet, useApi, DistrictSummary } from "@/lib/api";
import { fmtInt } from "@/lib/format";
import { GapBadge, PageHeader, SectionHeader, Spinner, ErrorState } from "@/components/ui";

interface CompareRow {
  district_id: number;
  district: string;
  state: string;
  overall_gap: number;
  employment_demand: number;
  training_supply: number;
  emerging_count: number;
  critical_gaps: number;
  high_gaps: number;
  training_capacity: number;
  recommendation_count: number;
  top_gaps: { skill: string; gap_score: number; gap_label: string }[];
  top_emerging: { skill: string; growth_pct: number }[];
}

export default function ComparePage() {
  return (
    <Suspense fallback={<Spinner />}>
      <Compare />
    </Suspense>
  );
}

function Compare() {
  const search = useSearchParams();
  const { data: districts, error } = useApi<DistrictSummary[]>("/api/districts");
  const [ids, setIds] = useState<number[]>([]);
  const [rows, setRows] = useState<CompareRow[]>([]);
  const [loading, setLoading] = useState(false);

  // Initial selection: URL ids, else two contrasting districts (data-driven).
  useEffect(() => {
    if (!districts) return;
    const fromUrl = (search.get("ids") ?? "")
      .split(",")
      .map((x) => parseInt(x, 10))
      .filter((n) => !isNaN(n));
    if (fromUrl.length) {
      setIds(fromUrl.slice(0, 4));
      return;
    }
    const byDemand = [...districts].sort((a, b) => b.employment_demand - a.employment_demand);
    const hub = byDemand[0];
    // A contrasting district: high demand but very different top-gap profile.
    const contrast = byDemand.find((d) => d.top_gaps[0]?.skill !== hub.top_gaps[0]?.skill) ?? byDemand[Math.floor(byDemand.length / 2)];
    setIds([hub.id, contrast.id]);
  }, [districts, search]);

  useEffect(() => {
    if (!ids.length) {
      setRows([]);
      return;
    }
    setLoading(true);
    apiGet<{ districts: CompareRow[] }>(`/api/analytics/compare?ids=${ids.join(",")}`)
      .then((r) => setRows(r.districts))
      .finally(() => setLoading(false));
  }, [ids]);

  const available = useMemo(
    () => (districts ?? []).filter((d) => !ids.includes(d.id)).sort((a, b) => a.name.localeCompare(b.name)),
    [districts, ids]
  );

  if (error) return <ErrorState message={error} />;

  function addDistrict(id: number) {
    if (id && ids.length < 4) setIds([...ids, id]);
  }
  function remove(id: number) {
    setIds(ids.filter((x) => x !== id));
  }

  const metrics: { key: keyof CompareRow; label: string; accent?: string; fmt?: (v: number) => string }[] = [
    { key: "overall_gap", label: "Overall skill gap", accent: "var(--critical)" },
    { key: "employment_demand", label: "Employment demand" },
    { key: "training_supply", label: "Training supply" },
    { key: "critical_gaps", label: "Critical gaps" },
    { key: "high_gaps", label: "High gaps" },
    { key: "emerging_count", label: "Emerging skills" },
    { key: "training_capacity", label: "Training capacity", fmt: fmtInt },
    { key: "recommendation_count", label: "Recommended actions" },
  ];

  return (
    <div>
      <PageHeader
        title="Compare districts"
        subtitle="Same country, different districts — different labour demand, different skill gaps, different recommended training plans."
      />

      <div className="flex flex-wrap items-center gap-2 mb-4">
        {ids.map((id) => {
          const d = districts?.find((x) => x.id === id);
          return (
            <span key={id} className="chip bg-primary-soft text-primary-strong">
              {d?.name ?? id}
              <button onClick={() => remove(id)} aria-label="Remove"><X size={13} /></button>
            </span>
          );
        })}
        {ids.length < 4 && (
          <select
            onChange={(e) => { addDistrict(parseInt(e.target.value, 10)); e.target.value = ""; }}
            className="py-1.5 px-3 rounded-md border border-border bg-surface text-sm"
            defaultValue=""
          >
            <option value="" disabled>+ Add district</option>
            {available.map((d) => (
              <option key={d.id} value={d.id}>{d.name} — {d.state}</option>
            ))}
          </select>
        )}
      </div>

      {loading || !rows.length ? (
        <Spinner />
      ) : (
        <>
          <div className="card overflow-x-auto mb-6">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="th">Metric</th>
                  {rows.map((r) => (
                    <th key={r.district_id} className="th text-right">
                      {r.district}
                      <div className="font-normal normal-case text-subtle">{r.state}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {metrics.map((m) => (
                  <tr key={m.key} className="hover:bg-surface-2">
                    <td className="td text-muted">{m.label}</td>
                    {rows.map((r) => (
                      <td key={r.district_id} className="td text-right num font-medium" style={m.accent ? { color: m.accent } : undefined}>
                        {m.fmt ? m.fmt(r[m.key] as number) : (r[m.key] as number).toFixed(0)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${rows.length}, minmax(0,1fr))` }}>
            {rows.map((r) => (
              <div key={r.district_id} className="card p-4">
                <div className="font-semibold">{r.district}</div>
                <div className="text-xs text-subtle mb-3">{r.state}</div>

                <SectionHeader title="Top skill gaps" />
                <div className="space-y-1.5 mb-4">
                  {r.top_gaps.map((g) => (
                    <div key={g.skill} className="flex items-center justify-between text-sm">
                      <span className="truncate mr-2">{g.skill}</span>
                      <GapBadge label={g.gap_label} score={g.gap_score} />
                    </div>
                  ))}
                </div>

                <SectionHeader title="Emerging skills" />
                <div className="space-y-1.5">
                  {r.top_emerging.length === 0 && <span className="text-sm text-muted">None.</span>}
                  {r.top_emerging.map((g) => (
                    <div key={g.skill} className="flex items-center justify-between text-sm">
                      <span className="truncate mr-2">{g.skill}</span>
                      <span className="num" style={{ color: "var(--balanced)" }}>+{g.growth_pct.toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <p className="text-sm text-muted mt-6 card p-4">
            <b>The core innovation:</b> the same engine, run on each district&apos;s own
            labour-market signals, produces a distinct skill-gap profile and a distinct
            training plan. There is no hard-coded per-district logic.
          </p>
        </>
      )}
    </div>
  );
}
