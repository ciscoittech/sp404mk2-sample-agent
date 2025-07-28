# Create Sample Workspace Command

**Command**: `/create-sample-workspace {issue-number} [title]`

Creates a organized workspace for sample collection, curation, and review for a specific GitHub issue.

## Usage

```bash
/create-sample-workspace 123
/create-sample-workspace 123 "jazz-drums"
```

## Implementation

You are a Music Production specialist helping create organized sample collection environments. When this command is executed:

### Phase 1: Preparation
1. **Fetch latest collection requirements from GitHub issue**
2. **Verify issue exists and extract genre/style info**
3. **Check for existing workspace for this collection**
4. **Analyze requirements to determine folder structure**

### Phase 2: Workspace Creation
1. **Generate workspace name**: `samples/task-{number}-{slugified-title}/`
2. **Create organized directory structure based on sample type**
3. **Initialize metadata tracking files**
4. **Set up review queue directories**

### Phase 3: Environment Setup
1. **Create workspace configuration file**
2. **Initialize sample database entries**
3. **Set up preview generation scripts**
4. **Create initial collection scratchpad**
5. **Verify audio tools are available**

### Phase 4: Documentation
1. **Create README with collection guidelines**
2. **Document folder structure and naming conventions**
3. **Set up specialist review templates**
4. **Initialize quality tracking metrics**

## Expected Directory Structure

### For Drum Collections:
```
samples/task-123-jazz-drums/
├── README.md                      # Collection overview
├── metadata.json                  # Collection metadata
├── config/
│   ├── workspace.json            # Workspace settings
│   └── specialists.json          # Assigned specialists
├── raw/                          # Original downloads
│   ├── youtube/
│   ├── archive.org/
│   └── direct/
├── processed/                    # Analyzed samples
│   ├── drums/
│   │   ├── kicks/
│   │   │   ├── acoustic/
│   │   │   └── electronic/
│   │   ├── snares/
│   │   │   ├── rimshots/
│   │   │   └── standard/
│   │   ├── hats/
│   │   │   ├── closed/
│   │   │   └── open/
│   │   ├── cymbals/
│   │   │   ├── crashes/
│   │   │   └── rides/
│   │   └── percussion/
│   │       ├── congas/
│   │       └── tambourines/
│   └── _metadata/
│       └── bpm_analysis.json
├── review_queue/                 # Pending approval
│   ├── high_priority/
│   ├── standard/
│   └── experimental/
├── approved/                     # Human-approved
│   └── [mirrors processed structure]
├── rejected/                     # Failed quality checks
│   └── [samples with issues]
├── specialist_reviews/           # Expert assessments
│   ├── music_historian/
│   ├── sound_engineer/
│   └── dj_beatmaker/
└── exports/                      # SP404MK2-ready
    ├── kits/
    └── banks/
```

### For Melodic Collections:
```
samples/task-124-soul-keys/
├── processed/
│   ├── keys/
│   │   ├── rhodes/
│   │   │   ├── clean/
│   │   │   └── effects/
│   │   ├── wurlitzer/
│   │   ├── piano/
│   │   │   ├── grand/
│   │   │   └── upright/
│   │   └── organ/
│   │       ├── hammond/
│   │       └── farfisa/
│   └── _metadata/
│       ├── key_analysis.json
│       └── chord_detection.json
```

### For Vocal Collections:
```
samples/task-125-vocal-chops/
├── processed/
│   ├── vocals/
│   │   ├── phrases/
│   │   │   ├── verses/
│   │   │   └── hooks/
│   │   ├── chops/
│   │   │   ├── single_words/
│   │   │   └── short_phrases/
│   │   ├── adlibs/
│   │   └── harmonies/
│   └── _metadata/
│       ├── lyric_transcription.json
│       └── pitch_analysis.json
```

## Workspace Configuration Files

### workspace.json:
```json
{
  "workspace_id": "task-123-jazz-drums",
  "issue_number": 123,
  "created_date": "2024-01-27",
  "genre": ["jazz", "hard-bop"],
  "era": "1960s",
  "target_count": 50,
  "quality_threshold": 7.0,
  "specialists": ["music_historian", "dj_beatmaker", "sound_engineer"],
  "file_naming": {
    "pattern": "{category}_{description}_{bpm}BPM_{key}.wav",
    "example": "kick_vintage_blue_note_97BPM_Am.wav"
  },
  "technical_specs": {
    "format": "WAV",
    "sample_rate": 44100,
    "bit_depth": 24,
    "normalization": -6.0
  }
}
```

### specialists.json:
```json
{
  "assigned_specialists": [
    {
      "role": "music_historian",
      "focus": "Verify authentic 1960s hard bop characteristics",
      "checklist": [
        "Era-appropriate recording techniques",
        "Correct instrumentation",
        "Historical context accuracy"
      ]
    },
    {
      "role": "dj_beatmaker",
      "focus": "Assess chopping potential and groove",
      "checklist": [
        "Clean loop points",
        "Consistent timing",
        "Mix compatibility"
      ]
    },
    {
      "role": "sound_engineer",
      "focus": "Technical quality and SP404MK2 optimization",
      "checklist": [
        "Proper gain staging",
        "Frequency balance",
        "No unwanted artifacts"
      ]
    }
  ]
}
```

## Sample Naming Conventions

### Drum Samples:
```
{instrument}_{character}_{source}_{bpm}BPM.wav

Examples:
kick_punchy_vinyl_95BPM.wav
snare_crispy_live_102BPM.wav
hat_tight_studio_98BPM.wav
```

