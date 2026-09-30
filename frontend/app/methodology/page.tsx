"use client";

import { useApi, Meta } from "@/lib/api";
import { ErrorState, PageHeader, SectionHeader, Spinner } from "@/components/ui";

function WeightTable({ title, weights }: { title: string; weights: Record<string, number> }) {
  return (
    <div className="card p-4">
      <SectionHeader title={title} />
      <table className="w-full">
        <tbody>
          {Object.entries(weights).map(([k, v]) => (
            <tr key={k}>
              <td className="td capitalize">{k.replace(/_/g, " ")}</td>
              <td className="td text-right num">{v.toFixed(2)}</td>
            </tr>
          ))}
          <tr>
            <td className="td font-semibold">Total</td>
            <td className="td text-right num font-semibold">
              {Object.values(weights).reduce((a, b) => a + b, 0).toFixed(2)}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default function MethodologyPage() {
  const { data: meta, loading, error } = useApi<Meta>("/api/meta");
  if (error) return <ErrorState message={error} />;
  if (loading || !meta) return <Spinner />;

  const m = meta.methodology;

  return (
    <div className="max-w-4xl">
      <PageHeader
        title="Methodology"
        subtitle="How SkillPulse India turns labour-market signals into district skill-gap intelligence. Every score is transparent and every weight is configurable."
      />

      <div className="card p-5 mb-6">
        <SectionHeader title="Pipeline" />
        <p className="text-sm leading-relaxed">
          <b>Data → NLP → Statistics/ML → Gap engine → Recommendation → Visualization.</b>{" "}
          Job postings, employer surveys, industry consultations, training records and
          placement outcomes are aggregated per district. Skills are extracted from job
          text, normalised to a canonical taxonomy, scored for demand and emergence,
          compared against local training supply, and converted into explainable
          recommendations. The LLM layer is an optional enhancement — it never makes the
          decision.
        </p>
      </div>

      <div className="space-y-6">
        <section>
          <h2 className="text-lg font-semibold mb-2">1. Skill extraction & normalisation</h2>
          <p className="text-sm text-muted mb-2">
            A deterministic alias dictionary matches surface forms (e.g. “Python 3”, “AWS
            Cloud”, “devsecops”) to canonical skills, backed by a TF-IDF cosine-similarity
            semantic layer for terms not in the dictionary. Sentence-transformer embeddings
            can be enabled as a drop-in upgrade. Inspired by ESCO-based and weakly-supervised
            skill-extraction literature.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-2">2. Demand index (0–100)</h2>
          <p className="text-sm text-muted mb-3">
            A weighted blend of six components, each normalised to 0–100. Job volume is
            log-scaled to compress heavy tails; growth is measured over the 12-month window
            with denominator smoothing to avoid low-volume distortion.
          </p>
          <WeightTable title="Demand weights" weights={m.demand_weights} />
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-2">3. Emerging-skill detection</h2>
          <p className="text-sm text-muted mb-3">
            Emergence combines demand growth, recency of activity, cross-industry adoption
            and employer signals, then labels each skill Emerging / Growing / Stable /
            Declining from the data — not by hand.
          </p>
          <WeightTable title="Emergence weights" weights={m.emergence_weights} />
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-2">4. Supply index & skill gap</h2>
          <p className="text-sm text-muted mb-3">
            Supply blends local training capacity, completion, placement and learner
            pipeline. The gap is <code className="num">clamp(Demand − Supply, 0, 100)</code>,
            classified by configurable thresholds.
          </p>
          <div className="grid sm:grid-cols-2 gap-4">
            <WeightTable title="Supply weights" weights={m.supply_weights} />
            <div className="card p-4">
              <SectionHeader title="Gap thresholds" />
              <table className="w-full">
                <tbody>
                  {m.gap_thresholds.map((t) => (
                    <tr key={t.label}>
                      <td className="td">{t.label}</td>
                      <td className="td text-right num">≥ {t.min}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-2">5. Course alignment & obsolescence</h2>
          <p className="text-sm text-muted mb-3">
            Existing courses are scored on skill-demand alignment, placement, utilisation and
            curriculum freshness. Low scores are flagged for review — never auto-deleted.
          </p>
          <WeightTable title="Alignment weights" weights={m.alignment_weights} />
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-2">6. Forecasting</h2>
          <p className="text-sm text-muted">
            A simple, transparent ensemble (linear trend + moving average + exponential
            smoothing) estimates 3/6/12-month demand with an uncertainty band widening over
            the horizon. Forecasts are estimates, not guarantees.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-2">7. Recommendation engine</h2>
          <p className="text-sm text-muted">
            Transparent rules over the computed signals produce actions — Create, Expand,
            Update, Reduce, Upskill trainers, Invest in equipment, or Monitor — each ranked
            by a priority score (0.5·gap + 0.3·demand + 0.2·emergence) and shipped with its
            evidence. No per-district outcome is hard-coded.
          </p>
        </section>

        <section className="card p-5" style={{ borderColor: "var(--moderate)" }}>
          <h2 className="text-lg font-semibold mb-2">Data provenance & limitations</h2>
          <p className="text-sm mb-3">{meta.disclaimer}</p>
          <ul className="text-sm text-muted space-y-1.5 list-disc pl-5">
            <li>
              This prototype runs on a <b>synthetic</b> dataset (
              {meta.provenance.job_postings.toLocaleString()} job signals,{" "}
              {meta.provenance.districts} districts, {meta.provenance.courses} courses)
              covering {meta.coverage_months.length} months. District names and coordinates
              are real; all labour statistics are generated for demonstration.
            </li>
            <li>The model cannot perfectly predict future employment; treat forecasts as scenarios.</li>
            <li>Recommendations are decision-support, not authoritative policy.</li>
            <li>The platform analyses districts, industries, skills and courses — never individual citizens.</li>
            <li>AI-assisted components require human validation before any policy implementation.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-2">Research basis</h2>
          <ul className="text-sm text-muted space-y-1 list-disc pl-5">
            <li>ILO — Towards a more effective Labour Market Information System in India</li>
            <li>ESCO-based and weakly-supervised skill extraction from job postings</li>
            <li>LLM-based ESCO skill matching; emerging-skill detection from job ads</li>
            <li>AI-assisted education–employment alignment and course generation</li>
          </ul>
        </section>
      </div>
    </div>
  );
}
