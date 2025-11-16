# Create Sample Issue Command

**Command**: `/create-sample-issue {title} [description]`

AI-powered GitHub issue creation for SP404MK2 sample collection and processing tasks with intelligent specialist assignment.

## Usage

```bash
/create-sample-issue "Process Wanns Wavs collection for vibe analysis"
/create-sample-issue "Build jazz kit from YouTube samples" "Need drums, bass, and keys around 90 BPM"
/create-sample-issue "Fix slow batch processing" "500+ samples taking too long to analyze"
```

## Implementation

You are an AI-powered sample project analyst that creates comprehensive GitHub issues. When this command is executed:

### Phase 1: Requirements Analysis
1. **Parse title and description** for task requirements
2. **Identify task type** (collection, analysis, download, organization, etc.)
3. **Estimate complexity** (simple, moderate, complex)
4. **Determine resource needs** (API calls, processing time, storage)
5. **Extract technical specifications** (BPM, format, quantity)

### Phase 2: AI-Powered Analysis

#### Task Type Detection Prompt:
```
Analyze this sample-related task:

Title: {title}
Description: {description}

Identify the primary task type:
1. Collection - Finding and downloading samples
2. Analysis - Processing audio (BPM, key, vibe)
3. Organization - Arranging samples into kits/folders
4. Processing - Batch operations on existing samples
5. Technical - Bug fixes, performance issues
6. Feature - New functionality requests

Also identify secondary tasks involved.
```

#### Complexity Assessment Prompt:
```
Assess the complexity of this sample task:

Title: {title}
Description: {description}
Task Type: {identified_type}

Consider:
1. Technical complexity (1-10 scale)
2. Estimated processing time
3. API/resource requirements
4. Number of samples involved
5. Risk factors

Provide realistic estimates for SP404MK2 workflow.
```

#### Specialist Assignment Prompt:
```
Assign the optimal specialists for this task:

Title: {title}
Task Type: {identified_type}
Complexity: {complexity_score}

Available Specialists:
- Groove Analyst: Rhythm, timing, swing analysis
- Era Expert: Musical history, production techniques
- Vibe Analyst: Mood, texture, emotional qualities
- Sample Compatibility: Musical matching, key/BPM relationships
- Batch Processor: Large collection handling, rate limiting
- Kit Builder: SP-404 bank assembly, pad layout
- Download Manager: YouTube/source acquisition
- Musical Search: Query optimization, source discovery

Recommend 2-4 specialists with specific roles.
```

#### Label Generation Prompt:
```
Suggest GitHub labels for this issue:

Title: {title}
Type: {task_type}
Specialists: {assigned_specialists}

Available labels:
- Type: bug, enhancement, analysis, collection, organization
- Priority: critical, high, medium, low
- Component: youtube, batch, vibe, groove, kit, database
- Status: needs-triage, ready, blocked
- Size: small (1-2hr), medium (1 day), large (1 week)

Select 3-5 relevant labels.
```

### Phase 3: Technical Planning

#### Implementation Strategy:
```
Create implementation plan for:

Title: {title}
Type: {task_type}
Specialists: {specialists}

Include:
1. Agent workflow sequence
2. Resource requirements
3. Processing estimates
4. Output format
5. Success criteria

Focus on SP404MK2 workflow efficiency.
```

### Phase 4: GitHub Issue Creation

#### Issue Template:
```markdown
# {title}

## Task Type
**Primary**: {primary_type}
**Secondary**: {secondary_types}

## Description
{enhanced_description}

## Technical Analysis
**Complexity**: {complexity}/10
**Estimated Time**: {time_estimate}
**Samples Involved**: {sample_count}
**API Requirements**: {api_needs}

## Specialist Assignment
{specialist_assignments}

### Specialist Breakdown:
{specialist_role_details}

## Implementation Plan
{implementation_strategy}

## Resource Requirements
- **Storage**: {storage_estimate}
- **Processing**: {cpu_requirements}
- **API Calls**: {api_estimate}
- **Rate Limits**: {rate_considerations}

## Success Criteria
{success_criteria}

## Definition of Done
- [ ] All samples processed successfully
- [ ] Quality checks passed
- [ ] Metadata properly tagged
- [ ] Results organized per specification
- [ ] Documentation updated
- [ ] Tests passing (if applicable)

## Labels
{assigned_labels}

---
*Created by SP404 Sample Agent System*
```

## Specialist Role Definitions

### Groove Analyst (`/groove-analyst`)
**Triggers**: "drums", "rhythm", "swing", "timing", "groove"
**Responsibilities**:
- BPM detection and verification
- Swing percentage analysis
- Micro-timing evaluation
- Groove style classification

### Era Expert (`/era-expert`)
**Triggers**: "vintage", "70s", "80s", "90s", "era", "old school"
**Responsibilities**:
- Period authentication
- Production technique identification
- Equipment recommendations
- Search query enhancement

### Vibe Analyst (`/vibe-analyst`)
**Triggers**: "mood", "vibe", "feeling", "texture", "atmosphere"
**Responsibilities**:
- Emotional quality assessment
- Genre classification
- Energy level analysis
- Compatibility tagging

### Sample Compatibility (`/sample-compatibility`)
**Triggers**: "match", "compatible", "work together", "kit"
**Responsibilities**:
- Harmonic analysis
- BPM matching
- Frequency compatibility
- Kit cohesion scoring

