# Limitations & roadmap

## Known limitations

1. **Synthetic data.** The prototype runs on a generated dataset. It demonstrates the
   method and the product, not real labour-market findings. District names/coords are real;
   all labour statistics are synthetic.
2. **Forecasting is intentionally simple.** A linear + moving-average + exponential-smoothing
   ensemble with an uncertainty band. It estimates near-term direction; it is not a
   causal or macroeconomic model. Treat forecasts as scenarios.
3. **Extraction taxonomy is curated (~47 skills).** Real deployment needs a full taxonomy
   (e.g. ESCO/NCO) and the transformer semantic layer enabled for messy real text.
4. **Supply modelling is coarse.** Capacity/completion/placement are the current supply
   signals; real MIS data (trainer availability, equipment, learner outcomes over time)
   would enrich it.
5. **No authentication / multi-tenancy.** The API is read-only and unauthenticated,
   appropriate for a demo, not for production.
6. **Docker & PostgreSQL paths are provided but unverified** on the build machine (neither
   was installed). SQLite is the verified path; the code is Postgres-ready via `DATABASE_URL`.
7. **E2E tests are manual** (headless-browser verification). Playwright specs are planned.

## Ethical guardrails (built in)

- Analyses **districts, industries, skills and courses — never individual citizens.**
- No ranking of people; no sensitive personal data.
- Recommendations are **decision-support**, explicitly not authoritative policy.
- Uncertainty is shown (forecast bands, confidence).
- Synthetic data is labelled everywhere; no invented credibility (no fake reviews, logos,
  ratings, awards, or claims).
- AI-assisted outputs require human validation before implementation.

## Roadmap

### Near term
- **Real ingestion adapters** for job boards / career pages, employer-survey intake, and
  training MIS; seed real NSO district labour indicators.
- **Enable transformer embeddings** (`requirements-ml.txt`) and expand the taxonomy to
  ESCO/NCO with occupation mapping.
- **Playwright E2E** across the demo flow; CI running pytest + build + E2E.
- **PostgreSQL + pgvector** deployment; verify docker-compose.

### Medium term
- **Confidence intervals from data volume** surfaced per metric; provenance drill-downs.
- **Proficiency levels** (entry/intermediate/advanced) per skill and role.
- **Occupation-level demand** (not just skills) with role → skill decomposition.
- **Scenario planning** ("what if we add 300 GenAI seats in Pune?").
- **Exportable district training plans** (PDF) for training authorities.

### Longer term
- **Automated employer-validation loop** (survey integration) feeding the demand signal.
- **Placement-outcome feedback** to close the loop on recommendation quality.
- **Role-based access** for national / state / district users.
- **Model monitoring** and periodic re-validation against realised outcomes.
