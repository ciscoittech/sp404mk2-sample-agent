import { useState } from 'react';
import { PageLayout } from '@/components/layout/PageLayout';
import { WaveformVisualizer } from '@/components/audio';
import { FilterPanel, type SampleFilters } from '@/components/samples/FilterPanel';
import { UploadDropZone } from '@/components/upload';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export function ComponentsDemo() {
  const [filters, setFilters] = useState<SampleFilters>({});

  // Sample audio URL for demo (you can replace with actual audio file URL)
  const sampleAudioUrl = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3';

  const handleFilterChange = (newFilters: SampleFilters) => {
    setFilters(newFilters);
    console.log('Filters applied:', newFilters);
  };

  return (
    <PageLayout title="Week 2 Components Demo">
      <div className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle>Week 2 Component Showcase</CardTitle>
            <CardDescription>
              Testing WaveformVisualizer, FilterPanel, and UploadDropZone
            </CardDescription>
          </CardHeader>
        </Card>

        <Tabs defaultValue="waveform" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="waveform">Waveform Player</TabsTrigger>
            <TabsTrigger value="filters">Advanced Filters</TabsTrigger>
            <TabsTrigger value="upload">File Upload</TabsTrigger>
          </TabsList>

          <TabsContent value="waveform" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Waveform Visualizer</CardTitle>
                <CardDescription>
                  Audio player with waveform visualization using wavesurfer.js
                </CardDescription>
              </CardHeader>
              <CardContent>
                <WaveformVisualizer audioUrl={sampleAudioUrl} height={128} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="filters" className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Filter Panel</CardTitle>
                  <CardDescription>
                    Advanced filtering with BPM range, genre, and key selection
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <FilterPanel onFilterChange={handleFilterChange} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Active Filters</CardTitle>
                  <CardDescription>Current filter state (check console)</CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-secondary p-4 rounded-lg text-xs overflow-auto">
                    {JSON.stringify(filters, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="upload" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Upload Drop Zone</CardTitle>
                <CardDescription>
                  Drag and drop file upload with react-dropzone
                </CardDescription>
              </CardHeader>
              <CardContent>
                <UploadDropZone />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </PageLayout>
  );
}
