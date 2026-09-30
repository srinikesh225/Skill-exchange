"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { useApi, CourseRow } from "@/lib/api";
import { fmtInt, COURSE_REC_LABELS } from "@/lib/format";
import {
  ErrorState,
  KpiCard,
  Meter,
  PageHeader,
  SectionHeader,
  Spinner,
} from "@/components/ui";

const COMPONENT_LABELS: Record<string, string> = {
  skill_demand: "Skill demand alignment",
  placement: "Placement rate",
  utilisation: "Capacity utilisation",
  freshness: "Curriculum freshness",
};

export default function CoursePage() {
  const params = useParams();
  const { data: c, loading, error } = useApi<CourseRow>(`/api/courses/${params.id}`);

  if (error) return <ErrorState message={error} />;
  if (loading || !c) return <Spinner />;

  return (
    <div>
      <Link href="/courses" className="text-sm text-muted hover:text-ink inline-flex items-center gap-1 mb-3">
        <ArrowLeft size={14} /> All courses
      </Link>

      <PageHeader title={c.name} subtitle={`${c.provider} · ${c.district}`} />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KpiCard label="Alignment score" value={c.alignment_score?.toFixed(0) ?? "—"} accent="var(--primary)" />
        <KpiCard label="Obsolescence risk" value={c.obsolescence_risk ?? "—"} />
        <KpiCard label="Placement rate" value={`${(c.placement_rate * 100).toFixed(0)}%`} />
        <KpiCard label="Utilisation" value={`${c.utilisation_pct.toFixed(0)}%`} hint={`${fmtInt(c.enrolled)}/${fmtInt(c.capacity)} seats`} />
      </div>

      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        <div className="card p-4">
          <SectionHeader title="Alignment breakdown" />
          <div className="space-y-3">
            {Object.entries(c.alignment_components).map(([k, v]) => (
              <div key={k}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{COMPONENT_LABELS[k] ?? k}</span>
                  <span className="num">{v.toFixed(0)}</span>
                </div>
                <Meter value={v} />
              </div>
            ))}
          </div>
          <div className="mt-4 p-3 rounded-md bg-surface-2 text-sm">
            Suggested action:{" "}
            <span className="font-medium">
              {COURSE_REC_LABELS[c.recommendation ?? ""] ?? c.recommendation}
            </span>
          </div>
        </div>

        <div className="card p-4">
          <SectionHeader title="Skills covered" />
          <div className="flex flex-wrap gap-1.5 mb-4">
            {c.skills.map((s) => (
              <span key={s} className="chip bg-primary-soft text-primary-strong">
                {s}
              </span>
            ))}
          </div>

          {c.missing_skills.length > 0 && (
            <>
              <SectionHeader title="In-demand skills not covered" />
              <div className="flex flex-wrap gap-1.5">
                {c.missing_skills.map((s) => (
                  <span key={s} className="chip" style={{ color: "var(--high)", border: "1px dashed var(--high)" }}>
                    {s}
                  </span>
                ))}
              </div>
              <p className="text-xs text-subtle mt-2">
                The local job market increasingly requests these; consider adding modules.
              </p>
            </>
          )}
        </div>
      </div>

      <div className="card p-4">
        <SectionHeader title="Programme details" />
        <dl className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
          {[
            ["Duration", `${c.duration_weeks} weeks`],
            ["Capacity", `${fmtInt(c.capacity)} seats/yr`],
            ["Enrolled", fmtInt(c.enrolled)],
            ["Completion rate", `${(c.completion_rate * 100).toFixed(0)}%`],
            ["Placements", fmtInt(c.placement_count)],
            ["Last updated", c.last_updated],
            ["Equipment", c.equipment_required ?? "—"],
            ["Trainers", c.trainer_requirements ?? "—"],
          ].map(([label, val]) => (
            <div key={label as string}>
              <dt className="text-xs text-subtle">{label}</dt>
              <dd className="mt-0.5">{val}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}
