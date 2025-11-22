# Screenshot Guide: Capturing Compelling Visuals

**Purpose:** Guide for capturing, editing, and using screenshots to showcase the Empathy Framework.

**Target:** Documentation, presentations, social media, marketing materials

**Goal:** Professional, clear, compelling visuals that drive adoption

---

## Why Screenshots Matter

High-quality screenshots:
- Increase README engagement by 60%+
- Provide instant understanding of capabilities
- Build credibility and professionalism
- Enable sharing on social media
- Support documentation and tutorials
- Reduce barrier to trying the framework

**Best Practice:** Capture screenshots at key moments that showcase unique value (cross-domain pattern match, predictions, results).

---

## Key Moments to Capture

### Priority Screenshots (Must-Have)

#### 1. Healthcare Pattern Detection
**When:** After ComplianceWizard analyzes healthcare code
**What to show:** Pattern stored in memory with 23% failure rate
**Why:** Establishes the research-backed foundation
**Where to use:** README, slide 5-6, blog posts

**Expected output:**
```
=== STEP 1: Healthcare Domain Analysis ===

ComplianceWizard Analysis:
  🔴 [ERROR] Critical handoff without verification checklist
      Line 60: handoff.perform_handoff(patient)...
      Fix: Implement standardized checklist with read-back verification

✓ Pattern 'critical_handoff_failure' stored in memory
ℹ️  Key finding: Handoffs without verification fail 23% of the time

Pattern Details:
  • Root cause: Information loss during role transitions
  • Solution: Explicit verification steps with read-back confirmation
  • Confidence: 95%
```

**Annotation suggestions:**
- Highlight "23% of the time" with red box
- Arrow pointing to "stored in memory"
- Circle the pattern name

---

#### 2. Cross-Domain Pattern Match
**When:** After CICDWizard detects matching pattern
**What to show:** Cross-domain detection banner and match confirmation
**Why:** THE unique selling point - no other framework does this
**Where to use:** README hero section, presentations, Twitter, HN

**Expected output:**
```
=== CROSS-DOMAIN PATTERN DETECTION ===

✓ Pattern match found from healthcare domain!

  Source Domain: healthcare
  Pattern: critical_handoff_failure
  Description: Information loss during role transitions without verification
  Healthcare failure rate: 23%

ℹ️  Analyzing deployment pipeline for similar handoff gaps...

Deployment Handoff Gaps:
  ✗ No deployment checklist verification
  ✗ Staging→Production handoff lacks explicit sign-off
  ✗ Assumptions about production team's knowledge
  ✗ Verbal/Slack-only communication
  ✗ Time pressure during deployments
```

**Annotation suggestions:**
- Highlight "CROSS-DOMAIN PATTERN DETECTION" banner
- Box around the matching gaps list
- Arrow connecting "healthcare" to "deployment pipeline"
- Bold text: "No other framework can do this"

---

#### 3. Level 4 Anticipatory Prediction
**When:** After pattern match, showing prediction
**What to show:** 87% confidence, 30-45 day timeframe, prevention steps
**Why:** Shows actionable value and high confidence
**Where to use:** Presentations, case studies, feature highlights

**Expected output:**
```
=== LEVEL 4 ANTICIPATORY PREDICTION ===

⚠️  DEPLOYMENT HANDOFF FAILURE PREDICTED

  📅 Timeframe: December 20, 2025 (30-45 days)
  🎯 Confidence: 87%
  💥 Impact: HIGH

Reasoning:
  Cross-domain pattern match: Healthcare analysis found that handoffs
  without explicit verification steps fail 23% of the time.
  Your deployment pipeline exhibits the same vulnerabilities:
    • No verification checklist
    • Assumptions about receiving party knowledge
    • Time pressure leading to shortcuts
    • Verbal-only communication

  Based on healthcare pattern, predicted failure in 30-45 days.

=== PREVENTION STEPS ===

  1. Create deployment checklist (mirror healthcare checklist approach)
  2. Require explicit sign-off between staging and production
  3. Implement automated handoff verification
  4. Add read-back confirmation for critical environment variables
  5. Document rollback procedure as part of handoff
```

