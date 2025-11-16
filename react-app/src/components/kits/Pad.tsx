import { useState } from 'react';
import { Play, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Sample } from '@/types/api';

interface PadProps {
  bank: 'A' | 'B' | 'C' | 'D';
  number: number;
  sample?: Sample;
  onRemove: () => void;
  onDrop: (sample: Sample) => void;
}

export function Pad({ bank, number, sample, onRemove, onDrop }: PadProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    try {
      const sampleData = e.dataTransfer.getData('application/json');
      if (sampleData) {
        const droppedSample = JSON.parse(sampleData) as Sample;
        onDrop(droppedSample);
      }
    } catch (error) {
      console.error('Error parsing dropped sample:', error);
    }
  };

  if (!sample) {
    return (
      <Card
        className={`
          border-2 border-dashed transition-all
          ${isDragOver ? 'border-primary bg-primary/10 scale-105' : 'border-border hover:border-primary/50'}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <CardContent className="p-4 h-32 flex items-center justify-center">
          <div className="text-center">
            <p className="text-xs text-muted-foreground font-mono">{bank}{number}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {isDragOver ? 'Drop here' : 'Empty'}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={`
        border-2 transition-all group
        ${isDragOver ? 'border-primary bg-primary/10 scale-105' : 'border-primary hover:shadow-lg'}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <CardContent className="p-3 h-32 flex flex-col justify-between">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <p className="text-xs font-mono text-muted-foreground">{bank}{number}</p>
            <p className="text-sm font-medium truncate mt-1">{sample.title}</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 opacity-0 group-hover:opacity-100"
            onClick={onRemove}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>

        <div className="flex items-center gap-2">
          {sample.bpm && (
            <Badge variant="secondary" className="text-xs font-mono">
              {Math.round(sample.bpm)}
            </Badge>
          )}
          {sample.musical_key && (
            <Badge variant="secondary" className="text-xs">
              {sample.musical_key}
            </Badge>
          )}
        </div>

        <Button variant="outline" size="sm" className="w-full">
          <Play className="h-3 w-3 mr-1" />
          Preview
        </Button>
      </CardContent>
    </Card>
  );
}
