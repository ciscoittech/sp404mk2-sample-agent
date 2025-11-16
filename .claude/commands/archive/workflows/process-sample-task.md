# Process Sample Task Command

**Command**: `/process-sample-task {issue-number}`

Complete AI-assisted sample collection workflow from GitHub issue to curated sample library using music specialist chains and multi-agent orchestration.

## Usage

```bash
/process-sample-task 123
```

## Implementation

You are an AI-powered sample collection orchestrator that coordinates specialist chains and agents to collect, analyze, and curate samples. When this command is executed:

### Phase 1: Task Analysis & Planning
1. **Fetch GitHub issue details** including labels, requirements, and metadata
2. **Analyze sample requirements** using AI to understand musical needs
3. **Determine specialist chain** based on genre, era, and complexity
4. **Create or update workspace** for organized sample collection
5. **Generate comprehensive scratchpad** with collection strategy

### Phase 2: Music Specialist Chain Orchestration
Based on issue labels and requirements, coordinate appropriate specialists:

#### Drums/Percussion Collection (`drums` label):
```
1. Crate Digger → Find authentic break sources
2. DJ/Beatmaker → Identify choppable sections, verify groove
3. Sound Engineer → Ensure punch and clarity
4. Analyzer Agent → BPM detection and classification
5. Reporter Agent → Create review queue
```

#### Melodic Samples (`keys`, `strings`, `brass` labels):
```
1. Music Historian → Verify era authenticity
2. Keyboard Player → Assess musical quality and playability
3. Genre Expert → Confirm style accuracy
4. Sound Engineer → Optimize frequency balance
5. Analyzer Agent → Key detection and tagging
6. Reporter Agent → Organize by key/scale
```

#### Vocal Samples (`vocals` label):
```
1. Genre Expert → Identify style characteristics
2. Crate Digger → Source rare vocal recordings
3. DJ/Beatmaker → Find choppable phrases
4. Sound Engineer → Clean and process
5. Analyzer Agent → Tempo and key analysis
6. Reporter Agent → Categorize by type
```

#### Full Production (`full-track`, `stems` labels):
```
1. Music Historian → Context and clearance info
2. Sound Engineer → Assess mix quality
3. DJ/Beatmaker → Identify usable sections
4. Genre Expert → Style verification
5. Analyzer Agent → Complete analysis
6. Reporter Agent → Detailed documentation
```

### Phase 3: Agent Execution Pipeline

For each specialist in the chain:

#### Discovery Phase (Collector Agent):
```
1. Consult {specialist} for source recommendations
2. Search specified platforms (YouTube, Archive.org, etc.)
3. Validate source availability and quality
4. Create download queue with priorities
```

#### Acquisition Phase (Downloader Agent):
```
1. Download samples in highest available quality
2. Convert to SP404MK2-compatible format
3. Apply initial gain staging
4. Create backup of raw files
```

#### Analysis Phase (Analyzer Agent):
```
1. Detect BPM with specialist verification
2. Analyze key/scale (for melodic content)
3. Measure audio characteristics (RMS, peak, frequency)
4. Generate waveform visualization
5. Create technical metadata
```

#### Curation Phase (Specialist Review):
```
1. Apply specialist-specific evaluation criteria
2. Rate samples on multiple dimensions:
   - Musical quality (1-10)
   - Technical quality (1-10)
   - Usability for SP404MK2 (1-10)
   - Rarity/uniqueness (1-10)
3. Provide usage recommendations
4. Flag any concerns (copyright, quality, etc.)
```

### Phase 4: Quality Control & Organization

#### Cross-Specialist Validation:
```
1. Verify consensus between specialists
2. Resolve conflicting assessments
3. Ensure technical specifications met
4. Validate against original requirements
5. Check for collection completeness
```

#### Sample Organization:
```
samples/
├── task-{issue-number}/
│   ├── approved/
│   │   ├── drums/
│   │   │   ├── kicks/
│   │   │   ├── snares/
│   │   │   └── hats/
│   │   ├── keys/
│   │   │   ├── rhodes/
│   │   │   ├── piano/
│   │   │   └── organ/
│   │   └── vocals/
│   │       ├── chops/
│   │       └── phrases/
│   ├── review_queue/
│   ├── rejected/
│   └── metadata/
```

### Phase 5: Review Queue & Documentation

