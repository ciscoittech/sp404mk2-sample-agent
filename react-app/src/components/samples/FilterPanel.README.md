# FilterPanel Component

Professional, collapsible filter panel for the SP404MK2 Sample Agent Samples page.

## Features

### 1. Collapsible Filter Sections
- **Genre Filter**: Multi-select with 14+ music genres
- **BPM Range**: Dual-thumb slider (60-180 BPM) with quick presets
- **Musical Key**: Dropdown selection with Major/Minor mode toggle
- **Tags**: Searchable multi-select with popular production tags

### 2. Smart UI/UX
- Smooth expand/collapse animations
- Active filter count badges
- Visual feedback for selected items
- Scroll areas for long lists
- Responsive design for sidebars

### 3. Professional Styling
- Dark theme compatible
- shadcn/ui components
- lucide-react icons
- Tailwind CSS utilities
- Consistent spacing and typography

## Installation

The component uses these shadcn/ui components (already installed):
```bash
# Components used:
- collapsible
- select
- slider
- badge
- button
- scroll-area
- input
- label
```

## Basic Usage

```tsx
import { useState } from 'react';
import { FilterPanel, SampleFilters } from '@/components/samples';

function SamplesPage() {
  const [filters, setFilters] = useState<SampleFilters>({
    bpm_min: 60,
    bpm_max: 180,
  });

  return (
    <div className="w-80">
      <FilterPanel
        filters={filters}
        onChange={setFilters}
      />
    </div>
  );
}
```

## Props

### `FilterPanelProps`

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `filters` | `SampleFilters` | Yes | - | Current filter state |
| `onChange` | `(filters: SampleFilters) => void` | Yes | - | Filter change handler |
| `availableTags` | `string[]` | No | `POPULAR_TAGS` | List of available tags |
| `className` | `string` | No | - | Additional CSS classes |

### `SampleFilters`

```typescript
interface SampleFilters {
  genres?: string[];        // Selected genres
  bpm_min?: number;        // Minimum BPM (default: 60)
  bpm_max?: number;        // Maximum BPM (default: 180)
  key?: string;            // Musical key (C, C#, D, etc.)
  key_mode?: 'major' | 'minor';  // Key mode
  tags?: string[];         // Selected tags
}
```

## Default Values

### Genres (14 options)
```typescript
['Hip-Hop', 'Trap', 'Jazz', 'Soul', 'Electronic', 'House',
 'Drum & Bass', 'Lo-Fi', 'Ambient', 'Funk', 'Disco', 'R&B',
 'Techno', 'Dubstep']
```

### Musical Keys (12 chromatic notes)
```typescript
['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
```

### BPM Presets
| Preset | Range | Description |
|--------|-------|-------------|
| 60-90 | 60-90 BPM | Slow/Hip-Hop |
| 90-120 | 90-120 BPM | Medium/Trap |
| 120-140 | 120-140 BPM | Fast/House |
| 140+ | 140-180 BPM | Very Fast/DnB |

### Popular Tags (20 options)
```typescript
['Vintage', 'Retro', 'Modern', 'Clean', 'Dirty', 'Warm', 'Bright',
 'Dark', 'Atmospheric', 'Punchy', 'Smooth', 'Gritty', 'Melodic',
 'Percussive', 'Bassline', 'Lead', 'Pad', 'Vocal', 'FX', 'Loop']
```

## Advanced Usage

### With Custom Tags
```tsx
<FilterPanel
  filters={filters}
  onChange={setFilters}
  availableTags={['Custom', 'Production', 'Master', 'Draft']}
/>
```

### With API Integration
```tsx
const handleFilterChange = (newFilters: SampleFilters) => {
  setFilters(newFilters);

  // Build API query
  const params = new URLSearchParams();
  if (newFilters.genres?.length) {
    params.append('genres', newFilters.genres.join(','));
  }
  if (newFilters.bpm_min) {
    params.append('bpm_min', newFilters.bpm_min.toString());
  }
  if (newFilters.bpm_max) {
    params.append('bpm_max', newFilters.bpm_max.toString());
  }

  fetch(`/api/samples?${params.toString()}`)
    .then(res => res.json())
    .then(setSamples);
};
```

### In a Sidebar Layout
```tsx
<div className="flex">
  {/* Sidebar */}
  <aside className="w-80 border-r p-4 overflow-y-auto">
    <FilterPanel
      filters={filters}
      onChange={handleFilterChange}
    />
  </aside>

  {/* Main content */}
  <main className="flex-1 p-6">
    <SampleGrid samples={samples} />
  </main>
</div>
```

