import { useState } from 'react';
import { PinnedSampleCard } from './PinnedSampleCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { usePinnedSamples } from '@/stores/pinnedSamplesStore';
import { useKits, useAssignSample } from '@/hooks/useKits';
import { Plus, AlertTriangle, Lightbulb, X, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import type { Sample } from '@/types/api';

interface PinnedSamplesSectionProps {
  allSamples: Sample[];
  onRecommendedSamplesFilter?: (samples: Sample[]) => void;
}

export function PinnedSamplesSection({ allSamples, onRecommendedSamplesFilter }: PinnedSamplesSectionProps) {
  const { pinnedSamples, clearAll, hasBpmMismatch, getAverageBpm } = usePinnedSamples();
  const { data: kits } = useKits();
  const assignSample = useAssignSample();
  const [isAddingToKit, setIsAddingToKit] = useState(false);

  // Don't render if no samples are pinned
  if (pinnedSamples.length === 0) {
    return null;
  }

  const bpmMismatch = hasBpmMismatch();
  const avgBpm = getAverageBpm();

  // Find recommended samples (compatible BPM and key)
  const getRecommendedSamples = (): Sample[] => {
    if (allSamples.length === 0) return [];

    const pinnedIds = new Set(pinnedSamples.map(s => s.id));
    const pinnedKeys = pinnedSamples
      .map(s => s.musical_key)
      .filter((key): key is string => key !== null && key !== undefined);

    // Check if pinned samples have percussion tags
    const hasPercussion = pinnedSamples.some(s =>
      s.tags?.some(tag => ['kick', 'snare', 'drum', 'perc'].some(p => tag.toLowerCase().includes(p)))
    );

    return allSamples
      .filter(s => !pinnedIds.has(s.id)) // Exclude already pinned
      .filter(s => {
        // BPM compatibility (±10 BPM tolerance, or no BPM for percussion)
        if (s.bpm && avgBpm) {
          const bpmDiff = Math.abs(s.bpm - avgBpm);
          if (bpmDiff > 10) return false;
        }
        // Allow samples without BPM (common for percussion/one-shots)

        // Key compatibility (only check for melodic samples)
        if (pinnedKeys.length > 0 && s.musical_key) {
          // Sample has a key, check compatibility
          const isCompatibleKey = pinnedKeys.some(key =>
            key.split(' ')[0] === s.musical_key?.split(' ')[0] // Match root note
          );
          if (!isCompatibleKey) return false;
        }
        // Samples without keys (percussion) are always compatible

        // If looking for percussion, prioritize percussion samples
        if (hasPercussion) {
          const isPercussion = s.tags?.some(tag =>
            ['kick', 'snare', 'drum', 'perc', 'hat', 'cymbal'].some(p => tag.toLowerCase().includes(p))
          );
          if (isPercussion) return true;
        }

        return true;
      })
      .slice(0, 5); // Show top 5 recommendations
  };

  const recommendedSamples = getRecommendedSamples();

  // Add all pinned samples to the currently selected kit
  const handleAddAllToKit = async () => {
    const currentKit = kits?.items?.[0]; // Get first kit (or we could ask user to select)

    if (!currentKit) {
      toast.error('No kit selected', {
        description: 'Please create or select a kit first'
      });
      return;
    }

    setIsAddingToKit(true);

    try {
      // Find first available pads
      const usedPads = new Set(
        currentKit.samples.map(s => `${s.pad_bank}${s.pad_number}`)
      );

      const availablePads: Array<{ bank: 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J'; number: number }> = [];
      const banks: Array<'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J'> = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];

      // Find available pads
      for (const bank of banks) {
        for (let padNumber = 1; padNumber <= 16; padNumber++) {
          if (!usedPads.has(`${bank}${padNumber}`)) {
            availablePads.push({ bank, number: padNumber });
            if (availablePads.length >= pinnedSamples.length) break;
          }
        }
        if (availablePads.length >= pinnedSamples.length) break;
      }

      if (availablePads.length < pinnedSamples.length) {
        toast.error('Not enough available pads', {
          description: `Need ${pinnedSamples.length} pads, only ${availablePads.length} available`
        });
        setIsAddingToKit(false);
        return;
      }

      // Assign all samples
      const assignments = pinnedSamples.map((sample, index) => ({
        sample,
        pad: availablePads[index]
      }));

      for (const { sample, pad } of assignments) {
        await assignSample.mutateAsync({
          kitId: currentKit.id,
          assignment: {
            sample_id: sample.id,
            pad_bank: pad.bank,
            pad_number: pad.number
          }
        });
      }

      const padAssignments = assignments
        .map(a => `${a.pad.bank}${a.pad.number}`)
        .join(', ');

      toast.success('Samples added to kit', {
        description: `${pinnedSamples.length} samples assigned to pads: ${padAssignments}`
      });

      // Clear pinned samples after successful add
      clearAll();
    } catch (error) {
      console.error('Error adding samples to kit:', error);
      toast.error('Failed to add samples to kit', {
        description: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setIsAddingToKit(false);
    }
  };

  return (
    <div className="space-y-4 pb-4 border-b border-border">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold">
            📌 Pinned Samples
          </h3>
          <Badge variant="secondary" className="text-xs">
            {pinnedSamples.length}/3
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            onClick={handleAddAllToKit}
            disabled={isAddingToKit}
            title="Add all pinned samples to current kit"
          >
            {isAddingToKit ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Adding...
              </>
            ) : (
              <>
                <Plus className="h-4 w-4 mr-2" />
                Add All to Kit
              </>
            )}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={clearAll}
            title="Clear all pinned samples"
          >
            Clear All
          </Button>
        </div>
      </div>

      {/* BPM Mismatch Warning */}
      {bpmMismatch && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription className="text-sm">
            BPM mismatch detected! Your pinned samples have different tempos.
            {avgBpm && ` Average BPM: ${avgBpm}`}
          </AlertDescription>
        </Alert>
      )}

      {/* Pinned Sample Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {pinnedSamples.map((sample) => (
          <PinnedSampleCard key={sample.id} sample={sample} />
        ))}
      </div>

      {/* Smart Recommendations */}
      {recommendedSamples.length > 0 && (
        <>
          <Separator />
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-yellow-500" />
              <p className="text-sm font-medium">
                Recommended Samples
              </p>
              <Badge variant="outline" className="text-xs">
                {recommendedSamples.length} compatible
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              These samples match the BPM and key of your pinned selection
              {avgBpm && ` (${avgBpm} BPM)`}
            </p>

            {/* Show filter button if callback provided */}
            {onRecommendedSamplesFilter && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onRecommendedSamplesFilter(recommendedSamples)}
              >
                Show Only Recommended ({recommendedSamples.length})
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
