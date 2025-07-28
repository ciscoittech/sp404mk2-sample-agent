# Create Sample Task Command

**Command**: `/create-sample-task {title} [description]`

AI-powered GitHub issue creation for sample collection tasks with intelligent specialist assignment and collection strategy planning.

## Usage

```bash
/create-sample-task "Jazz drum breaks from Blue Note Records"
/create-sample-task "Vintage Rhodes sounds" "Need warm, soulful electric piano samples from 1970s recordings"
/create-sample-task "Lo-fi hip hop vocal chops" "Female jazz vocals suitable for chopping, 85-95 BPM"
```

## Implementation

You are an AI-powered music production analyst that creates comprehensive sample collection tasks. When this command is executed:

### Phase 1: Requirements Analysis
1. **Parse title and description** for musical requirements
2. **Identify sample category** (drums, keys, vocals, bass, etc.)
3. **Determine genre and era** (Jazz, Soul, Hip-Hop, etc.)
4. **Estimate collection complexity** (simple, moderate, complex)
5. **Extract technical specifications** (BPM, key, format)

### Phase 2: AI-Powered Music Analysis

#### Complexity Assessment Prompt:
```
Analyze this sample collection request for SP404MK2:

Title: {title}
Description: {description}

Assess:
1. Collection difficulty (1-10 scale)
2. Estimated samples to review
3. Source availability (YouTube, direct, rare)
4. Legal/copyright considerations
5. Audio quality requirements

Focus on practical, achievable collections.
```

#### Music Specialist Selection Prompt:
```
Based on this sample collection request, determine the optimal specialist chain:

Title: {title}
Description: {description}

Available Music Specialists:
- Music Historian: Genre history, era authenticity, cultural context
- Sound Engineer: Audio quality, frequency analysis, mastering specs
- Keyboard Player: Musical theory, chord progressions, playing techniques
- DJ/Beatmaker: BPM analysis, loop points, chopping potential
- Crate Digger: Rare finds, sample sources, clearance knowledge
- Genre Expert: Deep knowledge of specific musical styles

Select 2-4 specialists and explain their role in this collection.
```

#### Label Suggestion Prompt:
```
Suggest appropriate GitHub labels for this sample task:

Title: {title}
Description: {description}

Available labels:
- Type: samples, preset, pattern, workflow
- Genre: jazz, soul, hip-hop, electronic, funk, rock, world
- Instrument: drums, keys, bass, vocals, percussion, strings
- Era: vintage, modern, 60s, 70s, 80s, 90s, 00s
- Difficulty: easy-find, moderate-find, rare-find
- Priority: urgent, high-priority, low-priority

Select 3-5 most relevant labels.
```

### Phase 3: Collection Strategy Planning

#### Source Identification:
```
Identify potential sources for these samples:

Requirements: {parsed_requirements}

Consider:
1. YouTube channels/playlists
2. Archive.org collections
3. Specific record labels
4. Live performance recordings
5. Direct artist sources

Prioritize legally accessible sources.
```

#### Sample Specifications:
```
Define technical specifications for collection:

1. Audio format requirements (WAV, MP3, etc.)
2. Sample rate and bit depth
3. BPM range (if applicable)
4. Key/scale preferences
5. Length requirements (one-shots vs loops)
6. Processing preferences (raw vs processed)

Align with SP404MK2 capabilities.
```

### Phase 4: GitHub Issue Creation

#### Issue Template Population:
```markdown
# {title}

## Description
{ai_enhanced_description}

## Music Analysis
**Genre/Style**: {identified_genre}
**Era**: {time_period}
**Complexity**: {complexity_score}/10
**Estimated Samples**: {sample_count}

## Technical Requirements
- **Format**: {audio_format}
- **BPM Range**: {bpm_range}
- **Key/Scale**: {musical_key}
- **Length**: {sample_length}
- **Quality**: {quality_specs}

## Specialist Chain Recommendation
{recommended_specialists}

### Specialist Roles:
{specialist_role_breakdown}

## Collection Strategy
{ai_generated_collection_plan}

## Potential Sources
{identified_sources}

## Legal Considerations
{copyright_notes}

## Review Criteria
- [ ] Audio quality meets specifications
- [ ] BPM accuracy (±2 BPM tolerance)
- [ ] Clean samples (no clipping/artifacts)
- [ ] Appropriate length for SP404MK2
- [ ] Musical usefulness verified
- [ ] Metadata properly tagged

## Agent Workflow
1. **Collector Agent**: Search and validate sources
2. **Downloader Agent**: Retrieve samples
3. **Analyzer Agent**: Process and tag audio
4. **{specialist_1}**: {specialist_1_task}
5. **{specialist_2}**: {specialist_2_task}
6. **Reporter Agent**: Create review queue

## Definition of Done
- [ ] All samples collected and analyzed
- [ ] BPM detection completed
- [ ] Samples organized by category
- [ ] Review queue populated
- [ ] Specialist evaluations complete
- [ ] Human review ready

## MVP Scope
{mvp_boundaries}

## Future Enhancements
{advanced_features}
```

## Music Specialist Profiles

### Music Historian
**Expertise**: Genre evolution, cultural context, era authenticity
**Tasks**:
- Verify historical accuracy of samples
- Provide context for sample selection
- Identify influential artists/albums
- Ensure cultural sensitivity

### Sound Engineer
**Expertise**: Audio quality, frequency analysis, technical specs
**Tasks**:
- Assess audio fidelity
- Recommend processing techniques
- Identify technical issues
- Optimize for SP404MK2 playback

