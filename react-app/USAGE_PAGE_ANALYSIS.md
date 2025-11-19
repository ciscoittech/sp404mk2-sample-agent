# UsagePage.tsx Analysis - Phase 0 HTMX Migration

**Created**: 2025-11-18
**Status**: Analysis Complete - Ready for Implementation

---

## HTMX Usage Page Analysis

**Source File**: `frontend/pages/usage.html`
**Target**: `react-app/src/pages/UsagePage.tsx`

### Current Features (HTMX/Alpine.js)

1. **Summary Cards (4 metrics)**
   - Total Spend (Month) - `$0.0000` format
   - Tokens Used - Total + Input/Output breakdown
   - Budget Status - Remaining budget + percentage bar
   - Top Model - Most used model + cost + call count

2. **Charts (Chart.js)**
   - Operation Breakdown - Doughnut chart showing cost by operation
   - Daily Cost Trend - Line chart showing last 30 days

3. **Data Tables**
   - Model Comparison Table - Shows all models with calls, tokens, cost, avg cost/call
   - Recent API Calls - Last 50 calls with timestamp, model, operation, tokens, cost

4. **Budget Alerts**
   - Warning state (80%+ usage)
   - Exceeded state (100%+ usage)
   - Dynamic alert messages

5. **Auto-refresh**
   - Polls data every 30 seconds
   - Manual refresh via page reload

6. **CSV Export**
   - Export usage data via `/api/v1/usage/export`

---

## API Endpoints Discovered

### Public Endpoints (No Auth Required)
```
GET /api/v1/public/usage/summary
  Returns: { summary: {...}, budget: {...} }

GET /api/v1/public/usage/daily?days=30
  Returns: { days: 30, data: [{date, cost, tokens}] }

GET /api/v1/public/usage/recent?limit=50
  Returns: { limit: 50, count: X, calls: [...] }
```

### Authenticated Endpoints
```
GET /api/v1/usage/summary?start_date=...&end_date=...
  Returns: { total_cost, total_tokens, input_tokens, output_tokens, call_count, by_operation: {...}, by_model: {...} }

GET /api/v1/usage/daily?days=30
  Returns: { days: 30, data: [{date, cost, tokens}] }

GET /api/v1/usage/budget
  Returns: { status: "ok"|"warning"|"exceeded", warnings: [...], monthly: {...}, daily: {...} }

GET /api/v1/usage/recent?limit=50
  Returns: { limit: 50, count: X, calls: [{id, model, operation, tokens, cost, created_at, sample_id, batch_id}] }

GET /api/v1/usage/export?start_date=...&end_date=...
  Returns: CSV file download
```

---

## Metrics to Display

### 1. Cost Metrics
- **Total API Cost** (this month) - `$X.XXXX` format
- **Tokens Used** - Total count with input/output breakdown
- **Budget Remaining** - `$XX.XX` with percentage bar
- **Budget Status** - Visual indicator (green/yellow/red)

### 2. Model Metrics
- **Top Model** - Most expensive model with cost + call count
- **Model Comparison Table**:
  - Model name
  - Call count
  - Total tokens
  - Total cost
  - Average cost per call

### 3. Operation Metrics
- **Cost by Operation** - Breakdown by operation type
  - `chat`
  - `collector_search`
  - `collector_discover`
  - `vibe_analysis`

### 4. Time-based Metrics
- **Daily Cost Trend** - Last 30 days line chart
- **Recent API Calls** - Last 50 calls with full details

### 5. Activity Log Metrics
- Timestamp
- Model used
- Operation type
- Token usage (input/output)
- Cost per call
- Related sample/batch ID

---

## Data Models (TypeScript)

