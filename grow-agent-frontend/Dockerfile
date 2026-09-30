# Dockerfile for grow-agent-frontend (Next.js) on Cloud Run

# Rebuild the source code only when needed
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
COPY next.config.* ./
COPY tsconfig*.json ./
COPY .env.production ./
COPY app ./app
COPY public ./public
COPY lib ./lib
RUN npm install

RUN npm run build

# Production image, copy all the files and run next
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=8080

# Copy public assets
COPY --from=builder /app/public ./public

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 8080

CMD ["node", "server.js"]
