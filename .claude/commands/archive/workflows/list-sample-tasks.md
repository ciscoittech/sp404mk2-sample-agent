# List Sample Tasks Command

**Command**: `/list-sample-tasks`

Displays all active sample collection tasks with their status, specialist progress, and collection health metrics.

## Usage

```bash
/list-sample-tasks
```

## Implementation

You are a Music Production coordinator providing comprehensive sample collection overview. When this command is executed:

### Phase 1: Discover Active Tasks
1. **Query GitHub for open sample collection issues** (label: `agent-task`)
2. **Scan samples directory for active workspaces**
3. **Check agent queue for running processes**
4. **Gather metadata from each collection**

### Phase 2: Health Assessment
For each collection task, check:
1. **Collection progress**: Samples collected vs target
2. **Quality metrics**: Average scores, approval rates
3. **Specialist status**: Reviews completed, pending decisions
4. **Agent activity**: Current phase, last activity
5. **Storage usage**: Disk space per collection

### Phase 3: Format Output
Present information in structured format:
1. **Summary header** with total collections
2. **Individual task details** with progress bars
3. **Specialist activity indicators**
4. **Quality metrics and alerts**
5. **Recommended actions**

## Expected Output Format

```
🎵 Active Sample Collections (4 total)
=====================================

📁 Task #123: Jazz drum breaks from Blue Note Records
🎯 Target: 50 samples | 📊 Collected: 42 | ✅ Approved: 35
🏷️  Labels: drums, jazz, vintage, 1960s
👥 Specialists: Music Historian, DJ/Beatmaker, Sound Engineer
📈 Progress: ████████░░ 84% (Review phase)
⭐ Quality: 8.5/10 average | 🎧 BPM Range: 85-115

Specialist Status:
  🎓 Music Historian: ✅ 42/42 reviewed (9.2/10 avg)
  🎧 DJ/Beatmaker: 🔄 38/42 reviewed (8.3/10 avg)
  🔧 Sound Engineer: 🔄 35/42 reviewed (8.0/10 avg)

Agent Activity:
  ✅ Collector: Complete (47 sources found)
  ✅ Downloader: Complete (42 samples acquired)
  ✅ Analyzer: Complete (BPM/key detection done)
  🔄 Reporter: Creating review queue...

💾 Storage: 1.2 GB | 🕐 Last activity: 5 min ago
🎯 Next: Complete specialist reviews → Human curation

---

📁 Task #124: Vintage Rhodes sounds from soul records
🎯 Target: 30 samples | 📊 Collected: 28 | ✅ Approved: 15
🏷️  Labels: keys, soul, rhodes, 1970s
👥 Specialists: Keyboard Player, Genre Expert (Soul), Sound Engineer
📈 Progress: ██████░░░░ 60% (Analysis phase)
⭐ Quality: 7.8/10 average | 🎹 Keys: C, F, Bb dominant

Specialist Status:
  🎹 Keyboard Player: 🔄 20/28 reviewed (8.1/10 avg)
  🎵 Genre Expert: ⏳ Waiting for samples
  🔧 Sound Engineer: 🔄 15/28 reviewed (7.5/10 avg)

Agent Activity:
  ✅ Collector: Complete (32 sources found)
  ✅ Downloader: Complete (28 samples acquired)
  🔄 Analyzer: Key detection 75% complete
  ⏳ Reporter: Pending

💾 Storage: 856 MB | 🕐 Last activity: 12 min ago
⚠️ Alert: 3 samples need re-analysis (corrupted key data)

---

📁 Task #125: Lo-fi hip hop vocal chops
🎯 Target: 40 samples | 📊 Collected: 12 | ✅ Approved: 5
🏷️  Labels: vocals, lo-fi, hip-hop, chops
👥 Specialists: Genre Expert (Lo-fi), DJ/Beatmaker, Sound Engineer
📈 Progress: ███░░░░░░░ 30% (Collection phase)
⭐ Quality: 7.2/10 average | 🎤 Types: Female (8), Male (4)

Specialist Status:
  🎵 Genre Expert: ✅ 12/12 reviewed (7.5/10 avg)
  🎧 DJ/Beatmaker: 🔄 8/12 reviewed (7.0/10 avg)
  🔧 Sound Engineer: ⏳ Waiting for more samples

Agent Activity:
  🔄 Collector: Searching additional sources...
  ⏸️ Downloader: Paused (waiting for sources)
  ⏳ Analyzer: Pending
  ⏳ Reporter: Pending

💾 Storage: 124 MB | 🕐 Last activity: 2 hours ago
❌ Issue: Limited sources found, considering scope adjustment

---

📁 Task #126: Brazilian percussion loops [DRAFT]
🎯 Target: 25 samples | 📊 Collected: 0 | ✅ Approved: 0
🏷️  Labels: percussion, world, brazilian, loops
👥 Specialists: Music Historian, Genre Expert (Brazilian), Crate Digger
📈 Progress: ░░░░░░░░░░ 0% (Planning phase)
⭐ Quality: N/A | 🥁 Instruments: Planned

Specialist Status:
  🎓 Music Historian: ⏳ Awaiting samples
  🌎 Genre Expert: 📝 Creating source list
  📦 Crate Digger: 🔍 Researching archives

Agent Activity:
  ⏳ All agents pending task start

💾 Storage: 0 MB | 🕐 Created: 1 day ago
💡 Ready to start: Run /process-sample-task 126

=====================================
📊 COLLECTION SUMMARY
=====================================

Total Active Tasks: 4
Total Samples Collected: 82/145 (57%)
Average Quality Score: 7.9/10
Total Storage Used: 2.2 GB

By Status:
  🔄 In Progress: 3
  📝 Planning: 1
  ✅ Ready for Review: 2
  ⏸️ Paused: 1

By Genre:
  🎵 Jazz: 1 task (42 samples)
  🎵 Soul: 1 task (28 samples)
  🎵 Hip-Hop: 1 task (12 samples)
  🎵 World: 1 task (0 samples)

🚨 Attention Required:
============================
• Task #124: Fix corrupted key detection data
• Task #125: Source shortage - consider expanding search
• Task #123: Complete specialist reviews for human curation

💡 Quick Actions:
================
• /process-sample-task 126    - Start Brazilian percussion
• /review-samples 123         - Begin human curation
• /fix-analysis 124          - Re-run key detection
• /expand-search 125         - Find more vocal sources
```

