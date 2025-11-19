import { memo, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Activity } from 'lucide-react';
import type { SimilarityResult } from '@/types/api';

interface MatchingVisualizationProps {
  result: SimilarityResult;
  compact?: boolean;
}

function MatchingVisualizationComponent({ result, compact = false }: MatchingVisualizationProps) {
  const [isOpen, setIsOpen] = useState(false);

  const getScoreColor = (score: number) => {
    if (score > 0.8) return 'bg-green-500';
    if (score > 0.6) return 'bg-yellow-500';
    if (score > 0.4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getScoreTextColor = (score: number) => {
    if (score > 0.8) return 'text-green-600 dark:text-green-400';
    if (score > 0.6) return 'text-yellow-600 dark:text-yellow-400';
    if (score > 0.4) return 'text-orange-600 dark:text-orange-400';
    return 'text-red-600 dark:text-red-400';
  };

  // Normalize scores for visualization (0-1 scale)
  const scores = [
    { label: 'Vibe', value: result.similarity, display: `${Math.round(result.similarity * 100)}%` },
    { label: 'Energy', value: result.energy_level || 0.5, display: result.energy_level ? `${Math.round(result.energy_level * 100)}%` : 'N/A' },
    { label: 'Dance', value: result.danceability || 0.5, display: result.danceability ? `${Math.round(result.danceability * 100)}%` : 'N/A' },
    { label: 'Acoustic', value: result.acousticness || 0.5, display: result.acousticness ? `${Math.round(result.acousticness * 100)}%` : 'N/A' },
  ];

  // Compact version - 3 dots showing top scores
  if (compact) {
    const topScores = [...scores].sort((a, b) => b.value - a.value).slice(0, 3);

    return (
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 px-2"
            title="View matching details"
          >
            <div className="flex gap-1 items-center">
              {topScores.map((score, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full ${getScoreColor(score.value)}`}
                  title={`${score.label}: ${score.display}`}
                />
              ))}
            </div>
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Similarity Analysis</DialogTitle>
          </DialogHeader>
          <FullVisualization result={result} scores={scores} />
        </DialogContent>
      </Dialog>
    );
  }

  // Full version
  return <FullVisualization result={result} scores={scores} />;
}

interface FullVisualizationProps {
  result: SimilarityResult;
  scores: Array<{ label: string; value: number; display: string }>;
}

function FullVisualization({ result, scores }: FullVisualizationProps) {
  const getScoreColor = (score: number) => {
    if (score > 0.8) return 'bg-green-500';
    if (score > 0.6) return 'bg-yellow-500';
    if (score > 0.4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getScoreTextColor = (score: number) => {
    if (score > 0.8) return 'text-green-600 dark:text-green-400';
    if (score > 0.6) return 'text-yellow-600 dark:text-yellow-400';
    if (score > 0.4) return 'text-orange-600 dark:text-orange-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Activity className="h-5 w-5 text-primary" />
          <h3 className="text-2xl font-bold">
            <span className={getScoreTextColor(result.similarity)}>
              {Math.round(result.similarity * 100)}%
            </span>
            {' '}Match
          </h3>
        </div>
        <p className="text-sm text-muted-foreground">
          Similarity score based on vibe and musical characteristics
        </p>
      </div>

      {/* Score bars */}
      <div className="space-y-2">
        {scores.map((score) => (
          <div key={score.label} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">{score.label}</span>
              <span className={getScoreTextColor(score.value)}>
                {score.display}
              </span>
            </div>
            <div className="h-2 bg-secondary rounded-full overflow-hidden">
              <div
                className={`h-full ${getScoreColor(score.value)} transition-all duration-300`}
                style={{ width: `${score.value * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Detailed breakdown */}
      <div className="border rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Attribute</TableHead>
              <TableHead>Value</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell className="font-medium">BPM</TableCell>
              <TableCell className="text-sm">
                {result.bpm ? `${Math.round(result.bpm)} BPM` : 'No BPM data'}
              </TableCell>
            </TableRow>

            <TableRow>
              <TableCell className="font-medium">Musical Key</TableCell>
              <TableCell className="text-sm">
                {result.musical_key || 'No key data'}
              </TableCell>
            </TableRow>

            <TableRow>
              <TableCell className="font-medium">Genre</TableCell>
              <TableCell className="text-sm">
                {result.genre || 'No genre data'}
              </TableCell>
            </TableRow>

            <TableRow>
              <TableCell className="font-medium">Mood</TableCell>
              <TableCell className="text-sm">
                {result.mood || 'No mood data'}
                {result.mood_secondary && ` / ${result.mood_secondary}`}
              </TableCell>
            </TableRow>

            <TableRow>
              <TableCell className="font-medium">Energy Level</TableCell>
              <TableCell className="text-sm">
                {result.energy_level !== undefined ? `${Math.round(result.energy_level * 100)}%` : 'No data'}
              </TableCell>
            </TableRow>

            <TableRow>
              <TableCell className="font-medium">Danceability</TableCell>
              <TableCell className="text-sm">
                {result.danceability !== undefined ? `${Math.round(result.danceability * 100)}%` : 'No data'}
              </TableCell>
            </TableRow>

            <TableRow>
              <TableCell className="font-medium">Vibe Tags</TableCell>
              <TableCell className="text-sm">
                {result.vibe_tags && result.vibe_tags.length > 0 ? (
                  <div className="flex flex-wrap gap-1">
                    {result.vibe_tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  'No vibe tags'
                )}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-green-500 rounded-full" />
          <span>&gt;80% Perfect</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-yellow-500 rounded-full" />
          <span>60-80% Good</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-orange-500 rounded-full" />
          <span>40-60% Partial</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-500 rounded-full" />
          <span>&lt;40% Weak</span>
        </div>
      </div>
    </div>
  );
}

export const MatchingVisualization = memo(MatchingVisualizationComponent);
