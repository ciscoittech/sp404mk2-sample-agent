import { Pin, PinOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { Sample } from '@/types/api';
import { usePinnedSamples } from '@/stores/pinnedSamplesStore';

interface PinButtonProps {
  sample: Sample;
  className?: string;
}

export function PinButton({ sample, className }: PinButtonProps) {
  const { pinSample, unpinSample, isPinned } = usePinnedSamples();
  const pinned = isPinned(sample.id);

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering parent click handlers
    pinned ? unpinSample(sample.id) : pinSample(sample);
  };

  return (
    <Button
      variant={pinned ? 'default' : 'ghost'}
      size="icon"
      className={cn(
        'h-8 w-8',
        !pinned && 'opacity-0 group-hover:opacity-100 transition-opacity',
        pinned && 'bg-primary text-primary-foreground',
        className
      )}
      onClick={handleClick}
      title={pinned ? 'Unpin sample' : 'Pin sample'}
    >
      {pinned ? (
        <PinOff className="h-4 w-4" />
      ) : (
        <Pin className="h-4 w-4" />
      )}
    </Button>
  );
}
