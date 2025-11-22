# README GIF Guide: Animated Demo for Repository

**Purpose:** Create a compelling, professional animated GIF for the README that shows the Level 5 demo in action.

**Target:** 10-15 seconds, < 5MB, 800x600px, embedded at top of README

---

## Why an Animated GIF?

An animated GIF in your README:
- Shows the framework in action immediately
- Reduces barrier to understanding
- Increases GitHub star conversion rate by 40%+
- Works on all platforms (mobile, web, desktop)
- No video player required
- Autoplays on scroll

**Best Practice:** Place GIF in README right after the Quick Start section, before detailed documentation.

---

## Option 1: Using asciinema + agg (Recommended)

### Tools Required

```bash
# Install asciinema for terminal recording
brew install asciinema  # macOS
# or
sudo apt-get install asciinema  # Ubuntu/Debian

# Install agg for converting to GIF
cargo install --git https://github.com/asciinema/agg
# or download binary from https://github.com/asciinema/agg/releases
```

### Recording Process

#### Step 1: Configure Terminal

```bash
# Set optimal terminal size for GIF
# 80 columns x 24 rows is perfect for README
export COLUMNS=80
export LINES=24

# Simplify prompt to avoid clutter
export PS1="\$ "

# Clear screen
clear

# Set font size (adjust in terminal preferences)
# Recommended: 14-16pt for readability
```

#### Step 2: Record the Demo

```bash
# Record asciinema session
asciinema rec empathy_demo.cast

# Now run the demo commands
$ python examples/level_5_transformative/run_full_demo.py

# During recording:
# - Type commands at natural speed (not too fast)
# - Pause 1-2 seconds after key output
# - Let important text be visible
# - Press Enter to continue at demo prompt

# Stop recording
# Press Ctrl+D or type 'exit'
```

#### Step 3: Trim and Edit (Optional)

```bash
# If you need to edit timing or remove parts
# Use asciinema's built-in editing

# Play back to check
asciinema play empathy_demo.cast

# Cut from beginning (remove setup time)
asciinema cat empathy_demo.cast | head -n -50 > empathy_trimmed.cast

# Adjust speed (make it 1.5x faster)
# Edit the .cast file header, change "speed": 1.0 to "speed": 1.5
```

#### Step 4: Convert to GIF

```bash
# Convert to GIF with optimal settings
agg \
  --font-family "Monaco, Menlo, monospace" \
  --font-size 14 \
  --line-height 1.4 \
  --theme monokai \
  --fps-cap 10 \
  --speed 1.5 \
  --cols 80 \
  --rows 24 \
  empathy_demo.cast empathy_demo.gif

# Options explained:
# --font-family: Use monospace font
# --font-size 14: Readable on all devices
# --line-height 1.4: Good spacing
# --theme monokai: Professional dark theme
# --fps-cap 10: Smooth but smaller file size
# --speed 1.5: Speed up for brevity
# --cols/rows: Fixed dimensions
```

#### Step 5: Optimize File Size

```bash
# Check file size
ls -lh empathy_demo.gif

# If > 5MB, optimize with gifsicle
brew install gifsicle  # macOS
sudo apt-get install gifsicle  # Linux

# Optimize
gifsicle -O3 --colors 256 --lossy=80 empathy_demo.gif -o empathy_demo_optimized.gif

# Further compression if needed
gifsicle -O3 --colors 128 --lossy=100 empathy_demo.gif -o empathy_demo_small.gif

# Compare sizes
ls -lh empathy_demo*.gif
```

---

## Option 2: Using Terminalizer

### Installation

```bash
# Install via npm
npm install -g terminalizer

# Verify installation
terminalizer --version
```

### Recording Process

```bash
# Initialize config
terminalizer init

# Edit config.yml for optimal settings
# Key settings:
# - cols: 80
# - rows: 24
# - frameDelay: 100 (milliseconds)
# - maxIdleTime: 2000
# - fontSize: 14
# - theme: monokai

# Record
terminalizer record empathy_demo

# Run your demo commands
$ python examples/level_5_transformative/run_full_demo.py

# Stop recording (Ctrl+D)

# Render to GIF
terminalizer render empathy_demo -o empathy_demo.gif

# Optimize quality
terminalizer render empathy_demo \
  --quality 100 \
  --output empathy_demo.gif
```

---

## Option 3: Screen Recording + Conversion

### For macOS

