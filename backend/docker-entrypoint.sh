#!/usr/bin/env bash
set -e

# Decide whether to (re)generate the dataset:
#  - Default (SQLite): the image already has a baked skillpulse.db -> skip (fast start,
#    used by the Render deployment).
#  - A non-SQLite DATABASE_URL (e.g. Postgres via docker-compose): the target database is
#    separate from the baked file, so seed it on start.
NEED_GEN=0
[ -f skillpulse.db ] || NEED_GEN=1
case "${DATABASE_URL:-sqlite}" in
  sqlite*|"") : ;;   # SQLite -> rely on the baked DB
  *) NEED_GEN=1 ;;   # Postgres/other -> seed the external DB
esac

if [ "$NEED_GEN" = "1" ]; then
  echo "Generating demo dataset into ${DATABASE_URL:-local SQLite file}..."
  python scripts/generate_demo_data.py
fi

# Bind to the platform-provided port (Render/Fly set $PORT); default 8000 locally.
echo "Starting API on 0.0.0.0:${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
