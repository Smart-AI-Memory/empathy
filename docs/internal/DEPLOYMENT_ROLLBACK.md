# Deployment Rollback Procedures

**Last Updated**: December 15, 2025
**Applies To**: Railway deployments of smartaimemory.com

---

## Overview

This document outlines procedures for rolling back deployments when issues are detected in production.

---

## Quick Rollback (Railway Dashboard)

### 1. Identify Last Known Good Deployment

1. Navigate to Railway dashboard: https://railway.app
2. Select the `empathy-framework` project
3. Click on the `website` service
4. Go to the **Deployments** tab
5. Identify the last successful deployment before the issue

### 2. Rollback to Previous Deployment

**Option A: Re-deploy from Git Commit**
```bash
# Find the last good commit
git log --oneline -10

# Note the commit hash (e.g., abc123f)
# In Railway dashboard:
# 1. Click "New Deployment"
# 2. Select "Deploy from Git"
# 3. Enter the commit hash
# 4. Click "Deploy"
```

**Option B: Use Railway CLI**
```bash
# Install Railway CLI if not already installed
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Rollback to previous deployment
railway rollback
```

### 3. Verify Rollback

After rollback:
1. Check deployment logs for errors
2. Visit https://smartaimemory.com
3. Test critical paths:
   - Blog posts load: `/blog/building-ai-memory-with-redis`
   - Docs dropdown works
   - FAQ page loads: `/faq`
   - Navigation functions correctly

---

## Common Rollback Scenarios

### Scenario 1: Blog Post Not Rendering

**Symptoms:**
- White/empty page on blog posts
- 500 errors in Railway logs

**Quick Fix:**
1. Check if static assets are missing in `.next/standalone`
2. Verify `output: 'standalone'` in `next.config.ts`
3. Check Dockerfile copies static assets correctly

**Rollback If:**
- Fix takes > 15 minutes
- Production traffic is significantly impacted

### Scenario 2: Navigation Broken

**Symptoms:**
- Dropdowns don't work
- Links return 404
- Mobile menu doesn't open

**Quick Fix:**
1. Check for JavaScript errors in browser console
2. Verify Next.js build completed successfully
3. Check for TypeScript errors in deployment logs

**Rollback If:**
- Navigation completely non-functional
- Users can't access core pages

### Scenario 3: Performance Degradation

**Symptoms:**
- Page load times > 3 seconds
- High server response times in Railway metrics
- Memory usage climbing

**Quick Fix:**
1. Check Redis connection (if applicable)
2. Review recent code changes for N+1 queries
3. Check for memory leaks in Node.js process

**Rollback If:**
- Page load times > 5 seconds
- Server approaching memory limits

---

## Rollback Decision Matrix

| Severity | Impact | Response Time | Action |
|----------|--------|---------------|--------|
| **Critical** | Site down or major functionality broken | Immediate | Rollback immediately, investigate later |
| **High** | Important features broken, workarounds exist | < 15 min | Attempt quick fix, rollback if not resolved in 15 min |
| **Medium** | Minor bugs, limited user impact | < 1 hour | Fix forward, rollback only if fix is complex |
| **Low** | Cosmetic issues, no functional impact | Next deploy | Fix in next scheduled deployment |

---

## Post-Rollback Checklist

After rolling back:

- [ ] Document what went wrong in incident log
- [ ] Notify team of rollback in Slack/Discord
- [ ] Create GitHub issue for the problem
- [ ] Test fix locally before re-deploying
- [ ] Update monitoring/alerts if needed
- [ ] Review deployment process for improvements

---

## Git Rollback Commands

### Revert Last Commit (Safe)
```bash
# Creates a new commit that undoes the last commit
git revert HEAD
git push origin main

# Railway will auto-deploy the revert commit
```

### Reset to Previous Commit (Dangerous)
```bash
# ⚠️ WARNING: This rewrites history
# Only use if the bad commit hasn't been deployed widely

# Find the commit to reset to
git log --oneline -10

# Reset to that commit (replace abc123 with actual hash)
git reset --hard abc123

# Force push (requires bypassing branch protection)
git push --force origin main
```

**Note:** Force pushes trigger Railway rule violations but are allowed for main branch.

---

## Railway-Specific Considerations

### Health Checks
- Railway uses the `HEALTHCHECK` in Dockerfile
- Unhealthy containers are automatically restarted
- Check health check logs: `railway logs --filter healthcheck`

### Build Cache
- Railway caches Docker layers
- If rollback fails, try: **Settings → Clear Build Cache**

### Environment Variables
- Rollback doesn't revert environment variables
- Manually check if env vars changed: **Settings → Variables**
- Restore previous values if needed

---

## Emergency Contacts

- **Primary**: Patrick Roebuck (repository owner)
- **Railway Support**: https://railway.app/help
- **GitHub Issues**: https://github.com/Smart-AI-Memory/empathy-framework/issues

---

## Testing Before Re-deployment

After fixing the issue that caused the rollback:

1. **Local Testing**
   ```bash
   # Build and test locally
   cd website
   npm run build:railway
   npm run start

   # Test in browser at localhost:3000
   ```

2. **Docker Testing**
   ```bash
   # Build Docker image locally
   docker build -t empathy-test .

   # Run container
   docker run -p 3000:3000 empathy-test

   # Test at localhost:3000
   ```

3. **Staging Deployment** (if available)
   - Deploy to staging environment first
   - Run full test suite
   - Manual QA testing
   - Monitor for 15 minutes before production

4. **Production Deployment**
   - Deploy during low-traffic window if possible
   - Monitor logs actively for 30 minutes
   - Have rollback plan ready

---

## Rollback History Log

Keep a record of rollbacks for pattern analysis:

| Date | Commit | Issue | Root Cause | Time to Rollback | Time to Fix |
|------|--------|-------|------------|------------------|-------------|
| 2025-12-15 | abc123f | Blog empty page | Dockerfile config | 5 min | 2 hours |
| | | | | | |

---

## Prevention Strategies

To minimize need for rollbacks:

1. **Pre-deployment Checks**
   - Run `empathy health` before pushing
   - Check Docker build locally
   - Review code review report
   - Verify all tests pass

2. **Automated Testing**
   - Pre-commit hooks catch basic issues
   - CI/CD runs full test suite
   - TypeScript catches type errors

3. **Gradual Rollout** (Future)
   - Canary deployments (1% → 10% → 100%)
   - Feature flags for new features
   - A/B testing for major changes

4. **Monitoring**
   - Set up Railway metrics alerts
   - Monitor error rates in logs
   - Track page load times

---

**Remember**: It's better to rollback quickly and investigate than to leave a broken site in production trying to fix forward.