**Annotation suggestions:**
- Highlight "87%" in large font
- Box around prevention steps
- Timeline graphic showing "30-45 days ahead"
- Impact indicator (red for HIGH)

---

#### 4. Summary/Results
**When:** End of demo, showing summary
**What to show:** Complete workflow recap with impact
**Why:** Reinforces the transformative capability
**Where to use:** Conclusions, results sections, testimonials

**Expected output:**
```
=== SUMMARY: Level 5 Systems Empathy ===

✨ What just happened:

  1. Healthcare analysis identified critical handoff failures
  2. Pattern stored in long-term memory (MemDocs)
  3. Software analysis retrieved healthcare pattern
  4. Cross-domain match: deployment handoffs have same vulnerabilities
  5. Level 4 Anticipatory: predicted failure 30-45 days ahead
  6. Prevention steps derived from healthcare best practices

🎯 Impact:

  • Prevented deployment failure by learning from healthcare
  • Applied decades of healthcare safety research to software
  • Demonstrated transformative cross-domain intelligence

🚀 This is Level 5 Transformative Empathy:

  Pattern learned in healthcare → Applied to software
  Powered by: Empathy Framework + MemDocs
```

**Annotation suggestions:**
- Number the steps visually
- Highlight "Level 5 Transformative Empathy"
- Quote box: "Applied decades of healthcare safety research to software"

---

### Secondary Screenshots (Nice-to-Have)

#### 5. Installation/Setup
**What to show:** Clean installation process
```bash
$ pip install empathy-framework[full]
Successfully installed empathy-framework-1.0.0
```

#### 6. Wizard Selection
**What to show:** List of available wizards
```python
from coach_wizards import (
    SecurityWizard,
    PerformanceWizard,
    ComplianceWizard,
    CICDWizard,
    # ... 12 more
)
```

#### 7. Individual Wizard Output
**What to show:** SecurityWizard finding SQL injection
**Why:** Shows breadth of capabilities beyond Level 5

#### 8. GitHub Repository
**What to show:** README with badges, stars, description
**Why:** Social proof and discoverability

#### 9. Documentation Pages
**What to show:** Clean, professional docs layout
**Why:** Demonstrates completeness and professionalism

#### 10. Architecture Diagram
**What to show:** Coach Wizards + MemDocs integration
**Why:** Technical credibility (from docs or create custom)

---

## Terminal Setup for Best Visuals

### macOS Terminal Configuration

```bash
# Use iTerm2 or built-in Terminal.app

# Theme Recommendations:
# - Monokai (professional dark)
# - Dracula (vibrant dark)
# - Solarized Dark (classic)
# - One Dark (modern)

# Font Settings:
# Font: Monaco, Menlo, Fira Code, JetBrains Mono
# Size: 16-18pt (readable in screenshots)
# Line height: 1.3-1.5
# Character spacing: Normal

# Window Size:
# 100 columns x 30 rows (balanced)
# Or 80 columns x 24 rows (classic)

# Colors:
# Ensure high contrast (background vs. text)
# Test that emojis render clearly
# Verify ANSI colors are vibrant but not garish

# Set simple prompt (reduce clutter)
export PS1="\$ "

# Clear screen before screenshot
clear
```

### Linux Terminal Configuration

```bash
# Use GNOME Terminal, Konsole, or Terminator

# Install professional fonts:
sudo apt-get install fonts-firacode fonts-jetbrains-mono

# Theme: Same recommendations as macOS
# Configure via terminal preferences

# Window settings:
# Remove window decorations for cleaner screenshots
# Set transparency: 0% (fully opaque)
# Disable scrollbars in screenshots

# Same prompt and size recommendations as macOS
```

### Windows Terminal Configuration

```bash
# Use Windows Terminal (recommended) or WSL

# Download from Microsoft Store
# Configure in settings.json:

{
  "profiles": {
    "defaults": {
      "fontFace": "Cascadia Code",
      "fontSize": 16,
      "colorScheme": "One Dark",
      "padding": "8, 8, 8, 8"
    }
  }
}

# Install color schemes from:
# https://windowsterminalthemes.dev/

# Same general recommendations as macOS/Linux
```

