# Process Issue with Smart Specialist Injection

**Command**: `/process-issue-smart {issue_number}`

AI-powered GitHub issue processor that automatically identifies and injects the most appropriate specialist(s) based on issue content, labels, and technical requirements.

## Specialist Mapping

### Automatic Specialist Selection
```yaml
issue_patterns:
  groove_analyst:
    keywords: ["groove", "rhythm", "swing", "timing", "pocket", "BPM analysis", "beat detection"]
    labels: ["groove", "rhythm-analysis", "audio"]
    files: ["src/agents/groove_analyst.py", "src/tools/audio.py"]
    
  era_expert:
    keywords: ["era", "decade", "vintage", "production", "70s", "80s", "90s", "analog", "equipment"]
    labels: ["era", "production-knowledge", "historical"]
    files: ["src/agents/era_expert.py"]
    
  sample_compatibility:
    keywords: ["compatibility", "harmonic", "key matching", "relationship", "kit building"]
    labels: ["compatibility", "music-theory", "organization"]
    files: ["src/agents/sample_relationship.py"]
    
  python_ai_architect:
    keywords: ["pydantic", "langchain", "turso", "async", "API", "architecture", "agent"]
    labels: ["technical", "architecture", "ai", "agent"]
    files: ["src/agents/", "src/config.py", "pyproject.toml"]
    
  musical_search_specialist:
    keywords: ["search", "query", "discover", "youtube", "find samples", "collection"]
    labels: ["search", "discovery", "samples"]
    files: ["src/agents/collector.py", "src/tools/download.py"]
```

## Implementation

### Phase 1: Issue Analysis
```python
async def analyze_issue(issue_number: int) -> IssueAnalysis:
    """Analyze issue to determine required specialists."""
    
    # Fetch issue details
    issue = await fetch_github_issue(issue_number)
    
    # Extract components
    title = issue.title.lower()
    body = issue.body.lower()
    labels = [label.name for label in issue.labels]
    
    # Analyze content
    required_specialists = []
    confidence_scores = {}
    
    for specialist, patterns in SPECIALIST_PATTERNS.items():
        score = 0
        
        # Check keywords
        for keyword in patterns['keywords']:
            if keyword in title:
                score += 3  # Title matches are stronger
            if keyword in body:
                score += 1
        
        # Check labels
        for label in patterns['labels']:
            if label in labels:
                score += 5  # Label matches are very strong
        
        confidence_scores[specialist] = score
        if score >= 3:  # Threshold for inclusion
            required_specialists.append(specialist)
    
    return IssueAnalysis(
        issue_number=issue_number,
        specialists=required_specialists,
        confidence=confidence_scores,
        primary_specialist=max(confidence_scores, key=confidence_scores.get)
    )
```

### Phase 2: Specialist Injection
```markdown
## Dynamic Specialist Loading

Based on issue #{issue_number}: "{title}"

### Primary Specialist: {primary_specialist}
Loading specialized knowledge for {specialist_description}...

### Supporting Specialists:
{secondary_specialists}

### Activated Capabilities:
- {capability_list}

### Context Awareness:
The following domain knowledge is now active:
{loaded_knowledge_summary}
```

### Phase 3: Execution with Context
```python
async def execute_with_specialists(issue: Issue, specialists: List[str]) -> None:
    """Execute issue with injected specialist knowledge."""
    
    # Load specialist prompts
    specialist_knowledge = {}
    for specialist in specialists:
        with open(f".claude/commands/{specialist}.md") as f:
            specialist_knowledge[specialist] = f.read()
    
    # Create enhanced context
    enhanced_prompt = f"""
    You are now enhanced with the following specialist knowledge:
    
    {chr(10).join([f"### {s.upper()}\n{k}" for s, k in specialist_knowledge.items()])}
    
    Use this specialized knowledge to implement issue #{issue.number}: {issue.title}
    
    Remember to:
    1. Apply domain-specific patterns and best practices
    2. Use appropriate terminology and concepts
    3. Follow the architectural patterns from the specialists
    4. Maintain consistency with the specialist's approach
    """
    
    # Execute with enhanced context
    await process_issue_with_context(issue, enhanced_prompt)
```

