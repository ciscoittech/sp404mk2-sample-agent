import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { samplesApi } from '@/api';
import { queryKeys } from '@/lib/queryClient';
import type { Sample } from '@/types/api';

// List samples with filters
export function useSamples(params?: {
  page?: number;
  limit?: number;
  search?: string;
  genre?: string;
  bpm_min?: number;
  bpm_max?: number;
  key?: string;
  tags?: string[];
}) {
  return useQuery({
    queryKey: queryKeys.samples.list(params),
    queryFn: () => samplesApi.list(params),
  });
}

// Get single sample
export function useSample(id: number) {
  return useQuery({
    queryKey: queryKeys.samples.detail(id),
    queryFn: () => samplesApi.getById(id),
    enabled: !!id,
  });
}

// Upload sample
export function useUploadSample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, metadata }: { file: File; metadata?: Partial<Sample> }) =>
      samplesApi.upload(file, metadata),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.samples.lists() });
    },
  });
}

// Update sample
export function useUpdateSample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: Partial<Sample> }) =>
      samplesApi.update(id, updates),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.samples.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.samples.lists() });
    },
  });
}

// Delete sample
export function useDeleteSample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => samplesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.samples.lists() });
    },
  });
}

// Analyze sample with AI
export function useAnalyzeSample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => samplesApi.analyze(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.samples.detail(id) });
    },
  });
}