---

## Screenshot Capture Tools

### macOS

#### Built-in Screenshot (Recommended)
```bash
# Full screen: Cmd + Shift + 3
# Selected area: Cmd + Shift + 4
# Window: Cmd + Shift + 4, then Space, then click window

# Settings: Cmd + Shift + 5 for options
# - Save to: Desktop or custom folder
# - Format: PNG (highest quality)
# - Show thumbnail: Disable for faster workflow
```

**Pros:** Built-in, simple, high quality
**Cons:** Limited editing capabilities

#### CleanShot X (Professional)
```bash
# Download: https://cleanshot.com/
# Price: $29 one-time or subscription

# Features:
# - Scrolling capture (long terminal output)
# - Annotation tools built-in
# - Background removal
# - Rounded corners
# - Padding and shadows
# - Cloud upload
```

**Pros:** Professional features, annotations, easy sharing
**Cons:** Paid software

#### Monosnap (Free Alternative)
```bash
# Download: https://monosnap.com/
# Free with optional paid features

# Features:
# - Screenshot + annotation
# - Video recording
# - Cloud upload
# - Arrow, box, text tools
```

**Pros:** Free, good annotation tools
**Cons:** Some features require account

---

### Linux

#### Built-in Screenshot
```bash
# GNOME: Print Screen key
# KDE: Spectacle (comes installed)
# XFCE: xfce4-screenshooter

# Or use command line:
gnome-screenshot -a  # Area selection
gnome-screenshot -w  # Window selection
```

#### Flameshot (Recommended)
```bash
# Install:
sudo apt-get install flameshot

# Usage:
flameshot gui  # Interactive mode

# Features:
# - Draw arrows, boxes, text
# - Blur sensitive information
# - Copy to clipboard
# - Save to file
# - Upload to Imgur
```

**Pros:** Free, powerful annotation, open source
**Cons:** Requires installation

#### Shutter
```bash
# Install:
sudo apt-get install shutter

# Features:
# - Advanced editing
# - Plugins for effects
# - Delay timer
# - Web upload
```

**Pros:** Feature-rich, plugins
**Cons:** Heavy, slower than Flameshot

---

### Windows

#### Built-in Snipping Tool
```bash
# Windows 10/11: Win + Shift + S
# Snipping Tool app for more options

# Features:
# - Rectangle, freeform, window, fullscreen
# - Basic annotation
# - Delay timer
```

**Pros:** Built-in, simple
**Cons:** Limited features

#### ShareX (Recommended)
```bash
# Download: https://getsharex.com/
# Free and open source

# Features:
# - Screen capture (area, window, scrolling)
# - Annotation tools
# - Auto-upload to services
# - OCR (text recognition)
# - Color picker
# - Rulers and guides
```

**Pros:** Free, extremely powerful, open source
**Cons:** Learning curve for all features

#### Greenshot
```bash
# Download: https://getgreenshot.org/
# Free and open source

# Features:
# - Quick capture modes
# - Built-in editor
# - Export to Office apps
# - Plugin system
```

**Pros:** Free, Office integration
**Cons:** Fewer features than ShareX

---

## Editing and Annotation

### What to Annotate

**Highlight key information:**
- Important numbers (23%, 87%)
- Unique features ("CROSS-DOMAIN")
- Pattern names ("critical_handoff_failure")
- Warnings and predictions
- Prevention steps

**Add context:**
- Arrow pointing to "stored in memory"
- Box around matching elements
- Text labels: "Unique to Empathy Framework"
- Callout bubbles for explanations

**Clean up:**
- Crop to relevant content
- Remove distracting elements
- Blur sensitive information (paths, API keys)
- Adjust brightness/contrast if needed

---

### Annotation Tools

