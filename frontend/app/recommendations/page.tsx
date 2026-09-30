"use client";

import { useState } from "react";
import { HelpCircle } from "lucide-react";
import { useApi, Recommendation } from "@/lib/api";
import { fmtInt, ACTION_LABELS } from "@/lib/format";
import {
  ActionBadge,
  ErrorState,
  PageHeader,
  PriorityBadge,
  Spinner,
} from "@/components/ui";
import { WhyPanel } from "@/components/WhyPanel";

const ACTIONS = ["", "CREATE_COURSE", "EXPAND_COURSE", "UPDATE_COURSE", "REDUCE_CAPACITY", "UPSKILL_TRAINERS", "MONITOR"];
const PRIORITIES = ["", "Critical", "High", "Medium", "Low"];

export default function RecommendationsPage() {
  const [action, setAction] = useState("");
  const [priority, setPriority] = useState("");
  const [why, setWhy] = useState<Recommendation | null>(null);

  const qs = new URLSearchParams({ limit: "300" });
  if (action) qs.set("action", action);
  if (priority) qs.set("priority", priority);
  const { data, loading, error } = useApi<Recommendation[]>(`/api/recommendations?${qs.toString()}`);

  if (error) return <ErrorState message={error} />;

  return (
    <div>
      <PageHeader
        title="Recommendations"
        subtitle="Evidence-based training actions across all districts, ranked by priority. Every action links to its supporting evidence."
      />

      <div className="flex flex-wrap items-center gap-3 mb-4">
        <select value={action} onChange={(e) => setAction(e.target.value)} className="py-2 px-3 rounded-md border border-border bg-surface text-sm">
          {ACTIONS.map((a) => (
            <option key={a} value={a}>{a ? ACTION_LABELS[a] ?? a : "All actions"}</option>
          ))}
        </select>
        <select value={priority} onChange={(e) => setPriority(e.target.value)} className="py-2 px-3 rounded-md border border-border bg-surface text-sm">
          {PRIORITIES.map((p) => (
            <option key={p} value={p}>{p || "All priorities"}</option>
          ))}
        </select>
        {data && <span className="text-sm text-muted">{data.length} shown</span>}
      </div>

      {loading || !data ? (
        <Spinner />
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="th">Priority</th>
                <th className="th">Action</th>
                <th className="th">District</th>
                <th className="th">Skill</th>
                <th className="th text-right">Gap</th>
                <th className="th text-right">Postings</th>
                <th className="th"></th>
              </tr>
            </thead>
            <tbody>
              {data.map((r) => (
                <tr key={r.id} className="hover:bg-surface-2">
                  <td className="td"><PriorityBadge priority={r.priority} /></td>
                  <td className="td"><ActionBadge action={r.action} /></td>
                  <td className="td">{r.district}</td>
                  <td className="td font-medium">{r.skill}</td>
                  <td className="td text-right num">{r.evidence.gap_score.toFixed(0)}</td>
                  <td className="td text-right num">{fmtInt(r.evidence.job_postings)}</td>
                  <td className="td text-right">
                    <button onClick={() => setWhy(r)} className="btn btn-outline text-sm">
                      <HelpCircle size={14} /> Why?
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <WhyPanel rec={why} onClose={() => setWhy(null)} />
    </div>
  );
}
