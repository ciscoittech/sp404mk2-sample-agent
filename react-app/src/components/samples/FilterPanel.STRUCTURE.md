# FilterPanel Component Structure

Visual representation of the FilterPanel component hierarchy and features.

## Component Tree

```
FilterPanel
├── Header
│   ├── Filter Icon + Title + Active Count Badge
│   └── Clear All Button (destructive variant)
│
├── Genre Filter (Collapsible)
│   ├── Trigger (Music Icon + "Genre" + Count Badge)
│   └── Content
│       └── ScrollArea (180px)
│           └── Multi-select buttons (14 genres)
│               └── Selected items show X icon
│
├── BPM Range Filter (Collapsible)
│   ├── Trigger (Activity Icon + "BPM Range")
│   └── Content
│       ├── Dual-thumb Slider (60-180)
│       │   └── Label showing current range
│       └── Quick Preset Buttons (2x2 grid)
│           ├── 60-90 (Slow/Hip-Hop)
│           ├── 90-120 (Medium/Trap)
│           ├── 120-140 (Fast/House)
│           └── 140+ (Very Fast/DnB)
│
├── Musical Key Filter (Collapsible)
│   ├── Trigger (Hash Icon + "Musical Key" + Selected Badge)
│   └── Content
│       ├── Key Select Dropdown
│       │   ├── "Any Key" option
│       │   └── 12 chromatic keys (C - B)
│       └── Mode Toggle (only if key selected)
│           ├── Major Button
│           └── Minor Button
│
├── Tags Filter (Collapsible)
│   ├── Trigger (Tag Icon + "Tags" + Count Badge)
│   └── Content
│       ├── Active Tags Display (if any selected)
│       │   └── Removable Badge Pills (hover = destructive)
│       ├── Search Input (filter tags)
│       └── ScrollArea (200px)
│           └── Tag Badges (clickable)
│               └── Selected = filled, Unselected = outline
│
└── Apply Filters Button (primary, full width)
    └── Filter Icon + Text + Active Count
```

## State Management

```typescript
// Parent component manages filter state
const [filters, setFilters] = useState<SampleFilters>({
  genres?: string[];        // Multi-select array
  bpm_min?: number;        // Range start (60-180)
  bpm_max?: number;        // Range end (60-180)
  key?: string;            // Single key (C, C#, etc.)
  key_mode?: 'major' | 'minor';  // Optional mode
  tags?: string[];         // Multi-select array
});

// Component receives controlled props
<FilterPanel
  filters={filters}          // Current state
  onChange={setFilters}      // Update handler
/>
```

## Internal State (Component-managed)

```typescript
// Collapsible section states
const [genreOpen, setGenreOpen] = useState(true);    // Default open
const [bpmOpen, setBpmOpen] = useState(true);        // Default open
const [keyOpen, setKeyOpen] = useState(false);       // Default closed
const [tagsOpen, setTagsOpen] = useState(false);     // Default closed

// Tag search filter
const [tagSearch, setTagSearch] = useState('');
```

## Computed Values (Memoized)

```typescript
// Active filter count for badge
const activeFilterCount = useMemo(() => {
  // Sum of all active filters
  genres.length + (bpm !== default ? 1 : 0) +
  (key ? 1 : 0) + tags.length
}, [filters]);

// Filtered tags based on search
const filteredTags = useMemo(() => {
  // Case-insensitive search
  tags.filter(tag => tag.toLowerCase().includes(search))
}, [tagSearch, availableTags]);
```

## Event Handlers

### Genre Toggle
```typescript
handleGenreToggle(genre: string) => {
  // Add if not selected, remove if selected
  // Update parent via onChange
}
```

### BPM Change
```typescript
handleBpmChange(value: number[]) => {
  // Update range from slider
  onChange({ ...filters, bpm_min: value[0], bpm_max: value[1] })
}

handleBpmPreset(min: number, max: number) => {
  // Quick preset buttons
  onChange({ ...filters, bpm_min: min, bpm_max: max })
}
```

### Key Change
```typescript
handleKeyChange(key: string) => {
  // "any" clears the key
  onChange({ ...filters, key: key === 'any' ? undefined : key })
}

handleKeyModeChange(mode: 'major' | 'minor') => {
  // Toggle mode (click again to clear)
  onChange({ ...filters, key_mode: current === mode ? undefined : mode })
}
```

