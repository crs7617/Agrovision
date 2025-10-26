# Frontend Dockerfile - Next.js (production build)
# Use a node image compatible with Next 16 / React 19
FROM node:20-alpine AS deps
WORKDIR /app

# Install deps
COPY package.json package-lock.json* pnpm-lock.yaml* ./
# If you're using npm/yarn/pnpm the lock file will vary; try to install with npm by default
RUN npm ci --legacy-peer-deps || true

# Copy source
FROM node:20-alpine AS builder
WORKDIR /app
COPY . .

# Install and build
RUN npm ci --legacy-peer-deps
RUN npm run build

# Production image
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copy build artifacts
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# Install only production deps
RUN npm ci --only=production --legacy-peer-deps || true

EXPOSE 3000

# Default start command for Next.js production
CMD ["npm", "run", "start"]