## Health Indicators

### Status Icons:
- ✅ **Green**: Complete/passing
- 🔄 **Blue**: In progress
- ⏳ **Gray**: Pending/waiting
- ⚠️ **Yellow**: Warning/attention needed
- ❌ **Red**: Error/blocked
- ⏸️ **Paused**: Temporarily halted

### Progress Phases:
1. **Planning (0-10%)**: Source identification
2. **Collection (10-40%)**: Downloading samples
3. **Analysis (40-60%)**: Technical processing
4. **Review (60-90%)**: Specialist evaluation
5. **Curation (90-100%)**: Human approval

## Detailed Metrics Calculation

### Quality Score Aggregation:
```python
def calculate_quality_metrics(task):
    specialist_scores = []
    for specialist in task.specialists:
        if specialist.reviews:
            avg_score = sum(specialist.reviews) / len(specialist.reviews)
            specialist_scores.append(avg_score)
    
    overall_quality = sum(specialist_scores) / len(specialist_scores)
    return {
        'overall': overall_quality,
        'by_specialist': specialist_scores,
        'approved_rate': task.approved / task.collected
    }
```

### Collection Health Check:
```python
health_checks = {
    'progress_rate': check_collection_velocity,
    'quality_trend': analyze_quality_trajectory,
    'specialist_consensus': measure_agreement,
    'technical_issues': count_processing_errors,
    'storage_efficiency': calculate_compression_ratio
}
```

### Activity Monitoring:
```python
def get_agent_activity(task_id):
    return {
        'last_activity': get_latest_timestamp(),
        'active_agent': get_current_agent(),
        'phase_duration': calculate_phase_time(),
        'estimated_completion': predict_finish_time()
    }
```

## Specialist Activity Details

### Specialist Workload View:
```
👥 Specialist Workload Summary
==============================

🎓 Music Historian (2 active tasks)
   • Task #123: 42/42 complete (9.2/10 avg) ✅
   • Task #126: Pending start ⏳
   • Total reviews: 42 | Avg time: 2.3 min/sample

🎧 DJ/Beatmaker (3 active tasks)
   • Task #123: 38/42 in progress (8.3/10 avg) 🔄
   • Task #125: 8/12 in progress (7.0/10 avg) 🔄
   • Task #126: Pending start ⏳
   • Total reviews: 46 | Avg time: 1.8 min/sample

🔧 Sound Engineer (4 active tasks)
   • Task #123: 35/42 in progress (8.0/10 avg) 🔄
   • Task #124: 15/28 in progress (7.5/10 avg) 🔄
   • Task #125: Awaiting samples ⏳
   • Task #126: Pending start ⏳
   • Total reviews: 50 | Avg time: 3.1 min/sample
```

