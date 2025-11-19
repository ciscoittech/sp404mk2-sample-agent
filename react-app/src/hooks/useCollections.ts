import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { collectionsApi } from '@/api';
import { queryKeys } from '@/lib/queryClient';
import type {
  Collection,
  CreateCollectionRequest,
  UpdateCollectionRequest,
  AddSamplesToCollectionRequest,
} from '@/types/collections';

// List all collections
export function useCollections() {
  return useQuery({
    queryKey: queryKeys.collections.all,
    queryFn: () => collectionsApi.list(),
  });
}

// Get single collection
export function useCollection(id: number) {
  return useQuery({
    queryKey: queryKeys.collections.detail(id),
    queryFn: () => collectionsApi.get(id),
    enabled: !!id,
  });
}

// Get samples in a collection (paginated)
export function useCollectionSamples(id: number, skip = 0, limit = 50) {
  return useQuery({
    queryKey: queryKeys.collections.samples(id, skip, limit),
    queryFn: () => collectionsApi.getSamples(id, skip, limit),
    enabled: !!id,
  });
}

// Get samples in a collection with infinite scroll
export function useCollectionSamplesInfinite(id: number) {
  return useInfiniteQuery({
    queryKey: queryKeys.collections.samplesList(id),
    queryFn: ({ pageParam = 0 }) => collectionsApi.getSamples(id, pageParam, 50),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      const totalFetched = allPages.reduce((sum, page) => sum + page.items.length, 0);
      return totalFetched < lastPage.total ? totalFetched : undefined;
    },
    enabled: !!id,
  });
}

// Create collection
export function useCreateCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateCollectionRequest) => collectionsApi.create(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.collections.all });
    },
  });
}

// Update collection
export function useUpdateCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: UpdateCollectionRequest }) =>
      collectionsApi.update(id, updates),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.collections.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.collections.all });
    },
  });
}

// Delete collection
export function useDeleteCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => collectionsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.collections.all });
    },
  });
}

// Add samples to collection
export function useAddSamplesToCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, request }: { id: number; request: AddSamplesToCollectionRequest }) =>
      collectionsApi.addSamples(id, request),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.collections.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.collections.samplesList(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.collections.all });
    },
  });
}

// Remove sample from collection
export function useRemoveSampleFromCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ collectionId, sampleId }: { collectionId: number; sampleId: number }) =>
      collectionsApi.removeSample(collectionId, sampleId),
    onSuccess: (_, { collectionId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.collections.detail(collectionId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.collections.samplesList(collectionId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.collections.all });
    },
  });
}

// Evaluate smart collection
export function useEvaluateSmartCollection() {
  return useMutation({
    mutationFn: (id: number) => collectionsApi.evaluateSmartCollection(id),
  });
}
