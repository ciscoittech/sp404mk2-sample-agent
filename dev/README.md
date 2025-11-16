# Dev Docs - Feature Development Documentation

**Purpose**: Strategic planning and context preservation for all feature development.

---

## Folder Structure

```
dev/
├── active/          # Current features in development
│   └── {feature}/
│       ├── {feature}-plan.md     # Complete implementation plan
│       ├── {feature}-context.md  # Key decisions and discoveries
│       └── {feature}-tasks.md    # Phase-based task checklist
└── completed/       # Archived completed features
```

---

## Workflow

### 1. Create Feature Plan

```bash
/dev-docs "Add real-time sample analysis streaming"
```

**Creates**:
- `dev/active/sample-analysis-streaming/`
  - `sample-analysis-streaming-plan.md` - Architecture and phases
  - `sample-analysis-streaming-context.md` - Decisions tracker
  - `sample-analysis-streaming-tasks.md` - Task checklist

### 2. Implement Feature

**As you work**:
- Mark tasks complete in `tasks.md`
- Update discoveries in `context.md`
- Reference `plan.md` for architecture

**Automatic Quality Checks** (via hooks):
- Type checking (mypy)
- Linting (ruff)
- Test validation (pytest)
- Error escalation at 5+ errors

### 3. Session End

```bash
/dev-docs-update "sample-analysis-streaming"
```

**Updates**:
- `context.md` with session work
- Marks completed tasks
- Documents blockers
- Preserves context for next session

### 4. Code Review

```bash
/code-review "sample-analysis-streaming"
```

**Validates**:
- Code matches plan architecture
- Security best practices
- Performance requirements
- Test coverage

### 5. Archive

After feature is merged:
```bash
mv dev/active/sample-analysis-streaming dev/completed/
```

---

## File Descriptions

### plan.md
**Purpose**: Complete implementation plan created before coding

**Contents**:
- Executive Summary
- Architecture Design (2-3 pages)
- Phase Breakdown (4-5 pages)
- Task List (2-3 pages)
- Risk Analysis (1-2 pages)
- Success Metrics (1 page)

**When to Read**: Before starting, during architecture questions, before major changes

### context.md
**Purpose**: Living document tracking key decisions and discoveries

**Contents**:
- Key Files and Locations
- Architecture Decisions Made
- Next Steps
- Discoveries During Implementation
- Blockers and Solutions

**When to Update**: End of session, when making key decisions, when discovering issues

### tasks.md
**Purpose**: Phase-based task checklist for tracking progress

**Contents**:
- Tasks organized by phase
- Checkboxes for completion
- Hour estimates
- Dependencies

**When to Update**: After completing each task, when adding new tasks discovered during implementation

---

## Benefits

✅ **Context Never Lost**: Survives session compaction and developer handoffs
✅ **Architecture Validated**: Code review against plan before merge
✅ **Clear Progress**: Task checklist shows what's done and what's next
✅ **Zero Errors**: Automated build checks catch issues immediately
✅ **30% Faster**: Strategic planning prevents scope creep and rework

---

## Example Features

```
dev/active/
├── hybrid-audio-analysis/
│   ├── hybrid-audio-analysis-plan.md
│   ├── hybrid-audio-analysis-context.md
│   └── hybrid-audio-analysis-tasks.md
├── sp404-export-enhancement/
│   └── ...
└── kit-builder-ai/
    └── ...
```

---

## Archived Commands

Old sample/workflow commands are in `.claude/commands/archive/`:
- Still accessible with `/archive/` prefix
- Preserves domain knowledge
- Reduces command namespace clutter

---

**Last Updated**: 2025-11-16
**System**: Dev-Docs v1.0 (customized for SP404MK2 FastAPI project)
