# /build Command - Feature Development with TDD

Build new features using Test-Driven Development with parallel agent orchestration.

## Usage
```
/build "feature description"
/build "Add BPM-based sample filtering to API"
/build "Create audio waveform visualization component"
```

## Workflow

### Stage 1: Analysis & Design (Parallel)
Launch 3 agents simultaneously to analyze and design:

```markdown
Use the Task tool to launch these agents in PARALLEL:

1. **System Architect** - Design system structure
   - Prompt: "Design the architecture for: {feature_description}. Include API endpoints, database schema changes, service layer interface, and integration points. Consider SP-404MK2 requirements if applicable."
   - Tools: Read, Write, Grep, Glob
   - Output: Architecture specification document

2. **Testing Specialist** - Create test plan
   - Prompt: "Create an MVP-level test plan (2-5 tests) for: {feature_description}. Follow the project's testing philosophy: real integrations, no mocks, focus on critical paths."
   - Tools: Read, Grep
   - Output: Test specifications (describe tests, don't implement yet)

3. **Research Agent** (if needed) - Find existing patterns
   - Prompt: "Search the codebase for existing patterns related to: {feature_description}. Find similar implementations, service patterns, API endpoints, and database models that can be reused."
   - Tools: Read, Grep, Glob
   - Output: Relevant code patterns and examples
```

**Wait for all 3 agents to complete before proceeding.**

### Stage 2: Test-First Implementation (TDD Red Phase)

```markdown
Use the Task tool to launch:

**Testing Specialist** - Write failing tests
- Prompt: "Implement the test plan from Stage 1 as Pytest tests. Write 2-5 failing tests that define the expected behavior of: {feature_description}. Use real database fixtures and real files. Make tests fail initially (TDD Red phase)."
- Tools: Read, Write, Edit, Bash
- Output: Test files with failing tests
```

**Run tests to verify they fail (TDD Red phase).**

### Stage 3: Implementation (TDD Green Phase)

Based on the architecture and component types, launch appropriate specialists:

#### For API Features
```markdown
Launch in SEQUENCE:

1. **Database Specialist** (if schema changes needed)
   - Prompt: "Implement database changes for: {feature_description}. Create SQLAlchemy models and Alembic migration based on architect's design."
   - Tools: Read, Write, Edit, Bash
   - Output: Models and migration files

2. **FastAPI Specialist** → **Senior Engineer**
   - Prompt: "Implement the API endpoints for: {feature_description}. Use dual response pattern (JSON + HTMX). Follow architect's design and make failing tests pass."
   - Tools: All tools (*)
   - Output: API endpoint implementation
```

#### For Frontend Features
```markdown
Launch:

**Frontend Specialist** → **Senior Engineer**
- Prompt: "Implement the frontend for: {feature_description}. Use HTMX, Alpine.js, and DaisyUI. Follow architect's design and integrate with existing API endpoints."
- Tools: All tools (*)
- Output: HTML pages/components
```

#### For AI/Audio Features
```markdown
Launch in SEQUENCE or PARALLEL (depending on dependencies):

1. **Audio Processing Specialist** → **Senior Engineer** (if audio processing)
   - Prompt: "Implement audio processing for: {feature_description}. Use librosa for feature extraction or soundfile for format conversion."
   - Tools: All tools (*)
   - Output: Audio processing service

2. **AI Integration Specialist** → **Senior Engineer** (if AI analysis)
   - Prompt: "Implement AI integration for: {feature_description}. Use OpenRouter API with cost tracking. Follow hybrid analysis pattern."
   - Tools: All tools (*)
   - Output: AI integration service
```

**Run tests to verify they pass (TDD Green phase).**

### Stage 4: Code Review & Quality Assurance

```markdown
Use the Task tool to launch:

**Code Reviewer**
- Prompt: "Review the implementation of: {feature_description}. Check code quality, security (SQL injection, XSS), performance, testing coverage (MVP-level appropriate?), and adherence to project conventions."
- Tools: Read, Grep, Glob
- Output: Review report with approval decision (APPROVED, APPROVED WITH SUGGESTIONS, NEEDS CHANGES)
```

### Stage 5: Integration & Finalization

```markdown
If reviewer approves:

**Senior Engineer** - Final integration
- Prompt: "Integrate and finalize: {feature_description}. Address reviewer suggestions, run all tests, update documentation if needed, ensure migrations are applied."
- Tools: All tools (*)
- Output: Production-ready feature
```

## Agent Selection Matrix

### Simple CRUD API
- Architect → Testing Specialist → Senior Engineer → Reviewer
- Optional: Database Specialist (if complex schema)

### Frontend Feature
- Architect → Frontend Specialist → Senior Engineer → Reviewer
- May need: FastAPI Specialist (if new endpoints)

### Audio Processing
- Architect → Audio Processing Specialist → Testing Specialist → Senior Engineer → Reviewer

### AI Integration
- Architect → AI Integration Specialist → Testing Specialist → Senior Engineer → Reviewer

### Full-Stack Feature
- Use Workflow Orchestrator to coordinate multiple teams

## Quality Gates

### Before Implementation
- [ ] Architecture design complete
- [ ] Test plan created (2-5 tests)
- [ ] Existing patterns researched

### Before Review
- [ ] All tests written and failing (Red)
- [ ] Implementation complete
- [ ] All tests passing (Green)
- [ ] Migrations tested

### Before Completion
- [ ] Code review approved
- [ ] No critical security issues
- [ ] Documentation updated
- [ ] Ready for deployment

## Parallel Execution Guidelines

**Use parallel execution when:**
- Tasks are independent (design, research, test planning)
- No data dependencies between agents
- Can reduce wall-clock time significantly

**Use sequential execution when:**
- Tasks have dependencies (database before API)
- One agent's output needed by next
- Debugging is easier with sequential flow

## Example Execution

### User Request
```
/build "Add batch export to SP-404MK2 format with BPM organization"
```

### Stage 1 (Parallel - 2 minutes)
- System Architect designs API, database, service
- Testing Specialist creates test plan (3 tests)
- Research finds existing export patterns

### Stage 2 (5 minutes)
- Testing Specialist writes 3 failing tests

### Stage 3 (15 minutes, sequential)
- Database Specialist adds organization field to sp404_exports
- FastAPI Specialist implements POST /api/v1/sp404/batches/export
- Audio Processing Specialist adds BPM organization logic
- Senior Engineer integrates all components

### Stage 4 (3 minutes)
- Code Reviewer checks quality → APPROVED WITH SUGGESTIONS

### Stage 5 (2 minutes)
- Senior Engineer applies suggestions, runs final tests

**Total: ~27 minutes for complex full-stack feature**

## Success Criteria
- Feature implements requirements accurately
- All tests pass (2-5 MVP-level tests)
- Code review approved
- No security vulnerabilities
- Documentation complete
- Ready for production deployment
