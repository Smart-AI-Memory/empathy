# License Implementation Guide

## Recommended Approach: Fair Source License

Based on your business model ($99/developer/year, free for ≤5 employees), here's how to implement the Fair Source License correctly.

---

## Step 1: Choose Your License Strategy

### ✅ RECOMMENDED: Fair Source License

**Replace:**
- `LICENSE` (currently Apache 2.0)

**With:**
- `LICENSE` → Fair Source License (from LICENSE-FAIR-SOURCE.md)

**Why:**
- Legally enforceable commercial terms
- Clear usage limits (5 employees = free, 6+ = paid)
- Source remains visible for inspection
- Auto-converts to open source after 4 years

**Tradeoffs:**
- ❌ NOT "OSI-approved open source"
- ❌ Can't claim "open source" in marketing (use "source available")
- ❌ Some companies have "OSI-only" policies (maybe 10-15% of market)
- ✅ Clear revenue protection
- ✅ Can enforce $99/year legally
- ✅ No honor system - real contract

---

## Step 2: Update Files

### Files to Update:

1. **LICENSE** (replace entirely)
   ```bash
   cp LICENSE-FAIR-SOURCE.md LICENSE
   rm LICENSE-COMMERCIAL.md  # No longer needed
   ```

2. **setup.py** (line 95)
   ```python
   # FROM:
   "License :: OSI Approved :: Apache Software License",

   # TO:
   "License :: Other/Proprietary License",
   # OR
   "License :: Freely Distributable",
   ```

3. **README.md** - Add license badge
   ```markdown
   ![License: Fair Source](https://img.shields.io/badge/License-Fair%20Source-blue.svg)

   ## License

   This project is licensed under the Fair Source License, version 0.9.

   - **Free:** Students, educators, organizations with ≤5 employees
   - **Commercial:** $99/developer/year for organizations with 6+ employees
   - **Auto-converts:** Becomes Apache 2.0 on January 1, 2029

   See [LICENSE](LICENSE) for full terms.
   ```

4. **pyproject.toml or setup.py** - License classifier
   ```python
   classifiers=[
       "License :: Other/Proprietary License",
       # or
       "License :: Freely Distributable",
   ]
   ```

5. **All source files** - Copyright headers
   ```python
   """
   Copyright 2025 Deep Study AI, LLC
   Licensed under the Fair Source License, version 0.9
   See LICENSE for details
   """
   ```

---

## Step 3: GitHub & PyPI Settings

### GitHub:

