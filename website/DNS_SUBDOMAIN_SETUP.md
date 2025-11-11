# DNS Subdomain Setup Guide

This guide will help you set up two subdomains for Smart AI Memory:
1. **wizards.smartaimemory.com** - Software and AI wizard examples
2. **healthcare.smartaimemory.com** - AI Nurse Florence dashboard

## Prerequisites

- Access to your domain registrar or DNS provider (where smartaimemory.com is registered)
- Server IP addresses where you'll host each subdomain
- SSH access to your deployment servers

## Recommended Subdomain Structure

```
wizards.smartaimemory.com      → Software & AI wizard examples
healthcare.smartaimemory.com   → AI Nurse Florence dashboard
```

## Step 1: Determine Your Hosting IPs

First, decide where you'll deploy each subdomain. Options:

### Option A: Vercel (Recommended)
- Vercel provides automatic DNS for subdomains
- No need for A records, use CNAME instead
- Free SSL certificates
- Global CDN

### Option B: Railway
- Railway provides a deployment URL
- Use CNAME record pointing to Railway's domain
- Automatic SSL

### Option C: Self-Hosted VPS
- You'll need the server IP address
- Use A records pointing to your server IP
- Example: `123.456.789.012`

## Step 2: Configure DNS A Records

### For Domain Registrars (Namecheap, GoDaddy, etc.)

1. **Log in to your domain registrar**
   - Go to your domain management panel
   - Find "DNS Management" or "Advanced DNS"

2. **Add A Records for each subdomain**

   **For wizards subdomain:**
   ```
   Type: A Record
   Host: wizards
   Value: [Your server IP or use CNAME for Vercel/Railway]
   TTL: 3600 (1 hour) or Auto
   ```

   **For healthcare subdomain:**
   ```
   Type: A Record
   Host: healthcare
   Value: [Your server IP or use CNAME for Vercel/Railway]
   TTL: 3600 (1 hour) or Auto
   ```

3. **Alternative: CNAME Records (for Vercel/Railway)**

   **For wizards subdomain:**
   ```
   Type: CNAME Record
   Host: wizards
   Value: cname.vercel-dns.com (or your Railway domain)
   TTL: 3600 (1 hour) or Auto
   ```

   **For healthcare subdomain:**
   ```
   Type: CNAME Record
   Host: healthcare
   Value: cname.vercel-dns.com (or your Railway domain)
   TTL: 3600 (1 hour) or Auto
   ```

### Example DNS Configuration (A Records)

If your server IP is `192.0.2.100`:

| Type | Host       | Value          | TTL  |
|------|------------|----------------|------|
| A    | wizards    | 192.0.2.100    | 3600 |
| A    | healthcare | 192.0.2.100    | 3600 |

### Example DNS Configuration (CNAME Records for Vercel)

| Type  | Host       | Value                              | TTL  |
|-------|------------|------------------------------------|------|
| CNAME | wizards    | cname.vercel-dns.com               | 3600 |
| CNAME | healthcare | cname.vercel-dns.com               | 3600 |

## Step 3: Deploy Each Subdomain

### Option 1: Vercel Deployment (Recommended)

1. **Deploy wizards subdomain:**
   ```bash
   cd website  # or wherever your wizards app is
   vercel --prod
   ```

2. **Add custom domain in Vercel dashboard:**
   - Go to your project settings
   - Navigate to "Domains"
   - Add `wizards.smartaimemory.com`
   - Vercel will provide DNS instructions

3. **Repeat for healthcare subdomain:**
   ```bash
   cd healthcare-dashboard  # your healthcare app
   vercel --prod
   ```
   - Add `healthcare.smartaimemory.com` in Vercel dashboard

### Option 2: Railway Deployment

1. **Deploy wizards subdomain:**
   ```bash
   cd wizards-app
   railway init
   railway up
   ```

2. **Add custom domain in Railway dashboard:**
   - Go to your project settings
   - Add custom domain: `wizards.smartaimemory.com`
   - Railway will provide CNAME value

3. **Repeat for healthcare subdomain**

### Option 3: Self-Hosted VPS

