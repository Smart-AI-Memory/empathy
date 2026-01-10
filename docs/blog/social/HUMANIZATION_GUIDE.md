# Content Humanization Guide

**Purpose:** Mark specific spots where YOU should add personal touches to make posts authentic.

**Legend:**
- 🎯 **[ADD PERSONAL STORY]** - Share a specific moment/experience
- ⚠️ **[ADD HONEST MISTAKE]** - What went wrong initially?
- 💭 **[ADD DOUBT/SKEPTICISM]** - What made you unsure?
- 🕐 **[ADD SPECIFIC DATE/TIME]** - When did this happen?
- 💬 **[ADD CASUAL ASIDE]** - Conversational comment
- 🔧 **[ADD WHAT BROKE]** - Specific error/problem you hit
- 📊 **[ADD SURPRISING FINDING]** - What surprised you?
- ❓ **[ADD OPEN QUESTION]** - Genuine question to readers

---

## Blog Post (docs/blog/07-cutting-claude-costs-with-intelligent-fallback.md)

### Opening Paragraph (Lines 11-15)

**Current:**
```markdown
## TL;DR

I reduced my Claude API costs by **78% ($211/year saved)** by implementing
intelligent model routing: try Sonnet 4.5 first, upgrade to Opus 4.5 only
when needed.
```

**Add Before This:**
```markdown
🎯 [ADD PERSONAL STORY - 2-3 sentences]

Examples:
- "I'll be honest - I started tracking this because my co-founder saw
  the API bill and said 'what the hell are we paying for?' Awkward."

- "Last month I got the Anthropic bill notification and literally said
  'wait, what?' out loud. That's when I decided to actually look at
  what I was spending money on."

- "This started as a 'quick check' on our API usage. Three hours and
  873 analyzed calls later, I realized we were bleeding money."
```

### Section: "The Problem" (Lines 21-30)

**After "The inefficiency:" line, add:**
```markdown
💭 [ADD DOUBT/SKEPTICISM]

Example:
"At first I thought 'eh, $10/month, who cares?' But then I did the
math on scaling. If we 10x our usage (which is the plan), that's
$100/month wasted. That's real money."
```

### Section: "The Solution" (Lines 47-60)

**After the diagram, add:**
```markdown
⚠️ [ADD HONEST MISTAKE]

Example:
"Full disclosure: I tried manual routing first ('if task looks hard,
use Opus'). Terrible idea. I was wrong 90% of the time. Either wasting
money or wasting time on retries."
```

### Section: "Implementation" (Lines 85-140)

**After Step 1, before Step 2, add:**
```markdown
🔧 [ADD WHAT BROKE]

Example:
"⚠️ Quick gotcha I hit: The model IDs changed between Sonnet 4.0 and 4.5.
Took me 20 minutes to figure out why my calls were failing. Make sure
you're using 'claude-sonnet-4-5' not 'claude-sonnet-4-20250514'."
```

### Section: "My Real-World Results" (Lines 155-175)

**Before the results table, add:**
```markdown
🕐 [ADD SPECIFIC DATE/TIME]

Example:
"Started tracking this on January 3rd, 2026. These numbers are from
Jan 3 - Feb 2 (exactly 30 days)."
```

**After results table, add:**
```markdown
📊 [ADD SURPRISING FINDING]

Example:
"The most surprising part? I expected code reviews to need Opus at least
some of the time. Nope. Sonnet caught every security issue I threw at it.
SQL injection, XSS, the works. I was genuinely surprised."
```

### Section: "Key Lessons" (Lines 215-240)

**At the end of this section, add:**
```markdown
💬 [ADD CASUAL ASIDE]

Example:
"Lesson 5 (unofficial): Your instincts about task complexity are probably
wrong. Mine definitely were. Trust the data, not your gut."
```

### End of Post (Line 320+)

