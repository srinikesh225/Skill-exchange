"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useState } from "react";
import {
  ArrowRight,
  Building2,
  LineChart,
  Radar,
  Sparkles,
} from "lucide-react";
import { useApi, DistrictSummary, Overview } from "@/lib/api";
import { fmtInt } from "@/lib/format";
import { GapBadge, Spinner, ErrorState } from "@/components/ui";

const IndiaMap = dynamic(() => import("@/components/IndiaMap"), {
  ssr: false,
  loading: () => <Spinner label="Loading map…" />,
});

const STEPS = [
  { icon: Building2, title: "Observe", body: "Ingest job postings, employer surveys, industry consultations and placement outcomes for every district." },
  { icon: LineChart, title: "Analyse", body: "Extract and normalise skills, then score demand from volume, growth, employer signals and salary." },
  { icon: Radar, title: "Detect", body: "Surface emerging skills and compute where local training supply falls short of demand." },
  { icon: Sparkles, title: "Recommend", body: "Generate evidence-backed actions: which programmes to launch, expand, update or retire." },
];

export default function HomePage() {
  const { data: districts, loading, error } = useApi<DistrictSummary[]>("/api/districts");
  const { data: overview } = useApi<Overview>("/api/analytics/overview");
  const [selected, setSelected] = useState<DistrictSummary | null>(null);

  return (
    <div className="space-y-10">
      {/* Hero */}
      <section className="grid lg:grid-cols-[1.1fr_0.9fr] gap-6 items-center">
        <div>
          <div className="inline-flex items-center gap-2 chip bg-primary-soft text-primary-strong mb-4">
            District Labour Market Intelligence · SIH26134
          </div>
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight leading-[1.08]">
            Know what skills your district will need next.
          </h1>
          <p className="mt-4 text-muted text-lg max-w-xl">
            SkillPulse India turns job-market signals, employer demand and training-supply
            data into district-level skill-gap intelligence — so training authorities can
            decide which programmes to launch, expand, update or retire.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <a href="#map" className="btn btn-primary">
              Explore the district map <ArrowRight size={16} />
            </a>
            <Link href="/methodology" className="btn btn-outline">
              View methodology
            </Link>
          </div>
          {overview && (
            <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                ["Districts", overview.totals.districts],
                ["Job signals", overview.totals.job_postings],
                ["Skills tracked", overview.totals.skills],
                ["Actions generated", overview.totals.recommendations],
              ].map(([label, val]) => (
                <div key={label as string}>
                  <div className="num text-2xl font-semibold">{fmtInt(val as number)}</div>
                  <div className="text-xs text-subtle">{label}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card p-5">
          <div className="label mb-2">The core idea</div>
          <div className="space-y-3 text-sm">
            <div className="flex items-center gap-2 text-subtle line-through">
              User → Search → Course
            </div>
            <div className="flex items-center gap-2 font-medium">
              Data → Analysis → Skill gap → Recommendation → Training plan
            </div>
            <p className="text-muted">
              This is a decision-support data product, not a course marketplace. Every
              recommendation is derived from observed demand and comes with its evidence.
            </p>
          </div>
        </div>
      </section>

      {/* Map */}
      <section id="map" className="scroll-mt-20">
        <div className="flex items-end justify-between mb-3">
          <div>
            <h2 className="text-xl font-semibold tracking-tight">
              India district skill-gap map
            </h2>
            <p className="text-muted text-sm">
              Each point is a district, coloured by its overall skill-gap index. Click one
              to see its intelligence.
            </p>
          </div>
          <Link href="/districts" className="btn btn-outline text-sm hidden sm:inline-flex">
            Browse as table
          </Link>
        </div>

        {error ? (
          <ErrorState message={error} />
        ) : (
          <div className="grid lg:grid-cols-[1fr_360px] gap-4">
            <div className="card overflow-hidden h-[520px]">
              {loading || !districts ? (
                <Spinner label="Loading districts…" />
              ) : (
                <IndiaMap
                  districts={districts}
                  onSelect={setSelected}
                  selectedId={selected?.id}
                />
              )}
            </div>
            <DistrictPeek selected={selected} />
          </div>
        )}
      </section>

      {/* How it works */}
      <section>
        <h2 className="text-xl font-semibold tracking-tight mb-1">How it works</h2>
        <p className="text-muted text-sm mb-4">
          From job-market signals to district training plans.
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {STEPS.map((s, i) => (
            <div key={s.title} className="card p-5">
              <div className="flex items-center gap-2">
                <span
                  className="grid place-items-center h-9 w-9 rounded-md"
                  style={{ background: "var(--primary-soft)", color: "var(--primary-strong)" }}
                >
                  <s.icon size={18} />
                </span>
                <span className="num text-subtle text-sm">0{i + 1}</span>
              </div>
              <div className="mt-3 font-semibold">{s.title}</div>
              <p className="text-sm text-muted mt-1">{s.body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function DistrictPeek({ selected }: { selected: DistrictSummary | null }) {
  if (!selected) {
    return (
      <div className="card p-5 flex items-center justify-center text-center text-muted text-sm h-[520px]">
        Select a district on the map to preview its skill-gap intelligence.
      </div>
    );
  }
  return (
    <div className="card p-5 h-[520px] overflow-y-auto">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="text-lg font-semibold leading-tight">{selected.name}</h3>
          <div className="text-sm text-muted">{selected.state}</div>
        </div>
        <div className="text-right">
          <div className="num text-3xl font-semibold" style={{ color: "var(--critical)" }}>
            {selected.overall_gap.toFixed(0)}
          </div>
          <div className="text-xs text-subtle">Overall gap</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 mt-4 text-center">
        {[
          ["Demand", selected.employment_demand],
          ["Supply", selected.training_supply],
          ["Emerging", selected.emerging_count],
        ].map(([l, v]) => (
          <div key={l as string} className="bg-surface-2 rounded-md py-2">
            <div className="num text-lg font-semibold">{(v as number).toFixed(0)}</div>
            <div className="text-xs text-subtle">{l}</div>
          </div>
        ))}
      </div>

      <div className="mt-4">
        <div className="label mb-2">Top skill gaps</div>
        <div className="space-y-1.5">
          {selected.top_gaps.map((g) => (
            <div key={g.skill} className="flex items-center justify-between text-sm">
              <span>{g.skill}</span>
              <GapBadge label={g.gap_label ?? ""} score={g.gap_score} />
            </div>
          ))}
        </div>
      </div>

      <Link
        href={`/districts/${selected.id}`}
        className="btn btn-primary w-full justify-center mt-5"
      >
        Open district intelligence <ArrowRight size={16} />
      </Link>
    </div>
  );
}
