import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { kitsApi } from '@/api';
import { queryKeys } from '@/lib/queryClient';
import type { Kit } from '@/types/api';

// List kits
export function useKits(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.kits.list(params),
    queryFn: () => kitsApi.list(params),
  });
}

// Get single kit
export function useKit(id: number) {
  return useQuery({
    queryKey: queryKeys.kits.detail(id),
    queryFn: () => kitsApi.getById(id),
    enabled: !!id,
  });
}

// Create kit
export function useCreateKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (kit: { name: string; description?: string; is_public?: boolean }) =>
      kitsApi.create(kit),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() });
    },
  });
}

// Update kit
export function useUpdateKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      updates,
    }: {
      id: number;
      updates: { name?: string; description?: string; is_public?: boolean };
    }) => kitsApi.update(id, updates),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.kits.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() });
    },
  });
}

// Delete kit
export function useDeleteKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => kitsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() });
    },
  });
}

// Assign sample to pad
export function useAssignSample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      kitId,
      assignment,
    }: {
      kitId: number;
      assignment: {
        sample_id: number;
        pad_bank: 'A' | 'B' | 'C' | 'D';
        pad_number: number;
        volume?: number;
        pitch_shift?: number;
      };
    }) => kitsApi.assignSample(kitId, assignment),
    onSuccess: (_, { kitId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.kits.detail(kitId) });
    },
  });
}

// Remove sample from pad
export function useRemoveSample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      kitId,
      padBank,
      padNumber,
    }: {
      kitId: number;
      padBank: string;
      padNumber: number;
    }) => kitsApi.removeSample(kitId, padBank, padNumber),
    onSuccess: (_, { kitId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.kits.detail(kitId) });
    },
  });
}

// Export kit
export function useExportKit() {
  return useMutation({
    mutationFn: (id: number) => kitsApi.export(id),
  });
}

// Build kit with AI
export function useBuildKitWithAI() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (prompt: string) => kitsApi.buildWithAI(prompt),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() });
    },
  });
}
