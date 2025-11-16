import { useState, useMemo } from 'react';
import { useVibeSearch } from '@/hooks/useVibeSearch';
import { SampleGrid } from '@/components/samples/SampleGrid';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Search, Sparkles } from 'lucide-react';
import type { VibeSearchFilters } from '@/types/api';

const VIBE_SUGGESTIONS = [
  'Dark moody loop',
  'Energetic trap drums',
  'Smooth jazz vibes',
  'Chill lo-fi beat',
  'Funk bass groove',
  'Ambient pad',
  'Vintage vinyl sample',
  'Heavy bass drop',
];

export function VibeSearchPage() {
  const [query, setQuery] = useState('');
  const [filters] = useState<VibeSearchFilters>({});
  const vibeSearch = useVibeSearch();

  const handleSearch = (searchQuery: string) => {
    if (!searchQuery.trim()) {
      return;
    }
    vibeSearch.mutate({ query: searchQuery, filters, limit: 20 });
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    handleSearch(suggestion);
  };

  const results = vibeSearch.data?.results || [];
  const isLoading = vibeSearch.isPending;
  const error = vibeSearch.error;

  // Calculate stats
  const stats = useMemo(() => {
    if (!results.length) return null;
    const similarities = results.map(r => r.similarity);
    const avgSimilarity = similarities.reduce((a, b) => a + b, 0) / similarities.length;
    const bpms = results.map(r => r.bpm).filter(Boolean);
    return {
      count: results.length,
      avgSimilarity: (avgSimilarity * 100).toFixed(1),
      bpmMin: Math.min(...bpms),
      bpmMax: Math.max(...bpms),
    };
  }, [results]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Vibe Search</h1>
        <p className="text-muted-foreground mt-1">
          Find samples by describing the vibe you want
        </p>
      </div>

      {/* Search Input */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Describe Your Vibe</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <Textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., 'Dark, moody loop with atmospheric pads' or 'Energetic trap drums with heavy bass'"
              className="min-h-20"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                  handleSearch(query);
                }
              }}
            />
            <Button
              onClick={() => handleSearch(query)}
              disabled={!query.trim() || isLoading}
              className="w-full gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4" />
                  Search Vibes
                </>
              )}
            </Button>
          </div>

          {/* Suggestions */}
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-2">
              Try these vibes:
            </p>
            <div className="flex flex-wrap gap-2">
              {VIBE_SUGGESTIONS.map((suggestion) => (
                <Badge
                  key={suggestion}
                  variant="outline"
                  className="cursor-pointer hover:bg-primary/10"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  <Sparkles className="h-3 w-3 mr-1" />
                  {suggestion}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error State */}
      {error && (
        <Card className="bg-destructive/10 border-destructive/20">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">
              {error instanceof Error ? error.message : 'Search failed'}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Results Stats */}
      {stats && (
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-2xl font-bold">{stats.count}</p>
                <p className="text-xs text-muted-foreground">Results Found</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.avgSimilarity}%</p>
                <p className="text-xs text-muted-foreground">Avg Match</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.bpmMin}</p>
                <p className="text-xs text-muted-foreground">Min BPM</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.bpmMax}</p>
                <p className="text-xs text-muted-foreground">Max BPM</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results Grid */}
      {results.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-4">
            Matching Samples ({results.length})
          </h2>
          <SampleGrid samples={results} />
        </div>
      )}

      {/* Empty State */}
      {!isLoading && results.length === 0 && query && (
        <Card className="text-center py-12">
          <CardContent>
            <p className="text-muted-foreground">
              No samples found for "{query}". Try a different vibe!
            </p>
          </CardContent>
        </Card>
      )}

      {/* Initial State */}
      {!isLoading && results.length === 0 && !query && (
        <Card className="text-center py-12 bg-primary/5 border-primary/20">
          <CardContent>
            <Sparkles className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
            <p className="text-muted-foreground">
              Describe what kind of sample you're looking for. Our AI will find
              the perfect matches from your library.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
