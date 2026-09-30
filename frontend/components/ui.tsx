"use client";

import { ReactNode } from "react";
import { AlertCircle, Loader2 } from "lucide-react";
import {
  gapColorVar,
  priorityColorVar,
  ACTION_LABELS,
} from "@/lib/format";

export function PageHeader({
  title,
  subtitle,
  right,
}: {
  title: string;
  subtitle?: string;
  right?: ReactNode;
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3 mb-5">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {subtitle && <p className="text-muted mt-1 text-sm max-w-2xl">{subtitle}</p>}
      </div>
      {right}
    </div>
  );
}

export function SectionHeader({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="flex items-baseline justify-between mb-3">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-subtle">
        {title}
      </h2>
      {hint && <span className="text-xs text-subtle">{hint}</span>}
    </div>
  );
}

export function KpiCard({
  label,
  value,
  unit,
  hint,
  accent,
}: {
  label: string;
  value: ReactNode;
  unit?: string;
  hint?: string;
  accent?: string;
}) {
  return (
    <div className="card p-4">
      <div className="label">{label}</div>
      <div className="mt-1.5 flex items-baseline gap-1">
        <span
          className="num text-3xl font-semibold"
          style={accent ? { color: accent } : undefined}
        >
          {value}
        </span>
        {unit && <span className="text-sm text-muted">{unit}</span>}
      </div>
      {hint && <div className="text-xs text-subtle mt-1">{hint}</div>}
    </div>
  );
}

export function GapBadge({ label, score }: { label: string; score?: number }) {
  const color = gapColorVar(label);
  return (
    <span
      className="chip"
      style={{ background: `color-mix(in srgb, ${color} 14%, transparent)`, color }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />
      {label}
      {score !== undefined && <span className="num opacity-80">{score.toFixed(0)}</span>}
    </span>
  );
}

export function PriorityBadge({ priority }: { priority: string }) {
  const color = priorityColorVar(priority);
  return (
    <span
      className="chip"
      style={{ background: `color-mix(in srgb, ${color} 14%, transparent)`, color }}
    >
      {priority}
    </span>
  );
}

export function ActionBadge({ action }: { action: string }) {
  return (
    <span className="chip bg-surface-2 border border-border text-ink">
      {ACTION_LABELS[action] ?? action}
    </span>
  );
}

export function EmergenceBadge({ label }: { label: string }) {
  const map: Record<string, string> = {
    Emerging: "var(--primary)",
    Growing: "var(--balanced)",
    Stable: "var(--muted)",
    Declining: "var(--high)",
  };
  const color = map[label] ?? "var(--muted)";
  return (
    <span className="chip" style={{ color }}>
      {label}
    </span>
  );
}

/** Horizontal 0-100 meter used for demand/supply/component bars. */
export function Meter({
  value,
  color = "var(--primary)",
  max = 100,
}: {
  value: number;
  color?: string;
  max?: number;
}) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <div className="h-2 w-full rounded-full bg-surface-2 overflow-hidden">
      <div className="h-full rounded-full" style={{ width: `${pct}%`, background: color }} />
    </div>
  );
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-muted text-sm py-10 justify-center">
      <Loader2 className="animate-spin" size={16} />
      {label ?? "Loading…"}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="card p-6 flex items-start gap-3 text-sm">
      <AlertCircle size={18} style={{ color: "var(--critical)" }} className="shrink-0 mt-0.5" />
      <div>
        <div className="font-medium">Couldn’t load data</div>
        <div className="text-muted mt-1">{message}</div>
        <div className="text-subtle mt-2 text-xs">
          Is the API running? Start it with{" "}
          <code className="num">uvicorn app.main:app</code> in the backend folder, and
          load demo data with <code className="num">python scripts/generate_demo_data.py</code>.
        </div>
      </div>
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return <div className="card p-6 text-sm text-muted text-center">{message}</div>;
}
