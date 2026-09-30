"use client";

import { X } from "lucide-react";
import { Recommendation } from "@/lib/api";
import { fmtInt, fmtPct, fmtSalaryINR } from "@/lib/format";
import { ActionBadge, PriorityBadge } from "@/components/ui";

export function WhyPanel({
  rec,
  onClose,
}: {
  rec: Recommendation | null;
  onClose: () => void;
}) {
  if (!rec) return null;
  const e = rec.evidence;

  const facts: { label: string; value: string }[] = [
    { label: "Demand index", value: e.demand_index.toFixed(0) },
    { label: "Training supply index", value: e.supply_index.toFixed(0) },
    { label: "Skill gap", value: `${e.gap_score.toFixed(0)} (${e.gap_label})` },
    { label: "12-month demand growth", value: fmtPct(e.growth_rate_pct) },
    { label: "Relevant job postings", value: fmtInt(e.job_postings) },
    { label: "Employers signalling demand", value: fmtInt(e.employers) },
    { label: "Industries requesting skill", value: fmtInt(e.cross_industry) },
    { label: "Local training seats", value: fmtInt(e.training_seats) },
    { label: "Placement rate (related)", value: `${e.placement_rate_pct.toFixed(0)}%` },
    { label: "Average advertised salary", value: fmtSalaryINR(e.avg_salary) },
  ];

  return (
    <div className="fixed inset-0 z-[1000] flex justify-end">
      <div className="absolute inset-0 bg-ink/30" onClick={onClose} aria-hidden />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Recommendation evidence"
        className="relative bg-surface w-full max-w-md h-full overflow-y-auto shadow-panel border-l border-border"
      >
        <div className="sticky top-0 bg-surface border-b border-border px-5 py-4 flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <ActionBadge action={rec.action} />
              <PriorityBadge priority={rec.priority} />
            </div>
            <h3 className="mt-2 font-semibold leading-snug">{rec.headline}</h3>
          </div>
          <button
            onClick={onClose}
            className="btn btn-outline !p-1.5 shrink-0"
            aria-label="Close"
          >
            <X size={16} />
          </button>
        </div>

        <div className="p-5 space-y-5">
          <section>
            <div className="label mb-2">Why this recommendation</div>
            <ul className="space-y-1.5">
              {e.rationale.map((r, i) => (
                <li key={i} className="text-sm flex gap-2">
                  <span
                    className="mt-1.5 h-1.5 w-1.5 rounded-full shrink-0"
                    style={{ background: "var(--primary)" }}
                  />
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <div className="label mb-2">Evidence</div>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-2">
              {facts.map((f) => (
                <div key={f.label} className="border-b border-border pb-1.5">
                  <dt className="text-xs text-subtle">{f.label}</dt>
                  <dd className="num text-sm font-medium">{f.value}</dd>
                </div>
              ))}
            </dl>
          </section>

          {(rec.suggested_course || rec.suggested_capacity > 0) && (
            <section className="card p-4 bg-surface-2">
              <div className="label mb-2">Proposed programme</div>
              {rec.suggested_course && (
                <div className="font-medium">{rec.suggested_course}</div>
              )}
              {rec.suggested_capacity > 0 && (
                <div className="text-sm text-muted mt-0.5">
                  Suggested capacity:{" "}
                  <span className="num font-medium text-ink">
                    {rec.suggested_capacity}
                  </span>{" "}
                  seats
                </div>
              )}
              {rec.target_skills?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {rec.target_skills.map((s) => (
                    <span key={s} className="chip bg-primary-soft text-primary-strong">
                      {s}
                    </span>
                  ))}
                </div>
              )}
              {e.equipment_note && (
                <div className="text-xs text-muted mt-2">{e.equipment_note}</div>
              )}
            </section>
          )}

          {e.existing_courses?.length > 0 && (
            <section>
              <div className="label mb-2">Existing local courses</div>
              <div className="flex flex-wrap gap-1.5">
                {e.existing_courses.map((c) => (
                  <span key={c} className="chip bg-surface-2 border border-border">
                    {c}
                  </span>
                ))}
              </div>
            </section>
          )}

          <p className="text-xs text-subtle border-t border-border pt-3">
            Decision-support output derived from synthetic demo signals. Requires human
            validation before any policy action.
          </p>
        </div>
      </div>
    </div>
  );
}