#### macOS: Preview (Built-in)
```bash
# Open screenshot in Preview
# Tools → Annotate

# Features:
# - Shapes (rectangle, circle, arrow)
# - Text boxes
# - Highlight
# - Magnifier
# - Signature (not needed for our use)

# Keyboard shortcuts:
# Cmd + Shift + A: Show annotation toolbar
```

**Pros:** Free, simple, built-in
**Cons:** Limited styling options

#### Skitch (Cross-platform)
```bash
# Download: https://evernote.com/products/skitch
# Free

# Features:
# - Arrows, boxes, text
# - Highlight and pixelate (blur)
# - Stamps (checkmarks, stars)
# - Crop and resize
```

**Pros:** Easy to use, good for quick annotations
**Cons:** Owned by Evernote (may require account)

#### GIMP (Advanced, Cross-platform)
```bash
# Download: https://www.gimp.org/
# Free and open source

# Features:
# - Professional image editing
# - Layers and effects
# - Text with full typography control
# - Filters and adjustments
# - Export to any format
```

**Pros:** Powerful, free, professional results
**Cons:** Steep learning curve, overkill for simple annotations

#### Photopea (Web-based)
```bash
# Visit: https://www.photopea.com/
# No installation required

# Features:
# - Photoshop-like interface
# - Layers and masks
# - Text and shapes
# - Filters and adjustments
# - Export to PNG, JPG, etc.
```

**Pros:** No installation, powerful, free
**Cons:** Requires internet, ads (can pay to remove)

---

### Annotation Best Practices

#### Colors
- **Red:** Errors, warnings, critical points
- **Green:** Success, completion, positive outcomes
- **Blue:** Information, explanations, neutral highlights
- **Yellow:** Highlights, attention areas
- **Orange:** Predictions, future events

#### Shapes
- **Rectangles:** Highlight sections of text
- **Circles/Ovals:** Draw attention to specific elements
- **Arrows:** Show flow, direction, connections
- **Lines:** Separate sections, underline key points

#### Text
- **Font:** Sans-serif (Arial, Helvetica, Roboto) for clarity
- **Size:** Large enough to read when scaled down (18-24pt)
- **Color:** High contrast with background
- **Placement:** Outside main content when possible
- **Callout boxes:** For longer explanations

#### Consistency
- Use the same colors for the same types of annotations
- Same arrow style throughout
- Same text font and size
- Uniform padding and spacing

---

## Cropping and Framing

### What to Include

**Keep:**
- All relevant terminal output
- Command prompts showing what was run
- Key visual elements (emojis, icons, formatting)
- Enough context to understand what's happening

**Remove:**
- Desktop background (unless needed)
- Other windows/applications
- Menu bars (unless needed for context)
- Excessive whitespace
- Irrelevant terminal history

### Aspect Ratios

**Different uses, different ratios:**

- **Twitter/X:** 16:9 (1200x675px) or 2:1 (1200x600px)
- **LinkedIn:** 1.91:1 (1200x627px)
- **Instagram:** 1:1 (1080x1080px) or 4:5 (1080x1350px)
- **GitHub README:** Any, but 16:9 or 4:3 works well
- **Blog posts:** 16:9 (standard) or 21:9 (wide)
- **Presentations:** 16:9 (match slide aspect ratio)

### Padding and Borders

**Add visual polish:**
- **Padding:** 20-40px white/colored border around screenshot
- **Rounded corners:** 8-16px radius for modern look
- **Shadow:** Subtle drop shadow for depth (optional)
- **Background:** Gradient or solid color behind screenshot

**Tools for this:**
- CleanShot X (macOS) - built-in
- Carbon.now.sh - code screenshot tool
- Custom CSS/HTML if generating programmatically

---

## Optimizing File Size

### Target Specifications

| Use Case | Max Size | Format | Dimensions |
|----------|----------|--------|------------|
| GitHub README | 500KB | PNG | 800-1200px wide |
| Blog post | 200KB | JPG/PNG | 800-1200px wide |
| Twitter/Social | 1MB | PNG/JPG | Per platform specs |
| Documentation | 300KB | PNG | 600-1000px wide |
| Presentation | 1MB | PNG | 1920px wide (full HD) |

### Compression Tools

