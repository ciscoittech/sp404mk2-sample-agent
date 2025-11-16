# React Kit Builder Agent

**Purpose**: Build SP-404MK2 kit builder interface with 48-pad layout and drag-and-drop
**Expertise**: React DnD, grid layouts, SP-404 hardware conventions, pad management
**When to Use**: Implementing kit builder, pad grid, sample assignment features
**Output**: Complete SP-404 kit builder with drag-and-drop sample assignment

---

## What This Agent Does

This agent builds the SP-404MK2 kit builder interface by:

1. **Creating Pad Grid** - 4 banks (A/B/C/D) × 12 pads = 48 total pads
2. **Implementing Drag & Drop** - Assign samples to pads via drag
3. **Managing Pad State** - Empty, assigned, playing states
4. **Building Pad Controls** - Play, remove, volume, pitch controls
5. **Kit Management** - Save, export, share kits
6. **Sample Recommendations** - AI-powered suggestions for empty pads

---

## When to Activate

**Use this agent when**:
- Building SP-404 kit interface
- Implementing pad grid layout
- Adding drag-and-drop sample assignment
- Creating kit management features
- Need hardware-accurate pad layout

**Success Criteria**:
- ✅ 48-pad grid displays correctly
- ✅ Drag-and-drop sample assignment works
- ✅ Pads show assigned sample info
- ✅ Pad controls (play, remove) functional
- ✅ Kits save and load correctly
- ✅ Matches SP-404MK2 hardware layout

---

## Agent Workflow

### Phase 1: Create Pad Component (30 min)

```typescript
// src/components/kits/Pad.tsx
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Sample } from '@/types/api';

interface PadProps {
  bank: 'A' | 'B' | 'C' | 'D';
  number: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
  sample?: Sample;
  isPlaying?: boolean;
  onAssign?: (sample: Sample) => void;
  onRemove?: () => void;
  onPlay?: () => void;
  onDrop?: (sample: Sample) => void;
}

export function Pad({
  bank,
  number,
  sample,
  isPlaying,
  onRemove,
  onPlay,
  onDrop,
}: PadProps) {
  const isEmpty = !sample;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.add('bg-primary/10');
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.currentTarget.classList.remove('bg-primary/10');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('bg-primary/10');

    const sampleData = e.dataTransfer.getData('application/json');
    if (sampleData && onDrop) {
      onDrop(JSON.parse(sampleData));
    }
  };

  return (
    <Card
      className={cn(
        'relative h-24 transition-all',
        isEmpty && 'border-dashed border-muted-foreground/25',
        isPlaying && 'ring-2 ring-accent animate-pulse',
        !isEmpty && 'hover:border-primary cursor-pointer'
      )}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Pad Label */}
      <div className="absolute top-1 left-2 text-xs font-mono text-muted-foreground">
        {bank}{number}
      </div>

      {/* Empty State */}
      {isEmpty && (
        <div className="flex items-center justify-center h-full text-muted-foreground/50 text-sm">
          Drop sample here
        </div>
      )}

      {/* Assigned Sample */}
      {!isEmpty && sample && (
        <div className="p-2 pt-5">
          <div className="text-sm font-medium truncate">
            {sample.title}
          </div>
          <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
            {sample.bpm && <span>{Math.round(sample.bpm)} BPM</span>}
            {sample.musical_key && <span>{sample.musical_key}</span>}
          </div>

          {/* Pad Controls */}
          <div className="flex items-center gap-1 mt-2">
            <Button
              size="icon"
              variant="ghost"
              className="h-6 w-6"
              onClick={(e) => {
                e.stopPropagation();
                onPlay?.();
              }}
            >
              <Play className="h-3 w-3" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-6 w-6"
              onClick={(e) => {
                e.stopPropagation();
                onRemove?.();
              }}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
}
```

### Phase 2: Create Pad Grid (30 min)

