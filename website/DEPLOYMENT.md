# Deployment Guide

This guide covers deploying the Smart AI Memory website to various platforms.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Vercel Deployment](#vercel-deployment)
- [Railway Deployment](#railway-deployment)
- [Self-Hosted Deployment](#self-hosted-deployment)
- [Docker Deployment](#docker-deployment)

## Environment Variables

Create a `.env.local` file with the following variables:

```bash
# Required for SendGrid email integration
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@smartaimemory.com
CONTACT_EMAIL=contact@smartaimemory.com

# Required for Plausible Analytics
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=smartaimemory.com

# Optional: Self-hosted Plausible
# NEXT_PUBLIC_PLAUSIBLE_API_HOST=https://plausible.io

# Optional: Mailchimp (alternative to SendGrid for newsletter)
# MAILCHIMP_API_KEY=your_mailchimp_api_key
# MAILCHIMP_LIST_ID=your_list_id
# MAILCHIMP_SERVER_PREFIX=us1

# Site Configuration
NEXT_PUBLIC_SITE_URL=https://smartaimemory.com
NODE_ENV=production
```

## Vercel Deployment

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Smart-AI-Memory/empathy/tree/main/website)

### Manual Deployment

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
cd website
vercel
```

4. Add environment variables in Vercel dashboard:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add all required variables from `.env.example`

5. Deploy to production:
```bash
vercel --prod
```

### Vercel Configuration

The `vercel.json` file is already configured. Key settings:

- **Framework**: Next.js
- **Build Command**: `npm run build`
- **Region**: Washington DC (iad1)
- **Environment Variables**: Managed via Vercel dashboard

## Railway Deployment

### Setup

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Initialize project:
```bash
cd website
railway init
```

4. Add environment variables:
```bash
railway variables set SENDGRID_API_KEY=your_key
railway variables set NEXT_PUBLIC_PLAUSIBLE_DOMAIN=smartaimemory.com
# Add all other variables...
```

5. Deploy:
```bash
railway up
```

### Railway Configuration

The `railway.toml` file configures:

- Build command
- Start command
- Health checks
- Environment detection

### GitHub Actions (Automatic Deployment)

The repository includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that automatically deploys to Railway on push to `main`.

**Setup:**

1. Add `RAILWAY_TOKEN` to GitHub Secrets:
   - Go to repository Settings > Secrets and variables > Actions
   - Add new secret: `RAILWAY_TOKEN`
   - Get token from Railway dashboard

2. Add other secrets:
   - `NEXT_PUBLIC_PLAUSIBLE_DOMAIN`
   - `NEXT_PUBLIC_SITE_URL`

3. Push to main branch - automatic deployment!

## Self-Hosted Deployment

### Requirements

- Node.js 20+
- npm or yarn
- Process manager (PM2 recommended)

### Setup

1. Clone repository:
```bash
git clone https://github.com/Smart-AI-Memory/empathy.git
cd empathy/website
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` with your environment variables

4. Build application:
```bash
npm run build
```

5. Start with PM2:
```bash
npm install -g pm2
pm2 start npm --name "smartaimemory-website" -- start
pm2 save
pm2 startup
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name smartaimemory.com www.smartaimemory.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d smartaimemory.com -d www.smartaimemory.com
```

## Docker Deployment

### Dockerfile

Create a `Dockerfile` in the website directory:

```dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package*.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

RUN mkdir .next
RUN chown nextjs:nodejs .next

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  website:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
      - NEXT_PUBLIC_PLAUSIBLE_DOMAIN=${NEXT_PUBLIC_PLAUSIBLE_DOMAIN}
    restart: unless-stopped
```

### Build and Run

```bash
docker-compose up -d
```

## Post-Deployment Checklist

- [ ] Environment variables configured
- [ ] SendGrid API key added and verified
- [ ] Plausible Analytics tracking working
- [ ] Contact form tested
- [ ] Newsletter signup tested
- [ ] SSL certificate installed
- [ ] Domain DNS configured
- [ ] Sitemap accessible at /sitemap.xml
- [ ] Robots.txt accessible at /robots.txt
- [ ] All pages loading correctly
- [ ] Dark mode working
- [ ] Mobile responsiveness verified
- [ ] Performance tested (Lighthouse score)
- [ ] SEO meta tags verified

## Monitoring

### Vercel

- Built-in analytics dashboard
- Real-time logs
- Performance insights

### Railway

- Deployment logs
- Metrics dashboard
- Health checks

### Self-Hosted

Use PM2 monitoring:
```bash
pm2 monit
pm2 logs
```

## Troubleshooting

### Build Failures

1. Check Node.js version (should be 20+)
2. Delete `node_modules` and `.next`:
   ```bash
   rm -rf node_modules .next
   npm install
   npm run build
   ```

### Email Not Sending

1. Verify SendGrid API key
2. Check SendGrid sender verification
3. Review logs for error messages

### Analytics Not Tracking

1. Verify `NEXT_PUBLIC_PLAUSIBLE_DOMAIN` is set
2. Check browser console for errors
3. Verify Plausible script is loading

## Support

For deployment issues:
- GitHub Issues: https://github.com/Smart-AI-Memory/empathy/issues
- Email: contact@smartaimemory.com
- Documentation: smartaimemory.com/docs
