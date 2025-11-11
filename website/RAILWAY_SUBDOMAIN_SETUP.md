# Railway Subdomain Deployment Guide

Quick guide to deploy your two subdomains on Railway tonight:
- **wizards.smartaimemory.com** - Software & AI wizard examples
- **healthcare.smartaimemory.com** - AI Nurse Florence dashboard

## Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

## Step 2: Login to Railway

```bash
railway login
```

This will open a browser window for authentication.

## Step 3: Deploy Wizards Subdomain

### 3.1 Navigate to your wizards app directory

```bash
cd /path/to/wizards-showcase
# Or if using the main website directory:
cd /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/website
```

### 3.2 Initialize Railway project

```bash
railway init
```

When prompted:
- **Project name**: `smartaimemory-wizards`
- **Environment**: `production`

### 3.3 Set environment variables

```bash
railway variables set NEXT_PUBLIC_SITE_URL=https://wizards.smartaimemory.com
railway variables set NEXT_PUBLIC_PLAUSIBLE_DOMAIN=wizards.smartaimemory.com
railway variables set SENDGRID_API_KEY=your_sendgrid_api_key_here
railway variables set SENDGRID_FROM_EMAIL=patrick.roebuck@pm.me
railway variables set CONTACT_EMAIL=patrick.roebuck@pm.me
railway variables set NODE_ENV=production
```

### 3.4 Deploy to Railway

```bash
railway up
```

### 3.5 Add custom domain in Railway dashboard

1. Go to https://railway.app/dashboard
2. Select your `smartaimemory-wizards` project
3. Click on "Settings" tab
4. Scroll to "Domains" section
5. Click "Add Custom Domain"
6. Enter: `wizards.smartaimemory.com`
7. Railway will show you a CNAME record to add to your DNS

**Railway will provide something like:**
```
CNAME: wizards → your-project.up.railway.app
```

## Step 4: Deploy Healthcare Subdomain

### 4.1 Navigate to healthcare dashboard directory

```bash
cd /path/to/healthcare-dashboard
```

### 4.2 Initialize Railway project

```bash
railway init
```

When prompted:
- **Project name**: `smartaimemory-healthcare`
- **Environment**: `production`

### 4.3 Set environment variables

```bash
railway variables set NEXT_PUBLIC_SITE_URL=https://healthcare.smartaimemory.com
railway variables set NEXT_PUBLIC_PLAUSIBLE_DOMAIN=healthcare.smartaimemory.com
railway variables set SENDGRID_API_KEY=your_sendgrid_api_key_here
railway variables set SENDGRID_FROM_EMAIL=patrick.roebuck@pm.me
railway variables set CONTACT_EMAIL=patrick.roebuck@pm.me
railway variables set NODE_ENV=production
# Add any healthcare-specific environment variables
```

### 4.4 Deploy to Railway

```bash
railway up
```

### 4.5 Add custom domain in Railway dashboard

1. Go to https://railway.app/dashboard
2. Select your `smartaimemory-healthcare` project
3. Click on "Settings" tab
4. Scroll to "Domains" section
5. Click "Add Custom Domain"
6. Enter: `healthcare.smartaimemory.com`
7. Railway will show you the CNAME record

## Step 5: Configure DNS (CNAME Records)

Log in to your DNS provider (where smartaimemory.com is registered) and add these CNAME records:

### For Wizards Subdomain

```
Type: CNAME
Host: wizards
Value: [your-wizards-project].up.railway.app
TTL: 3600 (or Auto)
```

### For Healthcare Subdomain

```
Type: CNAME
Host: healthcare
Value: [your-healthcare-project].up.railway.app
TTL: 3600 (or Auto)
```

**Example DNS Configuration:**

| Type  | Host       | Value                                    | TTL  |
|-------|------------|------------------------------------------|------|
| CNAME | wizards    | smartaimemory-wizards-prod.up.railway.app | 3600 |
| CNAME | healthcare | smartaimemory-healthcare-prod.up.railway.app | 3600 |

## Step 6: Wait for DNS Propagation & SSL

1. **DNS Propagation**: Usually takes 5-30 minutes
2. **SSL Certificate**: Railway automatically provisions SSL after DNS verification (1-5 minutes)

**Check DNS propagation:**
```bash
dig wizards.smartaimemory.com CNAME +short
dig healthcare.smartaimemory.com CNAME +short
```

**Online checker:**
- https://dnschecker.org

## Common DNS Provider Instructions

### Namecheap

