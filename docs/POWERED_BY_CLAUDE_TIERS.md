# Powered by Claude - Tier Structure

**Multi-LLM Support with Claude-First Approach**

The Empathy Framework supports multiple LLM providers while showcasing Claude's unique advantages for anticipatory AI.

---

## LLM Provider Strategy

### Supported Providers:

| Provider | Models | Key Advantages | Best For |
|----------|--------|---------------|----------|
| **Claude (Anthropic)** | Sonnet, Opus, Haiku | 200K context, prompt caching, thinking mode | Large codebases, complex reasoning |
| **GPT-4 (OpenAI)** | GPT-4, GPT-4 Turbo | Fast, widely adopted | General development tasks |
| **Gemini (Google)** | Gemini Pro, Ultra | Multimodal, enterprise integration | Enterprise customers on GCP |
| **Local Models** | Ollama, LM Studio | Privacy, zero cost | Sensitive code, air-gapped environments |

**Default provider:** Claude 3.5 Sonnet (optimal balance of performance, cost, and capabilities)

---

## Tier Structure

### Free Tier (Open Source)
**LLM Choice:** User brings their own API key for any provider

**Features:**
- Complete Empathy Framework (Apache 2.0)
- All 46 wizards
- Multi-LLM support (Claude, GPT-4, Gemini, local)
- One-click deployment tools
- Community support

**Claude Integration:**
- Documentation defaults to Claude examples
- README showcases Claude-specific features
- Recommended as "best experience" provider

**Cost:** $0

---

### Pro Tier ($99/year - Final Pricing)
**LLM Choice:** Powered by Claude (API credits included)

