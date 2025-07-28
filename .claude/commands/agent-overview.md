# SP404MK2 Sample Agent System Overview

**Command**: `/agent-overview`

You are the SP404MK2 Sample Agent system architect. This command provides a comprehensive overview of all agent capabilities and how they work together.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Conversational CLI Interface               │
│                    (Natural Language Input)                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      Agent Orchestra                         │
├─────────────────┴───────────────────────────────────────────┤
│  Discovery          Analysis           Organization          │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐          │
│  │Collector│       │ Groove  │       │Organizer│          │
│  │  Agent  │       │ Analyst │       │  Agent  │          │
│  └─────────┘       └─────────┘       └─────────┘          │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐          │
│  │Downloader│      │   Era   │       │   SP404 │          │
│  │  Agent  │       │ Expert  │       │Templates│          │
│  └─────────┘       └─────────┘       └─────────┘          │
│                    ┌─────────┐                              │
│                    │Relation │                              │
│                    │  Agent  │                              │
│                    └─────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

## Agent Capabilities

### 1. Conversational CLI (`sp404_chat.py`)
**Purpose**: Natural language interface for sample discovery
**Key Features**:
- Understands musical requests in plain English
- Integrates with all other agents automatically
- Streaming responses via OpenRouter (Gemma-2-27B)
- Executes searches based on detected intent

**Example Interactions**:
```
> "Find me some Dilla-style drums"
> "I need jazz piano loops from the 70s around 85 BPM"
> "Show me boom bap drums that would work with this soul sample"
```

### 2. Collector Agent + YouTube Discovery
**Purpose**: Intelligent sample discovery from YouTube
**Enhanced Features**:
- Quality scoring system (views, duration, channel reputation)
- Era-specific search term generation
- Producer style searches
- Filters out tutorials and non-sample content

**Quality Factors**:
- High view count (100k+) = Higher score
- Optimal duration (30s-5min) = Better for samples
- Music/producer channels = Prioritized
- Title keywords ("sample pack", "drum kit") = Boosted

### 3. Downloader Agent + Timestamp Extraction
**Purpose**: Precise sample extraction from sources
**Key Features**:
- YouTube video downloading via yt-dlp
- Timestamp-based segment extraction
- Fire emoji (🔥) quality detection
- Automatic format conversion
- Batch processing support

**Timestamp Formats Supported**:
- `0:45` - Simple minute:second
- `1:23:45` - Hour:minute:second
- `0:30 - 0:45` - Range extraction
- `0:30 kick pattern 🔥🔥🔥` - With descriptions

### 4. Groove Analyst Agent
**Purpose**: Deep rhythm and timing analysis
**Capabilities**:
- BPM detection with confidence scoring
- Swing percentage calculation (50-80%)
- Groove type classification
- Artist similarity matching
- Micro-timing analysis

**Artist References**:
- J Dilla: 62-68% swing, "drunk" timing
- Questlove: 58-65% swing, behind-the-beat
- 9th Wonder: 55-62% swing, snare emphasis
- Metro Boomin: 50-53% swing, trap precision

### 5. Era Expert Agent
**Purpose**: Musical production history analysis
**Features**:
- Automatic era detection from audio
- Equipment and technique database
- Genre-specific knowledge
- Modern recreation tips
- Search query enhancement

**Era Database**:
- 1950s-1960s: Tape machines, live recording
- 1970s: Analog consoles, funk/soul golden age
- 1980s: Digital revolution, gated reverbs
- 1990s: Sampling era, MPC dominance
- 2000s+: DAW production, loudness war

### 6. Sample Relationship Agent
**Purpose**: Musical compatibility analysis
**Analysis Types**:
- **Harmonic**: Key relationships, interval scoring
- **Rhythmic**: BPM matching, groove alignment
- **Frequency**: Spectral overlap, masking detection
- **Energy**: Dynamic level compatibility

**Compatibility Scoring**:
- 8-10: Excellent - use immediately
- 6-8: Good - minor adjustments
- 4-6: Moderate - careful arrangement
- 0-4: Poor - consider alternatives

### 7. Intelligent Organizer
**Purpose**: Smart sample library management
**Organization Strategies**:

1. **Musical Properties**
   ```
   drums/medium_70-90/Cmaj/
   bass/slow_60-70/Amin/
   ```

2. **Genre/Era**
   ```
   hip_hop/1990s/
   soul/1970s/
   ```

3. **Groove Style**
   ```
   boom_bap/heavy_swing/
   trap/straight/
   ```

4. **Compatibility Groups**
   ```
   compatible_group_1/
   compatible_group_2/
   ```

5. **SP-404 Banks**
   ```
   SP404_Bank_A/
   SP404_Bank_B/
   ```

6. **Project-Specific**
   ```
   beat_making/drums/
   live_looping/4bar_loops/
   ```

## Workflow Examples

### Complete Sample Discovery Workflow
1. User enters natural language request
2. Conversational CLI interprets intent
3. Collector Agent searches YouTube with enhanced queries
4. Downloader extracts samples (with timestamps if provided)
5. Groove Analyst examines rhythm characteristics
6. Era Expert identifies production period
7. Sample Relationship checks compatibility
8. Intelligent Organizer files samples appropriately

### Kit Building Workflow
1. Analyze existing samples for compatibility
2. Group highly compatible samples (7+ score)
3. Organize into SP-404 banks
4. Generate kit documentation

### Genre Research Workflow
1. Use Era Expert to identify target era
2. Generate era-specific search queries
3. Collect period-appropriate samples
4. Organize by genre/era structure

## Integration Points

### File Naming Convention
```
original_name_[BPM]bpm_[KEY]_[GROOVE].wav
Example: funky_break_95bpm_Amin_boom_bap.wav
```

### Metadata Storage
Each sample gets a `.json` companion file with:
- Original source information
- All analysis results
- Compatibility scores
- Agent processing history

### Command Line Usage
```bash
# Conversational interface
python sp404_chat.py

# Direct agent testing
python test_groove_analyst.py
python test_era_expert.py
python test_sample_relationship.py
python test_intelligent_organizer.py

# Organization
python -m sp404agent organize --strategy [strategy] --dir [path]
```

## Best Practices

1. **Start Simple**: Use conversational interface for discovery
2. **Batch Process**: Analyze multiple samples together
3. **Trust Scores**: High compatibility scores are reliable
4. **Use Templates**: SP-404 templates save time
5. **Regular Organization**: Re-organize as library grows

## Future Enhancements
- Real-time collaboration features
- Cloud storage integration
- Mobile companion app
- MIDI pattern analysis
- AI-powered sample generation

Remember: The system is designed to enhance creativity, not replace it. Use these tools to discover and organize, but trust your ears for final decisions.