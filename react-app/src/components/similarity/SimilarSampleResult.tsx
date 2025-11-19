import { memo, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Play } from 'lucide-react';
import { AddToCollectionMenu } from '@/components/collections/AddToCollectionMenu';
import { MatchingVisualization } from './MatchingVisualization';
import { useAudioPreview } from '@/hooks/useAudioPreview';
import type { SimilarityResult } from '@/types/api';

interface SimilarSampleResultProps {
  result: SimilarityResult;
  onSelect?: (sampleId: number) => void;
  onAddToCollection?: (sampleId: number) => void;
}

function SimilarSampleResultComponent({
  result,
  onSelect,
  onAddToCollection,
}: SimilarSampleResultProps) {
  const [isHovered, setIsHovered] = useState(false);
  const audioPreview = useAudioPreview(result.full_url);

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getScoreColor = (score: number) => {
    if (score > 0.8) return 'bg-green-500';
    if (score > 0.6) return 'bg-yellow-500';
    if (score > 0.4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const handleClick = () => {
    audioPreview.play();
    onSelect?.(result.id);
  };

  return (
    <Card
      className="group hover:border-primary/50 transition-all duration-200 cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
    >
      <div className="p-3 space-y-2">
        {/* Header with score and title */}
        <div className="flex items-start gap-3">
          {/* Similarity score badge */}
          <div className="flex-shrink-0">
            <Badge
              className={`${getScoreColor(result.similarity)} text-white font-bold px-2 py-1`}
            >
              {Math.round(result.similarity * 100)}%
            </Badge>
          </div>

          {/* Sample info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-sm truncate">{result.title}</h4>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {formatDuration(result.duration)}
                </p>
              </div>

              {/* Matching visualization dots */}
              <MatchingVisualization result={result} compact />
            </div>

            {/* Metadata */}
            <div className="flex items-center gap-2 mt-2 text-xs flex-wrap">
              {result.bpm && (
                <Badge variant="secondary" className="font-mono text-xs">
                  {Math.round(result.bpm)} BPM
                </Badge>
              )}
              {result.musical_key && (
                <Badge variant="secondary" className="font-mono text-xs">
                  {result.musical_key}
                </Badge>
              )}
              {result.genre && (
                <Badge variant="outline" className="text-xs">
                  {result.genre}
                </Badge>
              )}
              {result.mood && (
                <Badge variant="outline" className="text-xs">
                  {result.mood}
                </Badge>
              )}
            </div>

            {/* Vibe tags */}
            {result.vibe_tags && result.vibe_tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {result.vibe_tags.slice(0, 3).map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {result.vibe_tags.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{result.vibe_tags.length - 3}
                  </Badge>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Actions (visible on hover) */}
        <div
          className={`
            flex items-center gap-2 transition-all duration-200
            ${isHovered ? 'opacity-100 max-h-10' : 'opacity-0 max-h-0 overflow-hidden'}
          `}
        >
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={(e) => {
              e.stopPropagation();
              audioPreview.play();
            }}
          >
            <Play className="h-3 w-3 mr-1" />
            Preview
          </Button>
          <AddToCollectionMenu
            sampleId={result.id}
            variant="outline"
            size="sm"
            className="flex-1"
            onSuccess={() => onAddToCollection?.(result.id)}
          />
        </div>
      </div>
    </Card>
  );
}

export const SimilarSampleResult = memo(SimilarSampleResultComponent);
