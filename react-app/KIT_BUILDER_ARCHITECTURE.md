# Kit Builder - Component Architecture

## Visual Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│                            KitsPage                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Header: "Kit Builder" + [New Kit] Button                         │  │
│  │ Active Kit Selector: [Kit 1] [Kit 2*] [Kit 3]                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────┬──────────────────────────────────┐  │
│  │        PadGrid                │      SampleBrowser               │  │
│  │                               │                                  │  │
│  │  ┌─────────────────────────┐  │  ┌────────────────────────────┐ │  │
│  │  │ Bank Tabs: [A][B][C][D] │  │  │ Search: [____________]     │ │  │
│  │  └─────────────────────────┘  │  │ Filters: [All][Hip-Hop]... │ │  │
│  │                               │  └────────────────────────────┘ │  │
│  │  ┌──┬──┬──┬──┐               │  ┌────────────────────────────┐ │  │
│  │  │P1│P2│P3│P4│ Bank A        │  │ SampleCard (draggable)     │ │  │
│  │  ├──┼──┼──┼──┤               │  │ ┌────────────────────────┐ │ │  │
│  │  │P5│P6│P7│P8│               │  │ │ 🎵 808-kick.wav        │ │ │  │
│  │  ├──┼──┼──┼──┤               │  │ │ [Waveform]             │ │ │  │
│  │  │P9│10│11│12│               │  │ │ 120 BPM | C            │ │ │  │
│  │  └──┴──┴──┴──┘               │  │ │ [Play] [Add to Kit]    │ │ │  │
│  │                               │  │ └────────────────────────┘ │ │  │
│  │  Each Pad:                    │  └────────────────────────────┘ │  │
│  │  - Drop zone                  │  ┌────────────────────────────┐ │  │
│  │  - Shows sample if assigned   │  │ SampleCard (draggable)     │ │  │
│  │  - [X] Remove button          │  │ ...more samples...         │ │  │
│  │  - [▶] Play button            │  └────────────────────────────┘ │  │
│  │                               │                                  │  │
│  └───────────────────────────────┴──────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
KitsPage
│
├─ PageLayout (wrapper)
│
├─ Dialog (kit creation)
│  └─ Input (kit name)
│
├─ Kit Selector
│  └─ Button[] (one per kit)
│     └─ DropdownMenu (export/delete)
│
├─ PadGrid
│  └─ Tabs (banks A/B/C/D)
│     └─ TabsContent (per bank)
│        └─ Pad × 12
│           ├─ Card (drop zone)
│           ├─ Badge (BPM, key)
│           ├─ Button (play)
│           └─ Button (remove)
│
└─ SampleBrowser
   ├─ Input (search)
   ├─ Button[] (genre filters)
   └─ ScrollArea
      └─ SampleCard[] (draggable)
         ├─ WaveformVisualizer
         ├─ Badge[] (BPM, key, tags)
         └─ Button (add to kit)
```

## Data Flow

### Creating a Kit
```
User clicks "New Kit"
  ↓
Dialog opens
  ↓
User enters name
  ↓
handleCreateKit()
  ↓
useCreateKit.mutateAsync()
  ↓
POST /api/v1/kits
  ↓
Kit created in database
  ↓
React Query invalidates cache
  ↓
UI updates with new kit
  ↓
Kit auto-selected
```

### Drag-and-Drop Assignment
```
User drags sample from browser
  ↓
SampleCard.handleDragStart()
  ↓
dataTransfer.setData('application/json', sample)
  ↓
User drags over pad
  ↓
Pad.handleDragOver()
  ↓
Visual feedback (border glow)
  ↓
User drops sample
  ↓
Pad.handleDrop()
  ↓
Parse JSON → get Sample object
  ↓
onDrop(sample) → PadGrid
  ↓
onAssignSample(bank, number, sample) → KitsPage
  ↓
handleAssignSample()
  ↓
useAssignSample.mutateAsync()
  ↓
POST /api/v1/kits/{id}/assign
  ↓
Sample assigned in database
  ↓
React Query invalidates cache
  ↓
UI updates (pad shows sample)
  ↓
Toast notification
```

### Quick Add (Button Click)
```
User clicks "Add to Kit" on sample
  ↓
SampleBrowser.onAddToKit(sample)
  ↓
findFirstEmptyPad()
  ↓
If empty pad found:
  handleAssignSample(bank, number, sample)
  ↓
  [Same as drag-and-drop flow]
Else:
  Toast warning ("All pads full")
```

### Remove Sample
```
User hovers pad with sample
  ↓
[X] button appears
  ↓
User clicks [X]
  ↓
Pad.onRemove()
  ↓
PadGrid.onRemoveSample(bank, number)
  ↓
KitsPage.handleRemoveSample()
  ↓
useRemoveSample.mutateAsync()
  ↓
DELETE /api/v1/kits/{id}/pads/{bank}/{number}
  ↓
Assignment deleted from database
  ↓
React Query invalidates cache
  ↓
UI updates (pad shows "Empty")
  ↓