#### Automated Review Queue Creation:
```
1. Generate sample preview pages
2. Create listening playlist
3. Add specialist assessments
4. Include technical analysis
5. Prepare for human review
```

## Scratchpad Template

The command creates/updates a scratchpad with this structure:

```markdown
# Sample Task #{number}: {title}

## Original Requirements
- **GitHub Issue**: #{number}
- **Genre/Style**: {genres}
- **Era**: {time_period}
- **Complexity**: {complexity}/10
- **Target Count**: {sample_count}

## Specialist Chain Strategy
Active chain: {determined_specialist_chain}

### Specialist Assignments:
1. **{specialist_1}**: {role_description}
2. **{specialist_2}**: {role_description}
3. **{specialist_3}**: {role_description}

## Collection Progress

### Phase 1: Discovery (Collector + {specialist})
- [ ] Sources identified: {source_count}
- [ ] Samples discovered: {discovered_count}
- [ ] Quality pre-screening complete
- [ ] Download queue prepared

### Phase 2: Acquisition (Downloader)
- [ ] Downloads completed: {downloaded}/{total}
- [ ] Format conversion done
- [ ] Initial processing applied
- [ ] Backup created

### Phase 3: Analysis (Analyzer + Specialists)
- [ ] BPM detection: {completed}/{total}
- [ ] Key analysis: {completed}/{total}
- [ ] Quality assessment complete
- [ ] Specialist reviews: {reviewed}/{total}

### Phase 4: Curation (All Specialists)
- [ ] Musical quality verified
- [ ] Technical standards met
- [ ] Usability confirmed
- [ ] Organization complete

### Phase 5: Review Queue (Reporter)
- [ ] Preview pages generated
- [ ] Metadata documented
- [ ] Playlist created
- [ ] Ready for human review

## Specialist Assessments

### {Specialist_1} Evaluation:
{detailed_assessment}

### {Specialist_2} Evaluation:
{detailed_assessment}

## Technical Metrics
- **Total Samples**: {count}
- **Average Quality**: {score}/10
- **BPM Range**: {min}-{max}
- **Key Distribution**: {key_stats}
- **File Sizes**: {size_summary}

## Review Queue Status
- **Approved**: {approved_count}
- **Pending**: {pending_count}
- **Rejected**: {rejected_count}

## Next Steps
{recommended_actions}
```

## AI-Powered Coordination Prompts

### Sample Discovery Prompt:
```
As {specialist_name}, analyze these requirements for sample discovery:

Genre: {genre}
Era: {era}
Specific needs: {requirements}

Recommend:
1. Top 5 sources to explore
2. Search terms and filters
3. Quality indicators to look for
4. Red flags to avoid
5. Expected sample yield

Focus on SP404MK2 usability and creative potential.
```

### Quality Assessment Prompt:
```
As {specialist_name}, evaluate this sample:

File: {filename}
Genre: {detected_genre}
BPM: {detected_bpm}
Key: {detected_key}
Technical specs: {audio_analysis}

Rate on:
1. Musical quality (1-10)
2. Technical quality (1-10)
3. SP404MK2 suitability (1-10)
4. Creative potential (1-10)

Provide specific usage recommendations.
```

### Specialist Coordination Prompt:
```
Coordinate between specialists for sample collection #{number}:

Current phase: {phase}
Active specialists: {specialists}
Decisions needed: {pending_decisions}

Resolve:
1. Any conflicting assessments
2. Priority order for samples
3. Technical vs musical trade-offs
4. Final recommendations

Ensure all specialists' expertise is utilized.
```

## Progress Monitoring

### Real-Time Status Updates:
```
🎵 Processing Sample Task #123: Jazz drum breaks

✅ Phase 1: Discovery Complete (15 minutes)
   • Music Historian consulted
   • 5 sources identified
   • 47 potential samples found

🔄 Phase 2: Acquisition (In Progress - 20 minutes)
   • Downloader Agent active
   • Downloaded: 31/47 samples
   • Converting to 24-bit WAV
   • Next: Complete remaining downloads

⏳ Phase 3: Analysis (Pending)
⏳ Phase 4: Curation (Pending)
⏳ Phase 5: Review Queue (Pending)

Estimated completion: 45 minutes remaining
```

