import { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { SampleCard } from '@/components/samples/SampleCard';
import { useSamples } from '@/hooks/useSamples';
import type { Sample } from '@/types/api';

interface SampleBrowserProps {
  onAddToKit?: (sample: Sample) => void;
}

export function SampleBrowser({ onAddToKit }: SampleBrowserProps) {
  const [search, setSearch] = useState('');
  const [selectedGenre, setSelectedGenre] = useState<string>();
  const [bpmRange, setBpmRange] = useState<[number, number]>();

  const { data: samples, isLoading } = useSamples({
    limit: 50,
    search: search || undefined,
    genre: selectedGenre,
    bpm_min: bpmRange?.[0],
    bpm_max: bpmRange?.[1],
  });

  const genres = ['Hip-Hop', 'Electronic', 'Jazz', 'Soul', 'Drum Break', 'Vintage'];

  return (
    <div className="h-full flex flex-col border-l border-border bg-background">
      <div className="p-4 border-b border-border space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">Sample Browser</h3>
          <Badge variant="secondary">{samples?.total || 0} samples</Badge>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search samples..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Filter by Genre</span>
          </div>
          <div className="flex flex-wrap gap-1">
            <Button
              variant={selectedGenre === undefined ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedGenre(undefined)}
            >
              All
            </Button>
            {genres.map((genre) => (
              <Button
                key={genre}
                variant={selectedGenre === genre ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedGenre(genre)}
              >
                {genre}
              </Button>
            ))}
          </div>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {isLoading && (
            <div className="text-center py-8 text-muted-foreground">
              Loading samples...
            </div>
          )}

          {!isLoading && samples?.items.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No samples found
            </div>
          )}

          {samples?.items.map((sample) => (
            <SampleCard
              key={sample.id}
              sample={sample}
              draggable
              onAddToKit={onAddToKit}
            />
          ))}
        </div>
      </ScrollArea>

      <div className="p-4 border-t border-border text-xs text-muted-foreground">
        <p>Drag samples onto pads to assign them</p>
      </div>
    </div>
  );
}
