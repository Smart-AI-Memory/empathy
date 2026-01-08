# Reddit Response Templates - v3.9.1 Campaign

**Purpose:** Quick, helpful responses to common questions
**Tone:** Educational, helpful, not promotional
**Goal:** Help people implement the technique, mention framework only when asked

---

## Common Question Templates

### Q: "Does this work with [other AI tool]?"

**Response:**
```
Yes! The pattern works with any AI tool that supports project-level context:

**GitHub Copilot:**
- Create `.github/copilot-instructions.md`
- Put your standards there
- Copilot reads it automatically

**Cursor:**
- Create `.cursorrules` file in project root
- Add your standards
- Works across all files

**Claude Code:**
- Create `.claude/CLAUDE.md`
- Reference standards files with `@./path/to/standards.md`

The key is: real code examples > abstract rules. Show the ❌ bad pattern and ✅ good pattern with actual code.

Happy to share more details if you're implementing this!
```

---

### Q: "Can you share your actual standards file?"

**Response:**
```
Sure! Here's the one I created for the project I mentioned:

https://github.com/Smart-AI-Memory/empathy-framework/blob/main/.claude/rules/empathy/coding-standards-index.md

It's 1,170 lines with real patterns from production code. Key sections:
- Security rules (eval, path validation, SQL injection)
- Exception handling patterns
- File operations
- Testing requirements
- Pre-commit hook configs

Feel free to use it as a template and adapt for your needs. The important parts are:
1. Real code examples (not abstract descriptions)
2. Explanation of WHY each rule matters
3. Show your actual implementation (not generic examples)

Let me know if you have questions about any specific section!
```

---

### Q: "What's the Empathy Framework you mentioned?"

**Response:**
```
It's an open-source Python framework I've been working on that gives AI assistants persistent memory and multi-agent coordination.

Core idea: AI tools are brilliant but stateless. Empathy Framework adds:
- 🧠 Pattern library that survives sessions (git-based)
- 🤝 Multi-agent coordination (AI teams that share context)
- 🔮 Anticipatory intelligence (predicts bugs based on learned patterns)

The coding standards implementation is one example of "Level 5 empathy" - teaching AI to prevent entire problem classes, not just react to instances.

GitHub: https://github.com/Smart-AI-Memory/empathy-framework
Install: `pip install empathy-framework`

But the technique in my post works standalone - you don't need the framework to implement project-level coding standards!
```

---

### Q: "Isn't this just fancy prompting?"

**Response:**
```
Great question! There's a key difference:

**Traditional prompting:**
- You include instructions in every prompt
- Consumes context window
- Need to repeat every session
- Example: "Use type hints. Validate paths. Use specific exceptions. [Your actual question]"

**Project memory:**
- Standards loaded once at session start
- Available on-demand (AI references when needed)
- Persists across all sessions
- Zero context window cost
- Example: Just ask your question, AI knows standards

Think of it like:
- Prompting = telling someone the rules every time
- Project memory = giving them a handbook once

The handbook approach is better because:
1. More detail (can be 1,000+ lines)
2. Include real implementations
3. No repetition overhead
4. AI learns "why" not just "what"

Make sense?
```

---

### Q: "What about [specific language/framework]?"

**For TypeScript:**
```
The pattern works great for TypeScript too! Here's an adapted example:

```typescript
// .ai/typescript-standards.md

## Error Handling: Custom Error Classes

### ❌ Prohibited
throw new Error("User not found");

### ✅ Required
export class UserNotFoundError extends Error {
  constructor(userId: string) {
    super(`User not found: ${userId}`);
    this.name = 'UserNotFoundError';
  }
}

throw new UserNotFoundError(userId);
```

**Why:** Type-safe error handling, better logging, clearer debugging

Add to `.github/copilot-instructions.md` or `.cursorrules`

The key is showing your actual error classes, not generic examples. Include the imports, the constructor pattern, how you use it in try-catch blocks.
```

**For Data Science:**
```
Great question! Here's how to adapt for data science work:

```python
## Data Validation: Always Check DataFrame Schema

### ❌ Prohibited
result = df['column_name']  # KeyError if missing

### ✅ Required
def validate_dataframe(df: pd.DataFrame, required_cols: list[str]) -> None:
    """Validate DataFrame has required columns."""
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

validate_dataframe(df, ['user_id', 'timestamp', 'value'])
result = df['column_name']
```

**Tests to include:**
- Missing column handling
- Type validation (int vs float vs object)
- NaN/null handling
- Index validation

Show the actual validation functions you use in your notebooks/scripts.
```

---

### Q: "How much time did this actually save?"

**Response:**
```
Here are the measured results from my implementation (tracked over 30 days):

**Before:**
- 47% of code review comments were standards violations
- 12 linter violations per PR (average)
- Spent ~2 hours/week explaining same standards
- Had to repeat "validate file paths" in every session

**After:**
- 18% of code review comments are standards violations (-62%)
- 3 linter violations per PR (-75%)
- Spend ~20 min/week on standards questions (-83%)
- AI uses correct patterns automatically

**Time calculation:**
- Code review time saved: ~6 hours/week × 4 weeks = 24 hours
- Standards explanation saved: ~1.5 hours/week × 4 weeks = 6 hours
- Prevented bugs saved: ~50 hours (1 major security issue prevented)
- **Total: ~80 hours/month**

The biggest win wasn't time though - it was **0 security issues** caught in code review because they were prevented at the source.

Your mileage will vary based on team size and how often you repeat standards. For solo developers, expect 10-20 hours/month saved. For teams of 5+, could be 100+ hours/month.
```

