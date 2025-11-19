# Batch Pages HTMX to React Migration Analysis

## SUBTASK 1: Analysis Complete

### 1. Active Batches Page (active-batches.html)

**UI Elements:**
- Card-based grid layout for active batch processes
- Batch name (extracted from collection_path)
- Status badge (processing/pending/completed)
- Progress bar with percentage
- Samples count (processed/total)
- Error count indicator
- Created timestamp
- Cancel button (for processing batches only)
- Empty state with SVG icon

**HTMX Attributes:**
- `hx-post="/api/v1/public/batch/{batch_id}/cancel"` - Cancel batch action
- `hx-confirm="Are you sure..."` - Confirmation dialog
- `hx-target="closest .card"` - Replace card element
- `hx-swap="outerHTML"` - Replace entire element

**Key Data:**
```typescript
interface BatchCard {
  id: string;
  collection_path: string;
  status: 'pending' | 'processing' | 'completed';
  processed_samples: number;
  total_samples: number;
  progress_percentage: number;
  error_count: number;
  created_at: Date;
}
```

---

### 2. Batch Details Modal (batch-details.html)

**UI Elements:**
- Grid layout with metadata (2 columns)
- Status badge
- Samples count display
- Success rate calculation
- Duration display (seconds/minutes/hours)
- Error log alert box (if errors exist)
- Options divider section
- Options key-value pairs (dynamic)
- Import Results button (if export_path exists)
- Download Results button (if export_path exists)
- Import response div

**HTMX Attributes:**
- `hx-post="/api/v1/public/batch/{batch_id}/import"` - Import results to samples
- `hx-target="#import-response"` - Update import response area
- `hx-swap="innerHTML"` - Replace inner content
- Download link (no HTMX, direct href)

**Key Data:**
```typescript
interface BatchDetails {
  id: string;
  status: BatchStatus;
  processed_samples: number;
  total_samples: number;
  success_count: number;
  error_count: number;
  started_at?: Date;
  completed_at?: Date;
  error_log: string[];
  options: Record<string, any>;
  export_path?: string;
}
```

**Calculations:**
- Success Rate: `(success_count / processed_samples * 100)`
- Duration: `completed_at - started_at` (formatted as s/m/h)

---

### 3. Batch History Table (batch-history.html)

**UI Elements:**
- Zebra-striped table
- Columns: Collection, Status, Samples, Success Rate, Duration, Created, Actions
- Collection name + path (two lines)
- Status badge (color-coded)
- Success rate with color coding (>80% green, >60% yellow, <60% red)
- Duration formatted (s/m/h)
- Created timestamp (mm/dd HH:MM)
- Details button (opens modal)
- Retry button (for failed batches only)
- Modal dialog for each batch
- Empty state with SVG icon

**HTMX Attributes:**
- `hx-get="/api/v1/public/batch/{batch_id}"` - Get batch details
- `hx-target="#batch-details-{batch_id}"` - Update modal content
- `hx-swap="innerHTML"` - Replace modal content
- `onclick="batch_details_{batch_id}.showModal()"` - Open modal
- `hx-post="/api/v1/public/batch/{batch_id}/retry"` - Retry failed batch
- `hx-target="closest tr"` - Replace table row
- `hx-swap="outerHTML"` - Replace entire row

**Key Data:**
```typescript
interface BatchHistoryRow {
  id: string;
  collection_path: string;
  status: BatchStatus;
  processed_samples: number;
  total_samples: number;
  success_count: number;
  error_count: number;
  created_at: Date;
  completed_at?: Date;
}
```

---

### 4. API Endpoints Summary

**Authenticated Routes (`/api/v1/batch`):**
- `POST /` - Create batch (BatchCreate)
- `GET /` - List batches (page, limit, status filter)
- `GET /{batch_id}` - Get batch details
- `POST /{batch_id}/cancel` - Cancel batch
- `WebSocket /{batch_id}/progress` - Real-time updates

**Public Routes (`/api/v1/public/batch`):**
- `POST /` - Create batch (Form data, HTMX support)
- `GET /` - List batches (HTMX support, returns HTML partials)
- `GET /{batch_id}` - Get batch (HTMX support)
- `POST /{batch_id}/import` - Import results to samples
- `POST /{batch_id}/cancel` - Cancel batch
- `POST /{batch_id}/retry` - Retry failed batch
- `GET /{batch_id}/export` - Download JSON file

---

