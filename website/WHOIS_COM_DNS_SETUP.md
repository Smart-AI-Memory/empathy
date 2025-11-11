# Whois.com DNS Configuration for Railway Subdomains

Quick guide for adding CNAME records in whois.com for your Railway deployments.

## Step-by-Step: Adding CNAME Records in Whois.com

### 1. Log in to Whois.com

1. Go to https://www.whois.com
2. Click "Sign In" (top right)
3. Enter your credentials

### 2. Access DNS Management

1. After login, click on "My Account" or "Dashboard"
2. Find your domain: `smartaimemory.com`
3. Click on the domain name to manage it
4. Look for "DNS Management" or "Manage DNS" option
5. Click on it to access DNS settings

### 3. Add CNAME Record for Wizards Subdomain

After deploying to Railway and getting your CNAME value (e.g., `smartaimemory-wizards-prod.up.railway.app`):

1. Click "Add New Record" or "Add Record"
2. **Record Type**: Select `CNAME`
3. **Host/Name**: Enter `wizards`
4. **Points To/Value**: Enter the Railway domain you got (e.g., `smartaimemory-wizards-prod.up.railway.app`)
5. **TTL**: Leave as default (3600) or select "1 hour"
6. Click "Save" or "Add Record"

**Example:**
```
Type: CNAME
Host: wizards
Value: smartaimemory-wizards-prod.up.railway.app
TTL: 3600
```

### 4. Add CNAME Record for Healthcare Subdomain

Repeat the same process:

1. Click "Add New Record" or "Add Record"
2. **Record Type**: Select `CNAME`
3. **Host/Name**: Enter `healthcare`
4. **Points To/Value**: Enter the Railway domain (e.g., `smartaimemory-healthcare-prod.up.railway.app`)
5. **TTL**: Leave as default (3600)
6. Click "Save" or "Add Record"

**Example:**
```
Type: CNAME
Host: healthcare
Value: smartaimemory-healthcare-prod.up.railway.app
TTL: 3600
```

### 5. Verify Your DNS Records

After saving, your DNS records should look like this:

| Type  | Host       | Value                                    | TTL  |
|-------|------------|------------------------------------------|------|
| A     | @          | [your current IP]                        | 3600 |
| CNAME | www        | smartaimemory.com                        | 3600 |
| CNAME | wizards    | smartaimemory-wizards-prod.up.railway.app | 3600 |
| CNAME | healthcare | smartaimemory-healthcare-prod.up.railway.app | 3600 |

## Whois.com Interface Notes

### If You See "Advanced DNS" or "DNS Zone File"

Some registrars show an "Advanced" mode with a text-based zone file. If you see this:

```
wizards.smartaimemory.com.    3600    IN    CNAME    smartaimemory-wizards-prod.up.railway.app.
healthcare.smartaimemory.com. 3600    IN    CNAME    smartaimemory-healthcare-prod.up.railway.app.
```

Note: The trailing dots (`.`) are normal in zone files.

### Common Whois.com DNS Settings Locations

Depending on your account type, DNS settings may be at:
- **Account Dashboard** → Domain List → DNS Management
- **Domain Details** → DNS Settings
- **Manage Domain** → Advanced DNS

### Important Notes for Whois.com

1. **Do NOT use '@' for subdomains** - Use just the subdomain name (`wizards`, not `@wizards`)
2. **Do NOT add a trailing dot** in the Host field (whois.com adds it automatically)
3. **DO include the full Railway domain** in the Value field
4. **Propagation time**: Whois.com typically propagates in 5-15 minutes

## Get Railway CNAME Values

Before configuring DNS in whois.com, deploy to Railway and get your CNAME values:

### Step 1: Deploy Wizards App to Railway

```bash
cd /path/to/wizards-app
railway init
# Name: smartaimemory-wizards
railway up
```

### Step 2: Add Custom Domain in Railway Dashboard