```typescript
// src/components/kits/PadGrid.tsx
import { Pad } from './Pad';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { Kit, PadAssignment, Sample } from '@/types/api';

interface PadGridProps {
  kit: Kit;
  onPadAssign: (bank: string, padNumber: number, sample: Sample) => void;
  onPadRemove: (bank: string, padNumber: number) => void;
  onPadPlay: (sample: Sample) => void;
  currentlyPlaying?: number;
}

export function PadGrid({
  kit,
  onPadAssign,
  onPadRemove,
  onPadPlay,
  currentlyPlaying,
}: PadGridProps) {
  const banks = ['A', 'B', 'C', 'D'] as const;

  const getPadSample = (bank: string, padNumber: number): Sample | undefined => {
    return kit.samples?.find(
      (assignment) =>
        assignment.pad_bank === bank &&
        assignment.pad_number === padNumber
    )?.sample;
  };

  return (
    <Tabs defaultValue="A" className="w-full">
      <TabsList className="grid w-full grid-cols-4">
        {banks.map((bank) => (
          <TabsTrigger key={bank} value={bank}>
            Bank {bank}
          </TabsTrigger>
        ))}
      </TabsList>

      {banks.map((bank) => (
        <TabsContent key={bank} value={bank} className="mt-4">
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
            {Array.from({ length: 12 }, (_, i) => i + 1).map((padNumber) => {
              const sample = getPadSample(bank, padNumber);

              return (
                <Pad
                  key={`${bank}-${padNumber}`}
                  bank={bank}
                  number={padNumber as any}
                  sample={sample}
                  isPlaying={sample?.id === currentlyPlaying}
                  onDrop={(droppedSample) =>
                    onPadAssign(bank, padNumber, droppedSample)
                  }
                  onRemove={() => onPadRemove(bank, padNumber)}
                  onPlay={() => sample && onPadPlay(sample)}
                />
              );
            })}
          </div>
        </TabsContent>
      ))}
    </Tabs>
  );
}
```

### Phase 3: Make Sample Cards Draggable (15 min)

```typescript
// Update src/components/samples/SampleCard.tsx
export function SampleCard({ sample, onPlay }: SampleCardProps) {
  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData('application/json', JSON.stringify(sample));
    e.dataTransfer.effectAllowed = 'copy';
  };

  return (
    <Card
      draggable
      onDragStart={handleDragStart}
      className="cursor-grab active:cursor-grabbing"
    >
      {/* ... rest of card content */}
    </Card>
  );
}
```

### Phase 4: Create Kit Builder Page (45 min)

```typescript
// src/pages/KitBuilderPage.tsx
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { PadGrid } from '@/components/kits/PadGrid';
import { SampleRecommendations } from '@/components/kits/SampleRecommendations';
import { KitHeader } from '@/components/kits/KitHeader';
import { useKit, useAssignSample, useRemoveSample } from '@/hooks/useKits';
import { useAudioPlayer } from '@/hooks/useAudioPlayer';
import type { Sample } from '@/types/api';

export function KitBuilderPage() {
  const { kitId } = useParams<{ kitId: string }>();
  const { data: kit, isLoading } = useKit(Number(kitId));
  const assignMutation = useAssignSample();
  const removeMutation = useRemoveSample();
  const { handlePlaySample, currentSampleId } = useAudioPlayer();

  const handlePadAssign = async (
    bank: string,
    padNumber: number,
    sample: Sample
  ) => {
    if (!kit) return;

    await assignMutation.mutateAsync({
      kitId: kit.id,
      sampleId: sample.id,
      padBank: bank,
      padNumber,
    });
  };

  const handlePadRemove = async (bank: string, padNumber: number) => {
    if (!kit) return;

    const assignment = kit.samples?.find(
      (a) => a.pad_bank === bank && a.pad_number === padNumber
    );

    if (assignment) {
      await removeMutation.mutateAsync({
        kitId: kit.id,
        assignmentId: assignment.id,
      });
    }
  };

  if (isLoading) {
    return <div>Loading kit...</div>;
  }

  if (!kit) {
    return <div>Kit not found</div>;
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-[1800px]">
      <KitHeader kit={kit} />

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6 mt-6">
        {/* Main Pad Grid */}
        <div className="space-y-4">
          <PadGrid
            kit={kit}
            onPadAssign={handlePadAssign}
            onPadRemove={handlePadRemove}
            onPadPlay={handlePlaySample}
            currentlyPlaying={currentSampleId}
          />
        </div>

        {/* Sidebar - Recommendations */}
        <aside>
          <SampleRecommendations
            kitId={kit.id}
            onAssign={handlePadAssign}
          />
        </aside>
      </div>
    </div>
  );
}
```