**Before "Resources" section, add:**
```markdown
❓ [ADD OPEN QUESTION]

Example:
"What am I missing here? If you're using Claude API and NOT doing this,
I'd genuinely love to hear why. Maybe I'm overlooking something obvious."
```

---

## Twitter Posts (docs/blog/social/twitter_claude_costs.md)

### Main Thread - Tweet 1

**Current:**
```
I cut my Claude API costs by 78% using one simple trick:
```

**Replace with:**
```
🎯 [ADD PERSONAL OPENER]

Examples:
- "Last Tuesday I looked at my Claude bill and just... stared at it.
  $25 for WHAT? So I actually investigated. Thread 🧵"

- "Real talk: I've been paying $25/month to Claude and had no idea
  what for. Finally tracked every call. Here's what I found 🧵"
```

### Main Thread - Tweet 4 (Results)

**After the numbers, add a new tweet:**
```
💭 [ADD DOUBT]

Example:
"Honestly thought this was too good to be true. Ran the tests 3 times
to make sure. Nope - Sonnet really just... works for this stuff."
```

### Quick Tips Section - Add New Tip

```
⚠️ [MISTAKE YOU MADE]

Example:
"Mistake I made: Started with Opus as default, Sonnet as fallback.
Backwards. Lost 2 days before I realized. Start cheap, upgrade when
proven necessary. Not the other way around."
```

### Engagement Posts - Add to Poll

**After the poll, add:**
```
💬 [PERSONAL CONTEXT]

Example:
"(I was firmly in the 'Always Opus' camp until I saw my bill.
Felt very smart. Was very wrong.)"
```

---

## LinkedIn Posts (docs/blog/social/linkedin_claude_costs.md)

### Post 1 (Main Post) - Opening

**Replace "THE PROBLEM:" with:**
```
🎯 [ADD CONTEXT - HOW THIS STARTED]

Example:
"THE PROBLEM:

Three weeks ago, our CFO forwarded me our Anthropic bill with one word:
'Why?'

Good question, actually. I had no idea.

Like many engineering teams, we were defaulting to the most powerful
LLM model 'to be safe.'"
```

### Post 1 - After "THE SOLUTION"

**Add before the numbered steps:**
```
⚠️ [ADD WHAT YOU TRIED FIRST]

Example:
"Initial approach (FAILED):
Tried manually routing based on 'complexity score'. Spent 3 hours
building a heuristic. Wrong 80% of the time. Scrapped it.

Better approach:"
```

### Post 1 - After "THE RESULTS"

**Add:**
```
💭 [ADD SKEPTICISM YOU HAD]

Example:
"THE RESULTS:

(I ran these tests twice because the numbers seemed too good.
They're real.)

Over 30 days with 438 Anthropic calls:"
```

### Post 2 (Executive Summary) - After "BEFORE"

**Add:**
```
💬 [ADD THE CONVERSATION]

Example:
"BEFORE intelligent model routing:

CFO: 'Why are we spending $272/year on this?'
Me: 'Uh... quality?'
CFO: 'Can you prove that?'
Me: '...'

[Awkward silence]"
```

### Post 4 (Before/After) - Add Timeline Section

**Add new section after "Week 4":**
```
🔧 [WHAT BROKE ALONG THE WAY]

Week 1.5: Telemetry broke after 200 calls (int overflow)
Week 2.5: Circuit breaker was too aggressive (false positives)
Week 3.5: Realized we were tracking the wrong model IDs

Engineering is messy. Worth it.
```

### Post 7 (Thought Leadership) - Add Personal Admission

**After "I did this too. For months." add:**
```
💭 [ADD YOUR REALIZATION]

Example:
"The moment it clicked for me: I was reviewing a code gen task that
cost $0.05 (Opus). Out of curiosity, I re-ran it with Sonnet.
Cost: $0.01. Output: Literally identical.

That's when I felt dumb."
```

---

## Reddit Posts (docs/blog/social/reddit_claude_costs.md)

### r/MachineLearning Post - Opening

