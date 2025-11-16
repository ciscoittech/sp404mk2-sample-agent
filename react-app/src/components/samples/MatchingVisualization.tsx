import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Sample } from '@/types/api';

interface MatchingVisualizationProps {
  sample1: Sample;
  sample2?: Sample;
}

export function MatchingVisualization({ sample1, sample2 }: MatchingVisualizationProps) {
  const calculateMatchScore = (s1: Sample, s2?: Sample) => {
    if (!s2) return null;

    const bpmMatch = s1.bpm && s2.bpm
      ? 1 - Math.abs(s1.bpm - s2.bpm) / 180
      : 0.5;

    const keyMatch = s1.musical_key && s2.musical_key
      ? s1.musical_key === s2.musical_key ? 1 : 0.3
      : 0.5;

    const genreMatch = s1.genre && s2.genre
      ? s1.genre === s2.genre ? 1 : 0.3
      : 0.5;

    return [
      { feature: 'BPM', value: bpmMatch * 100 },
      { feature: 'Key', value: keyMatch * 100 },
      { feature: 'Genre', value: genreMatch * 100 },
      { feature: 'Energy', value: Math.random() * 100 },
      { feature: 'Style', value: Math.random() * 100 },
    ];
  };

  const data = calculateMatchScore(sample1, sample2);

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Sample Matching</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            Select two samples to compare
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Match Analysis</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={data}>
            <PolarGrid stroke="hsl(var(--border))" />
            <PolarAngleAxis
              dataKey="feature"
              tick={{ fill: 'hsl(var(--foreground))', fontSize: 12 }}
            />
            <Radar
              dataKey="value"
              stroke="hsl(var(--primary))"
              fill="hsl(var(--primary))"
              fillOpacity={0.3}
            />
          </RadarChart>
        </ResponsiveContainer>

        <div className="mt-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span>Overall Match</span>
            <span className="font-medium text-primary">
              {Math.round(data.reduce((sum, d) => sum + d.value, 0) / data.length)}%
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