### Phase 5: Create Kit Management Hooks (30 min)

```typescript
// src/hooks/useKits.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { kitsApi } from '@/api';
import { queryKeys } from '@/lib/queryClient';

// Get kit by ID
export function useKit(id: number) {
  return useQuery({
    queryKey: queryKeys.kits.detail(id),
    queryFn: () => kitsApi.getById(id),
    enabled: !!id,
  });
}

// List kits
export function useKits() {
  return useQuery({
    queryKey: queryKeys.kits.lists(),
    queryFn: () => kitsApi.list(),
  });
}

// Create kit
export function useCreateKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      kitsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() });
    },
  });
}

// Assign sample to pad
export function useAssignSample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      kitId,
      sampleId,
      padBank,
      padNumber,
    }: {
      kitId: number;
      sampleId: number;
      padBank: string;
      padNumber: number;
    }) => kitsApi.assignSample(kitId, sampleId, padBank, padNumber),
    onSuccess: (_, { kitId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.kits.detail(kitId) });
    },
  });
}

// Remove sample from pad
export function useRemoveSample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      kitId,
      assignmentId,
    }: {
      kitId: number;
      assignmentId: number;
    }) => kitsApi.removeSample(kitId, assignmentId),
    onSuccess: (_, { kitId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.kits.detail(kitId) });
    },
  });
}
```

### Phase 6: Add Sample Recommendations (30 min)

```typescript
// src/components/kits/SampleRecommendations.tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useKitRecommendations } from '@/hooks/useKits';
import { Plus } from 'lucide-react';
import type { Sample } from '@/types/api';

interface SampleRecommendationsProps {
  kitId: number;
  onAssign: (bank: string, padNumber: number, sample: Sample) => void;
}

export function SampleRecommendations({
  kitId,
  onAssign,
}: SampleRecommendationsProps) {
  const { data: recommendations, isLoading } = useKitRecommendations(kitId);

  if (isLoading) {
    return <div>Loading recommendations...</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Recommended Samples</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {recommendations?.map((sample) => (
          <div
            key={sample.id}
            className="flex items-start gap-2 p-2 rounded-lg border hover:bg-accent/50"
          >
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">
                {sample.title}
              </div>
              <div className="text-xs text-muted-foreground">
                {sample.bpm && `${Math.round(sample.bpm)} BPM`}
                {sample.musical_key && ` • ${sample.musical_key}`}
              </div>
            </div>
            <Button
              size="icon"
              variant="ghost"
              className="h-7 w-7 shrink-0"
              onClick={() => {
                // Find first empty pad
                // onAssign('A', 1, sample);
              }}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
```

---

## Testing Checklist

### Pad Grid Layout
- [ ] 4 banks (A, B, C, D) display correctly
- [ ] 12 pads per bank in correct grid
- [ ] Pad labels show bank + number (A1, A2, etc.)
- [ ] Responsive layout on mobile/tablet/desktop

### Drag & Drop
- [ ] Sample cards are draggable
- [ ] Drop zones highlight on drag over
- [ ] Samples assign to correct pad on drop
- [ ] Can drag samples between pads
- [ ] Visual feedback during drag

### Pad States
- [ ] Empty pads show "Drop sample here"
- [ ] Assigned pads show sample info
- [ ] Playing pads have animated border
- [ ] Hover effects work correctly

### Pad Controls
- [ ] Play button plays sample
- [ ] Remove button clears pad
- [ ] Controls don't trigger on drag
- [ ] Keyboard shortcuts work (Space, 1-9)

### Kit Management
- [ ] Kits save to backend
- [ ] Kits load from backend
- [ ] Changes sync via React Query
- [ ] Optimistic updates work

---

## Success Validation

**Kit Builder Complete When**:
1. ✅ 48-pad SP-404 layout displays correctly
2. ✅ Drag-and-drop sample assignment works
3. ✅ All pad controls functional
4. ✅ Kits save and load correctly
5. ✅ Sample recommendations appear
6. ✅ Matches SP-404MK2 hardware conventions

---

**Agent Version**: 1.0
**Last Updated**: 2025-11-16
**Status**: Ready for deployment
