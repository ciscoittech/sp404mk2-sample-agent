/**
 * FilterPanel Component Showcase
 *
 * Interactive demonstration of all FilterPanel features.
 * Use this file to test and preview the component in isolation.
 *
 * To use: Import this component in your app or create a route to it.
 */

import { useState } from 'react';
import { FilterPanel, SampleFilters } from './FilterPanel';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

export function FilterPanelShowcase() {
  const [filters, setFilters] = useState<SampleFilters>({
    bpm_min: 60,
    bpm_max: 180,
  });

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold">FilterPanel Component Showcase</h1>
          <p className="text-muted-foreground mt-2">
            Interactive demonstration of all features
          </p>
        </div>

        <Tabs defaultValue="demo" className="w-full">
          <TabsList>
            <TabsTrigger value="demo">Live Demo</TabsTrigger>
            <TabsTrigger value="state">Current State</TabsTrigger>
            <TabsTrigger value="features">Features</TabsTrigger>
          </TabsList>

          {/* Live Demo Tab */}
          <TabsContent value="demo" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Component Demo */}
              <Card>
                <CardHeader>
                  <CardTitle>FilterPanel Component</CardTitle>
                  <CardDescription>
                    Interact with the component to see how it works
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <FilterPanel
                    filters={filters}
                    onChange={setFilters}
                  />
                </CardContent>
              </Card>

              {/* Current Filter State */}
              <Card>
                <CardHeader>
                  <CardTitle>Current Filter State</CardTitle>
                  <CardDescription>
                    Live updates as you interact with the component
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">Active Filters:</h4>
                      <div className="flex flex-wrap gap-2">
                        {filters.genres && filters.genres.length > 0 && (
                          <Badge>Genres: {filters.genres.join(', ')}</Badge>
                        )}
                        {(filters.bpm_min !== 60 || filters.bpm_max !== 180) && (
                          <Badge>BPM: {filters.bpm_min}-{filters.bpm_max}</Badge>
                        )}
                        {filters.key && (
                          <Badge>
                            Key: {filters.key} {filters.key_mode || ''}
                          </Badge>
                        )}
                        {filters.tags && filters.tags.length > 0 && (
                          <Badge>Tags: {filters.tags.join(', ')}</Badge>
                        )}
                        {!filters.genres?.length &&
                          (filters.bpm_min === 60 && filters.bpm_max === 180) &&
                          !filters.key &&
                          !filters.tags?.length && (
                            <Badge variant="outline">No active filters</Badge>
                          )}
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h4 className="font-semibold mb-2">Raw State:</h4>
                      <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                        {JSON.stringify(filters, null, 2)}
                      </pre>
                    </div>

                    <Separator />

                    <div>
                      <h4 className="font-semibold mb-2">Query String:</h4>
                      <code className="bg-muted p-2 rounded text-xs block overflow-x-auto">
                        {buildQueryString(filters)}
                      </code>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* API Request Preview */}
            <Card>
              <CardHeader>
                <CardTitle>API Request Preview</CardTitle>
                <CardDescription>
                  What would be sent to your backend
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">Endpoint:</h4>
                    <code className="bg-muted p-2 rounded text-sm block">
                      GET /api/samples?{buildQueryString(filters) || 'bpm_min=60&bpm_max=180'}
                    </code>
                  </div>

                  <Separator />

                  <div>
                    <h4 className="font-semibold mb-2">Request Parameters:</h4>
                    <div className="grid grid-cols-2 gap-2">
                      {filters.genres?.length && (
                        <div className="bg-muted p-2 rounded">
                          <span className="font-mono text-xs">genres:</span>{' '}
                          <span className="text-xs">{filters.genres.join(',')}</span>
                        </div>
                      )}
                      {filters.bpm_min && (
                        <div className="bg-muted p-2 rounded">
                          <span className="font-mono text-xs">bpm_min:</span>{' '}
                          <span className="text-xs">{filters.bpm_min}</span>
                        </div>
                      )}
                      {filters.bpm_max && (
                        <div className="bg-muted p-2 rounded">
                          <span className="font-mono text-xs">bpm_max:</span>{' '}
                          <span className="text-xs">{filters.bpm_max}</span>
                        </div>
                      )}
                      {filters.key && (
                        <div className="bg-muted p-2 rounded">
                          <span className="font-mono text-xs">key:</span>{' '}
                          <span className="text-xs">{filters.key}</span>
                        </div>
                      )}
                      {filters.key_mode && (
                        <div className="bg-muted p-2 rounded">
                          <span className="font-mono text-xs">key_mode:</span>{' '}
                          <span className="text-xs">{filters.key_mode}</span>
                        </div>
                      )}
                      {filters.tags?.length && (
                        <div className="bg-muted p-2 rounded">
                          <span className="font-mono text-xs">tags:</span>{' '}
                          <span className="text-xs">{filters.tags.join(',')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* State Tab */}
          <TabsContent value="state">
            <Card>
              <CardHeader>
                <CardTitle>Complete State Object</CardTitle>
                <CardDescription>
                  Full JSON representation of current filters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted p-4 rounded-lg overflow-auto">
                  {JSON.stringify(filters, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Features Tab */}
          <TabsContent value="features" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FeatureCard
                title="Genre Filter"
                features={[
                  'Multi-select from 14 genres',
                  'Visual selection feedback',
                  'Active count badge',
                  'Scrollable list',
                  'Toggle selection with click',
                ]}
              />
              <FeatureCard
                title="BPM Range"
                features={[
                  'Dual-thumb slider (60-180)',
                  'Real-time range display',
                  '4 quick preset buttons',
                  'Labeled presets by genre',
                  'Smooth slider interaction',
                ]}
              />
              <FeatureCard
                title="Musical Key"
                features={[
                  '12 chromatic keys',
                  'Major/Minor mode toggle',
                  'Any Key option',
                  'Mode only shows when key selected',
                  'Clean dropdown interface',
                ]}
              />
              <FeatureCard
                title="Tags"
                features={[
                  'Searchable tag filter',
                  'Multi-select with badges',
                  '20 popular tags included',
                  'Active tags display',
                  'Click badge to remove',
                ]}
              />
              <FeatureCard
                title="UI/UX"
                features={[
                  'Smooth expand/collapse animations',
                  'Active filter count in header',
                  'Clear All button',
                  'Dark theme support',
                  'Responsive design',
                ]}
              />
              <FeatureCard
                title="Technical"
                features={[
                  'Full TypeScript support',
                  'Controlled component pattern',
                  'Memoized computations',
                  'Accessible ARIA labels',
                  'Zero dependencies',
                ]}
              />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// Helper component
function FeatureCard({ title, features }: { title: string; features: string[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {features.map((feature, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="text-primary mt-0.5">✓</span>
              <span className="text-sm">{feature}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

// Helper function
function buildQueryString(filters: SampleFilters): string {
  const params = new URLSearchParams();

  if (filters.genres && filters.genres.length > 0) {
    params.append('genres', filters.genres.join(','));
  }
  if (filters.bpm_min !== undefined && filters.bpm_min !== 60) {
    params.append('bpm_min', filters.bpm_min.toString());
  }
  if (filters.bpm_max !== undefined && filters.bpm_max !== 180) {
    params.append('bpm_max', filters.bpm_max.toString());
  }
  if (filters.key) {
    params.append('key', filters.key);
  }
  if (filters.key_mode) {
    params.append('key_mode', filters.key_mode);
  }
  if (filters.tags && filters.tags.length > 0) {
    params.append('tags', filters.tags.join(','));
  }

  return params.toString();
}

export default FilterPanelShowcase;