```bash
# Use built-in screen recording
# QuickTime Player → File → New Screen Recording
# Or use CMD+Shift+5 (macOS Mojave+)

# Record terminal window only
# Set terminal to 80x24 characters
# Run demo commands

# Convert MOV to GIF using ffmpeg
brew install ffmpeg

ffmpeg -i screen_recording.mov \
  -vf "fps=10,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 \
  empathy_demo.gif

# Optimize
gifsicle -O3 --colors 256 --lossy=80 empathy_demo.gif -o empathy_demo_final.gif
```

### For Linux

```bash
# Use Peek (GIF screen recorder)
sudo apt-get install peek

# Or use Kazam + ffmpeg
sudo apt-get install kazam ffmpeg

# Record with Kazam
kazam

# Convert with ffmpeg (same command as macOS)
```

### For Windows

```bash
# Use ScreenToGif
# Download from: https://www.screentogif.com/

# Or use OBS Studio + ffmpeg
# Download OBS: https://obsproject.com/
# Record terminal window
# Export as video
# Convert with ffmpeg
```

---

## Recommended Commands to Record

### Quick Demo (10-15 seconds)

```bash
# Clear terminal
clear

# Show installation
$ pip install empathy-framework[full]

# Run demo (pre-abbreviated version)
$ python examples/level_5_transformative/run_full_demo.py

# Show key output:
# - Healthcare analysis (2-3 seconds)
# - [Press Enter] (pause 1 second)
# - Cross-domain pattern match (2-3 seconds)
# - Prediction output (2-3 seconds)
# - Summary (2 seconds)
```

### What to Show

**Focus on these key moments:**

1. **Healthcare Pattern Detected** (3 seconds)
   ```
   ✓ Pattern 'critical_handoff_failure' stored
   ℹ️  Handoffs without verification fail 23%
   ```

2. **Cross-Domain Match** (4 seconds)
   ```
   CROSS-DOMAIN PATTERN DETECTION
   ✓ Pattern match from healthcare domain!
   ```

3. **Prediction** (5 seconds)
   ```
   ⚠️  DEPLOYMENT HANDOFF FAILURE PREDICTED
   📅 30-45 days
   🎯 87% confidence
   💥 HIGH impact
   ```

4. **Summary** (3 seconds)
   ```
   Pattern learned in healthcare → Applied to software
   Powered by: Empathy Framework + MemDocs
   ```

---

## Terminal Configuration for Best Results

### Colors and Theme

```bash
# Use a professional terminal theme
# Recommended themes:
# - Monokai
# - Dracula
# - Solarized Dark
# - One Dark

# Ensure high contrast
# - Background: Dark (#1e1e1e or similar)
# - Text: Light (#d4d4d4 or similar)
# - Accent colors: Vibrant but readable
```

### Font Settings

```bash
# Recommended fonts:
# - Fira Code (with ligatures)
# - JetBrains Mono
# - Monaco
# - Menlo
# - Source Code Pro

# Font size: 14-16pt
# Line height: 1.3-1.5
```

### Window Size

```bash
# Optimal dimensions for README GIF
# Width: 800-1000px
# Height: 500-650px
# Aspect ratio: ~4:3 or 16:10

# Terminal character dimensions
# 80-100 columns
# 24-30 rows
```

---

## Editing and Trimming

### Using asciinema play

```bash
# Play recording to find timestamps
asciinema play empathy_demo.cast

# Note timestamps of key moments
# Example:
# 0:00-0:03 - Healthcare analysis
# 0:03-0:04 - Press Enter pause
# 0:04-0:08 - Cross-domain match
# 0:08-0:13 - Prediction
# 0:13-0:15 - Summary
```

### Cutting Segments

```bash
# Extract specific time range
# This requires asciinema-edit (not built-in)
# Or edit the .cast JSON file directly

# The .cast file is JSON format:
{
  "version": 2,
  "width": 80,
  "height": 24,
  "timestamp": 1234567890,
  "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"},
  "events": [
    [0.0, "o", "$ "],
    [0.5, "o", "python demo.py\n"],
    ...
  ]
}

# Edit events array to remove unwanted segments
# Each event: [timestamp, type, data]
```

---

## Export Settings

### Target Specifications

```
Format: GIF
Size: < 5MB (ideally 2-3MB)
Dimensions: 800x600px or 1000x650px
Frame rate: 10 FPS (smooth enough, small file)
Colors: 256 colors (standard GIF palette)
Loop: Infinite (0)
Duration: 10-15 seconds
```

### Quality vs. Size Trade-offs