**Before "## TL;DR" add:**
```
🎯 [ADD WHY YOU'RE POSTING]

Example:
"Spent the last month tracking every Claude API call we make.
Found some interesting patterns around cost optimization.
Sharing the data in case it's useful to others."
```

### r/MachineLearning - After Methodology

**Add:**
```
⚠️ [ADD LIMITATIONS/CAVEATS YOU DISCOVERED]

Example:
"Important caveat I discovered around day 20: This data is ONLY
for coding tasks. I tried the same approach on creative writing
and the fallback rate jumped to 15%. Your domain matters."
```

### r/MachineLearning - End of Post

**Add:**
```
❓ [ADD GENUINE QUESTIONS]

Example:
"Discussion Questions:

1. Anyone else measuring this? What's your fallback rate?
2. At what failure threshold would you skip Sonnet entirely?
3. Is there a task type I should test that I'm missing?

Genuinely curious about other perspectives here."
```

### r/programming Post - Opening

**Replace first line with:**
```
🎯 [RELATABLE OPENER]

Example:
"Got my Claude bill last month. $25. Thought 'that seems high
but whatever.' Got it again this month. $25. Started wondering
what I was actually paying for.

Turns out: mostly waste."
```

### r/programming - After The Data

**Add:**
```
💭 [ADD YOUR SURPRISE]

Example:
"Not gonna lie, I was expecting to see at least SOME Opus usage.
Like maybe 10-15% of tasks. Zero. Not a single one in 30 days.

Either I got lucky or Sonnet is way more capable than I thought."
```

### r/Python Post - After Quick Example

**Add:**
```
⚠️ [ADD A WARNING FROM YOUR EXPERIENCE]

Example:
"Quick gotcha that cost me an hour:

If you're using the Anthropic SDK directly, make sure you're
setting the API key in the environment OR passing it explicitly.
The executor doesn't check both by default.

(I hit this in testing. Not fun.)"
```

### r/LocalLLaMA Post - After "The Numbers"

**Add:**
```
💬 [ADD COMMUNITY QUESTION]

Example:
"Probably gonna get roasted for this but: anyone here just using
local models for everything? I'm curious if the cost savings of
Ollama + good hardware beats the Sonnet→Opus approach.

Genuine question - not judging either way."
```

### r/artificial Post - After The Data Section

**Add:**
```
🔧 [ADD WHAT DIDN'T WORK]

Example:
"What I Tried That DIDN'T Work:

1. Complexity scoring (0.3 correlation with actual needs)
2. Prompt length as proxy (terrible predictor)
3. Manual task routing (wrong 80% of the time)
4. Time-of-day patterns (no correlation)

Basically: let the system decide. My intuition was garbage."
```

---

## Platform-Specific Edits to Make

### Twitter - Add These Throughout

1. **Typos in replies** (not main thread):
   - "lol yeah that was my thoguth too" → "thought*"
   - Shows you're typing in real-time

2. **React to traction:**
   - If thread gets 100+ likes: Add reply "okay this is getting more traction than expected..."
   - If someone disagrees: "fair point, didn't think of that"

3. **Add follow-up thread next day:**
   - "Update on the Claude cost thing from yesterday..."
   - Share one thing you learned from replies

### LinkedIn - Add These

1. **In first comment on your own post:**
```
💬 [ADD FOLLOW-UP]

Example:
"One thing I didn't include in the post: the hardest part wasn't
the code. It was convincing myself to actually measure instead of
assuming. We're so used to 'better safe than sorry' that we don't
question it."
```

2. **After 50+ reactions:**
```
Edit: Wow, this is getting way more engagement than expected.
A few folks have DM'd asking about [specific question]. I'll write
a follow-up post on that next week.
```

### Reddit - Critical Edits

1. **Add edits based on comments:**
```
Edit: u/username asked about [X]. Good question. [Answer here]

Edit 2: Several people asking about production usage. Running this
for 6 days now (since Jan 3rd). No issues so far but early days.

Edit 3: RIP inbox. Thanks for the gold, stranger!
```

