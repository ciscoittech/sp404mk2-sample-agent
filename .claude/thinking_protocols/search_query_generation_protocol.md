# Search Query Generation Thinking Protocol

## Purpose
This protocol guides AI agents through generating effective YouTube search queries for discovering high-quality sample packs, loops, and breaks that match user intent.

## 4-Step Thinking Process

### STEP 1: Decode User Intent and Musical Context
First, understand what the user is really asking for beyond their literal words:

**Questions to consider:**
- What musical style/genre are they describing?
- Are they referencing specific artists, producers, or eras?
- What emotional quality or vibe are they seeking?
- Are there technical requirements (BPM, key, format)?
- What's the implicit use case (drums, melodies, texture)?

**User intent patterns:**

| User Says | What They Actually Mean | Musical Context |
|-----------|------------------------|-----------------|
| "Dilla bounce" | Off-beat MPC drums, neo-soul samples | 85-95 BPM, jazzy, lo-fi |
| "That Alchemist sound" | Dusty soul/psych samples, vintage | 90s aesthetic, sample-heavy |
| "Drill drums" | Hard 808s, fast hi-hats, UK/Chicago style | 140+ BPM, aggressive |
| "Lo-fi bedroom vibes" | Warm, imperfect, intimate textures | Tape saturation, vinyl crackle |
| "70s soul breaks" | Live drum breaks from funk/soul records | 95-115 BPM, analog warmth |

**Example reasoning:**
```
User: "I need that Madlib sound"

Decoding:
- Madlib = Sample-heavy, jazz-influenced, experimental producer
- Known for: Rare vinyl digging, psychedelic sounds, off-kilter rhythms
- Era aesthetic: 60s-70s jazz/funk/soul, filtered through lo-fi MPC
- BPM range: Typically 85-100 BPM
- Characteristics: Dusty, warm, vintage, quirky, layered

Therefore searching for:
→ Jazz and soul samples with vintage character
→ Psychedelic and experimental sounds
→ Rare/obscure records (not mainstream)
→ Lo-fi processing aesthetic
```

### STEP 2: Generate Core Search Terms
Based on decoded intent, build foundational search terms:

**Genre/Style terms:**
- Primary genre: hip-hop, jazz, soul, funk, electronic, etc.
- Sub-genre: boom-bap, trap, drill, lo-fi, house, etc.
- Fusion terms: "jazz-funk", "psychedelic soul", "neo-soul"

**Era terms:**
- Decade: "60s", "70s", "80s", "90s", "2000s"
- Era descriptor: "vintage", "retro", "classic", "golden era", "old school"
- Specific year ranges: "1973-1977 funk"

**Texture descriptors:**
- Quality: "dusty", "crispy", "clean", "dirty", "gritty", "polished"
- Processing: "lo-fi", "hi-fi", "analog", "tape", "vinyl"
- Character: "warm", "bright", "dark", "ambient", "raw"

**Technical terms:**
- BPM: "90 BPM", "slow tempo", "uptempo", "140+"
- Format: "WAV", "one-shot", "loop", "break"
- Length: "long samples", "short hits"

**Example term generation:**
```
For "Madlib sound":
- Genre: jazz, soul, funk, psychedelic
- Era: 60s, 70s, vintage
- Texture: dusty, lo-fi, vinyl, rare
- Technical: samples, loops, breaks
```

### STEP 3: Build Platform-Optimized Queries
Combine terms into queries that work well on YouTube:

**YouTube search optimization rules:**

1. **Be Specific but Not Overly Narrow**
   - Good: "90s boom bap drum samples"
   - Bad: "samples" (too broad)
   - Bad: "1994 NYC underground hip hop drum breaks Akai MPC60" (too narrow)

2. **Include Sample/Pack Indicators**
   - Always add: "samples", "sample pack", "drum kit", "loop pack", "breaks"
   - YouTube favors these terms for sample content

3. **Front-load Important Terms**
   - Good: "jazz samples vintage 70s vinyl"
   - Less good: "vintage vinyl 70s jazz samples"
   - YouTube's algorithm weighs early terms more heavily