| Setting | Quality | File Size | Best For |
|---------|---------|-----------|----------|
| 256 colors, 10 FPS, no lossy | High | Large (8-15MB) | Detail-critical |
| 256 colors, 10 FPS, lossy 80 | Good | Medium (3-5MB) | **Recommended** |
| 128 colors, 8 FPS, lossy 100 | Fair | Small (1-2MB) | Mobile-first |

### Optimization Command Reference

```bash
# Light optimization (preserve quality)
gifsicle -O3 --colors 256 input.gif -o output.gif

# Medium optimization (recommended)
gifsicle -O3 --colors 256 --lossy=80 input.gif -o output.gif

# Aggressive optimization (small file priority)
gifsicle -O3 --colors 128 --lossy=100 --scale 0.8 input.gif -o output.gif

# Check savings
ls -lh input.gif output.gif
```

---

## Embedding in README

### Placement

```markdown
# Empathy Framework

**A five-level maturity model for AI-human collaboration**

![Coverage](https://img.shields.io/badge/coverage-90.66%25-brightgreen)
[![License](https://img.shields.io/badge/License-Fair%20Source%200.9-blue.svg)](LICENSE)

---

## See It In Action

![Empathy Framework Demo](docs/marketing/assets/empathy_demo.gif)

*Level 5 Transformative Empathy: Healthcare patterns predict software failures*

---

## Quick Start

```bash
pip install empathy-framework[full]
python examples/level_5_transformative/run_full_demo.py
```
```

### Alternative Placements

1. **Hero section** (immediately after title)
2. **After Quick Start** (show then tell)
3. **In Featured Example section** (contextual demo)
4. **Dedicated Demo section** (with detailed explanation)

### Accessibility

```markdown
<!-- Include alt text -->
![Empathy Framework Demo: Healthcare handoff pattern predicting software deployment failure](docs/marketing/assets/empathy_demo.gif)

<!-- Provide alternative static image -->
<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="docs/marketing/assets/empathy_demo_static.png">
  <img src="docs/marketing/assets/empathy_demo.gif" alt="Empathy Framework Demo">
</picture>

<!-- Link to video for more detail -->
![Demo](docs/marketing/assets/empathy_demo.gif)

*[Watch full demo video →](https://youtu.be/your-video-id)*
```

---

## Hosting Options

### Option 1: In Repository (Recommended)

```bash
# Store in docs/marketing/assets/
mkdir -p docs/marketing/assets
cp empathy_demo.gif docs/marketing/assets/

# Reference in README
![Demo](docs/marketing/assets/empathy_demo.gif)

# Pros: Version controlled, always available
# Cons: Increases repo size (use Git LFS if > 10MB)
```

### Option 2: GitHub Releases

```bash
# Upload to GitHub Release
# Then reference via URL
![Demo](https://github.com/Smart-AI-Memory/empathy-framework/releases/download/v1.0/empathy_demo.gif)

# Pros: Doesn't bloat repo
# Cons: Requires release management
```

### Option 3: External CDN

```bash
# Upload to imgur, giphy, or CDN
# Reference via URL
![Demo](https://i.imgur.com/abc123.gif)

# Pros: Fast loading, no repo impact
# Cons: Dependency on external service
```

### Option 4: Git LFS (Large Files)

```bash
# If GIF > 10MB, use Git LFS
git lfs install
git lfs track "*.gif"
git add .gitattributes
git add docs/marketing/assets/empathy_demo.gif
git commit -m "Add demo GIF via Git LFS"

# Pros: Handles large files efficiently
# Cons: Requires Git LFS setup
```

---

## Quality Checklist

Before publishing your GIF, verify:

- [ ] File size < 5MB (preferably 2-3MB)
- [ ] Dimensions: 800x600px to 1000x650px
- [ ] Duration: 10-15 seconds
- [ ] Frame rate: 8-10 FPS
- [ ] Colors: Clear and readable
- [ ] Text: Large enough to read on mobile
- [ ] Loops: Infinite (seamless if possible)
- [ ] Load time: < 3 seconds on 4G
- [ ] Mobile rendering: Tested on phone browser
- [ ] Accessibility: Alt text provided
- [ ] GitHub rendering: Verified in preview
- [ ] Key moments visible: Pattern match, prediction, etc.
- [ ] No sensitive information: API keys, paths, etc.
- [ ] Professional appearance: Clean, polished
- [ ] On-brand: Matches project aesthetic

---

## Advanced Tips

### Creating a Seamless Loop

