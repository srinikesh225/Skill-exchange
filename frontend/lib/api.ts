"use client";

import { useEffect, useState } from "react";

// Same-origin in dev thanks to next.config rewrites; override for other hosts.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

/** Small client-side data hook with loading + error state. */
export function useApi<T>(path: string | null): {
  data: T | null;
  loading: boolean;
  error: string | null;
} {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(path !== null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    if (path === null) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    apiGet<T>(path)
      .then((d) => active && setData(d))
      .catch((e) => active && setError(String(e.message ?? e)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [path]);

  return { data, loading, error };
}

// ---------------------------------------------------------------------------
// Response types
// ---------------------------------------------------------------------------

export interface SkillRef {
  skill: string;
  gap_score?: number;
  gap_label?: string;
  demand_index?: number;
  supply_index?: number;
  growth_pct?: number;
  emergence_score?: number;
  label?: string;
}

export interface DistrictSummary {
  id: number;
  name: string;
  state: string;
  latitude: number;
  longitude: number;
  overall_gap: number;
  employment_demand: number;
  training_supply: number;
  emerging_count: number;
  critical_gaps: number;
  high_gaps: number;
  oversupplied: number;
  recommendation_count: number;
  action_summary: Record<string, number>;
  top_emerging: SkillRef[];
  top_gaps: SkillRef[];
  oversupplied_skills: SkillRef[];
}

export interface DistrictDetail extends DistrictSummary {
  population: number;
  working_population: number;
  youth_population: number;
  unemployment_rate: number;
  lfpr: number;
  wpr: number;
  training_capacity: number;
  skill_count: number;
  industries: { industry: string; postings: number }[];
  top_occupations: { title: string; postings: number }[];
}

export interface SkillMetricRow {
  skill_id: number;
  skill: string;
  demand_index: number;
  demand_components: Record<string, number>;
  supply_index: number;
  supply_components: Record<string, number>;
  gap_score: number;
  gap_label: string;
  growth_rate: number;
  growth_pct: number;
  emergence_score: number;
  emergence_label: string;
  job_postings_count: number;
  training_seats: number;
  avg_salary: number;
}

export interface Recommendation {
  id: number;
  district_id: number;
  district?: string;
  skill_id: number;
  skill: string;
  action: string;
  priority: string;
  priority_score: number;
  suggested_course: string;
  suggested_capacity: number;
  target_skills: string[];
  headline: string;
  evidence: {
    demand_index: number;
    supply_index: number;
    gap_score: number;
    gap_label: string;
    emergence_label: string;
    growth_rate_pct: number;
    job_postings: number;
    employers: number;
    cross_industry: number;
    training_seats: number;
    placement_rate_pct: number;
    avg_salary: number;
    rationale: string[];
    equipment_note: string | null;
    existing_courses: string[];
  };
}

export interface ForecastResult {
  points: number[];
  lower: number[];
  upper: number[];
  milestones: Record<string, { point: number; lower: number; upper: number } | null>;
  method: string;
}

export interface TrendResult {
  skill_id: number;
  district_id: number | null;
  months: string[];
  counts: number[];
  forecast: ForecastResult;
}

export interface SkillMetricDetail {
  skill_id: number;
  skill: string;
  category: string;
  district_id: number;
  demand: {
    components: Record<string, number>;
    weights: Record<string, number>;
    contributions: Record<string, number>;
    index: number;
  };
  supply: { components: Record<string, number>; weights: Record<string, number>; index: number };
  gap_score: number;
  gap_label: string;
  growth_pct: number;
  emergence_score: number;
  emergence_label: string;
  job_postings_count: number;
  training_seats: number;
  avg_salary: number;
  related_skills: string[];
  top_industries: { industry: string; postings: number }[];
  top_occupations: { title: string; postings: number }[];
}

export interface CourseRow {
  id: number;
  name: string;
  provider: string;
  district_id: number;
  district: string;
  duration_weeks: number;
  capacity: number;
  enrolled: number;
  utilisation_pct: number;
  completion_rate: number;
  placement_rate: number;
  placement_count: number;
  last_updated: string;
  skills: string[];
  alignment_score: number | null;
  obsolescence_risk: string | null;
  recommendation: string | null;
  missing_skills: string[];
  alignment_components: Record<string, number>;
  equipment_required?: string;
  trainer_requirements?: string;
}

export interface Overview {
  totals: Record<string, number>;
  national_avg_gap: number;
  national_avg_demand: number;
  national_avg_supply: number;
  action_distribution: Record<string, number>;
  top_emerging_skills: { skill: string; skill_id: number; emergence_score: number; growth_pct: number; national_demand: number }[];
  top_gap_districts: { district_id: number; district: string; state: string; overall_gap: number; critical_gaps: number }[];
  states: { state: string; avg_gap: number; districts: number }[];
}

export interface Meta {
  app: string;
  subtitle: string;
  data_kind: string;
  disclaimer: string;
  coverage_months: string[];
  last_updated: string;
  provenance: Record<string, number>;
  methodology: {
    demand_weights: Record<string, number>;
    emergence_weights: Record<string, number>;
    supply_weights: Record<string, number>;
    alignment_weights: Record<string, number>;
    gap_thresholds: { min: number; label: string }[];
  };
}

export interface SkillListItem {
  id: number;
  canonical_name: string;
  category: string;
  aliases: string[];
  related_skills: string[];
  national_demand: number;
  national_gap: number;
  national_growth_pct: number;
  dominant_label: string;
  districts_present: number;
}