```typescript
// Summary Response
interface UsageSummary {
  total_cost: number;
  total_tokens: number;
  input_tokens: number;
  output_tokens: number;
  call_count: number;
  by_operation: Record<string, { cost: number; count: number }>;
  by_model: Record<string, { cost: number; tokens: number; count: number }>;
}

// Budget Status
interface BudgetStatus {
  status: 'ok' | 'warning' | 'exceeded';
  warnings: string[];
  monthly: {
    used: number;
    limit: number;
    percentage: number;
    remaining: number;
  };
  daily: {
    tokens_used: number;
    tokens_limit: number;
    percentage: number;
    tokens_remaining: number;
  };
}

// Daily Usage
interface DailyUsage {
  date: string;
  cost: number;
  tokens: number;
}

// API Call
interface ApiCall {
  id: number;
  model: string;
  operation: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  total_cost: number;
  created_at: string;
  sample_id: number | null;
  batch_id: string | null;
}

// Recent Calls Response
interface RecentCallsResponse {
  limit: number;
  count: number;
  calls: ApiCall[];
}
```

---

## Implementation Plan

### Phase 1: Core Data Fetching (Subtasks 2-3)
- Create `react-app/src/api/usage.ts` with all endpoint functions
- Create `react-app/src/hooks/useUsage.ts` with React Query hooks
- Use public endpoints for demo user (matches HTMX behavior)

### Phase 2: Component Structure (Subtask 4)
- Create page layout with 4 main sections
- Import shadcn/ui components (Card, Table, Badge)
- Define TypeScript types for all data

### Phase 3: Summary Cards (Subtask 5)
- 4 metric cards: Cost, Tokens, Budget, Top Model
- Show trending indicators (not in HTMX, but nice-to-have)
- Format currency correctly
- Add loading skeletons

### Phase 4: Charts (Subtask 6)
- Install recharts: `npm install recharts`
- Operation breakdown (doughnut → pie chart)
- Daily cost trend (line chart)
- Match Chart.js styling from HTMX

### Phase 5: Tables (Subtasks 7-8)
- Model comparison table
- Recent API calls activity log
- Add sorting/filtering capabilities
- Pagination for activity log

### Phase 6: Polish (Subtasks 9-10)
- Date range picker
- Refresh button
- CSV export button
- Budget alerts
- Loading states
- Empty states
- Responsive design

### Phase 7: Integration (Subtasks 11-12)
- Add route to App.tsx
- Update navigation in AppShell
- Test all functionality
- Verify data accuracy

---

## Sample Values (From HTMX Page)

```javascript
// Default empty state
summary: {
  total_cost: 0,
  total_tokens: 0,
  input_tokens: 0,
  output_tokens: 0,
  call_count: 0,
  by_operation: {},
  by_model: {}
}

// Budget defaults
budgetData: {
  status: 'ok',
  warnings: [],
  monthly: {
    used: 0,
    limit: 10,
    percentage: 0,
    remaining: 10
  },
  daily: {
    tokens_used: 0,
    tokens_limit: 100000,
    percentage: 0,
    tokens_remaining: 100000
  }
}
```

---

## Key Differences from HTMX

1. **No Alpine.js** - Use React state + hooks
2. **No Chart.js** - Use Recharts (better React integration)
3. **No manual polling** - Use React Query's refetchInterval
4. **Better TypeScript** - Full type safety
5. **Shadcn/ui** - Replace DaisyUI components
6. **Better accessibility** - Semantic HTML + ARIA labels

---

## Next Steps

1. ✅ Analysis complete
2. → Create API client module (`usage.ts`)
3. → Create custom hook (`useUsage.ts`)
4. → Build UsagePage component
5. → Add charts with Recharts
6. → Add to router
7. → Test functionality

---

## Notes

- HTMX page uses **public endpoints** (no auth) for demo user (user_id=1)
- React version should match this behavior initially
- Auto-refresh every 30 seconds (React Query: `refetchInterval: 30000`)
- CSV export can download directly via anchor tag with download attribute
- Budget alerts should be prominent (warning/error states)
- All costs display with **4 decimal places** (`$0.0000`)
- Percentages display with **1 decimal place** (`75.5%`)