1. **Set up Nginx virtual hosts:**

   Create `/etc/nginx/sites-available/wizards.smartaimemory.com`:
   ```nginx
   server {
       listen 80;
       server_name wizards.smartaimemory.com;

       location / {
           proxy_pass http://localhost:3001;  # Wizards app port
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

   Create `/etc/nginx/sites-available/healthcare.smartaimemory.com`:
   ```nginx
   server {
       listen 80;
       server_name healthcare.smartaimemory.com;

       location / {
           proxy_pass http://localhost:3002;  # Healthcare app port
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

2. **Enable the sites:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/wizards.smartaimemory.com /etc/nginx/sites-enabled/
   sudo ln -s /etc/nginx/sites-available/healthcare.smartaimemory.com /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **Set up SSL with Let's Encrypt:**
   ```bash
   sudo certbot --nginx -d wizards.smartaimemory.com -d healthcare.smartaimemory.com
   ```

## Step 4: Verify DNS Propagation

DNS changes can take 1-48 hours to propagate, but often work within minutes.

**Check DNS propagation:**
```bash
# Check A records
dig wizards.smartaimemory.com +short
dig healthcare.smartaimemory.com +short

# Check CNAME records
dig wizards.smartaimemory.com CNAME +short
dig healthcare.smartaimemory.com CNAME +short
```

**Online tools:**
- https://dnschecker.org
- https://www.whatsmydns.net

## Step 5: Deploy Your Applications

### Wizards Subdomain (Software & AI Examples)

Create a separate Next.js app or static site for wizard examples:

```bash
npx create-next-app@latest wizards-showcase
cd wizards-showcase
# Build your wizards example site
npm run build
```

Deploy to your chosen platform (Vercel/Railway/VPS)

### Healthcare Subdomain (AI Nurse Florence)

Deploy your existing healthcare dashboard:

```bash
cd healthcare-dashboard
# Update environment variables for production
# Build and deploy
npm run build
```

## Quick Start: Using Vercel (Fastest for Tonight)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   vercel login
   ```

2. **Deploy wizards app:**
   ```bash
   cd wizards-app
   vercel --prod
   # Follow prompts, then add custom domain in Vercel dashboard
   ```

3. **Deploy healthcare app:**
   ```bash
   cd healthcare-dashboard
   vercel --prod
   # Add custom domain in Vercel dashboard
   ```

4. **Add domains in Vercel dashboard:**
   - Go to each project → Settings → Domains
   - Add `wizards.smartaimemory.com` and `healthcare.smartaimemory.com`
   - Vercel will show you CNAME records to add to your DNS

5. **Add CNAME records in your DNS provider:**
   - Copy the CNAME values from Vercel
   - Add them to your DNS settings (as shown in Step 2)

6. **Wait for verification:**
   - Vercel will automatically verify and provision SSL
   - Usually takes 1-5 minutes

## Troubleshooting

### DNS Not Resolving

- **Check TTL**: Low TTL (300-3600) propagates faster
- **Clear DNS cache**: `sudo dscacheutil -flushcache` (macOS) or `ipconfig /flushdns` (Windows)
- **Wait**: Sometimes takes 1-24 hours

### SSL Certificate Issues

- **Vercel/Railway**: Automatic, no action needed
- **Let's Encrypt**: Run `sudo certbot renew` if expired
- **Verify ports**: Port 80 and 443 must be open

### App Not Loading

- **Check deployment**: Verify app is running on correct port
- **Check Nginx config**: `sudo nginx -t`
- **Check logs**: `sudo journalctl -u nginx -f`

## Environment Variables for Subdomains

### wizards.smartaimemory.com

```bash
NEXT_PUBLIC_SITE_URL=https://wizards.smartaimemory.com
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=wizards.smartaimemory.com
```

### healthcare.smartaimemory.com

```bash
NEXT_PUBLIC_SITE_URL=https://healthcare.smartaimemory.com
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=healthcare.smartaimemory.com
```

## Security Checklist

- [ ] SSL certificates installed (automatic with Vercel/Railway)
- [ ] HTTPS redirect enabled
- [ ] CORS configured if APIs are used
- [ ] Environment variables secured
- [ ] No hardcoded secrets in code

## Next Steps After Deployment

1. Update main website to link to subdomains
2. Add subdomain links to navigation
3. Update sitemap to include subdomain pages
4. Test all functionality on each subdomain
5. Monitor analytics for each subdomain separately

## Need Help?

If you encounter issues:
- Check Vercel/Railway documentation
- Verify DNS with `dig` or online tools
- Contact your DNS provider support
- Email: patrick.roebuck@pm.me

---

**Estimated Time to Deploy Tonight:**
- Vercel (CNAME): 10-30 minutes
- Railway (CNAME): 10-30 minutes
- Self-hosted (A records): 30-60 minutes + DNS propagation time

**Recommended: Use Vercel for fastest deployment tonight.**
