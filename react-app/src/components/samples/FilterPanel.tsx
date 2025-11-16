import { useState, useMemo } from 'react';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import {
  ChevronDown,
  ChevronUp,
  X,
  Filter,
  RotateCcw,
  Music,
  Activity,
  Hash,
  Tag,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Types
export interface SampleFilters {
  genres?: string[];
  bpm_min?: number;
  bpm_max?: number;
  key?: string;
  key_mode?: 'major' | 'minor';
  tags?: string[];
}

export interface FilterPanelProps {
  filters: SampleFilters;
  onChange: (filters: SampleFilters) => void;
  availableTags?: string[];
  className?: string;
}

// Constants
const GENRES = [
  'Hip-Hop',
  'Trap',
  'Jazz',
  'Soul',
  'Electronic',
  'House',
  'Drum & Bass',
  'Lo-Fi',
  'Ambient',
  'Funk',
  'Disco',
  'R&B',
  'Techno',
  'Dubstep',
];

const KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

const BPM_PRESETS = [
  { label: '60-90', min: 60, max: 90, description: 'Slow/Hip-Hop' },
  { label: '90-120', min: 90, max: 120, description: 'Medium/Trap' },
  { label: '120-140', min: 120, max: 140, description: 'Fast/House' },
  { label: '140+', min: 140, max: 180, description: 'Very Fast/DnB' },
];

const POPULAR_TAGS = [
  'Vintage',
  'Retro',
  'Modern',
  'Clean',
  'Dirty',
  'Warm',
  'Bright',
  'Dark',
  'Atmospheric',
  'Punchy',
  'Smooth',
  'Gritty',
  'Melodic',
  'Percussive',
  'Bassline',
  'Lead',
  'Pad',
  'Vocal',
  'FX',
  'Loop',
];

export function FilterPanel({
  filters,
  onChange,
  availableTags = POPULAR_TAGS,
  className,
}: FilterPanelProps) {
  // Collapsible section states
  const [genreOpen, setGenreOpen] = useState(true);
  const [bpmOpen, setBpmOpen] = useState(true);
  const [keyOpen, setKeyOpen] = useState(false);
  const [tagsOpen, setTagsOpen] = useState(false);

  // Tag search
  const [tagSearch, setTagSearch] = useState('');

  // Computed values
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.genres && filters.genres.length > 0) count += filters.genres.length;
    if (filters.bpm_min !== 60 || filters.bpm_max !== 180) count += 1;
    if (filters.key) count += 1;
    if (filters.tags && filters.tags.length > 0) count += filters.tags.length;
    return count;
  }, [filters]);

  const filteredTags = useMemo(() => {
    if (!tagSearch) return availableTags;
    return availableTags.filter((tag) =>
      tag.toLowerCase().includes(tagSearch.toLowerCase())
    );
  }, [tagSearch, availableTags]);

  // Handlers
  const handleGenreToggle = (genre: string) => {
    const currentGenres = filters.genres || [];
    const newGenres = currentGenres.includes(genre)
      ? currentGenres.filter((g) => g !== genre)
      : [...currentGenres, genre];

    onChange({
      ...filters,
      genres: newGenres.length > 0 ? newGenres : undefined,
    });
  };

  const handleBpmChange = (value: number[]) => {
    onChange({
      ...filters,
      bpm_min: value[0],
      bpm_max: value[1],
    });
  };

  const handleBpmPreset = (min: number, max: number) => {
    onChange({
      ...filters,
      bpm_min: min,
      bpm_max: max,
    });
  };

  const handleKeyChange = (key: string) => {
    onChange({
      ...filters,
      key: key === 'any' ? undefined : key,
    });
  };

  const handleKeyModeChange = (mode: 'major' | 'minor') => {
    onChange({
      ...filters,
      key_mode: filters.key_mode === mode ? undefined : mode,
    });
  };

  const handleTagToggle = (tag: string) => {
    const currentTags = filters.tags || [];
    const newTags = currentTags.includes(tag)
      ? currentTags.filter((t) => t !== tag)
      : [...currentTags, tag];

    onChange({
      ...filters,
      tags: newTags.length > 0 ? newTags : undefined,
    });
  };

  const handleTagRemove = (tag: string) => {
    const newTags = (filters.tags || []).filter((t) => t !== tag);
    onChange({
      ...filters,
      tags: newTags.length > 0 ? newTags : undefined,
    });
  };

  const handleClearAll = () => {
    onChange({
      bpm_min: 60,
      bpm_max: 180,
    });
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <h3 className="text-sm font-semibold">Filters</h3>
          {activeFilterCount > 0 && (
            <Badge variant="secondary" className="h-5 min-w-5 px-1.5">
              {activeFilterCount}
            </Badge>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleClearAll}
          disabled={activeFilterCount === 0}
          className="h-8 gap-1.5"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Clear All
        </Button>
      </div>

      {/* Filter Sections */}
      <div className="space-y-2">
        {/* Genre Filter */}
        <Collapsible open={genreOpen} onOpenChange={setGenreOpen}>
          <CollapsibleTrigger className="flex w-full items-center justify-between rounded-lg bg-muted/50 px-3 py-2 text-sm font-medium hover:bg-muted transition-colors">
            <div className="flex items-center gap-2">
              <Music className="h-4 w-4 text-muted-foreground" />
              <span>Genre</span>
              {filters.genres && filters.genres.length > 0 && (
                <Badge variant="secondary" className="h-4 min-w-4 px-1 text-xs">
                  {filters.genres.length}
                </Badge>
              )}
            </div>
            {genreOpen ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            )}
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-3 px-1 animate-in slide-in-from-top-1">
            <ScrollArea className="h-[180px]">
              <div className="space-y-1.5 pr-4">
                {GENRES.map((genre) => (
                  <button
                    key={genre}
                    onClick={() => handleGenreToggle(genre)}
                    className={cn(
                      'w-full flex items-center justify-between px-3 py-2 rounded-md text-sm transition-colors',
                      filters.genres?.includes(genre)
                        ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                        : 'hover:bg-muted'
                    )}
                  >
                    <span>{genre}</span>
                    {filters.genres?.includes(genre) && (
                      <X className="h-3.5 w-3.5" />
                    )}
                  </button>
                ))}
              </div>
            </ScrollArea>
          </CollapsibleContent>
        </Collapsible>

        {/* BPM Range Filter */}
        <Collapsible open={bpmOpen} onOpenChange={setBpmOpen}>
          <CollapsibleTrigger className="flex w-full items-center justify-between rounded-lg bg-muted/50 px-3 py-2 text-sm font-medium hover:bg-muted transition-colors">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span>BPM Range</span>
            </div>
            {bpmOpen ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            )}
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-3 px-3 space-y-4 animate-in slide-in-from-top-1">
            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                {filters.bpm_min ?? 60} - {filters.bpm_max ?? 180} BPM
              </Label>
              <Slider
                value={[filters.bpm_min ?? 60, filters.bpm_max ?? 180]}
                onValueChange={handleBpmChange}
                min={60}
                max={180}
                step={1}
                className="w-full"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              {BPM_PRESETS.map((preset) => (
                <Button
                  key={preset.label}
                  variant="outline"
                  size="sm"
                  onClick={() => handleBpmPreset(preset.min, preset.max)}
                  className={cn(
                    'flex flex-col h-auto py-2 gap-0.5',
                    filters.bpm_min === preset.min &&
                      filters.bpm_max === preset.max &&
                      'bg-primary text-primary-foreground hover:bg-primary/90'
                  )}
                >
                  <span className="text-xs font-semibold">{preset.label}</span>
                  <span className="text-[10px] text-muted-foreground">
                    {preset.description}
                  </span>
                </Button>
              ))}
            </div>
          </CollapsibleContent>
        </Collapsible>

        {/* Musical Key Filter */}
        <Collapsible open={keyOpen} onOpenChange={setKeyOpen}>
          <CollapsibleTrigger className="flex w-full items-center justify-between rounded-lg bg-muted/50 px-3 py-2 text-sm font-medium hover:bg-muted transition-colors">
            <div className="flex items-center gap-2">
              <Hash className="h-4 w-4 text-muted-foreground" />
              <span>Musical Key</span>
              {filters.key && (
                <Badge variant="secondary" className="h-4 px-1.5 text-xs">
                  {filters.key}
                  {filters.key_mode && ` ${filters.key_mode}`}
                </Badge>
              )}
            </div>
            {keyOpen ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            )}
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-3 px-3 space-y-3 animate-in slide-in-from-top-1">
            <div className="space-y-2">
              <Label className="text-xs">Key</Label>
              <Select
                value={filters.key ?? 'any'}
                onValueChange={handleKeyChange}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Any Key" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="any">Any Key</SelectItem>
                  {KEYS.map((key) => (
                    <SelectItem key={key} value={key}>
                      {key}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {filters.key && (
              <div className="space-y-2">
                <Label className="text-xs">Mode</Label>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleKeyModeChange('major')}
                    className={cn(
                      'flex-1',
                      filters.key_mode === 'major' &&
                        'bg-primary text-primary-foreground hover:bg-primary/90'
                    )}
                  >
                    Major
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleKeyModeChange('minor')}
                    className={cn(
                      'flex-1',
                      filters.key_mode === 'minor' &&
                        'bg-primary text-primary-foreground hover:bg-primary/90'
                    )}
                  >
                    Minor
                  </Button>
                </div>
              </div>
            )}
          </CollapsibleContent>
        </Collapsible>

        {/* Tags Filter */}
        <Collapsible open={tagsOpen} onOpenChange={setTagsOpen}>
          <CollapsibleTrigger className="flex w-full items-center justify-between rounded-lg bg-muted/50 px-3 py-2 text-sm font-medium hover:bg-muted transition-colors">
            <div className="flex items-center gap-2">
              <Tag className="h-4 w-4 text-muted-foreground" />
              <span>Tags</span>
              {filters.tags && filters.tags.length > 0 && (
                <Badge variant="secondary" className="h-4 min-w-4 px-1 text-xs">
                  {filters.tags.length}
                </Badge>
              )}
            </div>
            {tagsOpen ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            )}
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-3 px-3 space-y-3 animate-in slide-in-from-top-1">
            {/* Selected Tags Display */}
            {filters.tags && filters.tags.length > 0 && (
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">
                  Active Tags
                </Label>
                <div className="flex flex-wrap gap-1.5">
                  {filters.tags.map((tag) => (
                    <Badge
                      key={tag}
                      variant="secondary"
                      className="gap-1 pr-1 cursor-pointer hover:bg-destructive/90 transition-colors"
                      onClick={() => handleTagRemove(tag)}
                    >
                      {tag}
                      <X className="h-3 w-3" />
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Tag Search */}
            <div className="space-y-2">
              <Label className="text-xs">Search Tags</Label>
              <Input
                type="text"
                placeholder="Filter tags..."
                value={tagSearch}
                onChange={(e) => setTagSearch(e.target.value)}
                className="h-8 text-sm"
              />
            </div>

            {/* Available Tags */}
            <ScrollArea className="h-[200px]">
              <div className="flex flex-wrap gap-1.5 pr-4">
                {filteredTags.map((tag) => (
                  <Badge
                    key={tag}
                    variant={
                      filters.tags?.includes(tag) ? 'default' : 'outline'
                    }
                    className="cursor-pointer hover:bg-primary/90 transition-colors"
                    onClick={() => handleTagToggle(tag)}
                  >
                    {tag}
                  </Badge>
                ))}
                {filteredTags.length === 0 && (
                  <p className="text-xs text-muted-foreground py-4 text-center w-full">
                    No tags found
                  </p>
                )}
              </div>
            </ScrollArea>
          </CollapsibleContent>
        </Collapsible>
      </div>

      {/* Apply Button */}
      <Button
        onClick={() => onChange(filters)}
        className="w-full gap-2"
        size="sm"
      >
        <Filter className="h-4 w-4" />
        Apply Filters
        {activeFilterCount > 0 && `(${activeFilterCount})`}
      </Button>
    </div>
  );
}