### 5. React Migration Requirements

**New Components Needed:**
1. `BatchPage.tsx` - Main page container
2. `ActiveBatchesList.tsx` - Active batches cards section
3. `BatchCard.tsx` - Individual batch card component
4. `BatchDetailsModal.tsx` - Details modal dialog
5. `BatchHistoryTable.tsx` - History table component
6. `CreateBatchForm.tsx` - New batch creation form
7. `EmptyState.tsx` - Reusable empty state component

**Hooks Needed:**
1. `useBatches.ts` - React Query hooks for batch operations
   - `useActiveBatches()` - Query active batches
   - `useBatchHistory()` - Query completed batches
   - `useBatchDetails(id)` - Query single batch
   - `useCreateBatch()` - Mutation for creation
   - `useCancelBatch()` - Mutation for cancellation
   - `useRetryBatch()` - Mutation for retry
   - `useImportBatch()` - Mutation for import

**WebSocket Integration:**
- Connect to `/api/v1/batch/{batch_id}/progress`
- Update progress in real-time
- Handle connection states (connecting, open, closed, error)
- Auto-reconnect on disconnect
- Parse JSON messages: `{ type: "progress", data: BatchProgress }`

**TypeScript Types:**
```typescript
enum BatchStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

interface Batch {
  id: string;
  name: string;
  collection_path: string;
  status: BatchStatus;
  total_samples: number;
  processed_samples: number;
  success_count: number;
  error_count: number;
  progress_percentage: number;
  options: Record<string, any>;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  processing_time: number;
  success_rate: number;
  cache_dir?: string;
  export_path?: string;
  error_log: string[];
}

interface BatchListResponse {
  items: Batch[];
  total: number;
  page: number;
  pages: number;
}

interface BatchProgress {
  batch_id: string;
  status: BatchStatus;
  total_samples: number;
  processed_samples: number;
  success_count: number;
  error_count: number;
  percentage: number;
  current_sample?: string;
  eta_minutes?: number;
  message?: string;
}
```

---

### 6. Feature Mapping

| HTMX Feature | React Equivalent |
|-------------|------------------|
| `hx-post` | `useMutation()` from React Query |
| `hx-get` | `useQuery()` from React Query |
| `hx-confirm` | shadcn/ui `AlertDialog` component |
| `hx-target` | React state + conditional rendering |
| `hx-swap` | React re-render via state update |
| Auto-refresh | `refetchInterval` in useQuery |
| WebSocket | `useWebSocket` custom hook |
| Modal dialogs | shadcn/ui `Dialog` component |
| Form submission | `react-hook-form` or native |
| Toast notifications | shadcn/ui `Toast` component |

---

### 7. User Workflows

**Workflow 1: View Active Batches**
1. Navigate to /batches
2. See list of active/processing batches
3. Watch progress bars update in real-time
4. Click "Cancel" to stop a batch (with confirmation)

**Workflow 2: View Batch Details**
1. Click batch card or "Details" button
2. Modal opens with full details
3. See real-time progress updates (WebSocket)
4. View error log if errors occurred
5. Click "Import Results" when completed
6. Download JSON results file

**Workflow 3: View History**
1. Scroll to history section
2. See table of past batches
3. Filter by status/date
4. Click "Details" to view any batch
5. Click "Retry" for failed batches

**Workflow 4: Create New Batch**
1. Click "New Batch" button
2. Form dialog opens
3. Select collection path (dropdown/autocomplete)
4. Set options (vibe analysis, etc.)
5. Submit form
6. Batch starts processing
7. Redirect to batch details or show in active list

---

### 8. Implementation Priority

**Phase 1: Core Structure**
1. Create BatchPage.tsx skeleton
2. Define TypeScript types
3. Create useBatches hook with basic queries
4. Implement active batches list (no WebSocket yet)

**Phase 2: Basic Interactions**
5. Add batch details modal
6. Implement cancel mutation
7. Add batch history table
8. Add retry mutation

**Phase 3: Advanced Features**
9. Add WebSocket real-time updates
10. Implement create batch form
11. Add import/export functionality
12. Polish with loading states, animations

**Phase 4: Integration**
13. Add route to App.tsx
14. Add navigation to AppShell.tsx
15. End-to-end testing
16. Error handling improvements

---

## Next Steps

Proceed to SUBTASK 2: Create BatchPage.tsx structure with TypeScript interfaces and component skeleton.
