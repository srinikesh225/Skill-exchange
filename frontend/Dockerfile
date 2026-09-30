# SkillPulse India — frontend image (Next.js).
# NOTE: provided for the Docker path; not verified on the build machine.
FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
# Deterministic install from the lockfile, with generous retries so a transient
# ECONNRESET from the npm registry doesn't fail the whole image build.
# Falls back to `npm install` if the lockfile is absent or out of sync.
RUN npm config set fetch-retries 5 \
 && npm config set fetch-retry-mintimeout 20000 \
 && npm config set fetch-retry-maxtimeout 120000 \
 && npm config set fetch-timeout 600000 \
 && (npm ci || npm install)

FROM node:20-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Next.js bakes next.config rewrites() at BUILD time, so BACKEND_URL must be set
# here (not just at runtime) for the /api/* proxy to target the right host.
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=$BACKEND_URL
RUN npm run build

FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.mjs ./next.config.mjs
EXPOSE 3000
# BACKEND_URL is used by next.config rewrites to proxy /api/* to the API service.
ENV BACKEND_URL=http://backend:8000
CMD ["npm", "run", "start"]