**Features:**
- Everything in Free tier
- **Included Claude API credits** ($25/month = $300/year value)
- Extended wizard access with Claude-specific enhancements
- Level 4 Anticipatory predictions (requires Claude's extended context)
- Prompt caching enabled (90% cost savings on repeated queries)
- Thinking mode for complex analysis
- Book: "Empathy Framework: The Five Levels" (PDF, ePub, Mobi)
- Priority community support

**Claude-Specific Advantages:**
- **Large codebase analysis:** Process 500+ files in one call (200K context)
- **Cost optimization:** Prompt caching for security scans, performance checks
- **Deep reasoning:** Thinking mode for trajectory prediction
- **Faster responses:** Cached system prompts load instantly

**Claude API Usage:**
- Estimated: 500K-1M tokens/month
- Cost with caching: ~$15-25/month
- Framework covers: $25/month included
- Overage: User pays directly to Anthropic (transparent pricing)

**Branding:**
- "Powered by Claude" badge in IDE
- Results include "Analysis by Claude 3.5 Sonnet"
- Link to Anthropic in attribution

**Cost:** $99/year (early release pricing may be $129)

---

### Business Tier ($249/year per 3 seats)
**LLM Choice:** Powered by Claude OR bring your own (enterprise flexibility)

**Features:**
- Everything in Pro tier × 3 seats
- **Choice of Claude (included credits) OR custom LLM provider**
- Email support (48-hour response SLA)
- Team dashboard with usage analytics
- Shared team knowledge base
- SSO integration
- On-premise deployment option
- Custom wizard development support

**Enterprise LLM Options:**

1. **Powered by Claude (Default)**
   - $75/month API credits included (3 × $25)
   - Prompt caching, extended context, thinking mode
   - Enterprise SLA through Anthropic partnership

2. **Bring Your Own Provider**
   - Use existing OpenAI/Azure OpenAI contract
   - Use Google Cloud Vertex AI (Gemini)
   - Use self-hosted models (Ollama, LM Studio)
   - Framework provides unified interface

**Why enterprises choose Claude option:**
- No separate LLM contract needed
- Anthropic's enterprise support
- Optimized for framework features
- Transparent, predictable pricing

**Cost:** $249/year per 3-seat bundle

---

## Claude Integration Features (All Tiers)

### 1. Extended Context Analysis
**Available in:** Pro, Business (requires Claude)

```python
# Analyze entire repository in one call
result = await claude.analyze_large_codebase(
    codebase_files=all_repo_files,  # 500+ files
    analysis_prompt="Find security vulnerabilities and predict scaling issues"
)
```

**Unique to Claude:** 200K context window
- **Competitor limits:** GPT-4 (128K), Gemini (32K)
- **Empathy Framework use case:** Whole-repo analysis without chunking

### 2. Prompt Caching (90% Cost Reduction)
**Available in:** Pro, Business (Claude-specific feature)

**How it works:**
- System prompts cached for 5 minutes
- Repeated security scans reuse cached context
- **Cost:** 90% reduction for repeated queries

**Example savings:**
- Traditional: $3 per 1M input tokens
- With caching: $0.30 per 1M cached tokens (10x cheaper)

**Framework optimization:**
- Pre-commit hooks trigger multiple scans
- Same codebase context cached across scans
- Typical user: 10-50 scans/day become affordable

### 3. Thinking Mode (Complex Reasoning)
**Available in:** Pro, Business (Claude 3.5+)

**Use case:** Level 4 Anticipatory predictions

```python
# Enable thinking mode for trajectory analysis
result = await claude.generate(
    messages=[...],
    use_thinking=True  # Claude shows reasoning
)

# Result includes:
# - Predicted issues
# - Reasoning process (visible)
# - Confidence scores
# - Timeline estimates
```

**Why it matters:**
- Transparency: See how Claude predicts future bugs
- Accuracy: Extended reasoning improves predictions
- Trust: Developers understand AI recommendations

### 4. Multi-Turn Wizard Conversations
**Available in:** All tiers (works better with Claude)

**Empathy Framework pattern:**
- Wizard asks clarifying questions
- User refines requirements
- Multiple analysis passes

**Claude advantage:**
- Better context retention across turns
- More nuanced follow-up questions
- Maintains coherence in long sessions

---

## Competitive Positioning

### "Why Claude?" Messaging:

**For individual developers (Pro tier):**
> "Claude's 200K context means your entire codebase fits in one analysis. No chunking, no missed connections, no context loss. Just upload your project and get comprehensive security, performance, and prediction analysis in seconds."

**For teams (Business tier):**
> "Claude + Empathy Framework gives your team Level 4 Anticipatory AI: predict bugs 30 days before they ship, optimize performance before you hit scale limits, and prevent security issues before deployment. All with transparent reasoning and 90% cost savings through prompt caching."

**For enterprises (Custom):**
> "Choose Claude for best-in-class anticipatory analysis, or bring your own LLM provider. Empathy Framework's multi-provider architecture means you're never locked in, but Claude's extended context and reasoning capabilities make it the optimal choice for production use."

---

## Provider Comparison in Framework

### Feature Matrix:

| Feature | Claude 3.5 | GPT-4 Turbo | Gemini Pro | Local (Llama) |
|---------|-----------|-------------|------------|---------------|
| **Context window** | 200K ✅ | 128K | 32K | 4-32K |
| **Prompt caching** | Yes ✅ | No | Limited | N/A |
| **Thinking mode** | Yes ✅ | No | No | No |
| **Cost (1M tokens)** | $3-15 | $10-30 | $1-7 | $0 |
| **Speed** | Fast | Fast | Very Fast | Variable |
| **Privacy** | Cloud | Cloud | Cloud | Local ✅ |
| **Empathy Framework optimization** | Excellent ✅ | Good | Good | Basic |

**Recommendation in docs:**
> "For the best Empathy Framework experience, we recommend Claude 3.5 Sonnet. It's optimized for our Level 4 Anticipatory features and offers the best balance of performance, cost (with prompt caching), and reasoning quality."

---

## Revenue Sharing with Anthropic (Optional)

### Proposed Model (If Partnership Includes Licensing):

**Pro Tier ($99/year):**
- Deep Study AI revenue: $99
- Includes $300/year Claude API credits
- Net margin: ~$40/user/year (after Claude costs)
- **Optional license fee to Anthropic:** $10-15/user/year for "Powered by Claude" branding

**Business Tier ($249/year per 3 seats):**
- Deep Study AI revenue: $249
- Includes $900/year Claude API credits (3 × $300)
- Net margin: ~$100/year (after Claude costs, support)
- **Optional license fee to Anthropic:** $25-35/bundle/year

**Why this works:**
- Anthropic gets: Brand exposure + API revenue + license fee
- Deep Study AI gets: Partnership credibility + technical support
- Users get: Transparent pricing, best-in-class tools

**Alternative (Simpler):**
- No license fee
- Partnership based on API revenue sharing
- Anthropic benefits from increased Claude adoption
- Deep Study AI benefits from featured placement

---

## Implementation Roadmap

### Phase 1: Enhanced Claude Provider (✅ DONE)
- Prompt caching support
- Extended context (200K)
- Thinking mode integration
- Large codebase analysis method

### Phase 2: Pro Tier Launch (Month 1-2)
- Stripe integration for payments
- Claude API credit provisioning
- Usage tracking dashboard
- "Powered by Claude" branding

### Phase 3: Business Tier (Month 2-3)
- Multi-seat management
- Team dashboard
- Enterprise billing
- Optional: Bring-your-own-LLM support

### Phase 4: Anthropic Partnership (Month 3-6)
- Featured in Claude ecosystem
- Joint marketing campaigns
- Technical support channel
- Optional: Investment or licensing terms

---

## FAQ: Multi-Provider Strategy

**Q: Why not exclusively use Claude?**
A: While Claude is our default and recommended provider, multi-provider support ensures:
- Enterprise customers can use existing LLM contracts
- Privacy-sensitive users can run local models
- We're not dependent on one vendor's pricing/policies
- Competition keeps us innovating

**Q: Does Anthropic benefit from non-Claude users?**
A: Yes! Every framework user sees Claude as the recommended provider. Many start with free tier (their own API key) but upgrade to Pro (Claude included) for convenience and optimization.

**Q: What if Claude API pricing changes?**
A: Our multi-provider architecture means we can adjust:
- Shift default to more cost-effective models
- Pass reasonable increases to users
- Negotiate volume discounts with Anthropic
- Users always have choice

**Q: How do Claude-specific features work with other providers?**
A: Framework gracefully degrades:
- Prompt caching → Standard mode with OpenAI/Gemini
- Extended context → Automatic chunking with smaller context windows
- Thinking mode → Standard generation (hidden reasoning)
- Large codebase analysis → Batched analysis with multiple calls

---

## Branding Guidelines

### "Powered by Claude" Badge Usage:

**Pro Tier:**
- Display in IDE extension status bar
- Include in analysis results: "Analysis by Claude 3.5 Sonnet"
- Show in settings: "Using Claude for optimal performance"
- Link to Anthropic: "Learn more about Claude"

**Marketing Materials:**
- Website: "Powered by Claude" logo
- Documentation: Claude examples as default
- Case studies: Feature Claude prominently
- Social media: Tag @AnthropicAI in relevant posts

**Attribution:**
```
Results generated by Claude 3.5 Sonnet
Powered by Anthropic's Claude API
Learn more: https://anthropic.com
```

---

## Summary

**Multi-LLM Strategy with Claude-First Approach:**

1. **Open Source (Free):** Support all providers, recommend Claude
2. **Pro Tier ($99):** Include Claude API credits, showcase advanced features
3. **Business Tier ($249):** Claude included OR bring your own
4. **Enterprise (Custom):** Full flexibility with Claude optimization

**Benefits:**
- **Users:** Choice, transparency, best-in-class tools
- **Anthropic:** Brand exposure, API revenue, enterprise validation
- **Deep Study AI:** Partnership credibility, technical support, sustainable business

**Next Steps:**
1. Launch Pro tier with included Claude credits
2. Establish Anthropic partnership
3. Scale to 1,000s of users
4. Expand to enterprise healthcare market

---

*Document Version: 1.0*
*Last Updated: January 2025*
*Contact: patrick.roebuck@deepstudyai.com*