### Tag Toggle
```typescript
handleTagToggle(tag: string) => {
  // Add if not in array, remove if in array
  onChange({ ...filters, tags: newTags })
}

handleTagRemove(tag: string) => {
  // Remove from active tags badge pills
  onChange({ ...filters, tags: filtered })
}
```

### Clear All
```typescript
handleClearAll() => {
  // Reset to defaults
  onChange({
    bpm_min: 60,
    bpm_max: 180,
    // All other fields undefined
  })
}
```

## Visual States

### Collapsible Sections
- **Trigger**: Always visible, clickable header
  - Muted background (`bg-muted/50`)
  - Hover effect (`hover:bg-muted`)
  - Icon + Label + Badge (if active) + Chevron
- **Content**: Expands/collapses with animation
  - `animate-in slide-in-from-top-1`
  - Padding and spacing for content

### Badges
- **Header Badge**: Shows total active filters
  - `variant="secondary"`
  - Min width for single digits
- **Section Badges**: Show count per section
  - Smaller size (`h-4`)
  - Only appears when section has active filters
- **Tag Badges**:
  - Active: `variant="default"` (filled)
  - Inactive: `variant="outline"` (outlined)
  - Removable: Show X icon, hover shows destructive color

### Buttons
- **Genre Buttons**: Full width, left-aligned
  - Selected: Primary background
  - Unselected: Transparent, hover muted
- **BPM Preset Buttons**: 2-column grid
  - Two-line layout (label + description)
  - Selected: Primary background
- **Mode Buttons**: 50/50 split
  - Selected: Primary background
  - Unselected: Outline variant
- **Clear All**: Ghost variant, disabled when no filters
- **Apply Filters**: Primary variant, full width

## Responsive Design

### Desktop Sidebar (Recommended: 320px / 20rem)
```tsx
<aside className="w-80 border-r p-4 overflow-y-auto">
  <FilterPanel filters={filters} onChange={setFilters} />
</aside>
```

### Mobile Sheet
```tsx
<Sheet>
  <SheetTrigger>
    <Button>Filters</Button>
  </SheetTrigger>
  <SheetContent side="left" className="w-80">
    <FilterPanel filters={filters} onChange={setFilters} />
  </SheetContent>
</Sheet>
```

## Accessibility Features

1. **Semantic Structure**: Proper heading hierarchy
2. **Keyboard Navigation**: All interactive elements focusable
3. **ARIA Support**: Via shadcn/ui components
4. **Focus Indicators**: Visible focus rings
5. **Screen Reader**: Descriptive labels and badges

## Animation Timeline

1. **Initial Render**: Genre and BPM sections open
2. **Section Toggle**:
   - Collapse: Fade out content (150ms)
   - Expand: Slide in from top (200ms)
3. **Filter Change**: Immediate badge updates
4. **Tag Search**: Debounced filtering (no delay for instant feedback)

## Performance Characteristics

- **Memoized Calculations**: activeFilterCount, filteredTags
- **No Unnecessary Re-renders**: Pure handlers, controlled inputs
- **Optimized Scrolling**: ScrollArea with virtualization-ready structure
- **Lazy Badge Rendering**: Only show when count > 0

## Theme Integration

Uses shadcn/ui theme tokens for dark mode support:

```css
/* Backgrounds */
bg-muted/50      /* Section triggers */
bg-muted         /* Hover states */
bg-primary       /* Selected items */
bg-card          /* Container (optional) */

/* Text */
text-muted-foreground  /* Icons, labels */
text-primary-foreground /* Selected text */

/* Interactive */
hover:bg-muted         /* Hover backgrounds */
hover:bg-primary/90    /* Selected hover */
focus-visible:ring     /* Focus indicator */
```

## File Size & Dependencies

**Main Component**: ~490 lines
**Types**: Exported interfaces for TypeScript
**Dependencies**:
- React hooks: useState, useMemo
- shadcn/ui: 9 components
- lucide-react: 9 icons
- Tailwind utilities: cn()

**Bundle Impact**: Minimal (tree-shaken, shared dependencies)
