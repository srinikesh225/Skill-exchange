# Demo script (~3 minutes)

Prereqs: backend running (`uvicorn app.main:app`) with demo data generated, frontend
running (`npm run dev`). Open **http://localhost:3000**.

---

**0:00 — The problem (15s).**
"Training programmes and job-market demand are misaligned, and it differs by district.
SkillPulse India is a decision-support tool, not a course portal: it goes
Data → Analysis → Skill gap → Recommendation → Training plan."

**0:15 — Home + map (20s).**
Point to the India map: "Every district, coloured by its skill-gap index, from real
job-market signals." Note the persistent banner: "All data is synthetic and clearly
labelled — no invented statistics."

**0:35 — Open Hyderabad (25s).**
Click Hyderabad → **Open district intelligence**. Walk the KPI cards (Skill Gap Index,
Demand, Supply, Emerging). "These are computed, not entered."

**1:00 — Gaps & emerging (20s).**
Show *Largest skill gaps* (Python, Azure, ML, Generative AI) and *Emerging skills*
(Azure +117 %, Deep Learning +100 %). "The engine found these from the data."

**1:20 — Drill into a skill (25s).**
Click **Generative AI** → skill explorer. Show the **demand score breakdown** (each
component and its weighted contribution summing to the index), then the **12-month forecast
with its uncertainty band**. "Transparent, and honest about uncertainty."

**1:45 — The "Why?" (25s).**
Back to Hyderabad → a recommendation → **Why?**. Read the rationale and the evidence grid:
postings, employers, seats, placement, salary. "Every recommendation shows its evidence —
nothing is a black box."

**2:10 — Compare districts (40s) — the key moment.**
Go to **Compare** (defaults to two contrasting districts, or add Ludhiana). Show that
Hyderabad's plan is Python/Azure/GenAI while a manufacturing district's is Welding/CNC.
**"Same country. Same engine. Different district → different demand → different skill gap →
different training plan. There is no hard-coded per-district logic."**

**2:50 — Close (10s).**
"Methodology page documents every formula and weight. Swap the synthetic dataset for real
job-market and training data, point the database at PostgreSQL, and this runs on live
signals."

---

## Backup talking points

- **Not a portal:** derives recommendations from observed demand, not a fixed catalogue.
- **Defensible:** statistics/ML do the work; the LLM is an optional enhancement, never the
  decision-maker.
- **Actionable:** Create / Expand / Update / Reduce / Upskill / Monitor, with suggested
  capacity and target skills.
- **Course intelligence:** flags obsolete/oversupplied courses for review (never auto-deletes).
- **Ethical:** analyses districts and skills, never individual citizens; requires human
  validation before policy.