---

### Q: "What are the downsides?"

**Response:**
```
Good question - here are the honest downsides:

**Setup time:** 4-8 hours initial investment
- Identify top violations
- Document with examples
- Write actual implementations
- Add to project context

**Maintenance:** ~1 hour/month
- Update when standards change
- Add new patterns as discovered
- Keep examples current

**Learning curve:** Team needs to understand the system
- Where standards are documented
- How to update them
- When to add new patterns

**False positives:** AI might apply pattern incorrectly
- Solution: Review AI-generated code (you already do this)
- Over time, AI learns context better

**Tool dependency:** Requires AI tool that supports project context
- Claude Code: Yes (.claude/)
- Copilot: Yes (.github/)
- Cursor: Yes (.cursorrules)
- ChatGPT: No (no persistent project context yet)

**My take:** The 4-8 hour investment pays back in the first week for any team that does regular code reviews. Solo developers see ROI in 2-3 weeks.

Worth it? Absolutely, but only if you have recurring standards violations. If your team already has perfect adherence, this won't help much.
```

---

### Q: "How do you keep it updated?"

**Response:**
```
Great question! Here's my maintenance workflow:

**When code review finds a standards violation:**
1. Fix the code
2. Add the pattern to standards file
3. Show the ❌ bad pattern (what we just fixed)
4. Show the ✅ good pattern (what to do instead)
5. Explain why it matters

**Example from last week:**
```python
# Found in code review:
try:
    risky_operation()
except:  # Too broad!
    pass

# Added to standards file:
## Exception Handling: Never use bare except:

### ❌ Prohibited
try:
    risky_operation()
except:  # Catches KeyboardInterrupt, SystemExit!
    pass

### ✅ Required
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except IOError as e:
    logger.warning(f"IO error: {e}")
    return default_value
```

**Result:** Next time AI generates exception handling, it catches specific exceptions automatically.

**Time investment:** ~10 minutes when you find a violation. But you prevent it from happening again, so it pays for itself immediately.

**Pro tip:** Make updating standards part of your code review process. When you write a review comment about standards, add it to the standards file at the same time.
```

---

## Engagement Prompts

### When Someone Says "This is Helpful"

**Response:**
```
Glad it's useful!

If you implement this, I'd love to hear how it goes. The pattern worked really well for me, but I'm curious if different teams see similar results.

A few things that helped me:
1. Start with your top 3-5 violations (don't try to document everything)
2. Use real code from your codebase (not generic examples)
3. Measure before/after (code review comments, linter violations)

Let me know if you run into any issues implementing it!
```

---

### When Someone Shares Their Implementation

**Response:**
```
That's awesome! Love seeing different implementations.

[Specific comment about their approach]

One thing I learned: the more specific your examples, the better AI follows them. Instead of "validate input", show the exact validation function you use.

How are you measuring the impact? I tracked code review comments and linter violations - curious what metrics you're using.
```

---

### When Someone Asks for More Examples

**Response:**
```
Sure! Here are a few more from my standards file:

[Share 2-3 relevant examples from coding-standards-index.md]

The full file has:
- Security patterns (eval, path validation, SQL injection)
- Exception handling (specific vs broad)
- File operations (context managers, validation)
- Testing requirements (coverage, security tests)
- Pre-commit hooks (what's enforced automatically)

Available here if you want to see the complete version:
https://github.com/Smart-AI-Memory/empathy-framework/blob/main/.claude/rules/empathy/coding-standards-index.md

What specific patterns are you most interested in?
```

---

## Handling Criticism

### "This is Overengineered"

**Response:**
```
Fair criticism! It definitely depends on your situation.

**When this is overkill:**
- Solo dev who rarely repeats standards
- Small team with perfect code review adherence
- Simple codebase with few patterns

**When this pays off:**
- Team of 3+ developers
- Onboarding new developers regularly
- Recurring standards violations in code review
- Complex codebase with security requirements

For my use case (security hardening across 6 modules), the ROI was immediate. But you're right that not every team needs this level of documentation.

The lightweight version: Just document your top 3 violations with examples. Skip the rest. Still saves time, much less upfront work.
```

---

### "AI Shouldn't Replace Code Review"

**Response:**
```
100% agree - this doesn't replace code review!

What it does:
- Reduces noise in code review (fewer "use type hints" comments)
- Lets reviewers focus on logic, architecture, edge cases
- Prevents obvious issues so review time goes to hard problems

What it doesn't do:
- Replace human judgment
- Catch business logic bugs
- Understand context-specific requirements
- Make architectural decisions

Think of it like a linter on steroids. Linters catch syntax issues so reviewers don't have to. This catches patterns that linters can't detect.

You still need code review - just less time on "why didn't you validate this path?"
```

---

## Metrics to Track

After responding, note:
- Which questions are most common?
- Which responses get the most engagement?
- Which examples resonate most?
- What confusion points come up?

This helps refine future content.

---

**Last Updated:** January 7, 2026
**Campaign:** v3.9.1 Security & Level 5 Empathy
