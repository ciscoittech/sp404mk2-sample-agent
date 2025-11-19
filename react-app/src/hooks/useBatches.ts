import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { batchesApi } from '@/api';
import { queryKeys } from '@/lib/queryClient';
import type { Batch, BatchCreateRequest } from '@/types/api';

// List all batches
export function useBatches(params?: {
  page?: number;
  limit?: number;
  status?: string;
}) {
  return useQuery({
    queryKey: queryKeys.batches.list(params),
    queryFn: () => batchesApi.list(params),
    refetchInterval: 5000, // Refetch every 5 seconds for active batches
  });
}

// List active batches (processing or pending)
export function useActiveBatches() {
  return useQuery({
    queryKey: queryKeys.batches.active(),
    queryFn: () => batchesApi.list({ status: 'processing' }),
    refetchInterval: 3000, // Refetch every 3 seconds for active batches
  });
}

// List batch history (completed, failed, cancelled)
export function useBatchHistory(params?: { page?: number; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.batches.history(),
    queryFn: () => batchesApi.list({ ...params }),
    refetchInterval: 10000, // Refetch every 10 seconds
  });
}

// Get single batch
export function useBatch(id: string | null) {
  return useQuery({
    queryKey: queryKeys.batches.detail(id!),
    queryFn: () => batchesApi.getById(id!),
    enabled: !!id,
    refetchInterval: (data) => {
      // Refetch faster if batch is processing
      if (data?.status === 'processing' || data?.status === 'pending') {
        return 2000; // 2 seconds
      }
      return false; // Don't refetch if completed/failed/cancelled
    },
  });
}

// Create batch
export function useCreateBatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: BatchCreateRequest) => batchesApi.create(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches.active() });
    },
  });
}

// Cancel batch
export function useCancelBatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => batchesApi.cancel(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches.active() });
    },
  });
}

// Retry batch
export function useRetryBatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => batchesApi.retry(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches.active() });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches.history() });
    },
  });
}

// Import batch results
export function useImportBatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => batchesApi.import(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.samples.lists() });
    },
  });
}