### Mobile Responsive (with Sheet)
```tsx
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';

function ResponsiveFilters() {
  return (
    <>
      {/* Desktop: Fixed sidebar */}
      <aside className="hidden md:block w-80 fixed">
        <FilterPanel filters={filters} onChange={setFilters} />
      </aside>

      {/* Mobile: Sheet overlay */}
      <Sheet>
        <SheetTrigger asChild>
          <Button className="md:hidden">Filters</Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-80">
          <FilterPanel filters={filters} onChange={setFilters} />
        </SheetContent>
      </Sheet>
    </>
  );
}
```

## Component Behavior

### Active Filter Count
The header shows a badge with the total number of active filters:
- Each selected genre counts as 1
- Custom BPM range counts as 1 (if not 60-180)
- Selected key counts as 1
- Each selected tag counts as 1

### Clear All
The "Clear All" button:
- Resets all filters to defaults
- Sets BPM to 60-180
- Clears genres, key, and tags
- Disabled when no filters are active

### Collapsible Sections
Each filter section:
- Can be independently expanded/collapsed
- Shows active filter count in header
- Genre and BPM are open by default
- Key and Tags are closed by default
- Smooth slide-in animations

### Tag Search
The tag filter includes:
- Search input to filter available tags
- Real-time filtering as you type
- Case-insensitive search
- Shows "No tags found" when empty

## Styling

### Default Classes
The component includes default styling with:
- `space-y-4`: Vertical spacing
- Dark theme support via theme variables
- Responsive text sizes
- Hover and active states
- Smooth transitions

### Custom Styling
Add custom classes via the `className` prop:
```tsx
<FilterPanel
  filters={filters}
  onChange={setFilters}
  className="rounded-xl shadow-lg p-6"
/>
```

### Theme Variables
Uses shadcn/ui theme tokens:
- `bg-muted`: Section backgrounds
- `bg-primary`: Selected items
- `text-muted-foreground`: Secondary text
- `border`: Component borders

## Accessibility

The component follows accessibility best practices:
- Semantic HTML structure
- ARIA labels via shadcn/ui components
- Keyboard navigation support
- Focus indicators
- Screen reader friendly

## Performance

### Optimizations
- `useMemo` for computed values (activeFilterCount, filteredTags)
- Debounced tag search
- Controlled component pattern
- No unnecessary re-renders

### Bundle Size
Imports only required icons and components to minimize bundle size.

## TypeScript Support

Full TypeScript support with:
- Exported `SampleFilters` interface
- Exported `FilterPanelProps` interface
- Type-safe event handlers
- IntelliSense for all props

## Examples

See `FilterPanel.example.tsx` for complete usage examples:
1. Basic usage
2. Sidebar layout
3. Custom tags
4. API integration
5. URL query params sync
6. Mobile responsive with Sheet

## File Location

```
react-app/src/components/samples/
├── FilterPanel.tsx          # Main component
├── FilterPanel.example.tsx  # Usage examples
├── FilterPanel.README.md    # This file
└── index.ts                 # Exports
```

## Backend Integration

The filter structure matches the backend API expectations:

```python
# FastAPI endpoint example
@app.get("/api/samples")
async def get_samples(
    genres: Optional[str] = None,  # Comma-separated
    bpm_min: Optional[int] = 60,
    bpm_max: Optional[int] = 180,
    key: Optional[str] = None,
    key_mode: Optional[str] = None,
    tags: Optional[str] = None,    # Comma-separated
):
    # Filter samples based on parameters
    pass
```

## Related Components

- `SampleCard`: Display individual samples
- `SampleGrid`: Grid layout for samples
- `MatchingVisualization`: Visual matching display

## Future Enhancements

Potential improvements:
- [ ] Save filter presets
- [ ] Share filter URLs
- [ ] Recent filters history
- [ ] Advanced key detection (scales, modes)
- [ ] Custom BPM presets
- [ ] Tag autocomplete from API
- [ ] Filter analytics
- [ ] Bulk operations on filtered samples

## Support

For issues or questions:
1. Check the examples in `FilterPanel.example.tsx`
2. Review this README
3. See shadcn/ui docs for component APIs
4. Check backend API documentation

## License

Part of SP404MK2 Sample Agent project.
