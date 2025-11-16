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
│  │Downloader│      │   Era   │       │   Kit   │          │
│  │  Agent  │       │ Expert  │       │ Builder │          │
│  └─────────┘       └─────────┘       └─────────┘          │
│                    ┌─────────┐       ┌─────────┐          │
│                    │  Vibe   │       │ Batch   │          │
│                    │ Analyst │       │Processor│          │
│                    └─────────┘       └─────────┘          │
│                    ┌─────────┐       ┌─────────┐          │
│                    │Relation │       │Reporter │          │
│                    │  Agent  │       │  Agent  │          │
│                    └─────────┘       └─────────┘          │
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

### 7. Vibe Analysis Agent
**Purpose**: Mood, texture, and emotional analysis
**Capabilities**:
- Emotional quality detection (happy, dark, energetic)
- Texture analysis (warm, cold, organic, digital)
- Energy level scoring (1-10 scale)
- Genre-specific vibe characteristics
- Compatibility based on mood

**Analysis Output**:
- Primary/secondary moods
- Best use context (intro, verse, chorus)
- Time of day association
- Seasonal feel

### 8. Batch Processor
**Purpose**: Large-scale collection processing
**Features**:
- Handles 10-10,000+ samples efficiently
- Rate limiting for API calls (5 RPM free tier)
- Smart caching and resume capability
- Progress tracking and ETA estimation
- Local pre-filtering to reduce API calls

**Processing Strategies**:
- Small (10-100): Simple sequential
- Medium (100-500): Batched with cache
- Large (500-5000): Distributed processing
- Massive (5000+): Staged with priorities

### 9. Reporter Agent
**Purpose**: GitHub integration and progress tracking
**Capabilities**:
- Create GitHub issues with specialist assignment
- Update issue status and progress
- Generate review queues with metadata
- Daily summary reports
- Error tracking and auto-issue creation

**Issue Features**:
- AI-enhanced descriptions
- Automatic label assignment
- Specialist recommendations
- Complexity estimation

### 10. Intelligent Organizer
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
7. Vibe Analyst determines mood and texture
8. Sample Relationship checks compatibility
9. Intelligent Organizer files samples appropriately
10. Reporter creates review queue

### Large Collection Processing (e.g., Wanns Wavs)
1. Point Batch Processor at collection folder
2. Local analysis extracts basic features (BPM, duration)
3. Vibe Analyst processes in batches of 5 (rate limited)
4. Results cached for resume capability
5. Compatibility scoring finds matching samples
6. Kit Builder assembles coherent banks
7. Export results for SP-404 import

### GitHub Issue-Driven Workflow
1. Create issue with `/create-sample-issue` command
2. AI analyzes task and assigns specialists
3. Reporter Agent creates GitHub issue
4. Specialists automatically engaged
5. Progress tracked and reported
6. Results attached to issue on completion

### Kit Building Workflow
1. Analyze existing samples for compatibility
2. Vibe Analyst groups by mood/energy
3. Sample Relationship scores combinations
4. Kit Builder creates optimal pad layouts
5. Export in SP-404 format with documentation

### Genre Research Workflow
1. Use Era Expert to identify target era
2. Musical Search generates enhanced queries
3. Download Manager handles acquisition
4. Batch process with all analysis agents
5. Organize by genre/era/vibe structure

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

## Specialist System

### Available Specialists
The system includes specialized command modules that provide deep expertise:

1. **Groove Analyst** (`/groove-analyst`) - Rhythm and timing expert
2. **Era Expert** (`/era-expert`) - Musical history and production
3. **Vibe Analyst** (`/vibe-analyst`) - Mood and texture analysis
4. **Sample Compatibility** (`/sample-compatibility`) - Musical matching
5. **Batch Processor** (`/batch-processor`) - Large-scale operations
6. **Kit Builder** (`/kit-builder`) - SP-404 bank assembly
7. **Download Manager** (`/download-manager`) - Source acquisition
8. **Musical Search** (`/musical-search-specialist`) - Query optimization

### Smart Assignment
When creating issues with `/create-sample-issue`, specialists are automatically assigned based on:
- Task type detection (collection, analysis, organization)
- Keyword matching (e.g., "vibe" → Vibe Analyst)
- Complexity assessment
- Required expertise

### Coordination
Specialists work together in chains:
- **Discovery Chain**: Search → Download → Analysis
- **Processing Chain**: Batch → Vibe → Compatibility
- **Organization Chain**: Analysis → Kit Build → Export

## Best Practices

1. **Start Simple**: Use conversational interface for discovery
2. **Batch Process**: Analyze multiple samples together  
3. **Trust Scores**: High compatibility scores are reliable
4. **Use Templates**: SP-404 templates save time
5. **Regular Organization**: Re-organize as library grows
6. **Cache Results**: Avoid re-processing with caching
7. **Issue Tracking**: Use GitHub issues for complex tasks
8. **Specialist Chains**: Let specialists coordinate

## Future Enhancements
- Real-time collaboration features
- Cloud storage integration
- Mobile companion app
- MIDI pattern analysis
- AI-powered sample generation

Remember: The system is designed to enhance creativity, not replace it. Use these tools to discover and organize, but trust your ears for final decisions.