4. **Use Producer/Artist Names When Relevant**
   - "J Dilla style samples" works better than describing the style
   - "Alchemist type loops" leverages YouTube's recommendation system

5. **Include Quality Indicators**
   - "WAV samples" (format quality)
   - "free download" (accessibility)
   - "high quality" (explicit quality claim)
   - "professional" (production value)

6. **Avoid Negative Terms**
   - Don't use: "not trap", "without vocals"
   - YouTube search doesn't handle negation well

**Query formula patterns:**

```
[Genre] + [Era/Style] + [Type] + [Format]
Example: "jazz soul 70s samples WAV"

[Artist Reference] + [Type] + [Technical]
Example: "Madlib style loops sample pack"

[Mood/Vibe] + [Genre] + [Type]
Example: "dusty vintage hip hop drums"

[Era] + [Genre] + [Specific Element] + [Type]
Example: "90s boom bap drum breaks"

[Technical] + [Genre] + [Type] + [Quality]
Example: "85-95 BPM jazz samples free download"
```

**Example query building:**
```
For "Madlib sound", build queries:

Base: jazz samples

Adding layers:
1. "jazz samples vintage 70s" (era)
2. "psychedelic soul samples rare" (style + scarcity)
3. "Madlib style sample pack loops" (direct reference)
4. "dusty jazz breaks vinyl samples" (texture + format)
5. "obscure soul samples for hip hop" (discovery + use case)
6. "60s jazz loops lo-fi aesthetic" (era + processing)
7. "Brazilian jazz samples rare groove" (specific + descriptor)
```

### STEP 4: Prioritize and Validate Queries
Rank queries by effectiveness and remove redundancy:

**Effectiveness criteria:**
1. **Specificity**: Balanced (not too broad, not too narrow)
2. **Discoverability**: Uses terms people actually search for
3. **Relevance**: Directly matches user intent
4. **Variety**: Covers different aspects of the request
5. **Actionability**: Returns downloadable sample content

**Query ranking example:**
```
For "Madlib sound":

Tier 1 (Best - Use First):
✓ "Madlib style sample pack loops"
  → Direct reference, clear intent, common search

✓ "dusty jazz samples vinyl texture"
  → Specific texture, era implied, quality indicator

✓ "obscure soul samples rare groove"
  → Captures "digging" aesthetic, specific genre

Tier 2 (Good - Use if more results needed):
✓ "60s psychedelic samples for hip hop"
  → Era-specific, use case clear

✓ "Brazilian jazz samples loops"
  → Specific genre Madlib uses often

Tier 3 (Acceptable - Use for breadth):
✓ "vintage soul breaks drum kit"
  → Broader, still relevant
```

**Validation checklist:**
- [ ] Each query has 2-4 core terms (not too simple, not overloaded)
- [ ] Queries include "samples", "pack", "loops", or "breaks"
- [ ] No duplicate queries (check for semantic overlap)
- [ ] Queries represent different angles on the same intent
- [ ] Terms are commonly used (not overly technical jargon)
- [ ] No queries that would return beats/songs instead of samples

**Remove redundancy:**
```
Before:
1. "jazz samples vintage"
2. "vintage jazz samples"  ← Same as #1, remove
3. "old jazz samples"      ← Similar to #1, remove
4. "jazz sample pack"      ← Keep, different angle

After:
1. "jazz samples vintage"
2. "jazz sample pack"
```

## Output Format

Return 5-8 queries, ranked by expected effectiveness:

```json
{
  "queries": [
    "primary query most likely to succeed",
    "secondary query with different angle",
    "tertiary query for breadth",
    ...
  ],
  "reasoning": "Brief explanation of query strategy"
}
```

## Common Pitfalls to Avoid

❌ **Being too literal**
```
Bad: User says "I need those dusty breaks"
     → Query: "dusty breaks"
Good: → Query: "vintage drum breaks lo-fi dusty"
```

❌ **Ignoring platform context**
```
Bad: "drum samples -trap -edm" (negation doesn't work)
Good: "boom bap drum samples 90s"
```

