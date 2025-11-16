# /debug Command - Problem Solving & Debugging

Debug issues across the SP404MK2 stack with specialized agent assistance.

## Usage
```
/debug "issue description"
/debug "API endpoint returns 500 error when uploading samples"
/debug "Vibe analysis WebSocket disconnects randomly"
/debug "BPM detection returning incorrect values"
```

## Workflow

### Stage 1: Initial Analysis

```markdown
**Senior Engineer** - Reproduce and analyze issue
- Prompt: "Reproduce and analyze this issue: {issue_description}. Read relevant code, check logs, run the code if possible, and identify the root cause. Report findings with specific file locations and line numbers."
- Tools: Read, Grep, Glob, Bash
- Output: Initial analysis with suspected root cause
```

### Stage 2: Specialized Diagnosis (based on issue type)

Based on the analysis, route to appropriate specialist:

#### API/Endpoint Issues
```markdown
**FastAPI Specialist** - Diagnose API problem
- Prompt: "Diagnose this API issue: {issue_description}. Check endpoint implementation, request/response handling, error handling, status codes, and dependency injection. Identify the bug."
- Tools: Read, Grep, Bash
- Output: Detailed diagnosis with fix recommendations
```

#### Database Issues
```markdown
**Database Specialist** - Diagnose database problem
- Prompt: "Diagnose this database issue: {issue_description}. Check queries, relationships, migrations, indexes, async patterns, and connection handling. Look for N+1 queries, missing rollbacks, or incorrect async usage."
- Tools: Read, Grep, Bash
- Output: Database-specific diagnosis
```

#### Frontend/HTMX Issues
```markdown
**Frontend Specialist** - Diagnose UI problem
- Prompt: "Diagnose this frontend issue: {issue_description}. Check HTMX attributes, Alpine.js data flow, form handling, WebSocket connections, and template rendering. Look for HTMX target mismatches or Alpine reactivity issues."
- Tools: Read, Grep, Bash
- Output: Frontend-specific diagnosis
```

#### Audio Processing Issues
```markdown
**Audio Processing Specialist** - Diagnose audio problem
- Prompt: "Diagnose this audio issue: {issue_description}. Check librosa usage, sample rate handling, format conversion, BPM detection, feature extraction. Look for incorrect parameters or file format issues."
- Tools: Read, Grep, Bash
- Output: Audio processing diagnosis
```

#### AI/OpenRouter Issues
```markdown
**AI Integration Specialist** - Diagnose AI problem
- Prompt: "Diagnose this AI integration issue: {issue_description}. Check OpenRouter API calls, retry logic, rate limiting, prompt formatting, token estimation, and cost tracking. Look for timeout issues or API errors."
- Tools: Read, Grep, Bash
- Output: AI integration diagnosis
```

### Stage 3: Fix Implementation

```markdown
**Senior Engineer** - Implement fix
- Prompt: "Implement the fix for: {issue_description}. Based on the diagnosis from Stage 2, make the necessary code changes. Add logging if needed. Test the fix to verify it resolves the issue."
- Tools: All tools (*)
- Output: Fixed code
```

### Stage 4: Verification

```markdown
1. Run existing tests to ensure no regressions
2. Manually test the fix
3. Check logs for proper error handling

**Testing Specialist** (if new test needed) - Add regression test
- Prompt: "Add a regression test for the bug: {issue_description}. Create 1-2 tests that would have caught this bug and will prevent it from recurring."
- Tools: Write, Edit, Bash
- Output: Regression test(s)
```

### Stage 5: Review

```markdown
**Code Reviewer** - Review fix
- Prompt: "Review the fix for: {issue_description}. Ensure the fix is correct, doesn't introduce new issues, has proper error handling, and includes appropriate testing."
- Tools: Read, Grep
- Output: Review approval
```

## Issue Type Detection

### API Errors (500, 400, 404)
- Check: Endpoint implementation, request validation, database operations
- Specialists: FastAPI Specialist, Database Specialist
- Common causes: Missing rollback, incorrect Pydantic schema, async/await issues

### Database Errors
- Check: Queries, relationships, migrations, connection handling
- Specialist: Database Specialist
- Common causes: N+1 queries, missing foreign keys, incorrect async patterns

### Frontend Errors
- Check: HTMX targets, Alpine.js reactivity, template rendering
- Specialist: Frontend Specialist
- Common causes: Wrong hx-target, duplicate IDs, Alpine data not initialized

### Audio Processing Errors
- Check: librosa calls, sample rates, format conversion
- Specialist: Audio Processing Specialist
- Common causes: Wrong sample rate, invalid audio format, file not found

### AI/API Integration Errors
- Check: OpenRouter calls, rate limits, prompts, cost tracking
- Specialist: AI Integration Specialist
- Common causes: Rate limit exceeded, timeout, incorrect model ID

### Performance Issues
- Check: Query optimization, N+1 queries, async patterns, caching
- Specialists: Database Specialist, Senior Engineer
- Common causes: Missing indexes, N+1 queries, blocking I/O

## Debugging Tools & Techniques

### Backend Debugging
```bash
# Check logs
tail -f backend/logs/app.log

# Run specific test
pytest backend/tests/path/to/test.py::test_name -v

# Check database
sqlite3 sp404_samples.db "SELECT * FROM samples LIMIT 5;"

# Test API endpoint
curl -X POST http://localhost:8100/api/v1/samples \
  -F "audio_file=@test.wav" \
  -F "name=Test"
```

### Frontend Debugging
```javascript
// Check HTMX requests in browser console
htmx.logAll();

// Check Alpine.js data
$data

// Monitor WebSocket
// Open DevTools → Network → WS
```

### Database Debugging
```python
# Enable SQLAlchemy query logging
engine = create_async_engine(
    DATABASE_URL,
    echo=True  # Prints all SQL queries
)
```

## Common Issue Patterns

### Issue: "API returns 500 error"
**Diagnosis Flow**:
1. Check logs for stack trace
2. Look for database rollback issues
3. Check async/await patterns
4. Verify Pydantic schema validation

**Common Fixes**:
- Add `await db.rollback()` in except block
- Fix incorrect async function call
- Update Pydantic schema to match data

### Issue: "HTMX doesn't update UI"
**Diagnosis Flow**:
1. Check hx-target matches element ID
2. Verify server returns correct template
3. Check hx-swap strategy
4. Look for duplicate IDs

**Common Fixes**:
- Correct hx-target ID
- Return HTML template for HTMX requests
- Change hx-swap strategy

### Issue: "BPM detection incorrect"
**Diagnosis Flow**:
1. Check sample rate used in librosa.load()
2. Verify onset detection parameters
3. Test with known BPM sample

**Common Fixes**:
- Use correct sample rate (22050 or 48000)
- Adjust onset detection sensitivity
- Add tempo confidence threshold

### Issue: "OpenRouter API timeout"
**Diagnosis Flow**:
1. Check retry logic is working
2. Verify timeout settings
3. Look for rate limiting

**Common Fixes**:
- Increase timeout value
- Add exponential backoff
- Use faster model for batch processing

## Success Criteria
- Issue root cause identified
- Fix implemented and tested
- No regressions introduced
- Regression test added (if appropriate)
- Code review approved
- Issue fully resolved
