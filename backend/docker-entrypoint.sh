#!/usr/bin/env bash
set -e

# Wait briefly for the database, then seed if empty, then serve.
echo "Generating demo dataset (idempotent)..."
python scripts/generate_demo_data.py || echo "Data generation step reported an issue; continuing."

echo "Starting API on 0.0.0.0:8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