### Specialist Activity Log:
```
[10:23] 🎓 Music Historian: "Focusing on Blue Note 1964-1967 hard bop era"
[10:31] 🎧 DJ/Beatmaker: "Identified 12 prime break sections"
[10:45] 🔧 Sound Engineer: "Recommending high-pass at 40Hz for all kicks"
[10:52] 🎹 Genre Expert (Jazz): "Confirming authentic hard bop characteristics"
```

## Integration with Existing Commands

### Command Chaining:
```bash
# Automatic progression
/create-sample-workspace 123    # If workspace doesn't exist
↓
/process-sample-task 123       # Full collection workflow
↓
/review-samples 123           # Human curation interface
```

### Parallel Processing:
```bash
# Multiple collections simultaneously
/process-sample-task 123 &     # Jazz drums
/process-sample-task 124 &     # Soul vocals
/list-sample-tasks            # Monitor all active collections
```

## Quality Gates

### Automated Checks:
```python
quality_gates = [
    {
        'name': 'Audio Quality',
        'check': 'verify_audio_specs',
        'requirement': 'pass',
        'criteria': 'No clipping, proper gain'
    },
    {
        'name': 'BPM Accuracy',
        'check': 'verify_bpm_detection',
        'requirement': 'pass',
        'criteria': '±2 BPM tolerance'
    },
    {
        'name': 'Metadata Complete',
        'check': 'verify_metadata',
        'requirement': 'pass',
        'criteria': 'All required fields'
    },
    {
        'name': 'Specialist Approval',
        'check': 'check_specialist_scores',
        'requirement': 'warn',
        'criteria': 'Average score ≥7/10'
    }
]
```

### Collection Metrics:
```
📊 Collection Quality Report - Task #123

Sample Count: 47 collected, 38 approved
Average Quality Score: 8.2/10

Breakdown by Specialist:
- Music Historian: 8.5/10 (authenticity)
- DJ/Beatmaker: 8.0/10 (usability)
- Sound Engineer: 7.9/10 (technical)
- Genre Expert: 8.4/10 (style accuracy)

Top Samples:
1. "BlueNote_DrumBreak_97BPM_Am.wav" - 9.5/10
2. "ArtBlakey_Shuffle_102BPM.wav" - 9.2/10
3. "HoraceSliver_Ride_94BPM.wav" - 9.0/10

Issues Found:
- 3 samples with slight clipping (fixed)
- 2 samples with incorrect BPM tags (corrected)
- 4 samples below quality threshold (rejected)
```

## Success Criteria

The command is successful when:
1. ✅ All requirements from issue analyzed and understood
2. ✅ Appropriate specialist chain executed
3. ✅ Target sample count achieved (±10%)
4. ✅ Average quality score ≥7/10
5. ✅ All samples properly analyzed and tagged
6. ✅ Organized according to musical categories
7. ✅ Review queue populated with previews
8. ✅ Specialist assessments documented
9. ✅ Human review interface ready
10. ✅ Collection metrics reported

## Error Handling & Recovery

### Common Failure Points:
1. **Source unavailable**: Try alternative sources, notify user
2. **Download failures**: Retry with different quality/format
3. **Analysis errors**: Fall back to manual tagging
4. **Specialist conflicts**: Escalate to human decision
5. **Quality below threshold**: Expand search parameters

### Recovery Strategies:
1. **Checkpoint saves**: Resume from last successful phase
2. **Partial completion**: Deliver what's available
3. **Alternative sources**: Automatically try backups
4. **Quality compromise**: Offer lower quality if needed
5. **Manual override**: Allow human intervention

### Error Reporting:
```
❌ Error in Phase 2: Download failures

Issue: 5 samples failed to download
Source: YouTube (copyright claim)
Specialist: Crate Digger recommends alternatives

Recovery options:
1. Try alternative sources (Archive.org)
2. Skip affected samples
3. Manual source entry

Recommendation: Option 1 (estimated 10 min)
```

## Configuration

### Agent Settings:
```python
AGENT_CONFIG = {
    'collector': {
        'model': 'google/gemini-flash-1.5',
        'timeout': 60000,
        'retry_attempts': 3
    },
    'analyzer': {
        'bpm_algorithm': 'madmom',
        'key_detection': 'essentia',
        'quality_threshold': 7.0
    },
    'specialists': {
        'consultation_model': 'anthropic/claude-3-haiku',
        'temperature': 0.3,
        'max_tokens': 1000
    }
}
```

This command orchestrates the complete sample collection workflow, leveraging both AI agents and music specialists to build high-quality sample libraries for the SP404MK2.