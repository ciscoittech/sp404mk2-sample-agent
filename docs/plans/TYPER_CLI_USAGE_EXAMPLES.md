# Typer CLI Hardware Assistant - Usage Examples

**Reference**: See [TYPER_CLI_HARDWARE_ASSISTANT.md](./TYPER_CLI_HARDWARE_ASSISTANT.md) for implementation plan

This document provides comprehensive usage examples for the planned Typer CLI hardware assistant.

---

## 📖 Table of Contents

1. [Quick Reference Commands](#quick-reference-commands)
2. [AI-Powered Smart Commands](#ai-powered-smart-commands)
3. [Workflow Examples](#workflow-examples)
4. [Scripting & Automation](#scripting--automation)
5. [Real-World Scenarios](#real-world-scenarios)
6. [Shell Integration](#shell-integration)
7. [Output Formats](#output-formats)

---

## Quick Reference Commands

### Fast Mode (No LLM, Instant Responses)

```bash
# Resampling quick reference
$ sp404 hardware resample --fast
📖 Resampling (from manual):
1. Hold [RESAMPLE] button
2. Press pad(s) to resample
3. Press empty pad to record to
4. Perform your pattern
5. Press [RESAMPLE] to finish

# List all effects
$ sp404 hardware effects --list
📖 Effects List:
- Lo-fi
- Cassette Sim
- 303 Vinyl Sim
- 404 Vinyl Sim
- Reverb
- Delay
- Filter
- Compressor
[... full list ...]

# Pattern sequencer quick guide
$ sp404 hardware pattern --fast
📖 Pattern Sequencer:
Two modes: Real-time recording and TR-REC...

# Looper reference
$ sp404 hardware looper --fast
📖 Looper Operation:
1. Hold [LOOPER] button...

# Button shortcuts
$ sp404 hardware quickref
╭─ Buttons Quick Reference ──────────────────╮
│ Operation    │ Button Combination         │
├──────────────┼────────────────────────────┤
│ Resample     │ Hold [RESAMPLE] + pads     │
│ Looper       │ Hold [LOOPER] + pad        │
│ Pattern      │ Press [PATTERN]            │
│ Save         │ [SHIFT] + [PROJECT]        │
╰──────────────┴────────────────────────────╯

# Search manual
$ sp404 hardware manual "bpm sync"
╭─ Manual Search: 'bpm sync' ─────────────────╮
│ Section     │ Match              │ Context │
├─────────────┼────────────────────┼─────────┤
│ performance │ Playing back BPM   │ ...     │
│ sequencer   │ BPM synchronization│ ...     │
╰─────────────┴────────────────────┴─────────╯
```

---

## AI-Powered Smart Commands

### Genre-Specific Recommendations

```bash
# Lo-fi hip-hop effects
$ sp404 hardware effects lofi
🤖 Consulting SP-404 manual with AI...

For lo-fi hip-hop production on the SP-404MK2:

**Essential Effects Chain**:

1. **Lo-fi Effect** - Core lo-fi sound
   - Reduces sample rate for digital warmth
   - Bit reduction adds character
   - Settings: Medium reduction, adjust to taste

2. **Cassette Sim** - Analog tape warmth
   - Wow and flutter for organic feel
   - Tape saturation for warmth
   - Settings: High wow/flutter, medium saturation

3. **Vinyl Sim (303 or 404)** - Dusty character
   - Crackle and pop for vintage feel
   - 303 for subtle, 404 for pronounced
   - Settings: Light to medium crackle

4. **Filter** - Tone shaping
   - Low-pass for warmth
   - Remove harsh highs
   - Settings: Cutoff around 8kHz

**Pro Workflow**:
- Apply effects individually to pads
- Resample to freeze effect combinations
- Layer resampled pads for depth
- Use compressor on final mix

**Creative Technique**:
Resample the same sample 3 times with different
cassette sim settings, then play them together
for a "triple-tape" effect!

# Boom bap drums
$ sp404 hardware effects hiphop
🤖 [AI provides boom bap-specific effect chains]

# Trap production
$ sp404 hardware effects trap --creative
🤖 [AI provides creative trap techniques]
```

### Natural Language Questions

```bash
# Ask anything about hardware
$ sp404 hardware ask "how do I layer effects with resampling?"
🤖 Consulting SP-404 manual with AI...

Layering effects with resampling on the SP-404MK2:

**The Technique** (called "effect freezing"):

1. **First Layer**:
   - Apply your first effect (e.g., Vinyl Sim)
   - Hold [RESAMPLE] + press source pad
   - Press empty pad to capture

2. **Second Layer**:
   - On the resampled pad, add second effect (e.g., Delay)
   - Resample again to new pad
   - Now you have both effects "frozen"

3. **Continue Layering**:
   - Each resample adds the current effect permanently
   - Can stack 5-10 effects this way
   - Creates unique textures impossible with live effects

**Why This Works**:
- SP-404 has 3 effect buses
- Resampling "prints" effects to audio
- Frees up effect buses for more processing
- Creates complex soundscapes

**Pro Tips**:
- Resample at each step for maximum flexibility
- Keep original pad for comparison
- Label pads by effect chain
- This is how Madlib and J Dilla worked!

# Specific workflow question
$ sp404 hardware ask "what's the best workflow for sampling vinyl?"
🤖 [AI provides comprehensive vinyl sampling workflow]

# Troubleshooting
$ sp404 hardware ask "why isn't my pattern saving?"
🤖 [AI diagnoses common pattern save issues]
```

### Smart Mode (Default AI)

```bash
# Resample with AI tips
$ sp404 hardware resample
🤖 Consulting SP-404 manual with AI...

Resampling on the SP-404MK2: Complete Guide

[Official manual steps PLUS creative techniques,
common mistakes, pro tips, genre-specific uses]

# Pattern creation guide
$ sp404 hardware pattern
🤖 [Comprehensive pattern guide with AI enhancements]

# Effects overview
$ sp404 hardware effects
🤖 [AI-enhanced effects overview with use cases]
```

### Specific Questions About Features

```bash
# Ask about specific mode
$ sp404 hardware pattern --mode trrec
🤖 TR-REC Mode on SP-404MK2:

[Detailed TR-REC explanation with step programming,
quantization, editing techniques]

# Ask about resample with question
$ sp404 hardware resample --ask "can I resample stereo?"
🤖 Yes! Resampling on SP-404MK2 is stereo:

[Explanation of stereo resampling, pan settings,
stereo effects preservation]
```

---

## Workflow Examples

### Beat Making Workflow

```bash
# Full workflow with AI guidance
$ sp404 hardware workflow beatmaking
🤖 Complete Beat Making Workflow on SP-404MK2:

**Phase 1: Sample Collection**
1. Record drums from vinyl or import samples
2. Organize in banks (kick = pad 1, snare = pad 2, etc.)
3. Edit and trim samples

**Phase 2: Pattern Creation**
1. Enter pattern mode ([PATTERN] button)
2. Choose recording method:
   - Real-time: Record performance naturally
   - TR-REC: Program steps precisely
3. Layer multiple patterns for complexity

**Phase 3: Effects & Processing**
1. Add effects to individual pads
2. Use resampling to freeze effect combinations
3. Create variations with different FX

**Phase 4: Mixing**
1. Switch to DJ mode ([SHIFT] + [SAMPLE])
2. Balance levels with crossfader and volume
3. Add final mix bus effects

**Phase 5: Export**
1. Resample final beat to single pad
2. Or export pattern to SD card
3. Save project for future edits

**Pro Tips**:
- Keep kick and snare dry, add FX to others
- Use compression on final mix
- Create multiple versions before finalizing

[Each phase includes detailed sub-steps and button combos]

# Interactive beat making (step-by-step)
$ sp404 hardware workflow beatmaking --interactive

Step 1/5: Sample Collection
Record drums from vinyl or import samples

[AI provides detailed guidance for this step]

Ready for step 2? [y/N]: y

Step 2/5: Pattern Creation
...

# Fast workflow overview
$ sp404 hardware workflow beatmaking --fast
📖 Beat Making Workflow Steps:
1. Sample Collection: Record or import drums
2. Pattern Creation: Create drum pattern
3. Effects: Add effects to pads
4. Mixing: Balance in DJ mode
5. Export: Export final beat
```

### Lo-Fi Production Workflow

```bash
$ sp404 hardware workflow lofi
🤖 Lo-Fi Hip-Hop Production Workflow:

**Step 1: Sample Selection** (5-10 minutes)
- Choose jazzy, soulful samples
- Look for chord progressions
- Vinyl sources ideal for authenticity

**Step 2: Lo-Fi Treatment** (10-15 minutes)
- Apply Cassette Sim for warmth
- Add Vinyl Sim for crackle
- Use Lo-fi effect for degradation
- Settings: [detailed settings for each]

**Step 3: Layering & Resampling** (15-20 minutes)
- Resample sample with Cassette Sim
- Resample again with Vinyl Sim
- Create variations with different settings
- Layer 2-3 versions together

**Step 4: Drum Pattern** (10-15 minutes)
- Use TR-REC for laid-back groove
- Add swing/shuffle timing
- Keep it simple and repetitive
- Classic: Kick-Snare-Kick-Snare

**Step 5: Final Mix** (5-10 minutes)
- Balance sample and drums
- Add subtle reverb to drum bus
- Optional: Filter sweep automation
- Resample final mix to one pad

**Total Time**: 45-70 minutes for complete beat

[Includes specific button combinations for each step]

# Interactive lo-fi workflow
$ sp404 hardware workflow lofi --interactive
[Guides through each step with AI assistance]
```

### Sample Organization Workflow

```bash
$ sp404 hardware workflow sampling
🤖 Sample Collection & Organization Workflow:

[Complete workflow for organizing sample library,
including bank structure, naming conventions,
backup strategies]
```

---

## Scripting & Automation

### Daily Practice Script

```bash
#!/bin/bash
# ~/.local/bin/sp404-daily-practice

echo "╔════════════════════════════════════╗"
echo "║   SP-404 Daily Practice Routine   ║"
echo "╚════════════════════════════════════╝"
echo ""

# Get tip of the day
sp404 hardware tip

echo ""
echo "Today's Practice Focus:"
echo ""

# Random workflow
workflows=("beatmaking" "lofi" "sampling")
random_workflow=${workflows[$RANDOM % ${#workflows[@]}]}

sp404 hardware workflow $random_workflow --fast

echo ""
echo "Remember: 30 minutes of focused practice!"
echo "Have fun! 🎵"
```

### Study Notes Generator

```bash
#!/bin/bash
# Generate comprehensive SP-404 notes

OUTPUT_DIR=~/Documents/SP404-Notes
mkdir -p $OUTPUT_DIR

echo "Generating SP-404 study notes..."

# Generate section notes
sp404 hardware resample --fast --format markdown > $OUTPUT_DIR/resampling.md
sp404 hardware effects --list --format markdown > $OUTPUT_DIR/effects.md
sp404 hardware pattern --fast --format markdown > $OUTPUT_DIR/patterns.md
sp404 hardware looper --fast --format markdown > $OUTPUT_DIR/looper.md

# Generate workflows
sp404 hardware workflow beatmaking --fast --format markdown > $OUTPUT_DIR/workflow-beatmaking.md
sp404 hardware workflow lofi --fast --format markdown > $OUTPUT_DIR/workflow-lofi.md

# Generate quick reference
sp404 hardware quickref --format markdown > $OUTPUT_DIR/quick-reference.md

echo "✓ Notes generated in $OUTPUT_DIR"
echo "Files created:"
ls -lh $OUTPUT_DIR
```

### Quick Lookup Function (Shell RC)

```bash
# Add to ~/.bashrc or ~/.zshrc

# Quick SP-404 lookup
sp() {
    if [ -z "$1" ]; then
        echo "Usage: sp <topic>"
        echo "Example: sp resample"
        return 1
    fi

    sp404 hardware "$1" --fast
}

# Ask SP-404 question
spask() {
    sp404 hardware ask "$*"
}

# Usage:
# $ sp resample        # Quick lookup
# $ spask how do I layer effects?
```

### Flashcards Generator

```bash
#!/bin/bash
# Generate Anki flashcards from manual

sp404 hardware quickref --format json | jq -r '.buttons | to_entries[] | "\(.key);\(.value)"' > sp404-flashcards.csv

echo "Flashcards ready for import into Anki!"
```

---

## Real-World Scenarios

### Scenario 1: In the Middle of Beat Making

```bash
# Quick reminder while producing
$ sp resample --fast
[Instant button combo reference]

# Back to making beats in < 5 seconds
```

### Scenario 2: Learning New Technique

```bash
# Deep dive into TR-REC
$ sp404 hardware pattern --mode trrec

# Get creative ideas
$ sp404 hardware ask "what are advanced TR-REC techniques?"

# Follow interactive tutorial
$ sp404 hardware workflow beatmaking --interactive
```

### Scenario 3: Genre-Specific Production Session

```bash
# Starting lo-fi session
$ sp404 hardware workflow lofi

# Need effect recommendations
$ sp404 hardware effects lofi --creative

# Specific question during production
$ spask "how much cassette sim is too much?"
```

### Scenario 4: Sample Library Organization Day

```bash
# Get workflow
$ sp404 hardware workflow sampling

# Follow step-by-step
$ sp404 hardware workflow sampling --interactive

# Generate notes for future reference
$ sp404 hardware workflow sampling --format markdown > ~/sp404-sample-org.md
```

### Scenario 5: Teaching Someone

```bash
# Show complete beginner guide
$ sp404 hardware workflow beatmaking > beginner-guide.md

# Generate quick reference card
$ sp404 hardware quickref --format markdown > quick-ref.md

# Share on Reddit/Discord
$ sp404 hardware effects lofi --format markdown | pbcopy
```

---

## Shell Integration

### Tab Completion Examples

```bash
# Bash/Zsh completion
$ sp404 hardware re<TAB>
resample

$ sp404 hardware effects --<TAB>
--list  --creative  --format  --help

$ sp404 hardware workflow <TAB>
beatmaking  lofi  sampling  export

# Fish completion
$ sp404 hardware w<TAB>
workflow (Complete workflow tutorials)
```

### Aliases

```bash
# Add to shell RC file

# Quick commands
alias sp-resample='sp404 hardware resample --fast'
alias sp-effects='sp404 hardware effects --list'
alias sp-pattern='sp404 hardware pattern --fast'
alias sp-tip='sp404 hardware tip'

# AI-powered
alias sp-ask='sp404 hardware ask'
alias sp-lofi='sp404 hardware workflow lofi'
alias sp-beat='sp404 hardware workflow beatmaking'

# With output format
alias sp-notes='sp404 hardware --format markdown'
```

### FZF Integration

```bash
# Interactive manual search with fzf
sp-search() {
    sp404 hardware manual "$*" --format plain | fzf --preview 'sp404 hardware manual {}'
}

# Interactive tip browser
sp-tips() {
    for i in {1..10}; do
        sp404 hardware tip --format plain
    done | fzf
}
```

---

## Output Formats

### Rich Format (Default)

```bash
$ sp404 hardware resample
[Beautiful Rich-formatted output with colors, panels, tables]
```

### Markdown Format

```bash
$ sp404 hardware resample --format markdown
# Resampling

To resample on the SP-404MK2:

1. Hold [RESAMPLE] button
2. Press pad(s) to resample
...
```

### Plain Text Format

```bash
$ sp404 hardware resample --format plain
Resampling

To resample on the SP-404MK2:

1. Hold RESAMPLE button
2. Press pads to resample
...
```

### JSON Format

```bash
$ sp404 hardware resample --format json
{
  "file": "sp404-sampling.md",
  "section": "Resampling",
  "content": "To resample on the SP-404MK2:\n\n1. Hold [RESAMPLE]..."
}

# Pipe to jq for processing
$ sp404 hardware resample --format json | jq -r '.content'
```

---

## Combining with Other Tools

### Export to PDF

```bash
# Generate and convert to PDF
sp404 hardware workflow lofi --format markdown | pandoc -o lofi-workflow.pdf
```

### Create Website

```bash
# Generate all docs
mkdir sp404-docs
for topic in resample effects pattern looper; do
    sp404 hardware $topic --format markdown > sp404-docs/$topic.md
done

# Serve with live-server
cd sp404-docs && live-server
```

### Send to Notion/Obsidian

```bash
# Format for Notion import
sp404 hardware workflow beatmaking --format markdown > ~/Notion/SP404/beatmaking.md
```

---

## Cost Management Examples

### Estimate Cost Before Running

```bash
# Check estimated cost for AI query
$ sp404 hardware ask "complex question" --estimate
Estimated cost: $0.00025
Proceed? [y/N]:
```

### Budget-Aware Mode

```bash
# Use fast mode to save money
$ sp404 hardware resample --fast  # $0
$ sp404 hardware effects --list   # $0

# Use AI only when needed
$ sp404 hardware effects lofi     # ~$0.0001

# Check spending
$ sp404 downloads stats
API Calls Today: 15
Total Cost: $0.0032
```

---

## Tips & Tricks

### Combine Multiple Commands

```bash
# Create comprehensive study guide
{
    sp404 hardware resample --fast
    echo "---"
    sp404 hardware effects --list
    echo "---"
    sp404 hardware pattern --fast
} > sp404-quick-guide.md
```

### Watch Mode (Auto-Refresh)

```bash
# Get new tip every 30 minutes
watch -n 1800 'sp404 hardware tip'
```

### Integration with Sample Collection

```bash
# After collecting samples, get export workflow
sp404 downloads list
sp404 hardware workflow export
```

---

## Comparison: Chat vs CLI

### Use Chat When:
- Learning new concepts
- Complex questions with follow-ups
- Exploring creative ideas
- Need conversational interface

```bash
python sp404_chat.py
> "Explain resampling workflow with creative techniques"
[Deep conversation with AI]
```

### Use CLI When:
- Quick lookups during production
- Need instant answers
- Scripting and automation
- Generating documentation

```bash
sp404 hardware resample --fast
[Instant answer in < 1 second]
```

### Use Both:
```bash
# Start with CLI for quick lookup
sp resample --fast

# If need more detail, ask in chat
python sp404_chat.py
> "I need advanced resampling techniques"
```

---

## Future Usage Patterns (Phase 6+)

### Voice Control (Planned)

```bash
$ sp404 hardware ask --voice "how do I resample"
🎤 Listening...
🤖 [Speaks answer aloud]
```

### Video Tutorial Integration (Planned)

```bash
$ sp404 hardware resample --show-video
🎥 Opening tutorial: "SP-404 Resampling Masterclass"
   Timestamp: 3:42 - Resampling with effects
```

### Community Integration (Planned)

```bash
$ sp404 hardware tip --community
💡 Top community tip (157 votes):
"Resample your looper output for infinite layering!"
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-14
**Status**: 📋 Planned Examples (Implementation Pending)
