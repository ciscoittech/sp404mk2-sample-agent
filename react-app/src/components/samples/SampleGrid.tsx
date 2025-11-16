import { SampleCard } from './SampleCard';
import type { Sample } from '@/types/api';

interface SampleGridProps {
  samples: Sample[];
  onPlay?: (sample: Sample) => void;
  onAddToKit?: (sample: Sample) => void;
}

export function SampleGrid({ samples, onPlay, onAddToKit }: SampleGridProps) {
  if (samples.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No samples found</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {samples.map((sample) => (
        <SampleCard
          key={sample.id}
          sample={sample}
          onPlay={onPlay}
          onAddToKit={onAddToKit}
        />
      ))}
    </div>
  );
}
