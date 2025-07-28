# Create Worktree Command

**Command**: `/create-worktree {issue-number} [title]`

Creates a new git worktree for parallel development of a specific GitHub issue.

## Usage

```bash
/create-worktree 123
/create-worktree 123 "dashboard improvements"
```

## Implementation

You are a Git/DevOps specialist helping create isolated development environments. When this command is executed:

### Phase 1: Preparation
1. **Fetch latest changes from origin**
2. **Verify issue exists and get details from GitHub**
3. **Check for existing worktree for this issue**
4. **Ensure no conflicts with existing branches**

### Phase 2: Worktree Creation
1. **Generate branch name**: `feature/issue-{number}-{slugified-title}`
2. **Create worktree directory**: `../pingtopass-issue-{number}/`
3. **Initialize branch from latest main**
4. **Set up development environment in new worktree**

### Phase 3: Environment Setup
1. **Navigate to new worktree directory**
2. **Install dependencies**: `pnpm install`
3. **Setup database**: `pnpm run db:push`
4. **Create initial scratchpad**: `/scratchpads/issue-{number}-{title}.md`
5. **Verify environment is working**: `pnpm run dev --port 3001`

### Phase 4: Documentation
1. **Update worktree registry** (if exists)
2. **Create entry in scratchpad with:**
   - Issue details and requirements
   - Specialist chain recommendations
   - Initial implementation plan
   - Testing strategy

## Expected Directory Structure

```
pingtopass-nuxt/                    # Main workspace
../pingtopass-issue-123/           # New worktree
├── .git -> pingtopass-nuxt/.git   # Git link
├── package.json                   # Project files
├── scratchpads/
│   └── issue-123-{title}.md      # Planning document
└── [all other project files]
```

## Branch Naming Convention

- Format: `feature/issue-{number}-{short-description}`
- Examples:
  - `feature/issue-123-dashboard-improvements`
  - `feature/issue-45-user-analytics`
  - `feature/issue-67-ai-question-generator`

## Error Handling

### Common Issues:
1. **Issue number doesn't exist**: Fetch from GitHub API to verify
2. **Worktree already exists**: Offer to switch to existing or create new branch
3. **Branch name conflicts**: Suggest alternative naming
4. **Network issues**: Provide offline mode instructions
5. **Dependency installation fails**: Provide troubleshooting steps

### Recovery Commands:
```bash
# If worktree creation fails mid-process
git worktree remove ../pingtopass-issue-{number} --force
git branch -D feature/issue-{number}-{title}

# If dependencies fail to install
cd ../pingtopass-issue-{number}
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

## Integration with Specialists

After creating the worktree, automatically analyze the issue and suggest specialist chain:

### Issue Analysis:
1. **Read issue labels and description**
2. **Determine complexity and scope**
3. **Recommend appropriate specialist chain**:
   - `ui` label → Vuetify + Nuxt + Testing
   - `database` label → Drizzle + Testing
   - `ai` label → LangChain + Testing
   - Multiple labels → Full-stack chain

### Scratchpad Template:
```markdown
# Issue #{number}: {title}

## Original Issue
- **GitHub Issue**: #{number}
- **Labels**: {labels}
- **Assignee**: {assignee}
- **Milestone**: {milestone}

## Requirements Analysis
{AI-generated analysis of requirements}

## Recommended Specialist Chain
{Based on labels and complexity}

## Implementation Plan
1. [ ] Analysis phase
2. [ ] Design phase  
3. [ ] Implementation phase
4. [ ] Testing phase
5. [ ] PR creation

## Technical Notes
{Space for implementation details}

## Testing Strategy
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests (if UI changes)

## Definition of Done
- [ ] All tests passing
- [ ] Code review completed
- [ ] No TypeScript errors
- [ ] Meets acceptance criteria
```

## Success Criteria

The command is successful when:
1. ✅ New worktree created with proper branch name
2. ✅ Dependencies installed successfully
3. ✅ Database schema synchronized
4. ✅ Development server can start
5. ✅ Scratchpad created with issue analysis
6. ✅ Specialist chain recommended
7. ✅ Ready for development work

## Next Steps

After successful worktree creation, user can:
1. **Start development** in the new isolated environment
2. **Use `/process-issue {number}`** to begin AI-assisted implementation
3. **Switch between worktrees** using standard git commands
4. **Run tests independently** in each worktree
5. **Deploy preview** from specific worktree