Toast notification
```

## State Management

### Local State (KitsPage)
```typescript
const [selectedKit, setSelectedKit] = useState<number>();
const [newKitName, setNewKitName] = useState('');
const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
```

### Server State (React Query)
```typescript
const { data: kits } = useKits();                    // All kits
const createKit = useCreateKit();                    // Mutation
const assignSample = useAssignSample();              // Mutation
const removeSample = useRemoveSample();              // Mutation
const { data: samples } = useSamples({ filters });   // Samples for browser
```

### Component State (Pad)
```typescript
const [isDragOver, setIsDragOver] = useState(false);  // Drop zone highlight
```

### Component State (SampleCard)
```typescript
const [isInView, setIsInView] = useState(false);      // Lazy loading
const [isHovered, setIsHovered] = useState(false);    // Hover effects
const [isDragging, setIsDragging] = useState(false);  // Drag feedback
```

### Component State (SampleBrowser)
```typescript
const [search, setSearch] = useState('');                      // Search query
const [selectedGenre, setSelectedGenre] = useState<string>();  // Genre filter
```

## Props Interface

### SampleCard
```typescript
interface SampleCardProps {
  sample: Sample;           // Required
  onPlay?: (sample: Sample) => void;
  onAddToKit?: (sample: Sample) => void;
  draggable?: boolean;      // NEW: Enable drag
}
```

### Pad
```typescript
interface PadProps {
  bank: 'A' | 'B' | 'C' | 'D';
  number: number;           // 1-12
  sample?: Sample;          // undefined = empty pad
  onRemove: () => void;
  onDrop: (sample: Sample) => void;  // NEW: Handle drop
}
```

### PadGrid
```typescript
interface PadGridProps {
  kit: Kit;                 // Current kit with samples
  onAssignSample: (bank: string, number: number, sample: Sample) => void;
  onRemoveSample: (bank: string, number: number) => void;
}
```

### SampleBrowser
```typescript
interface SampleBrowserProps {
  onAddToKit?: (sample: Sample) => void;  // Quick add callback
}
```

## Type Definitions

### Kit
```typescript
interface Kit {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  samples: PadAssignment[];  // All pad assignments
}
```

### PadAssignment
```typescript
interface PadAssignment {
  kit_id: number;
  sample_id: number;
  pad_bank: 'A' | 'B' | 'C' | 'D';
  pad_number: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
  volume?: number;          // 0.0 - 1.0
  pitch_shift?: number;     // -12 to +12 semitones
  sample: Sample;           // Nested sample data
}
```

### Sample
```typescript
interface Sample {
  id: number;
  user_id: number;
  title: string;
  file_path: string;
  file_url: string;         // For streaming
  duration?: number;
  genre?: string;
  bpm?: number;
  musical_key?: string;
  tags: string[];
  rating?: number;
  created_at: string;
  updated_at: string;
  audio_features?: AudioFeatures;
  ai_analysis?: AIAnalysis;
}
```

## Styling System

### Tailwind Classes Used

**Layout:**
- `flex`, `flex-col`, `flex-1`
- `grid`, `grid-cols-4`
- `h-[calc(100vh-4rem)]`
- `w-96`, `p-6`, `gap-3`

**States:**
- `hover:border-primary/50`
- `opacity-50`, `scale-95`
- `group-hover:opacity-100`
- `transition-all`, `duration-200`

**Borders:**
- `border-2`, `border-dashed`
- `border-primary`, `border-border`

**Colors:**
- `bg-primary/10` (drag-over highlight)
- `text-muted-foreground`
- `bg-card`, `bg-background`

### Component Variants (shadcn/ui)

**Button:**
- `variant="default"` - Selected kit
- `variant="outline"` - Unselected kit
- `variant="ghost"` - Remove button

**Badge:**
- `variant="secondary"` - BPM/key
- `variant="outline"` - Tags

**Card:**
- Default for pads and samples

## Performance Considerations

1. **Lazy Loading:**
   - Waveform visualizer loads only when in viewport
   - Intersection Observer API

2. **Memoization:**
   - SampleCard wrapped with React.memo()
   - Prevents re-renders on parent updates

3. **React Query:**
   - Automatic caching
   - Stale-while-revalidate
   - Background refetching

4. **Virtualization (Future):**
   - Could add for large sample lists (1000+)
   - react-virtual or react-window

## Accessibility

1. **Semantic HTML:**
   - `<button>` for actions
   - `<input>` for search
   - Proper heading hierarchy

2. **ARIA:**
   - Labels via shadcn/ui
   - Role attributes

3. **Keyboard:**
   - Tab navigation
   - Enter to submit
   - Escape to close dialogs

4. **Screen Reader:**
   - Toast notifications announced
   - Loading states announced

## Error Handling

1. **API Errors:**
   - Try/catch around all mutations
   - Toast error messages
   - Console.error for debugging

2. **Data Validation:**
   - TypeScript ensures type safety
   - Backend validates requests

3. **Edge Cases:**
   - No kits: Empty state
   - No samples: Empty state
   - All pads full: Warning toast
   - Invalid drag data: Console log

## Testing Strategy

### Unit Tests (Future)
- Test pad assignment logic
- Test drag-and-drop data transfer
- Test first empty pad finder
- Test genre filtering

### Integration Tests (Future)
- Create kit flow
- Assign sample flow
- Remove sample flow
- Search/filter flow

### E2E Tests (Future)
- Full user workflow
- Drag and drop interaction
- Multiple kit management

## Browser Compatibility

**Drag-and-Drop API:**
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile: ⚠️ Limited (no native drag-and-drop)

**Future Mobile Support:**
- Touch event handlers
- Long-press to drag
- react-dnd library (optional)
