# SkillPulse India — backend image.
# NOTE: provided for the PostgreSQL/Docker path; not verified on the build machine
# (Docker was unavailable there). The SQLite quickstart in README is the verified path.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# psycopg[binary] added here for the PostgreSQL path (not in requirements.txt,
# which keeps the SQLite quickstart dependency-light).
COPY requirements.txt .
RUN pip install -r requirements.txt "psycopg[binary]==3.2.3"

COPY . .

# Bake the reproducible demo dataset into the image so container start is fast
# (no per-boot generation) and works on read-only/ephemeral filesystems.
RUN python scripts/generate_demo_data.py

RUN chmod +x docker-entrypoint.sh
# Render/Fly inject $PORT; EXPOSE is informational only.
EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