2. **Add at the end of each post:**
```
❓ [ASK FOR FEEDBACK]

Example:
"What am I missing? I'm sure there's edge cases I haven't hit yet.
Would love to hear from folks running at higher volume."
```

---

## The Edit Checklist

Before posting ANY content, make sure you've added:

### Must-Haves (Add to EVERY post)
- [ ] 🎯 One personal story/context (how this started)
- [ ] ⚠️ One honest mistake you made
- [ ] 💭 One moment of doubt/skepticism
- [ ] 🕐 Specific dates/times (not "recently" but "Jan 3rd")
- [ ] ❓ One genuine question to readers

### Nice-to-Haves (Add to MOST posts)
- [ ] 💬 One casual aside or conversational comment
- [ ] 🔧 One specific thing that broke
- [ ] 📊 One surprising finding
- [ ] Platform-specific lingo (Reddit: "YMMV", Twitter: "ngl", LinkedIn: "Key insight:")

### After Posting (Add based on engagement)
- [ ] Edit with "Update:" based on comments
- [ ] Reply to every comment in first 2 hours
- [ ] Add "Edit 2:" after 24 hours with learnings
- [ ] Thank people for awards/engagement (Reddit/Twitter)

---

## Quick Reference: Where to Add What

| Content Type | Add At | What to Add |
|--------------|--------|-------------|
| **Opening** | First 2-3 sentences | Personal story of how this started |
| **Problem section** | After stating the problem | Your initial mistake or doubt |
| **Solution section** | Before the technical details | What you tried first that failed |
| **Results section** | Before the data | Specific date range |
| **Results section** | After the data | What surprised you most |
| **Middle sections** | Every 2-3 paragraphs | A casual aside or conversational comment |
| **Technical sections** | After code blocks | A gotcha/warning from your experience |
| **End** | Before conclusion | Open question to readers |
| **After posting** | Based on comments | "Edit:" with updates |

---

## Example: Fully Humanized Opening

**Original AI Version:**
```
# How I Cut My Claude API Costs by 78%

I reduced my Claude API costs by 78% ($211/year saved) by implementing
intelligent model routing: try Sonnet 4.5 first, upgrade to Opus 4.5
only when needed.
```

**Humanized Version:**
```
# I was spending $25/month on Claude and had no idea why

🎯 Three weeks ago my co-founder forwarded me our Anthropic bill with
one word: "Why?"

Embarrassing admission: I had no idea. We were just... using Opus for
everything because it seemed "safer."

💭 So I actually looked at what we were spending money on. Tracked
every API call for a month. Built telemetry. Ran tests. The whole thing.

⚠️ Tried to be clever with manual routing first ("if task is complex,
use Opus"). Spent 3 hours on it. Wrong 80% of the time. Scrapped it.

Then tried something simpler: just use Sonnet for everything, see what
breaks. If it breaks, upgrade to Opus automatically.

📊 Results surprised me: 438 calls over 30 days. Zero needed Opus.
Not a single one.

Saved $17.59/month doing this. Which doesn't sound like much until you
realize that's $211/year, and we're planning to 10x our API usage.

Anyway, here's how it works...
```

**Notice the additions:**
- 🎯 Personal context (co-founder question)
- 💭 Honest doubt (no idea what we were paying for)
- ⚠️ Failed attempt (manual routing)
- 📊 Surprising finding (zero needed Opus)
- 💬 Casual tone ("Anyway")

---

## Final Tip: The "24-Hour Rule"

1. Write your version with the edits above
2. Save it
3. Wait 24 hours
4. Read it out loud
5. If it sounds like YOU talking, post it
6. If it sounds like a press release, add more personality

**Test:** Could someone who knows you recognize your voice? If not, add more personal touches.

---

Use this guide as a template. Go through each piece of content and add these markers. It'll take 30-60 minutes per post but will make the content unmistakably yours.
