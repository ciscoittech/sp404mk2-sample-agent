import { useState } from 'react';
import { PageLayout } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SamplePlayer } from '@/components/audio/SamplePlayer';
import { WaveformVisualizer } from '@/components/audio/WaveformVisualizer.enhanced';
import type { Sample } from '@/types/api';

const mockSample: Sample = {
  id: 1,
  user_id: 1,
  title: 'Test Sample - Jazz Loop',
  file_path: '/samples/test.wav',
  file_url: 'http://localhost:8100/api/v1/public/samples/1/download',
  duration: 120,
  genre: 'Jazz',
  bpm: 120,
  musical_key: 'Am',
  tags: ['jazz', 'loop', 'vintage', 'mellow'],
  rating: 4,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

export function AudioPlayerTest() {
  const [playbackEvents, setPlaybackEvents] = useState<string[]>([]);

  const addEvent = (event: string) => {
    setPlaybackEvents((prev) => [`${new Date().toLocaleTimeString()}: ${event}`, ...prev.slice(0, 9)]);
  };

  return (
    <PageLayout title="Audio Player Test">
      <div className="space-y-8">
        {/* Introduction */}
        <Card>
          <CardHeader>
            <CardTitle>Audio Player Testing Suite</CardTitle>
            <CardDescription>
              Test the WaveformVisualizer and SamplePlayer components with various configurations.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <p>
                <strong>Keyboard Shortcuts:</strong>
              </p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>
                  <Badge variant="outline" className="mr-2">
                    Space
                  </Badge>
                  Play/Pause
                </li>
                <li>
                  <Badge variant="outline" className="mr-2">
                    ← →
                  </Badge>
                  Skip backward/forward 5 seconds
                </li>
                <li>
                  <Badge variant="outline" className="mr-2">
                    ↑ ↓
                  </Badge>
                  Increase/decrease volume
                </li>
                <li>
                  <Badge variant="outline" className="mr-2">
                    M
                  </Badge>
                  Mute/Unmute
                </li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Full SamplePlayer */}
        <Card>
          <CardHeader>
            <CardTitle>Full Sample Player</CardTitle>
            <CardDescription>Complete player with metadata and controls</CardDescription>
          </CardHeader>
          <CardContent>
            <SamplePlayer
              sample={mockSample}
              showMetadata={true}
              compact={false}
              onReady={() => addEvent('Player ready')}
              onPlay={() => addEvent('Playback started')}
              onPause={() => addEvent('Playback paused')}
              onFinish={() => addEvent('Playback finished')}
            />
          </CardContent>
        </Card>

        {/* Compact SamplePlayer */}
        <Card>
          <CardHeader>
            <CardTitle>Compact Sample Player</CardTitle>
            <CardDescription>Minimal player without metadata</CardDescription>
          </CardHeader>
          <CardContent>
            <SamplePlayer sample={mockSample} compact={true} showMetadata={false} />
          </CardContent>
        </Card>

        {/* WaveformVisualizer only */}
        <Card>
          <CardHeader>
            <CardTitle>Waveform Visualizer Only</CardTitle>
            <CardDescription>Just the waveform with full controls</CardDescription>
          </CardHeader>
          <CardContent>
            <WaveformVisualizer
              audioUrl={mockSample.file_url}
              height={128}
              showControls={true}
              compact={false}
            />
          </CardContent>
        </Card>

        {/* Compact Waveform */}
        <Card>
          <CardHeader>
            <CardTitle>Compact Waveform</CardTitle>
            <CardDescription>Minimal waveform for grid views</CardDescription>
          </CardHeader>
          <CardContent>
            <WaveformVisualizer
              audioUrl={mockSample.file_url}
              height={64}
              showControls={true}
              compact={true}
            />
          </CardContent>
        </Card>

        {/* Event Log */}
        <Card>
          <CardHeader>
            <CardTitle>Playback Events</CardTitle>
            <CardDescription>Recent audio player events</CardDescription>
          </CardHeader>
          <CardContent>
            {playbackEvents.length === 0 ? (
              <p className="text-sm text-muted-foreground">No events yet. Try playing the audio above.</p>
            ) : (
              <ul className="space-y-1 font-mono text-xs">
                {playbackEvents.map((event, index) => (
                  <li key={index} className="text-muted-foreground">
                    {event}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Feature Checklist */}
        <Card>
          <CardHeader>
            <CardTitle>Testing Checklist</CardTitle>
            <CardDescription>Manual testing checklist</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Audio loads and waveform displays correctly</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Play button starts playback</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Pause button stops playback</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Progress bar updates during playback</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Clicking waveform seeks to position</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Volume control adjusts audio level</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Speed control changes playback rate</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Skip buttons work (±5 seconds)</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Keyboard shortcuts work (Space, arrows, M)</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>No memory leaks (check DevTools after playing multiple samples)</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Responsive design works on mobile</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </PageLayout>
  );
}
