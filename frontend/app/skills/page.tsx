"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Wand2 } from "lucide-react";
import { apiGet, useApi, SkillListItem } from "@/lib/api";
import { fmtPct } from "@/lib/format";
import {
  EmergenceBadge,
  ErrorState,
  PageHeader,
  SectionHeader,
  Spinner,
} from "@/components/ui";

export default function SkillsPage() {
  const { data, loading, error } = useApi<SkillListItem[]>("/api/skills");
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("All");

  const categories = useMemo(() => {
    const set = new Set((data ?? []).map((s) => s.category));
    return ["All", ...Array.from(set).sort()];
  }, [data]);

  const rows = useMemo(() => {
    if (!data) return [];
    return data
      .filter((s) => cat === "All" || s.category === cat)
      .filter((s) => s.canonical_name.toLowerCase().includes(q.toLowerCase()))
      .sort((a, b) => b.national_demand - a.national_demand);
  }, [data, q, cat]);

  if (error) return <ErrorState message={error} />;

  return (
    <div>
      <PageHeader
        title="Skills"
        subtitle="Every skill in the taxonomy with national demand, gap and growth (averaged across districts)."
      />

      <ExtractionDemo />

      <div className="flex flex-wrap items-center gap-3 my-4">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search skill…"
          className="flex-1 min-w-[200px] px-3 py-2 rounded-md border border-border bg-surface text-sm"
        />
        <select
          value={cat}
          onChange={(e) => setCat(e.target.value)}
          className="py-2 px-3 rounded-md border border-border bg-surface text-sm"
        >
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {loading || !data ? (
        <Spinner />
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="th">Skill</th>
                <th className="th">Category</th>
                <th className="th text-right">Demand</th>
                <th className="th text-right">Gap</th>
                <th className="th text-right">Growth</th>
                <th className="th">Trend</th>
                <th className="th text-right">Districts</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((s) => (
                <tr key={s.id} className="hover:bg-surface-2">
                  <td className="td">
                    <Link href={`/skills/${s.id}`} className="font-medium hover:text-primary">
                      {s.canonical_name}
                    </Link>
                  </td>
                  <td className="td text-muted">{s.category}</td>
                  <td className="td text-right num">{s.national_demand.toFixed(0)}</td>
                  <td className="td text-right num">{s.national_gap.toFixed(0)}</td>
                  <td className="td text-right num">{fmtPct(s.national_growth_pct)}</td>
                  <td className="td"><EmergenceBadge label={s.dominant_label} /></td>
                  <td className="td text-right num">{s.districts_present}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function ExtractionDemo() {
  const [text, setText] = useState(
    "Hiring a senior data engineer with strong Python, SQL and AWS skills. Experience building ETL pipelines, plus exposure to LLMs and Kubernetes is a plus."
  );
  const [result, setResult] = useState<{ skill: string; confidence: number; method: string }[] | null>(null);
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    try {
      const r = await apiGet<{ skills: { skill: string; confidence: number; method: string }[] }>(
        `/api/skills/extract?text=${encodeURIComponent(text)}`
      );
      setResult(r.skills);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card p-4">
      <SectionHeader title="Try the skill-extraction pipeline" hint="Deterministic dictionary + TF-IDF" />
      <div className="grid md:grid-cols-[1fr_auto] gap-3">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={3}
          className="w-full px-3 py-2 rounded-md border border-border bg-surface text-sm resize-y"
          placeholder="Paste a job description…"
        />
        <button onClick={run} disabled={busy} className="btn btn-primary self-start">
          <Wand2 size={16} /> {busy ? "Extracting…" : "Extract skills"}
        </button>
      </div>
      {result && (
        <div className="mt-3 flex flex-wrap gap-2">
          {result.length === 0 && <span className="text-sm text-muted">No skills matched.</span>}
          {result.map((s) => (
            <span key={s.skill} className="chip bg-primary-soft text-primary-strong">
              {s.skill}
              <span className="num opacity-70">{(s.confidence * 100).toFixed(0)}%</span>
              <span className="opacity-60 text-[10px]">{s.method}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
