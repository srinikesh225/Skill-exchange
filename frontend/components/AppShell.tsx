"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, Info } from "lucide-react";
import { useApi, Meta } from "@/lib/api";

const NAV = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "National" },
  { href: "/districts", label: "Districts" },
  { href: "/skills", label: "Skills" },
  { href: "/courses", label: "Courses" },
  { href: "/recommendations", label: "Recommendations" },
  { href: "/compare", label: "Compare" },
  { href: "/methodology", label: "Methodology" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { data: meta } = useApi<Meta>("/api/meta");

  return (
    <div className="min-h-screen flex flex-col">
      {/* Synthetic-data provenance banner — always visible, never hidden. */}
      <div className="bg-primary-strong text-white text-xs">
        <div className="mx-auto max-w-[1400px] px-4 py-1.5 flex items-center gap-2">
          <Info size={13} className="shrink-0" />
          <span className="truncate">
            Demo dataset — synthetic data for prototype demonstration. Not official
            statistics. Recommendations require human validation before policy action.
          </span>
        </div>
      </div>

      <header className="sticky top-0 z-[500] bg-surface/95 backdrop-blur border-b border-border">
        <div className="mx-auto max-w-[1400px] px-4 h-14 flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-2 shrink-0">
            <span
              className="grid place-items-center h-8 w-8 rounded-md text-white"
              style={{ background: "var(--primary)" }}
            >
              <Activity size={18} />
            </span>
            <span className="font-semibold tracking-tight">
              SkillPulse <span className="text-primary">India</span>
            </span>
          </Link>
          <nav className="hidden md:flex items-center gap-1 overflow-x-auto">
            {NAV.map((item) => {
              const active =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                    active
                      ? "bg-primary-soft text-primary-strong font-medium"
                      : "text-muted hover:text-ink hover:bg-surface-2"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        {/* Mobile nav */}
        <nav className="md:hidden flex items-center gap-1 overflow-x-auto px-3 pb-2 border-t border-border pt-2">
          {NAV.map((item) => {
            const active =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-2.5 py-1 rounded text-xs whitespace-nowrap ${
                  active ? "bg-primary-soft text-primary-strong font-medium" : "text-muted"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </header>

      <main className="flex-1 mx-auto max-w-[1400px] w-full px-4 py-6">{children}</main>

      <footer className="border-t border-border bg-surface">
        <div className="mx-auto max-w-[1400px] px-4 py-6 text-sm text-muted flex flex-col md:flex-row md:items-center md:justify-between gap-2">
          <div>
            <span className="font-medium text-ink">SkillPulse India</span> · District
            Labour Market Intelligence & Skill Planning System
          </div>
          <div className="text-xs">
            {meta ? (
              <>
                Coverage: {meta.coverage_months.length} months · updated{" "}
                {meta.last_updated} · {meta.provenance.job_postings.toLocaleString()} job
                signals (synthetic)
              </>
            ) : (
              "Prototype for SIH26134"
            )}
          </div>
        </div>
      </footer>
    </div>
  );
}