```bash
# Record demo that ends in similar state to beginning
# For example, end with cleared screen or same prompt

# Or use gifsicle to create loop points
gifsicle --loopcount=0 empathy_demo.gif -o empathy_demo_loop.gif
```

### Adding Text Overlays

```bash
# Use ImageMagick to add annotations
brew install imagemagick

# Add title overlay (at specific frame)
convert empathy_demo.gif \
  -coalesce \
  -draw "text 10,20 'Level 5 Transformative Empathy'" \
  -layers optimize \
  empathy_demo_titled.gif
```

### Multi-Speed Versions

Create multiple versions for different use cases:

```bash
# Fast version (10s, README hero)
agg --speed 2.0 demo.cast demo_fast.gif

# Normal version (15s, documentation)
agg --speed 1.5 demo.cast demo_normal.gif

# Detailed version (30s, tutorial)
agg --speed 1.0 demo.cast demo_detailed.gif
```

### Platform-Specific Optimization

```bash
# GitHub-optimized (prioritize compatibility)
gifsicle -O3 --colors 256 --lossy=50 demo.gif -o demo_github.gif

# Twitter-optimized (< 15MB, < 512px wide)
gifsicle -O3 --colors 256 --scale 0.6 demo.gif -o demo_twitter.gif

# LinkedIn-optimized (< 5MB, square aspect)
gifsicle -O3 --colors 128 --lossy=100 --crop 0,50+800x800 demo.gif -o demo_linkedin.gif
```

---

## Troubleshooting

### GIF Too Large

**Problem:** GIF > 5MB after optimization

**Solutions:**
1. Reduce dimensions: `--scale 0.8`
2. Lower frame rate: `--fps-cap 8`
3. Reduce colors: `--colors 128`
4. Increase lossy compression: `--lossy=100`
5. Shorten duration: Edit .cast file
6. Use fewer frames: Record at lower FPS

### Text Unreadable

**Problem:** Terminal text too small or blurry

**Solutions:**
1. Increase font size in terminal (16-18pt)
2. Larger GIF dimensions (1000x650px)
3. Higher contrast theme
4. Fewer terminal rows (better zoom)
5. Bold font weight
6. Less text on screen (trim output)

### Colors Look Bad

**Problem:** Dithering or color banding

**Solutions:**
1. Use 256 colors instead of 128
2. Lower lossy compression value
3. Better source terminal theme
4. True-color terminal emulator
5. Match GIF palette to terminal theme

### Slow Loading

**Problem:** GIF takes too long to load

**Solutions:**
1. Reduce file size (see "GIF Too Large")
2. Use lazy loading in HTML
3. Provide thumbnail preview
4. Host on fast CDN
5. Offer video alternative

---

## Examples and Inspiration

### Great README GIFs to Study

1. **asciinema/asciinema** - Clean terminal recording
2. **junegunn/fzf** - Fast, focused functionality demo
3. **charmbracelet/glow** - Colorful, aesthetic appeal
4. **jesseduffield/lazygit** - Multi-step workflow
5. **koalaman/shellcheck** - Before/after comparison

### Analysis: What Makes Them Work

- **Focus:** One clear feature or workflow
- **Brevity:** 10-15 seconds maximum
- **Clarity:** Large text, high contrast
- **Context:** Obvious what's being demonstrated
- **Loop:** Seamless or natural start/end
- **Quality:** Professional appearance
- **Relevance:** Shows the "wow" factor immediately

---

## Maintenance

### Updating the GIF

When to update:
- Major UI changes
- Significant new features
- Rebranding or theme updates
- Better recording techniques available
- User feedback suggests improvements

How to version:
```bash
# Keep old versions for reference
mv empathy_demo.gif empathy_demo_v1.gif
# Create new version
# Update README reference
```

### Tracking Performance

Monitor README engagement:
- GitHub traffic analytics
- Time on page (via external analytics)
- Star conversion rate before/after GIF
- Click-through to demo installation

Iterate based on data:
- Test different durations
- A/B test placement
- Try different key moments
- Experiment with speed

---

## Conclusion

A well-crafted animated GIF can significantly boost README engagement and project adoption. Invest time in creating a polished, professional demo that showcases your framework's unique value proposition.

**Key Takeaways:**
- Keep it short (10-15s)
- Keep it small (< 5MB)
- Keep it readable (large text, high contrast)
- Show the "wow" factor (cross-domain pattern match)
- Optimize for mobile viewing
- Test before publishing

---

**Guide Version:** 1.0
**Last Updated:** January 2025
**Copyright:** 2025 Deep Study AI, LLC
