# Next.js Production Dockerfile for Railway
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY website/package.json website/package-lock.json* ./
RUN npm ci

# Copy website source
COPY website/ ./

# Build the app
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build:railway

# Runtime
ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000

CMD ["npm", "start"]
