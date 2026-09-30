"""Reproducibly (re)build the entire demo dataset and all computed intelligence.

    cd backend
    python scripts/generate_demo_data.py

Steps: create tables -> generate synthetic raw signals -> run the analytical
pipeline (demand/emergence/supply/gap/recommendations/course-alignment).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Make `import app...` work regardless of the current working directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal, init_db  # noqa: E402
from app.services import generator, pipeline  # noqa: E402


def main() -> None:
    t0 = time.time()
    print("[1/3] Creating database schema...")
    init_db()

    db = SessionLocal()
    try:
        print("[2/3] Generating synthetic raw signals (districts, skills, jobs, "
              "employer signals, courses)...")
        gen = generator.generate(db)
        for k, v in gen.items():
            if k != "months":
                print(f"      {k}: {v}")

        print("[3/3] Running analytical pipeline (demand -> emergence -> supply -> "
              "gap -> recommendations -> course alignment)...")
        comp = pipeline.compute(db)
        for k, v in comp.items():
            print(f"      {k}: {v}")
    finally:
        db.close()

    print(f"\nDone in {time.time() - t0:.1f}s. Synthetic demo dataset ready.")
    print("NOTE: all metrics are synthetic demo data, not official statistics.")


if __name__ == "__main__":
    main()