1. Go to https://railway.app/dashboard
2. Open `smartaimemory-wizards` project
3. Settings → Domains → Add Custom Domain
4. Enter: `wizards.smartaimemory.com`
5. **Railway shows you the CNAME value** - Copy this!

Example: `smartaimemory-wizards-prod.up.railway.app`

### Step 3: Add CNAME in Whois.com

Use the CNAME value Railway provided in whois.com DNS settings (as shown above).

### Step 4: Repeat for Healthcare App

```bash
cd /path/to/healthcare-dashboard
railway init
# Name: smartaimemory-healthcare
railway up
```

Then add domain in Railway dashboard and configure DNS in whois.com.

## Verification

### Check DNS Propagation

After adding CNAME records in whois.com:

```bash
# Check if CNAME is resolving
dig wizards.smartaimemory.com CNAME +short
# Should return: smartaimemory-wizards-prod.up.railway.app

dig healthcare.smartaimemory.com CNAME +short
# Should return: smartaimemory-healthcare-prod.up.railway.app
```

### Online DNS Checker

Use https://dnschecker.org to check propagation globally:
1. Enter `wizards.smartaimemory.com`
2. Select "CNAME" record type
3. Click "Search"

## Timeline

1. **Deploy to Railway**: 10 minutes
2. **Get CNAME values from Railway**: 1 minute
3. **Log in to whois.com**: 1 minute
4. **Add both CNAME records**: 3 minutes
5. **DNS propagation**: 5-15 minutes (whois.com is usually fast)
6. **Railway SSL provisioning**: 1-5 minutes (automatic)

**Total: 20-35 minutes** ✅

## Troubleshooting Whois.com

### "Record Already Exists"

If you get this error:
1. Check if subdomain already has a record
2. Delete old record first
3. Add new CNAME record

### "Invalid CNAME Format"

If whois.com rejects your CNAME:
1. Make sure you're using the full Railway domain
2. Don't add `http://` or `https://`
3. Don't add a trailing slash `/`
4. Use just: `your-project.up.railway.app`

### Can't Find DNS Management

If you can't find DNS settings:
1. Make sure domain is not locked
2. Check if nameservers are set to whois.com (not external like Cloudflare)
3. Contact whois.com support: support@whois.com

### DNS Not Propagating

1. **Wait**: Can take up to 24 hours (usually 5-15 min for whois.com)
2. **Clear cache**: `sudo dscacheutil -flushcache` (macOS)
3. **Check TTL**: Lower TTL (300-3600) propagates faster
4. **Verify in whois.com**: Make sure records were saved

## Complete Workflow for Tonight

```bash
# 1. Deploy wizards app
cd /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/website
railway login
railway init
railway variables set NEXT_PUBLIC_SITE_URL=https://wizards.smartaimemory.com
railway variables set NEXT_PUBLIC_PLAUSIBLE_DOMAIN=wizards.smartaimemory.com
railway up

# 2. Add domain in Railway dashboard → copy CNAME value

# 3. Add CNAME in whois.com:
#    Host: wizards
#    Value: [paste Railway CNAME]

# 4. Deploy healthcare app
cd /path/to/healthcare-dashboard
railway init
railway variables set NEXT_PUBLIC_SITE_URL=https://healthcare.smartaimemory.com
railway up

# 5. Add domain in Railway dashboard → copy CNAME value

# 6. Add CNAME in whois.com:
#    Host: healthcare
#    Value: [paste Railway CNAME]

# 7. Verify
dig wizards.smartaimemory.com CNAME +short
dig healthcare.smartaimemory.com CNAME +short

# 8. Wait for SSL (automatic)
```

## Support

- **Whois.com Support**: support@whois.com or live chat
- **Railway Docs**: https://docs.railway.app
- **Need help?**: patrick.roebuck@pm.me

---

**You're all set! Follow the steps above and you'll have both subdomains live tonight.** 🚀