1. **Repository Settings → License:**
   - Select "Other" (Fair Source isn't in dropdown)
   - Link to your LICENSE file

2. **README badge:**
   ```markdown
   [![License](https://img.shields.io/badge/license-Fair%20Source-blue)](LICENSE)
   ```

3. **About section:**
   - License: "Fair Source 0.9"

### PyPI:

**Important:** PyPI allows "Other/Proprietary License" or "Freely Distributable"

```python
# setup.py
classifiers=[
    "License :: Other/Proprietary License",
]
```

**Note:** You CAN publish to PyPI with non-OSI licenses. Many commercial projects do this (MongoDB, CockroachDB, etc.)

---

## Step 4: Website & Documentation

### Pricing Page:

Create clear pricing documentation:

```markdown
## Pricing

### Free Tier (No Cost, Forever)
- ✅ Students and educators
- ✅ Open source projects
- ✅ Organizations with ≤5 employees
- ✅ Personal projects
- ✅ Academic research

**No credit card required. No time limits.**

### Professional Tier ($99/developer/year)
- Organizations with 6+ employees
- One license covers ALL environments (dev, staging, prod, CI/CD)
- Includes updates and support
- Annual billing

**Volume discounts for 20+ developers**

### Enterprise Tier (Custom Pricing)
- Custom SLA
- Dedicated support
- Custom training
- Reseller agreements

[Buy Now] [Contact Sales]
```

### FAQ:

```markdown
## Licensing FAQ

**Q: Is this open source?**
A: The source code is publicly available and inspectable, but it uses the Fair Source License rather than an OSI-approved license. This allows us to provide free access to small teams while sustaining development through commercial licensing.

**Q: Can I see the source code?**
A: Yes! The full source code is available at github.com/Deep-Study-AI/Empathy

**Q: What happens after 4 years?**
A: On January 1, 2029, the license automatically converts to Apache 2.0 (fully open source).

**Q: Do I need a license for CI/CD?**
A: No - one license per developer covers ALL their environments (laptop, staging, production, CI/CD pipelines).

**Q: What counts as an "employee"?**
A: W-2 employees, 1099 contractors working >20 hours/week, and interns all count. Part-time contractors <20 hours/week typically don't count.

**Q: We have 7 employees but only 2 developers. Do we pay for 2 or 7?**
A: You pay for 2 (only developers who use/deploy the framework need licenses).

**Q: Can we use it free for evaluation?**
A: Yes - 30 days free evaluation for any company size.
```

---

## Step 5: Enforcement Strategy

### How to Verify Compliance:

1. **Honor system for small teams:**
   - Trust that ≤5 employee companies self-report accurately
   - Minimal verification needed

2. **Sales process for larger companies:**
   - During sales call: "How many developers will use this?"
   - License keys or activation codes (optional)
   - Annual invoicing creates paper trail

3. **Audit clause (use sparingly):**
   - Reserve right to audit with 30-day notice
   - Only use if you suspect major violations
   - Focus on education over litigation

### Suggested Compliance Flow:

```
1. Download/install framework
2. First run shows license notice:
   "This software is licensed under Fair Source 0.9
    Free for ≤5 employees | $99/dev/year for 6+ employees
    See LICENSE or visit deepstudyai.com/pricing"
3. For 6+ employees: "Purchase license at [URL]"
4. Optional: License key system (future enhancement)
```

---

## Step 6: Marketing Language

### ✅ Correct Terms:

- "Source available"
- "Publicly viewable source code"
- "Fair Source licensed"
- "Free for small teams"
- "Inspectable source code"

### ❌ Avoid Saying:

- "Open source" (technically incorrect)
- "Free software" (ambiguous)
- "MIT licensed" (wrong)

### ✅ Sample Marketing Copy:

> "Empathy Framework is **source available** under the Fair Source License. The full source code is publicly viewable for security review and learning. It's **free forever** for students, educators, and small teams (≤5 employees), with commercial licensing for larger organizations."

---

## Alternative: Keep Dual License (If You're Unsure)

If you want to test the market first:

**Option:** Keep Apache 2.0 for now, monitor adoption

1. Keep LICENSE as Apache 2.0
2. Keep LICENSE-COMMERCIAL.md
3. Add enforcement later when you have users
4. Switch to Fair Source in 6-12 months

**Pros:** Maximum adoption now
**Cons:** Hard to enforce payment (honor system only)

---

## Comparison Table

| Approach | Revenue Protection | Adoption | PyPI | Enforcement |
|----------|-------------------|----------|------|-------------|
| **Fair Source** (recommended) | ✅ Strong | ⚠️ Good | ✅ Yes | ✅ Legal |
| Apache 2.0 + Commercial | ❌ Weak | ✅ Best | ✅ Yes | ❌ Honor system |
| Proprietary (closed source) | ✅ Strongest | ❌ Limited | ✅ Yes | ✅ Legal |
| BSL (converts after 4 years) | ✅ Strong | ⚠️ Good | ✅ Yes | ✅ Legal |

---

## Recommended Timeline

**Today:**
1. Review Fair Source License terms
2. Decide if 4-year conversion date is right (can adjust)

**This Week:**
1. Copy LICENSE-FAIR-SOURCE.md to LICENSE
2. Update setup.py classifier
3. Update README with license badge and explanation

**Next Week:**
1. Create pricing page on website
2. Set up payment processing (Stripe, etc.)
3. Add license notice to CLI output

**Month 1:**
1. Monitor adoption and feedback
2. Refine pricing if needed
3. Add license key system (optional)

---

## My Recommendation

**Use Fair Source License immediately because:**

1. ✅ Matches your stated business model exactly
2. ✅ Legally enforceable (not honor system)
3. ✅ Still allows code inspection (trust & security)
4. ✅ Auto-converts to open source (good faith toward community)
5. ✅ Used successfully by similar companies (MariaDB, Sentry)

**Just be clear in marketing:**
- Don't say "open source"
- Do say "source available" and "free for small teams"
- Emphasize value, not license type

---

**Want me to implement this change now, or do you have questions first?**
