# SkillPulse India — frontend image (Next.js).
# NOTE: provided for the Docker path; not verified on the build machine.
FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

FROM node:20-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
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