### Melodic Samples:
```
{instrument}_{type}_{key}_{bpm}BPM_{bars}.wav

Examples:
rhodes_chord_Cmaj7_85BPM_4bar.wav
piano_riff_Am_92BPM_8bar.wav
organ_sustained_F_120BPM_2bar.wav
```

### Vocal Samples:
```
vocal_{type}_{gender}_{key}_{bpm}BPM.wav

Examples:
vocal_phrase_female_C_90BPM.wav
vocal_chop_male_Am_85BPM.wav
vocal_adlib_neutral_95BPM.wav
```

## Metadata Tracking

### Sample Metadata Structure:
```json
{
  "file_name": "kick_vintage_blue_note_97BPM_Am.wav",
  "file_path": "processed/drums/kicks/acoustic/",
  "source": {
    "url": "https://youtube.com/watch?v=...",
    "title": "Art Blakey - Moanin'",
    "timestamp": "2:34-2:36"
  },
  "technical": {
    "duration": 0.8,
    "bpm": 97,
    "key": "Am",
    "peak_db": -3.2,
    "rms_db": -12.5
  },
  "musical": {
    "instrument": "kick",
    "genre": "jazz",
    "era": "1960s",
    "character": "vintage, warm, punchy"
  },
  "analysis": {
    "quality_score": 8.5,
    "specialist_scores": {
      "music_historian": 9.0,
      "dj_beatmaker": 8.0,
      "sound_engineer": 8.5
    }
  },
  "status": "review_queue",
  "created_date": "2024-01-27T10:30:00Z"
}
```

## Review Queue Organization

### Priority Levels:
1. **High Priority**: Rare/unique samples, perfect quality
2. **Standard**: Good quality, useful samples
3. **Experimental**: Interesting but needs work

### Review Interface Files:
```
review_queue/
├── index.html              # Visual review interface
├── playlist.m3u           # Ordered listening playlist
├── review_log.json        # Review decisions
└── samples/
    ├── high_priority/
    │   └── [samples with preview.json]
    ├── standard/
    │   └── [samples with preview.json]
    └── experimental/
        └── [samples with preview.json]
```

### Preview JSON:
```json
{
  "sample": "kick_vintage_97BPM.wav",
  "preview_image": "kick_vintage_97BPM.png",
  "specialist_notes": {
    "music_historian": "Authentic 1964 Blue Note sound",
    "dj_beatmaker": "Perfect for boom-bap beats",
    "sound_engineer": "May need slight high-pass filter"
  },
  "suggested_uses": [
    "Main kick for jazz-influenced hip-hop",
    "Layer with modern 808 for hybrid sound"
  ],
  "similar_samples": ["kick_bluenote_95BPM.wav", "kick_prestige_98BPM.wav"]
}
```

## Scratchpad Template

```markdown
# Sample Workspace: Task #{number} - {title}

## Collection Overview
- **Issue**: #{number}
- **Title**: {title}
- **Genre**: {genre}
- **Target**: {target_count} samples
- **Created**: {date}

## Workspace Structure
{directory_tree}

## Naming Convention
Pattern: `{naming_pattern}`
Example: `{naming_example}`

## Specialist Guidelines

### {Specialist_1}:
Focus: {specialist_focus}
Checklist:
- [ ] {checkpoint_1}
- [ ] {checkpoint_2}
- [ ] {checkpoint_3}

### {Specialist_2}:
Focus: {specialist_focus}
Checklist:
- [ ] {checkpoint_1}
- [ ] {checkpoint_2}
- [ ] {checkpoint_3}

## Quality Standards
- Minimum quality score: {threshold}/10
- Required specialist approval: {min_specialists}
- Technical requirements: {tech_specs}

## Collection Progress
- [ ] Workspace initialized
- [ ] Folder structure created
- [ ] Metadata tracking ready
- [ ] Review queue set up
- [ ] Specialist templates created

## Quick Commands
- Start collection: `/process-sample-task {number}`
- Check status: `/list-sample-tasks`
- Begin review: `/review-samples {number}`
```

## Error Handling

### Common Issues:
1. **Insufficient disk space**: Check available space before creation
2. **Permission errors**: Ensure write access to samples directory
3. **Missing dependencies**: Verify audio tools installed
4. **Corrupt metadata**: Provide recovery/rebuild option

### Recovery Commands:
```bash
# If workspace creation fails
rm -rf samples/task-{number}-*
/create-sample-workspace {number} --force

# If metadata corrupted
/rebuild-workspace-metadata {number}

# If structure needs updating
/migrate-workspace-structure {number}
```

## Integration Features

### Automatic Services:
1. **File watching**: Monitor for new samples
2. **Preview generation**: Auto-create waveforms
3. **Metadata extraction**: Parse from filenames
4. **Quality checks**: Validate on addition

### Database Sync:
```python
# Automatically register workspace in database
def register_workspace(workspace_path, issue_number):
    db.execute("""
        INSERT INTO workspaces 
        (path, issue_number, created_date, status)
        VALUES (?, ?, ?, 'active')
    """, [workspace_path, issue_number, datetime.now()])
```

## Success Criteria

The command is successful when:
1. ✅ Complete directory structure created
2. ✅ Configuration files initialized
3. ✅ Metadata tracking operational
4. ✅ Review queue directories ready
5. ✅ Specialist templates created
6. ✅ Naming conventions documented
7. ✅ Scratchpad with guidelines created
8. ✅ Database entries registered
9. ✅ Preview generation configured
10. ✅ Ready for sample collection

## Next Steps

After successful workspace creation:
1. **Begin collection**: `/process-sample-task {number}`
2. **Monitor progress**: Check scratchpad for updates
3. **Review samples**: Use review queue interface
4. **Export to SP404MK2**: When collection complete