### Batch Processor (`/batch-processor`)
**Triggers**: "collection", "folder", "batch", "multiple", "500+"
**Responsibilities**:
- Large-scale processing
- Rate limit management
- Progress tracking
- Cache optimization

### Kit Builder (`/kit-builder`)
**Triggers**: "kit", "bank", "SP-404", "pads", "layout"
**Responsibilities**:
- Pad arrangement
- Bank organization
- Performance optimization
- Export formatting

### Download Manager (`/download-manager`)
**Triggers**: "YouTube", "download", "source", "timestamp"
**Responsibilities**:
- Source validation
- Quality optimization
- Timestamp extraction
- Format conversion

### Musical Search (`/musical-search-specialist`)
**Triggers**: "find", "search", "discover", "looking for"
**Responsibilities**:
- Query optimization
- Source identification
- Quality filtering
- Result ranking

## Smart Assignment Logic

```python
def assign_specialists(title, description, task_type):
    specialists = []
    text = f"{title} {description}".lower()
    
    # Primary assignment based on task type
    primary_specialists = {
        "collection": ["musical-search", "download-manager"],
        "analysis": ["vibe-analyst", "groove-analyst"],
        "organization": ["kit-builder", "sample-compatibility"],
        "processing": ["batch-processor"],
        "technical": ["python-ai-architect"],
    }
    
    specialists.extend(primary_specialists.get(task_type, []))
    
    # Secondary assignment based on keywords
    keyword_specialists = {
        "groove|rhythm|drums|swing": "groove-analyst",
        "mood|vibe|feeling|texture": "vibe-analyst",
        "era|vintage|70s|80s|90s": "era-expert",
        "compatible|match|together": "sample-compatibility",
        "batch|collection|folder|many": "batch-processor",
        "kit|bank|sp-404|pads": "kit-builder",
        "youtube|download|source": "download-manager",
        "search|find|discover": "musical-search-specialist"
    }
    
    for pattern, specialist in keyword_specialists.items():
        if re.search(pattern, text) and specialist not in specialists:
            specialists.append(specialist)
    
    # Limit to 4 specialists max
    return specialists[:4]
```

## Examples

### Example 1: Vibe Analysis Task
```
Input: "Analyze Wanns Wavs collection for mood and compatibility"
Analysis:
- Type: Processing/Analysis
- Complexity: 7/10 (500+ samples)
- Specialists: Vibe Analyst, Batch Processor, Sample Compatibility
- Labels: analysis, batch, vibe, large
- Time: 2-3 hours with rate limiting
```

### Example 2: YouTube Collection
```
Input: "Find boom bap drums from 90s YouTube videos"
Analysis:
- Type: Collection
- Complexity: 5/10
- Specialists: Musical Search, Download Manager, Era Expert, Groove Analyst
- Labels: collection, youtube, drums, medium
- Time: 1-2 hours
```

### Example 3: Kit Building
```
Input: "Build SP-404 jazz kit from existing samples"
Analysis:
- Type: Organization
- Complexity: 4/10
- Specialists: Kit Builder, Sample Compatibility, Vibe Analyst
- Labels: organization, kit, jazz, small
- Time: 30-60 minutes
```

## GitHub Integration

### Issue Creation:
```bash
# Use gh CLI for actual creation
gh issue create \
  --repo "bhunt/sp404mk2-sample-agent" \
  --title "$title" \
  --body "$body" \
  --label "$labels"
```

### Parse Issue Number:
```python
import re

def parse_issue_number(gh_output):
    # gh CLI returns: "https://github.com/owner/repo/issues/123"
    match = re.search(r'/issues/(\d+)', gh_output)
    return int(match.group(1)) if match else None
```

### Post-Creation Actions:
```
✅ Issue #{issue_number} created successfully!

Specialists assigned:
{specialist_list}

Next steps:
• Review issue at: {issue_url}
• Run: /process-sample-task {issue_number}
• Or start manually with assigned specialists
```

## Error Handling

### Common Issues:
1. **Vague requirements**: Request specific details
2. **No specialists match**: Suggest manual assignment
3. **Rate limit concerns**: Warn about API limits
4. **Large collections**: Recommend batching strategy
5. **GitHub API errors**: Save locally and retry

### Validation:
```python
def validate_issue(data):
    errors = []
    
    if not data.get('specialists'):
        errors.append("No specialists could be assigned")
    
    if data['complexity'] > 8:
        errors.append("High complexity - consider breaking down")
    
    if data['sample_count'] > 1000:
        errors.append("Very large collection - plan batching")
    
    return errors
```

## Success Criteria

The command succeeds when:
1. ✅ Task type correctly identified
2. ✅ Appropriate specialists assigned
3. ✅ Realistic complexity assessment
4. ✅ Clear implementation plan
5. ✅ GitHub issue created with metadata
6. ✅ Labels accurately reflect task
7. ✅ Next steps clearly communicated

## Configuration

```python
CONFIG = {
    'model': 'google/gemini-2.0-flash-exp',  # Fast, accurate
    'temperature': 0.3,  # Consistent analysis
    'max_tokens': 2000,
    'github_repo': 'bhunt/sp404mk2-sample-agent',
    'max_specialists': 4,
    'complexity_threshold': 8  # Warn above this
}
```