### Keyboard Player
**Expertise**: Musical theory, chord progressions, performance
**Tasks**:
- Identify key musical elements
- Assess harmonic content
- Evaluate playability
- Suggest musical applications

### DJ/Beatmaker
**Expertise**: BPM matching, loop points, sample chopping
**Tasks**:
- Verify BPM accuracy
- Identify optimal chop points
- Assess groove and timing
- Test mix compatibility

### Crate Digger
**Expertise**: Rare samples, obscure sources, sampling culture
**Tasks**:
- Locate hard-to-find samples
- Verify sample clearance status
- Share sampling history
- Recommend deep cuts

### Genre Expert
**Expertise**: Deep knowledge of specific musical styles
**Tasks**:
- Authenticate genre characteristics
- Identify sub-genre variations
- Recommend essential samples
- Provide style guidelines

## AI Analysis Examples

### Example 1: Simple Drum Collection
```
Input: "Basic hip-hop drum kit"
Analysis:
- Complexity: 3/10 (Common samples)
- Specialists: DJ/Beatmaker + Sound Engineer
- Sources: Classic break compilations
- MVP: 20 essential drums (kick, snare, hat)
```

### Example 2: Complex Jazz Collection
```
Input: "Rare 1960s hard bop horn sections for sampling"
Analysis:
- Complexity: 8/10 (Rare recordings)
- Specialists: Music Historian + Crate Digger + Sound Engineer + Genre Expert (Jazz)
- Sources: Blue Note archives, rare vinyl rips
- Challenge: "Start with well-known recordings before pursuing rare ones"
```

### Example 3: Vintage Keyboard Sounds
```
Input: "Fender Rhodes sounds from soul records"
Analysis:
- Complexity: 5/10 (Specific but findable)
- Specialists: Keyboard Player + Genre Expert (Soul) + Sound Engineer
- Sources: Motown, Stax, Philadelphia International
- MVP: 10 classic Rhodes patches with effects
```

## Sample Organization Structure

### Proposed Directory Layout:
```
review_queue/
└── task-{issue_number}/
    ├── metadata.json
    ├── specialist_reviews/
    │   ├── music_historian.md
    │   ├── sound_engineer.md
    │   └── {other_specialists}.md
    ├── raw_samples/
    │   └── [original downloads]
    ├── processed/
    │   ├── drums/
    │   ├── keys/
    │   ├── bass/
    │   └── vocals/
    └── approved/
        └── [human-approved samples]
```

## Quality Assurance

### Sample Quality Checklist:
- ✅ Proper gain staging (no clipping)
- ✅ Consistent file naming
- ✅ Accurate BPM tagging
- ✅ Key detection (when applicable)
- ✅ Loop points verified
- ✅ Metadata complete
- ✅ Specialist approval obtained
- ✅ Legal status documented

### Automated Validation:
```python
def validate_sample(file_path):
    checks = {
        'format': check_audio_format(file_path),
        'quality': analyze_audio_quality(file_path),
        'bpm': detect_and_verify_bpm(file_path),
        'length': check_sample_length(file_path),
        'metadata': verify_metadata_tags(file_path)
    }
    return all(checks.values())
```

## Integration with Agent System

### Post-Creation Actions:
After creating the issue:

1. **Initialize collection workspace**
2. **Assign to agent queue**
3. **Create initial scratchpad**:
   ```
   ✅ Issue #{issue_number} created successfully!
   
   Next steps:
   • /create-sample-workspace {issue_number} - Set up collection space
   • /process-sample-task {issue_number} - Start automated collection
   • Review issue on GitHub for refinements
   ```

### Agent Coordination:
```python
# Automatic agent assignment based on complexity
if complexity_score <= 3:
    agents = ['collector', 'downloader', 'analyzer']
elif complexity_score <= 6:
    agents = ['collector', 'downloader', 'analyzer', 'specialist_review']
else:
    agents = ['full_chain']  # All agents + human oversight
```

## Error Handling

### Common Issues:
1. **Vague requirements**: Request more specific details
2. **Unrealistic scope**: Suggest MVP approach
3. **Copyright concerns**: Flag and provide alternatives
4. **Technical limitations**: Explain SP404MK2 constraints
5. **Source unavailability**: Suggest alternative sources

### Recovery Strategies:
```bash
# If issue creation fails
echo "⚠️ Issue creation failed. Saving locally..."
echo "$issue_content" > "pending-tasks/sample-task-$(date +%s).md"
echo "Run /sync-pending-tasks when online"
```

## Success Criteria

The command is successful when:
1. ✅ Musical requirements clearly understood
2. ✅ Appropriate specialists assigned
3. ✅ Realistic collection scope defined
4. ✅ Sources identified and verified
5. ✅ Technical specifications documented
6. ✅ GitHub issue created with all metadata
7. ✅ Agent workflow ready to execute
8. ✅ Review process clearly defined

## Configuration

### AI Model Settings:
```python
AI_CONFIG = {
    'model': 'google/gemini-flash-1.5',  # Fast, music-aware
    'temperature': 0.3,  # Consistent analysis
    'max_tokens': 2000,  # Detailed responses
    'timeout': 30000    # 30 second timeout
}
```

### Music-Specific Templates:
Store templates in `/templates/sample-types/`:
- `drum-kit.md`
- `melodic-loops.md`
- `vocal-chops.md`
- `bass-lines.md`
- `full-tracks.md`