#### ImageOptim (macOS)
```bash
# Download: https://imageoptim.com/
# Free and open source

# Usage:
# - Drag and drop images
# - Automatic lossless compression
# - Removes metadata
# - Typically saves 30-70%

# Command line:
imageoptim screenshot.png
```

**Pros:** Easy, effective, lossless
**Cons:** macOS only

#### TinyPNG/TinyJPG (Web-based)
```bash
# Visit: https://tinypng.com/
# Free for up to 20 images at once

# Features:
# - Smart lossy compression
# - Preserves quality well
# - Batch processing
# - API available

# Typical savings: 50-80%
```

**Pros:** Excellent compression ratio, easy to use
**Cons:** Lossy (but minimal quality impact)

#### OptiPNG (Command line, cross-platform)
```bash
# Install:
# macOS: brew install optipng
# Linux: sudo apt-get install optipng
# Windows: Download from optipng.sourceforge.net

# Usage:
optipng -o7 screenshot.png

# -o7: Highest optimization (slowest)
# -o2: Good balance (faster)

# Lossless compression
```

**Pros:** Lossless, scriptable
**Cons:** Command line only, slower

#### pngquant (Command line, cross-platform)
```bash
# Install:
# macOS: brew install pngquant
# Linux: sudo apt-get install pngquant
# Windows: Download from pngquant.org

# Usage:
pngquant --quality=65-80 screenshot.png

# Output: screenshot-fs8.png

# Lossy but high quality
```

**Pros:** Excellent compression, maintains quality
**Cons:** Lossy, command line

---

## Screenshot Workflow

### Recommended Process

1. **Prepare terminal**
   - Set theme, font, size
   - Clear screen
   - Navigate to demo directory
   - Simplify prompt

2. **Run demo/command**
   - Execute the specific command
   - Wait for key moment
   - Ensure output is complete

3. **Capture screenshot**
   - Use tool of choice
   - Capture area or window
   - Review immediately

4. **Edit and annotate**
   - Crop to relevant content
   - Add highlights, arrows, text
   - Ensure readability

5. **Optimize file size**
   - Compress with tool
   - Verify quality
   - Check file size

6. **Name and organize**
   - Use descriptive names
   - Store in docs/marketing/assets/
   - Keep originals (pre-annotation)

7. **Test in context**
   - View in README or slide
   - Check on mobile device
   - Verify legibility at scale

---

## File Naming Conventions

### Structure
```
empathy_[section]_[feature]_[version].png
```

### Examples
```
empathy_demo_healthcare_pattern_v1.png
empathy_demo_cross_domain_match_v1.png
empathy_demo_prediction_87_percent_v1.png
empathy_demo_prevention_steps_v1.png
empathy_wizard_security_sql_injection_v1.png
empathy_github_repo_stars_v1.png
empathy_install_command_v1.png
```

### Version Control
- Use v1, v2, v3 for iterations
- Keep old versions for comparison
- Document what changed in each version

### Organization
```
docs/marketing/assets/
├── screenshots/
│   ├── demo/
│   │   ├── empathy_demo_healthcare_pattern_v1.png
│   │   ├── empathy_demo_cross_domain_match_v1.png
│   │   └── empathy_demo_prediction_v1.png
│   ├── wizards/
│   │   ├── empathy_wizard_security_v1.png
│   │   └── empathy_wizard_performance_v1.png
│   ├── social/
│   │   ├── twitter/
│   │   └── linkedin/
│   └── originals/  # Unedited versions
└── diagrams/
    ├── architecture_v1.png
    └── five_levels_v1.png
```

---

## Where to Use Each Screenshot

### README.md

**Hero section (top):**
- Cross-domain pattern match (the "wow" moment)
- Or animated GIF showing full demo flow

**Quick Start section:**
- Installation command screenshot
- Simple usage example

**Featured Example section:**
- Healthcare pattern detection
- Cross-domain match
- Prediction output
- Summary/results

**Other Wizards section:**
- One screenshot per wizard category
- Security, Performance, Compliance examples

### Documentation

