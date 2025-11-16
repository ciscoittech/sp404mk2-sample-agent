# FilterPanel Quick Reference Card

**One-page reference for the FilterPanel component**

---

## Import

```tsx
import { FilterPanel, SampleFilters } from '@/components/samples';
```

---

## Basic Usage

```tsx
const [filters, setFilters] = useState<SampleFilters>({
  bpm_min: 60,
  bpm_max: 180,
});

<FilterPanel
  filters={filters}
  onChange={setFilters}
/>
```

---

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `filters` | `SampleFilters` | ✅ | Current filter state |
| `onChange` | `(filters: SampleFilters) => void` | ✅ | Change handler |
| `availableTags` | `string[]` | ❌ | Custom tag list |
| `className` | `string` | ❌ | Extra CSS classes |

---

## SampleFilters Type

```tsx
interface SampleFilters {
  genres?: string[];           // Multi-select
  bpm_min?: number;           // 60-180
  bpm_max?: number;           // 60-180
  key?: string;               // C, C#, D...
  key_mode?: 'major' | 'minor'; // Optional
  tags?: string[];            // Multi-select
}
```

---

## API Query String

```typescript
// Build query from filters
const params = new URLSearchParams();

if (filters.genres?.length) {
  params.append('genres', filters.genres.join(','));
}
if (filters.bpm_min) {
  params.append('bpm_min', filters.bpm_min.toString());
}
if (filters.bpm_max) {
  params.append('bpm_max', filters.bpm_max.toString());
}
if (filters.key) {
  params.append('key', filters.key);
}
if (filters.key_mode) {
  params.append('key_mode', filters.key_mode);
}
if (filters.tags?.length) {
  params.append('tags', filters.tags.join(','));
}

fetch(`/api/samples?${params.toString()}`);
```

---

## Layout Examples

### Desktop Sidebar (Recommended)
```tsx
<div className="flex">
  <aside className="w-80 border-r p-4 sticky top-0 h-screen overflow-y-auto">
    <FilterPanel filters={filters} onChange={setFilters} />
  </aside>
  <main className="flex-1">
    {/* Content */}
  </main>
</div>
```

### Mobile Sheet
```tsx
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';

<Sheet>
  <SheetTrigger asChild>
    <Button>Filters</Button>
  </SheetTrigger>
  <SheetContent side="left" className="w-80">
    <FilterPanel filters={filters} onChange={setFilters} />
  </SheetContent>
</Sheet>
```

---

## Features

### Filter Sections (All Collapsible)
- **Genre**: 14 music genres, multi-select
- **BPM Range**: Slider (60-180) + 4 quick presets
- **Musical Key**: 12 keys + Major/Minor mode
- **Tags**: Searchable, 20 popular tags

### UI Features
- Active filter count badge
- Clear All button
- Apply Filters button
- Smooth animations
- Dark theme support
- ScrollArea for long lists

---

## Default Values

**Genres**: Hip-Hop, Trap, Jazz, Soul, Electronic, House, Drum & Bass, Lo-Fi, Ambient, Funk, Disco, R&B, Techno, Dubstep

**BPM Presets**:
- 60-90 (Slow/Hip-Hop)
- 90-120 (Medium/Trap)
- 120-140 (Fast/House)
- 140+ (Very Fast/DnB)

**Keys**: C, C#, D, D#, E, F, F#, G, G#, A, A#, B

**Tags**: Vintage, Retro, Modern, Clean, Dirty, Warm, Bright, Dark, Atmospheric, Punchy, Smooth, Gritty, Melodic, Percussive, Bassline, Lead, Pad, Vocal, FX, Loop

---

## Custom Tags

```tsx
<FilterPanel
  filters={filters}
  onChange={setFilters}
  availableTags={['Custom', 'Production', 'Master']}
/>
```

---

## With TanStack Query

```tsx
import { useQuery } from '@tanstack/react-query';

function useSamples(filters: SampleFilters) {
  return useQuery({
    queryKey: ['samples', filters],
    queryFn: () => fetch(`/api/samples?${buildQuery(filters)}`),
  });
}

function SamplesPage() {
  const [filters, setFilters] = useState(/* ... */);
  const { data } = useSamples(filters);

  return (
    <>
      <FilterPanel filters={filters} onChange={setFilters} />
      <SampleGrid samples={data?.samples} />
    </>
  );
}
```

---

## URL Sync (Optional)

```tsx
import { useSearchParams } from 'react-router-dom';

function SamplesPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = useMemo(() => ({
    genres: searchParams.get('genres')?.split(','),
    bpm_min: parseInt(searchParams.get('bpm_min') || '60'),
    bpm_max: parseInt(searchParams.get('bpm_max') || '180'),
    // ... more fields
  }), [searchParams]);

  const handleChange = (newFilters: SampleFilters) => {
    const params = new URLSearchParams();
    // Build params from newFilters
    setSearchParams(params);
  };

  return <FilterPanel filters={filters} onChange={handleChange} />;
}
```

---

## Backend Endpoint

```python
@app.get("/api/samples")
async def get_samples(
    genres: Optional[str] = None,    # Comma-separated
    bpm_min: Optional[int] = 60,
    bpm_max: Optional[int] = 180,
    key: Optional[str] = None,
    key_mode: Optional[str] = None,
    tags: Optional[str] = None,      # Comma-separated
):
    # Parse and filter
    genre_list = genres.split(",") if genres else None
    tag_list = tags.split(",") if tags else None

    # Query database
    query = db.query(Sample)
    if genre_list:
        query = query.filter(Sample.genre.in_(genre_list))
    if bpm_min and bpm_max:
        query = query.filter(Sample.bpm.between(bpm_min, bpm_max))
    # ... more filters

    return {"samples": query.all()}
```

---

## Styling

### Recommended Width
```tsx
<aside className="w-80"> {/* 320px */}
  <FilterPanel ... />
</aside>
```

### Custom Styling
```tsx
<FilterPanel
  filters={filters}
  onChange={setFilters}
  className="rounded-xl shadow-lg"
/>
```

---

## Common Patterns

### Reset Filters
```tsx
const resetFilters = () => {
  setFilters({ bpm_min: 60, bpm_max: 180 });
};
```

### Count Active Filters
```tsx
const activeCount = useMemo(() => {
  let count = 0;
  if (filters.genres?.length) count += filters.genres.length;
  if (filters.bpm_min !== 60 || filters.bpm_max !== 180) count++;
  if (filters.key) count++;
  if (filters.tags?.length) count += filters.tags.length;
  return count;
}, [filters]);
```

### Debounced Changes
```tsx
import { useDebouncedCallback } from 'use-debounce';

const debouncedChange = useDebouncedCallback(
  (filters) => fetchSamples(filters),
  300
);
```

---

## Files

- **FilterPanel.tsx** - Main component
- **FilterPanel.README.md** - Full documentation
- **FilterPanel.example.tsx** - 6 usage examples
- **FilterPanel.INTEGRATION.md** - Backend guide
- **FilterPanel.STRUCTURE.md** - Architecture
- **FilterPanel.MOCKUP.md** - Visual mockups
- **FilterPanel.SUMMARY.md** - Complete summary
- **FilterPanel.QUICKREF.md** - This file

---

## Dependencies

All available in project:
- React (useState, useMemo)
- shadcn/ui (9 components)
- lucide-react (9 icons)
- Tailwind CSS

---

## Status

✅ Production Ready
✅ TypeScript Compiled
✅ Fully Documented
✅ Examples Included

---

**Need Help?** See FilterPanel.README.md for complete docs
