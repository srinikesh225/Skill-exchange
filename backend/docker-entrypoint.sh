#!/usr/bin/env bash
set -e

# The image is built with the demo DB baked in (see Dockerfile). Regenerate only
# if it is somehow missing (e.g. a mounted empty volume).
if [ ! -f skillpulse.db ]; then
  echo "No database found; generating demo dataset..."
  python scripts/generate_demo_data.py
fi

# Bind to the platform-provided port (Render/Fly set $PORT); default 8000 locally.
echo "Starting API on 0.0.0.0:${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