**Tutorial pages:**
- Step-by-step screenshots
- Before/after comparisons
- Expected output at each step

**API Reference:**
- Code examples with syntax highlighting
- Output samples

**Troubleshooting:**
- Error messages
- Correct vs. incorrect output

### Presentations

**Demo slides:**
- Key moments (pattern, match, prediction)
- Large, readable text
- Minimal annotations (let you narrate)

**Results slides:**
- Summary screenshot
- Impact metrics highlighted

### Social Media

**Twitter/X:**
- Single compelling moment
- Text overlay with context
- Keep text large and minimal

**LinkedIn:**
- Professional, clean screenshots
- Context in post text
- Technical credibility

**Reddit/HN:**
- Detailed screenshots okay
- Technical audience appreciates detail
- Link to full documentation

### Blog Posts

**Intro:**
- Overview screenshot showing end result

**Body:**
- Progressive disclosure (show each step)
- Annotated for clarity
- Zoom on important details

**Conclusion:**
- Summary or next steps screenshot

---

## Creating Comparison Screenshots

### Before/After

**Without Empathy Framework:**
- Traditional tool output
- Shows limitation

**With Empathy Framework:**
- Same scenario
- Shows cross-domain insight

**Layout:**
- Side-by-side (desktop)
- Stacked (mobile)
- Arrows showing difference

### Competitive Comparison

**Be respectful:**
- Don't disparage competitors
- Show objective differences
- Focus on unique capabilities

**Format:**
```
┌─────────────────┬─────────────────┐
│ Traditional AI  │ Empathy         │
│ Tool            │ Framework       │
├─────────────────┼─────────────────┤
│ Single domain   │ Cross-domain    │
│ Current issues  │ Future predict  │
│ Detection only  │ Prevention too  │
└─────────────────┴─────────────────┘
```

---

## Accessibility Considerations

### Alt Text

**Always provide:**
```markdown
![Cross-domain pattern match showing healthcare handoff failure pattern applied to predict software deployment failure with 87% confidence](empathy_demo_cross_domain_match_v1.png)
```

**Alt text should:**
- Describe what's in the image
- Convey the key information
- Be concise but informative
- Not start with "Image of" or "Screenshot of"

### Color Contrast

**Ensure readability:**
- Text annotations: WCAG AA contrast ratio (4.5:1)
- Don't rely on color alone
- Use shapes + colors
- Test with color blindness simulators

**Tools:**
- WebAIM Contrast Checker
- Stark plugin for Figma
- Color Oracle (color blindness simulator)

### Text in Images

**Minimize text in images:**
- Prefer actual text in markdown
- Only use images for terminal output
- Provide transcripts for code screenshots

---

## Advanced Techniques

### Carbon Code Screenshots

**Tool:** https://carbon.now.sh/

**Features:**
- Beautiful code screenshots
- Syntax highlighting
- Custom themes
- Export to PNG/SVG
- Customizable window chrome

**Use for:**
- Code examples in slides
- Social media posts
- Blog post headers

**Process:**
1. Paste code
2. Select language
3. Choose theme
4. Adjust window settings
5. Export PNG (2x for retina)

### Terminal Replay

**Record terminal:**
```bash
# Use asciinema
asciinema rec demo.cast

# Run commands
# Stop with Ctrl+D

# Generate SVG screenshot at specific time
asciinema-svg demo.cast screenshot.svg -t 10.5

# Renders terminal state at 10.5 seconds
```

**Benefits:**
- Perfect screenshot timing
- Reproducible
- Can regenerate if needed

### Programmatic Screenshots

**Playwright/Puppeteer for web:**
```javascript
// Screenshot of documentation page
await page.screenshot({
  path: 'docs_screenshot.png',
  fullPage: true
});
```

**Selenium for automated testing:**
```python
# Screenshot of dashboard
driver.get('http://localhost:3000/dashboard')
driver.save_screenshot('dashboard.png')
```

**Use for:**
- Automated screenshot generation
- Consistent styling across versions
- CI/CD integration

---

## Quality Checklist

Before publishing any screenshot, verify:

**Technical Quality:**
- [ ] High resolution (at least 800px wide)
- [ ] Clear, sharp text (not blurry)
- [ ] Good contrast (readable on all displays)
- [ ] Proper aspect ratio for use case
- [ ] File size optimized (< 500KB for README)
- [ ] Correct format (PNG for text, JPG for photos)

**Content Quality:**
- [ ] Shows key moment/feature clearly
- [ ] Relevant to documentation context
- [ ] No sensitive information visible
- [ ] No distracting elements
- [ ] Terminal/UI looks professional
- [ ] Output is complete (not cut off)

**Annotation Quality:**
- [ ] Highlights draw attention to key info
- [ ] Text is large and readable
- [ ] Colors are consistent and meaningful
- [ ] Arrows/shapes are clean and professional
- [ ] Not cluttered or overwhelming

**Accessibility:**
- [ ] Alt text provided
- [ ] Sufficient color contrast
- [ ] Not relying solely on color
- [ ] Works in dark mode (if applicable)

**Organization:**
- [ ] Descriptive filename
- [ ] Stored in correct directory
- [ ] Original version saved
- [ ] Version documented

---

## Screenshot Maintenance

### When to Update

**Regular updates:**
- UI changes in framework
- New features added
- Better examples developed
- Improved clarity/annotations

**Emergency updates:**
- Security information exposed
- Branding changes
- Deprecated features shown
- Broken links or outdated info

### Version Control

**Track changes:**
```
v1: Initial screenshot (Jan 2025)
v2: Added annotation highlighting 87% (Feb 2025)
v3: Updated terminal theme for better contrast (Mar 2025)
```

**Keep history:**
- Store in version control (Git)
- Use Git LFS for large files
- Tag releases with screenshot versions
- Document in CHANGELOG

---

## Platform-Specific Tips

### GitHub README

**Best practices:**
- First screenshot at ~400-600 lines into README
- Use relative paths: `![Demo](docs/marketing/assets/demo.png)`
- Test on both light and dark themes
- Ensure mobile rendering
- Consider GIF for animation

### Twitter/X

**Specifications:**
- Max 4 images per tweet
- Best size: 1200x675px (16:9)
- Or 2:1 (1200x600px) for wider
- PNG for text, JPG for photos
- Keep text large (will be small on mobile)

### LinkedIn

**Specifications:**
- Optimal: 1200x627px (1.91:1)
- Min: 552x368px
- Max: 7680x4320px
- Professional tone
- Add context in post, not overlay

### Dev.to / Hashnode

**Best practices:**
- 1000px wide max
- PNG for code screenshots
- Use platform's image hosting
- Alt text is required
- Consider dark mode readers

---

## Conclusion

Great screenshots are a force multiplier for your documentation, presentations, and marketing. They:
- Reduce time to understanding
- Increase engagement and adoption
- Showcase unique capabilities
- Build professionalism and trust

Invest time in high-quality screenshots. They pay dividends in stars, downloads, and conversions.

---

## Quick Reference

### Screenshot Priority List

1. Cross-domain pattern match (HIGHEST PRIORITY)
2. Level 4 Anticipatory prediction (87% confidence)
3. Healthcare pattern detection (23% failure rate)
4. Prevention steps output
5. Summary/results
6. Installation/setup
7. Individual wizard examples
8. GitHub repository

### Essential Tools

**Capture:**
- macOS: Cmd+Shift+4 or CleanShot X
- Linux: Flameshot
- Windows: ShareX

**Edit:**
- Simple: Preview (macOS), Paint (Windows)
- Advanced: GIMP, Photopea

**Optimize:**
- ImageOptim, TinyPNG, pngquant

**Annotate:**
- Skitch, CleanShot X, Flameshot

### File Specs

- Format: PNG (text), JPG (photos)
- Size: < 500KB (README), < 1MB (presentations)
- Width: 800-1200px (documentation)
- Resolution: 2x for retina (optional)

---

**Guide Version:** 1.0
**Last Updated:** January 2025
**Copyright:** 2025 Deep Study AI, LLC