## Integration Features

### Real-Time Updates:
```bash
# Watch mode for live updates
/list-sample-tasks --watch

# Filter by status
/list-sample-tasks --status=review

# Sort by priority
/list-sample-tasks --sort=quality

# Export metrics
/list-sample-tasks --export=csv
```

### Quick Filters:
1. **By Genre**: Show only specific music styles
2. **By Specialist**: Tasks assigned to specific expert
3. **By Phase**: Collection/Analysis/Review/etc
4. **By Quality**: Above/below threshold
5. **By Age**: Recently updated/stale tasks

## Database Queries

### Task Status Query:
```sql
SELECT 
    t.issue_number,
    t.title,
    t.target_count,
    COUNT(s.id) as collected,
    COUNT(CASE WHEN s.status = 'approved' THEN 1 END) as approved,
    AVG(s.quality_score) as avg_quality,
    MAX(s.created_at) as last_activity
FROM tasks t
LEFT JOIN samples s ON t.id = s.task_id
WHERE t.status = 'active'
GROUP BY t.id
ORDER BY last_activity DESC;
```

### Specialist Performance:
```sql
SELECT 
    sp.name as specialist,
    COUNT(DISTINCT sr.task_id) as active_tasks,
    COUNT(sr.id) as total_reviews,
    AVG(sr.score) as avg_score,
    AVG(sr.review_time) as avg_time
FROM specialists sp
JOIN specialist_reviews sr ON sp.id = sr.specialist_id
WHERE sr.created_at > datetime('now', '-7 days')
GROUP BY sp.id;
```

## Alert System

### Automated Alerts:
1. **Quality dropping**: Average score trending down
2. **Stale collections**: No activity > 24 hours
3. **Storage warnings**: Approaching limits
4. **Specialist bottleneck**: Reviews backing up
5. **Source exhaustion**: Can't find more samples

### Alert Examples:
```
🚨 ALERTS (3)
============

⚠️ Task #124: Key detection failing (3 errors)
   → Suggested action: /fix-analysis 124

⚠️ Task #125: Collection stalled at 30%
   → Suggested action: /expand-search 125

⚠️ Storage: 85% full (17 GB / 20 GB)
   → Suggested action: /cleanup-rejected-samples
```

## Performance Optimization

### Caching Strategy:
1. **Cache task summaries** (5 minute TTL)
2. **Cache specialist scores** (10 minute TTL)
3. **Parallel metric calculation**
4. **Incremental updates** for large collections

### Display Optimization:
```python
# Paginate large result sets
def display_tasks(limit=10, offset=0):
    tasks = fetch_active_tasks(limit, offset)
    return format_task_display(tasks)

# Progressive loading
def load_task_details(task_id, detail_level='summary'):
    if detail_level == 'summary':
        return get_cached_summary(task_id)
    else:
        return fetch_full_details(task_id)
```

## Success Criteria

The command is successful when:
1. ✅ All active tasks discovered and displayed
2. ✅ Accurate progress percentages shown
3. ✅ Specialist statuses correctly reflected
4. ✅ Quality metrics properly calculated
5. ✅ Storage usage accurately reported
6. ✅ Alerts for issues prominently displayed
7. ✅ Quick action suggestions relevant
8. ✅ Performance acceptable (<3 seconds)
9. ✅ Visual hierarchy clear and scannable
10. ✅ Next steps obvious for each task

## Error Handling

### Common Issues:
1. **GitHub API unavailable**: Show cached data with warning
2. **Database query timeout**: Limit result set, show partial
3. **Corrupted workspace**: Offer repair options
4. **Missing metadata**: Regenerate from files

### Graceful Degradation:
- If GitHub fails, show local data only
- If database slow, show basic stats only
- If workspace corrupted, mark for repair
- Always show something useful

This command provides a comprehensive dashboard for managing multiple sample collection workflows, giving clear visibility into progress, quality, and next actions needed.