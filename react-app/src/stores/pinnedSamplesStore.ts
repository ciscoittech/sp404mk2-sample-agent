import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Sample } from '@/types/api';
import { toast } from 'sonner';

interface PinnedSamplesState {
  // State
  pinnedSamples: Sample[];
  maxPins: number;

  // Actions
  pinSample: (sample: Sample) => void;
  unpinSample: (sampleId: number) => void;
  clearAll: () => void;
  isPinned: (sampleId: number) => boolean;
  reorderPins: (fromIndex: number, toIndex: number) => void;

  // Helpers
  hasBpmMismatch: () => boolean;
  getAverageBpm: () => number | null;
  getPinnedIds: () => number[];
}

export const usePinnedSamples = create<PinnedSamplesState>()(
  persist(
    (set, get) => ({
      pinnedSamples: [],
      maxPins: 3,

      pinSample: (sample) => {
        const { pinnedSamples, maxPins } = get();

        // Prevent duplicates
        if (pinnedSamples.some(s => s.id === sample.id)) {
          toast.info('Sample already pinned');
          return;
        }

        // Enforce max limit
        if (pinnedSamples.length >= maxPins) {
          toast.error(`Maximum ${maxPins} samples can be pinned`);
          return;
        }

        set({ pinnedSamples: [...pinnedSamples, sample] });
        toast.success(`${sample.title} pinned`, {
          description: `${pinnedSamples.length + 1}/${maxPins} pins used`
        });
      },

      unpinSample: (sampleId) => {
        const sample = get().pinnedSamples.find(s => s.id === sampleId);
        set((state) => ({
          pinnedSamples: state.pinnedSamples.filter(s => s.id !== sampleId)
        }));
        if (sample) {
          toast.info(`${sample.title} unpinned`);
        }
      },

      clearAll: () => {
        const count = get().pinnedSamples.length;
        if (count === 0) return;

        set({ pinnedSamples: [] });
        toast.info(`${count} sample${count > 1 ? 's' : ''} unpinned`);
      },

      isPinned: (sampleId) => {
        return get().pinnedSamples.some(s => s.id === sampleId);
      },

      reorderPins: (fromIndex, toIndex) => {
        const samples = [...get().pinnedSamples];
        const [removed] = samples.splice(fromIndex, 1);
        samples.splice(toIndex, 0, removed);
        set({ pinnedSamples: samples });
      },

      hasBpmMismatch: () => {
        const samples = get().pinnedSamples;
        if (samples.length < 2) return false;

        const bpms = samples
          .map(s => s.bpm)
          .filter((bpm): bpm is number => bpm !== null && bpm !== undefined);

        if (bpms.length < 2) return false;

        const min = Math.min(...bpms);
        const max = Math.max(...bpms);

        // Consider mismatch if difference > 5 BPM
        return (max - min) > 5;
      },

      getAverageBpm: () => {
        const samples = get().pinnedSamples;
        const bpms = samples
          .map(s => s.bpm)
          .filter((bpm): bpm is number => bpm !== null && bpm !== undefined);

        if (bpms.length === 0) return null;

        const sum = bpms.reduce((acc, bpm) => acc + bpm, 0);
        return Math.round(sum / bpms.length);
      },

      getPinnedIds: () => {
        return get().pinnedSamples.map(s => s.id);
      }
    }),
    {
      name: 'pinned-samples-storage',
      partialize: (state) => ({
        pinnedSamples: state.pinnedSamples
      })
    }
  )
);
