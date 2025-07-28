# Create Issue Command

**Command**: `/create-issue {title} [description]`

AI-powered GitHub issue creation with intelligent labeling, specialist assignment, and technical planning.

## Usage

```bash
/create-issue "Add user dashboard analytics"
/create-issue "Fix slow dashboard queries" "Dashboard taking 5+ seconds to load, need database optimization"
/create-issue "AI-powered question generation" "Users want AI to generate practice questions from uploaded study materials"
```

## Implementation

You are an AI-powered project analyst that creates comprehensive GitHub issues. When this command is executed:

### Phase 1: Requirements Analysis
1. **Parse title and description** for technical requirements
2. **Identify feature area** (UI, database, AI, performance, etc.)
3. **Estimate complexity** (simple, moderate, complex)
4. **Determine MVP scope** and challenge feature creep
5. **Extract acceptance criteria** from natural language

### Phase 2: AI-Powered Analysis
Use the following prompts to analyze the request:

#### Complexity Assessment Prompt:
```
Analyze this feature request for a Nuxt.js IT certification platform:

Title: {title}
Description: {description}

Assess:
1. Technical complexity (1-10 scale)
2. Estimated development time
3. Risk factors
4. Dependencies on other systems
5. MVP version vs full implementation

Focus on simplicity and question any complexity over level 7.
```

#### Label Suggestion Prompt:
```
Based on this feature request, suggest appropriate GitHub labels:

Title: {title}
Description: {description}

Available labels:
- Type: bug, enhancement, technical-debt
- Area: ui, database, ai, performance, testing, twitter, security, deployment
- Priority: critical, high-priority, low-priority
- Workflow: needs-triage, ready, auto-merge

Select 2-4 most relevant labels and explain reasoning.
```

#### Specialist Chain Recommendation:
```
Determine the optimal specialist chain for this issue:

Title: {title}
Description: {description}
Labels: {suggested_labels}

Available specialists:
- Git/DevOps: Version control, deployment, CI/CD
- Vuetify/Spike: UI components, responsive design
- Nuxt Edge: Server-side rendering, routing, performance
- Drizzle/Turso: Database operations, schema design
- LangChain AI: AI features, LLM integration
- Testing/Quality: TDD, coverage, E2E testing
- Twitter Intelligence: Growth features, analytics

Recommend specialist chain order and coordination strategy.
```

### Phase 3: Technical Planning
Generate comprehensive technical details:

#### Acceptance Criteria Generation:
```
Create detailed acceptance criteria for:

Title: {title}
Description: {description}

Format as:
- Given [context]
- When [action]
- Then [expected result]

Include edge cases and error scenarios.
```

#### Implementation Strategy:
```
Outline implementation approach:

1. Architecture decisions needed
2. Database schema changes (if any)
3. API endpoints to create/modify
4. UI components needed
5. Testing strategy
6. Deployment considerations

Focus on MVP-first approach.
```

### Phase 4: GitHub Issue Creation

#### Issue Template Population:
```markdown
# {title}

## Description
{ai_enhanced_description}

## Technical Analysis
**Complexity**: {complexity_score}/10
**Estimated Time**: {time_estimate}
**Risk Level**: {risk_assessment}

## Acceptance Criteria
{ai_generated_acceptance_criteria}

## Implementation Plan
{ai_generated_implementation_plan}

## Specialist Chain Recommendation
{recommended_specialists}

## Technical Considerations
{technical_notes}

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Tests written and passing (TDD)
- [ ] Code review completed
- [ ] No TypeScript errors
- [ ] Performance benchmarks met
- [ ] Documentation updated

## MVP Scope
{mvp_boundaries}

## Future Enhancements
{nice_to_have_features}
```

## AI Analysis Examples

### Example 1: Simple UI Enhancement
```
Input: "Add loading spinner to dashboard"
Analysis:
- Complexity: 3/10 (Simple UI component)
- Time: 2-4 hours
- Labels: ui, enhancement
- Specialist: Vuetify + Testing
- MVP: Basic spinner, standard positioning
```

### Example 2: Complex AI Feature
```
Input: "AI-powered study plan generator based on user performance"
Analysis:
- Complexity: 8/10 (AI integration + data analysis)
- Time: 1-2 weeks
- Labels: ai, enhancement, database
- Specialist: LangChain + Drizzle + Testing
- MVP: Simple rule-based recommendations (NOT AI initially)
- Challenge: "Do we need AI for MVP? Can we start with algorithm-based recommendations?"
```

### Example 3: Performance Issue
```
Input: "Dashboard loads too slowly"
Analysis:
- Complexity: 6/10 (Performance investigation + fixes)
- Time: 3-5 days
- Labels: performance, bug, database
- Specialist: Nuxt Edge + Drizzle + Testing
- MVP: Identify bottleneck, implement caching
```

## MVP Philosophy Integration

### Complexity Challenges:
When complexity score > 7, automatically challenge the scope:

```
🚨 Complexity Alert: This feature scores {score}/10

MVP Questions:
1. What's the smallest version that provides value?
2. Can we split this into smaller issues?
3. Are there simpler alternatives to achieve the goal?
4. What would users accept as a first iteration?

Suggestions:
- Break into phases
- Start with manual process
- Use existing libraries instead of custom solutions
- Defer advanced features to v2
```

### Scope Boundary Enforcement:
```
📋 Scope Boundaries:

IN SCOPE (MVP):
- {core_functionality}
- {essential_features}

OUT OF SCOPE (Future):
- {advanced_features}
- {nice_to_haves}
- {edge_cases}

This keeps the issue focused and achievable.
```

## GitHub API Integration

### Issue Creation Payload:
```typescript
const issueData = {
  title: aiEnhancedTitle,
  body: generatedIssueBody,
  labels: suggestedLabels,
  assignees: [currentUser],
  milestone: currentSprintMilestone
};

const issue = await octokit.rest.issues.create({
  owner: 'bhunt',
  repo: 'pingtopass-nuxt',
  ...issueData
});
```

### Label Management:
```typescript
// Ensure all suggested labels exist
for (const label of suggestedLabels) {
  try {
    await octokit.rest.issues.getLabel({
      owner: 'bhunt',
      repo: 'pingtopass-nuxt',
      name: label
    });
  } catch (error) {
    if (error.status === 404) {
      // Create missing label with appropriate color
      await createLabel(label);
    }
  }
}
```

## Quality Assurance

### Issue Quality Checklist:
- ✅ Clear, specific title
- ✅ Detailed description with context
- ✅ Measurable acceptance criteria
- ✅ Appropriate labels assigned
- ✅ Complexity assessment included
- ✅ Implementation plan outlined
- ✅ MVP scope clearly defined
- ✅ Specialist chain recommended

### AI Analysis Validation:
```typescript
// Validate AI suggestions before creating issue
function validateAnalysis(analysis: IssueAnalysis): ValidationResult {
  const issues = [];
  
  if (analysis.complexity > 8) {
    issues.push("High complexity - consider breaking down");
  }
  
  if (analysis.labels.length < 2) {
    issues.push("Needs more specific labels");
  }
  
  if (!analysis.acceptanceCriteria.length) {
    issues.push("Missing acceptance criteria");
  }
  
  return {
    valid: issues.length === 0,
    issues
  };
}
```

## Integration with Existing Workflow

### Post-Creation Actions:
After creating the issue:

1. **Add to current sprint** (if appropriate)
2. **Notify team members** (if mentioned)
3. **Create scratchpad** for immediate development
4. **Suggest next actions**:
   ```
   ✅ Issue #123 created successfully!
   
   Next steps:
   • /create-worktree 123 - Start development
   • /process-issue 123 - Full AI-assisted implementation
   • Review and refine in GitHub if needed
   ```

### Scratchpad Auto-Creation:
```markdown
# Issue #123: {title}

## AI Analysis Summary
- Complexity: {complexity}/10
- Specialist Chain: {specialists}
- MVP Focus: {mvp_scope}

## Development Plan
{implementation_plan}

## Ready for Development
- [ ] Requirements clear
- [ ] Specialist chain identified
- [ ] Worktree created
- [ ] Development started
```

## Error Handling

### Common Issues:
1. **GitHub API rate limits**: Queue for later creation
2. **Invalid repository access**: Check permissions
3. **Malformed input**: Provide examples and guidance
4. **AI analysis fails**: Fall back to template-based creation
5. **Network connectivity**: Offer offline mode with sync

### Recovery Strategies:
```bash
# If issue creation fails
echo "⚠️ Issue creation failed. Saving locally..."
echo "$issue_content" > "pending-issues/issue-$(date +%s).md"
echo "Run /sync-pending-issues when online"
```

## Success Criteria

The command is successful when:
1. ✅ AI analysis provides accurate complexity assessment
2. ✅ Suggested labels are relevant and helpful
3. ✅ Acceptance criteria are specific and testable
4. ✅ Implementation plan is actionable
5. ✅ MVP scope is clearly defined and challenged when needed
6. ✅ GitHub issue is created with all metadata
7. ✅ Issue quality meets team standards
8. ✅ Next steps are clearly communicated

## Configuration

### AI Model Settings:
```typescript
const AI_CONFIG = {
  model: "claude-3-haiku",  // Fast, cost-effective for analysis
  temperature: 0.3,         // Lower for consistent, focused output
  max_tokens: 2000,         // Sufficient for detailed analysis
  timeout: 30000           // 30 second timeout
};
```

### Customizable Templates:
Store team-specific templates in `/templates/issue-types/`:
- `bug-report.md`
- `feature-request.md`
- `technical-debt.md`
- `performance-issue.md`

This allows customization while maintaining AI-powered enhancement.