## Smart Injection Examples

### Example 1: Groove Analysis Issue
```bash
/process-issue-smart 15
```
**Issue #15**: "Create Groove Analyst Agent for Rhythm Understanding"

**Auto-detected specialists**:
1. **groove-analyst** (primary) - For rhythm analysis algorithms
2. **python-ai-architect** (secondary) - For agent implementation
3. **era-expert** (tertiary) - For historical groove references

**Injected knowledge**:
- Swing quantification formulas
- Pocket detection algorithms  
- Pydantic AI agent patterns
- Famous drummer analysis methods

### Example 2: Search Enhancement Issue
```bash
/process-issue-smart 18
```
**Issue #18**: "Enhance YouTube Discovery with Deep Search"

**Auto-detected specialists**:
1. **musical-search-specialist** (primary) - For query optimization
2. **era-expert** (secondary) - For era-specific search terms
3. **python-ai-architect** (tertiary) - For implementation patterns

**Injected knowledge**:
- Query expansion strategies
- Platform-specific optimization
- Producer reference translations
- Async search patterns

## Multi-Specialist Coordination

### When Multiple Specialists are Needed:
```yaml
issue: "Build sample compatibility system with era awareness"
detected_specialists:
  - sample-compatibility (primary)
  - era-expert (secondary)
  - python-ai-architect (implementation)

coordination_strategy:
  1. sample-compatibility provides:
     - Harmonic relationship rules
     - Frequency compatibility logic
     
  2. era-expert enhances with:
     - Era-specific compatibility rules
     - Historical production context
     
  3. python-ai-architect implements:
     - Type-safe compatibility models
     - Efficient analysis algorithms
```

## Specialist Combination Patterns

### Common Powerful Combinations:
```yaml
"groove + era":
  use_case: "Implement era-specific groove detection"
  synergy: "Historical context improves groove classification"

"search + compatibility":
  use_case: "Find compatible samples automatically"
  synergy: "Search results filtered by musical compatibility"

"all specialists":
  use_case: "Complex feature requiring full musical intelligence"
  synergy: "Complete domain knowledge for sophisticated features"
```

## Usage Workflow

1. **Run the command**:
   ```bash
   /process-issue-smart 14
   ```

2. **Review detected specialists**:
   ```
   Analyzing issue #14...
   Detected: conversational-interface, musical-understanding
   Primary specialist: musical-search-specialist
   Secondary: python-ai-architect
   ```

3. **Confirm or adjust**:
   ```
   ✓ Auto-detected specialists look correct
   ? Add additional specialist? (optional)
   ```

4. **Begin enhanced execution**:
   ```
   Loading specialist knowledge...
   ✓ musical-search-specialist loaded
   ✓ python-ai-architect loaded
   
   Beginning implementation with enhanced context...
   ```

## Advanced Features

### Specialist Chaining
```python
# For complex issues requiring sequential specialist application
chain = SpecialistChain([
    ("era-expert", "identify_era_requirements"),
    ("groove-analyst", "define_groove_parameters"),  
    ("musical-search-specialist", "generate_searches"),
    ("python-ai-architect", "implement_solution")
])

await chain.execute(issue)
```

### Learning from History
```python
# Track which specialists were useful for which issues
specialist_effectiveness = {
    "groove-analyst": {
        "issues_processed": [15, 23, 31],
        "success_rate": 0.95,
        "common_pairings": ["python-ai-architect"]
    }
}
```

### Specialist Confidence Scoring
```yaml
issue: "Implement groove-aware sample organization"
specialist_scores:
  groove-analyst: 95%       # "groove" in title
  sample-compatibility: 70% # "organization" implies relationships
  python-ai-architect: 60%  # implementation needed
  era-expert: 20%          # no era-specific mentions
  
threshold: 50%
activated: [groove-analyst, sample-compatibility, python-ai-architect]
```

This smart injection system ensures that every issue is tackled with the most relevant domain expertise, automatically providing the right context and knowledge for optimal implementation.