❌ **Overloading with adjectives**
```
Bad: "dark moody atmospheric cinematic ambient electronic samples"
Good: "dark ambient electronic samples" OR "cinematic atmospheric samples"
```

❌ **Missing sample indicators**
```
Bad: "jazz 70s vinyl"
Good: "jazz samples 70s vinyl"
```

❌ **Too technical/academic**
```
Bad: "modal jazz samples with lydian dominant harmony"
Good: "jazz samples modal 60s"
```

❌ **Redundant queries**
```
Bad: ["jazz samples", "samples jazz", "jazz sample pack", "sample pack jazz"]
Good: ["jazz samples vintage", "jazz sample pack WAV"]
```

## Example Complete Query Generation

**User Input:** "Find me some of that Flying Lotus experimental electronic sound"

**STEP 1: Decode Intent**
```
Flying Lotus = Experimental electronic producer, jazz-influenced, abstract beats
Known for: Layered textures, glitchy sounds, jazz fusion, electronic experimentation
Era aesthetic: 2000s-2010s electronic, but uses vintage synths and samples
BPM range: Variable, often 80-110 BPM or half-time feels
Characteristics: Complex, textured, unpredictable, sophisticated

Musical context:
- Electronic + jazz fusion
- Experimental/IDM/beat music genre
- Textural emphasis (not just rhythmic)
- Vintage synths + modern production
- Glitch elements + smooth jazz
```

**STEP 2: Core Terms**
```
Genre/Style: electronic, jazz, experimental, IDM, glitch, abstract beats
Era: modern but vintage-influenced, 2000s, synthesizer
Texture: glitchy, textured, layered, complex, lo-fi-meets-hi-fi
Technical: samples, loops, synth, electronic
```

**STEP 3: Build Queries**
```
Using query formulas:

[Artist Reference] + [Type]:
→ "Flying Lotus style sample pack"

[Genre Fusion] + [Texture] + [Type]:
→ "experimental electronic jazz samples"

[Style] + [Era Tech] + [Type]:
→ "glitch samples vintage synth loops"

[Mood] + [Genre] + [Type]:
→ "abstract electronic samples textured"

[Genre] + [Specific Element] + [Type]:
→ "jazz fusion electronic drum samples"

[Style Descriptor] + [Type]:
→ "IDM samples experimental beats"

[Texture] + [Genre] + [Type]:
→ "layered electronic loops sample pack"
```

**STEP 4: Prioritize and Validate**
```
Ranking:

Tier 1 (Best):
1. "Flying Lotus style sample pack"
   → Direct reference, clear intent

2. "experimental electronic jazz samples"
   → Captures genre fusion clearly

3. "glitch samples vintage synth loops"
   → Specific textures FlyLo uses

Tier 2 (Good):
4. "abstract electronic samples textured"
   → Mood + texture emphasis

5. "IDM samples experimental beats"
   → Genre-specific

Tier 3 (Breadth):
6. "jazz fusion electronic drum samples"
   → Rhythmic focus

7. "layered electronic loops sample pack"
   → Texture emphasis

Validation:
✓ All queries 3-5 terms (good specificity)
✓ All include "samples", "loops", or "pack"
✓ No duplicates
✓ Cover different angles (reference, genre, texture, mood)
✓ Use common terms (no jargon)
```

**Output:**
```json
{
  "queries": [
    "Flying Lotus style sample pack",
    "experimental electronic jazz samples",
    "glitch samples vintage synth loops",
    "abstract electronic samples textured",
    "IDM samples experimental beats",
    "jazz fusion electronic drum samples",
    "layered electronic loops sample pack"
  ],
  "reasoning": "Queries balance direct artist reference with genre fusion and textural descriptors. Covers FlyLo's experimental electronic + jazz aesthetic while using discoverable YouTube search terms."
}
```

## Using This Protocol

1. **Always start with user intent decoding**
2. **Generate core terms before building queries**
3. **Use query formulas as templates, not rigid rules**
4. **Prioritize queries by effectiveness**
5. **Validate against platform optimization rules**
6. **Return 5-8 queries minimum for variety**

This thinking process ensures search queries that actually find relevant, high-quality samples on YouTube while capturing the nuances of musical intent.
