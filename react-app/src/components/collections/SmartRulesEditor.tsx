import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Loader2, X, Sparkles } from 'lucide-react';
import type { SmartRules } from '@/types/collections';
import { useEvaluateSmartCollection } from '@/hooks/useCollections';

interface SmartRulesEditorProps {
  value: SmartRules;
  onChange: (rules: SmartRules) => void;
  collectionId?: number;
  className?: string;
}

// Common genres from the sample library
const AVAILABLE_GENRES = [
  'hip-hop',
  'jazz',
  'soul',
  'electronic',
  'house',
  'trap',
  'lo-fi',
  'funk',
  'r&b',
  'disco',
  'rock',
  'pop',
  'ambient',
  'techno',
  'drum & bass',
];

// Common sample types
const SAMPLE_TYPES = ['loop', 'one-shot', 'drum', 'melody', 'vocal', 'fx', 'bass', 'synth'];

export function SmartRulesEditor({
  value,
  onChange,
  collectionId,
  className,
}: SmartRulesEditorProps) {
  const [localRules, setLocalRules] = useState<SmartRules>(value);
  const [tagInput, setTagInput] = useState('');
  const [previewCount, setPreviewCount] = useState<number | null>(null);
  const evaluateCollection = useEvaluateSmartCollection();

  // Update local rules when value changes
  useEffect(() => {
    setLocalRules(value);
  }, [value]);

  // Update parent when local rules change
  useEffect(() => {
    onChange(localRules);
  }, [localRules, onChange]);

  const handleGenreToggle = (genre: string) => {
    const currentGenres = localRules.genres || [];
    const newGenres = currentGenres.includes(genre)
      ? currentGenres.filter((g) => g !== genre)
      : [...currentGenres, genre];

    setLocalRules({ ...localRules, genres: newGenres.length > 0 ? newGenres : undefined });
  };

  const handleBpmChange = (values: number[]) => {
    setLocalRules({
      ...localRules,
      bpm_min: values[0],
      bpm_max: values[1],
    });
  };

  const handleAddTag = () => {
    if (!tagInput.trim()) return;

    const currentTags = localRules.tags || [];
    if (currentTags.includes(tagInput.trim())) {
      setTagInput('');
      return;
    }

    setLocalRules({
      ...localRules,
      tags: [...currentTags, tagInput.trim()],
    });
    setTagInput('');
  };

  const handleRemoveTag = (tag: string) => {
    const newTags = (localRules.tags || []).filter((t) => t !== tag);
    setLocalRules({ ...localRules, tags: newTags.length > 0 ? newTags : undefined });
  };

  const handleSampleTypeToggle = (type: string) => {
    const currentTypes = localRules.sample_types || [];
    const newTypes = currentTypes.includes(type)
      ? currentTypes.filter((t) => t !== type)
      : [...currentTypes, type];

    setLocalRules({ ...localRules, sample_types: newTypes.length > 0 ? newTypes : undefined });
  };

  const handleConfidenceChange = (values: number[]) => {
    setLocalRules({ ...localRules, min_confidence: values[0] });
  };

  const handlePreview = async () => {
    if (!collectionId) return;

    try {
      const result = await evaluateCollection.mutateAsync(collectionId);
      setPreviewCount(result.matching_samples);
    } catch (error) {
      console.error('Failed to preview collection:', error);
    }
  };

  const handleReset = () => {
    setLocalRules({});
    setPreviewCount(null);
  };

  const hasRules = Object.values(localRules).some((v) => v !== undefined && (Array.isArray(v) ? v.length > 0 : true));

  return (
    <div className={className}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-500" />
          <h3 className="text-lg font-semibold">Smart Collection Rules</h3>
        </div>

        {/* Genre selection */}
        <div className="space-y-3">
          <Label>Genres</Label>
          <div className="flex flex-wrap gap-2">
            {AVAILABLE_GENRES.map((genre) => (
              <Badge
                key={genre}
                variant={(localRules.genres || []).includes(genre) ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => handleGenreToggle(genre)}
              >
                {genre}
              </Badge>
            ))}
          </div>
        </div>

        <Separator />

        {/* BPM range */}
        <div className="space-y-3">
          <Label>BPM Range</Label>
          <div className="flex items-center gap-4">
            <span className="text-sm font-mono w-12">{localRules.bpm_min || 20}</span>
            <Slider
              min={20}
              max={200}
              step={1}
              value={[localRules.bpm_min || 20, localRules.bpm_max || 200]}
              onValueChange={handleBpmChange}
              className="flex-1"
            />
            <span className="text-sm font-mono w-12">{localRules.bpm_max || 200}</span>
          </div>
        </div>

        <Separator />

        {/* Tags */}
        <div className="space-y-3">
          <Label>Tags</Label>
          <div className="flex gap-2">
            <Input
              placeholder="Add tag..."
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddTag();
                }
              }}
            />
            <Button type="button" variant="outline" onClick={handleAddTag}>
              Add
            </Button>
          </div>
          {(localRules.tags || []).length > 0 && (
            <div className="flex flex-wrap gap-2">
              {(localRules.tags || []).map((tag) => (
                <Badge key={tag} variant="secondary" className="gap-1">
                  {tag}
                  <button
                    onClick={() => handleRemoveTag(tag)}
                    className="ml-1 hover:text-destructive"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          )}
        </div>

        <Separator />

        {/* Sample types */}
        <div className="space-y-3">
          <Label>Sample Types</Label>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_TYPES.map((type) => (
              <Badge
                key={type}
                variant={(localRules.sample_types || []).includes(type) ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => handleSampleTypeToggle(type)}
              >
                {type}
              </Badge>
            ))}
          </div>
        </div>

        <Separator />

        {/* Confidence threshold */}
        <div className="space-y-3">
          <Label>Minimum Confidence</Label>
          <div className="flex items-center gap-4">
            <Slider
              min={0}
              max={100}
              step={5}
              value={[localRules.min_confidence || 0]}
              onValueChange={handleConfidenceChange}
              className="flex-1"
            />
            <span className="text-sm font-mono w-12">{localRules.min_confidence || 0}%</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Only include samples with AI analysis confidence above this threshold
          </p>
        </div>

        <Separator />

        {/* Actions */}
        <div className="flex items-center gap-3">
          {collectionId && (
            <Button
              type="button"
              variant="outline"
              onClick={handlePreview}
              disabled={evaluateCollection.isPending || !hasRules}
            >
              {evaluateCollection.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Checking...
                </>
              ) : (
                'Preview Results'
              )}
            </Button>
          )}

          {previewCount !== null && (
            <Badge variant="secondary" className="text-sm">
              {previewCount} matching sample{previewCount !== 1 ? 's' : ''}
            </Badge>
          )}

          <div className="flex-1" />

          {hasRules && (
            <Button type="button" variant="ghost" onClick={handleReset}>
              Reset All
            </Button>
          )}
        </div>

        {/* Rules summary */}
        {hasRules && (
          <div className="rounded-lg bg-muted p-4 space-y-2">
            <p className="text-sm font-semibold">Active Rules:</p>
            <ul className="text-sm text-muted-foreground space-y-1">
              {(localRules.genres || []).length > 0 && (
                <li>
                  Genres: {(localRules.genres || []).join(', ')}
                </li>
              )}
              {(localRules.bpm_min || localRules.bpm_max) && (
                <li>
                  BPM: {localRules.bpm_min || 20} - {localRules.bpm_max || 200}
                </li>
              )}
              {(localRules.tags || []).length > 0 && (
                <li>
                  Tags: {(localRules.tags || []).join(', ')}
                </li>
              )}
              {(localRules.sample_types || []).length > 0 && (
                <li>
                  Types: {(localRules.sample_types || []).join(', ')}
                </li>
              )}
              {localRules.min_confidence && localRules.min_confidence > 0 && (
                <li>
                  Min Confidence: {localRules.min_confidence}%
                </li>
              )}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
