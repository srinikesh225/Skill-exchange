// Formatting + severity colour helpers shared across the UI.

export function fmtInt(n: number | null | undefined): string {
  if (n === null || n === undefined) return "—";
  return new Intl.NumberFormat("en-IN").format(Math.round(n));
}

export function fmtPct(n: number | null | undefined, digits = 0): string {
  if (n === null || n === undefined) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(digits)}%`;
}

export function fmtSalaryINR(monthly: number | null | undefined): string {
  if (!monthly) return "—";
  // Show monthly INR compactly (e.g. ₹85,000/mo)
  return `₹${new Intl.NumberFormat("en-IN").format(Math.round(monthly))}/mo`;
}

export function fmtMonth(ym: string): string {
  // "2026-09" -> "Sep 26"
  const [y, m] = ym.split("-");
  const names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${names[parseInt(m, 10)]} ${y.slice(2)}`;
}

// Severity → colour token (CSS variable value name used by tailwind classes).
export function gapColorVar(label: string): string {
  switch (label) {
    case "Critical":
      return "var(--critical)";
    case "High":
      return "var(--high)";
    case "Moderate":
      return "var(--moderate)";
    default:
      return "var(--balanced)";
  }
}

// Continuous colour for a 0-100 gap score (map + heat cells).
export function gapScoreColor(score: number): string {
  if (score >= 60) return "var(--critical)";
  if (score >= 40) return "var(--high)";
  if (score >= 20) return "var(--moderate)";
  return "var(--balanced)";
}

export function priorityColorVar(priority: string): string {
  switch (priority) {
    case "Critical":
      return "var(--critical)";
    case "High":
      return "var(--high)";
    case "Medium":
      return "var(--moderate)";
    default:
      return "var(--muted)";
  }
}

export const ACTION_LABELS: Record<string, string> = {
  CREATE_COURSE: "Create course",
  EXPAND_COURSE: "Expand course",
  UPDATE_COURSE: "Update curriculum",
  REDUCE_CAPACITY: "Reduce capacity",
  UPSKILL_TRAINERS: "Upskill trainers",
  INVEST_EQUIPMENT: "Invest in equipment",
  MONITOR: "Monitor",
};

export const COURSE_REC_LABELS: Record<string, string> = {
  KEEP: "Keep",
  REVIEW: "Review",
  UPDATE_CURRICULUM: "Update curriculum",
  RETIRE_OR_REDUCE: "Retire / reduce",
};