1. Log in to Namecheap
2. Domain List → Manage → Advanced DNS
3. Add New Record:
   - Type: CNAME Record
   - Host: `wizards`
   - Value: `your-project.up.railway.app`
   - TTL: Automatic
4. Repeat for `healthcare`

### GoDaddy

1. Log in to GoDaddy
2. My Products → DNS → Manage Zones
3. Add → CNAME
   - Name: `wizards`
   - Value: `your-project.up.railway.app`
   - TTL: 1 hour
4. Repeat for `healthcare`

### Cloudflare

1. Log in to Cloudflare
2. Select smartaimemory.com
3. DNS → Add record
   - Type: CNAME
   - Name: `wizards`
   - Target: `your-project.up.railway.app`
   - Proxy status: DNS only (gray cloud)
   - TTL: Auto
4. Repeat for `healthcare`

## Railway Configuration Files

### Create `railway.toml` in each project

**For wizards app:**
```toml
[build]
builder = "NIXPACKS"
buildCommand = "npm install && npm run build"

[deploy]
startCommand = "npm start"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[deploy.envVariables]]
name = "NODE_ENV"
value = "production"
```

**For healthcare app:**
```toml
[build]
builder = "NIXPACKS"
buildCommand = "npm install && npm run build"

[deploy]
startCommand = "npm start"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[deploy.envVariables]]
name = "NODE_ENV"
value = "production"
```

## Verify Deployment

### Check Railway Dashboard

1. Go to https://railway.app/dashboard
2. Verify both projects show "Active" status
3. Check deployment logs for any errors

### Test Domains

Once DNS propagates:

```bash
curl -I https://wizards.smartaimemory.com
curl -I https://healthcare.smartaimemory.com
```

Both should return `200 OK` with SSL.

## Update Main Website Links

After deployment, update the main website to link to the new subdomains:

**In `website/app/page.tsx`:**

```tsx
{/* Software Development Dashboard */}
<a
  href="https://wizards.smartaimemory.com"
  className="btn btn-primary"
  target="_blank"
  rel="noopener noreferrer"
>
  View Wizards Examples →
</a>

{/* Healthcare Dashboard (if you add it back as a link) */}
<a
  href="https://healthcare.smartaimemory.com"
  className="btn btn-primary"
  target="_blank"
  rel="noopener noreferrer"
>
  View Healthcare Dashboard →
</a>
```

## Continuous Deployment (Optional)

Connect Railway to your GitHub repository for automatic deployments:

1. In Railway dashboard → Settings
2. Connect to GitHub repository
3. Select branch (e.g., `main`)
4. Enable "Auto Deploy"

Now every push to main will automatically deploy!

## Monitoring

### View Logs

```bash
# For wizards project
railway logs

# Or in dashboard
```

### View Metrics

Railway dashboard shows:
- CPU usage
- Memory usage
- Network traffic
- Deployment history

## Troubleshooting

### Deployment Failed

```bash
# Check logs
railway logs

# Redeploy
railway up --detach
```

### Domain Not Working

1. **Verify DNS**: `dig wizards.smartaimemory.com CNAME +short`
2. **Check Railway domain status**: Dashboard → Settings → Domains
3. **Wait**: DNS can take up to 24 hours (usually 5-30 minutes)

### SSL Certificate Not Provisioning

1. Verify CNAME record is correct
2. Wait 5-10 minutes after DNS propagates
3. Check Railway dashboard for SSL status
4. Contact Railway support if issue persists

## Cost Estimate

Railway pricing:
- **Hobby Plan**: $5/month per project (includes $5 credit)
- **Usage-based**: After credit, pay for resources used
- **Estimate**: ~$5-20/month for both projects depending on traffic

## Quick Command Reference

```bash
# Login
railway login

# Initialize project
railway init

# Set environment variable
railway variables set KEY=value

# Deploy
railway up

# View logs
railway logs

# Open in browser
railway open

# Link to existing project
railway link

# Check status
railway status
```

## Timeline for Tonight

1. **Install CLI & Login**: 2 minutes
2. **Deploy wizards app**: 5-10 minutes
3. **Deploy healthcare app**: 5-10 minutes
4. **Add custom domains in Railway**: 2 minutes
5. **Configure DNS CNAME records**: 5 minutes
6. **Wait for DNS propagation**: 5-30 minutes
7. **SSL provisioning**: 1-5 minutes (automatic)

**Total: 25-60 minutes** 🚀

## Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Email me**: patrick.roebuck@pm.me

---

**Ready to deploy! Start with Step 1 and work through each step sequentially.**
