import { apiClient } from './client';
import type { Sample, PaginatedResponse } from '@/types/api';
import type {
  Collection,
  CreateCollectionRequest,
  UpdateCollectionRequest,
  AddSamplesToCollectionRequest,
} from '@/types/collections';

export const collectionsApi = {
  // List all collections
  list: async () => {
    const { data } = await apiClient.get<Collection[]>('/collections');
    return data;
  },

  // Get single collection by ID
  get: async (id: number) => {
    const { data } = await apiClient.get<Collection>(`/collections/${id}`);
    return data;
  },

  // Create new collection
  create: async (request: CreateCollectionRequest) => {
    const { data } = await apiClient.post<Collection>('/collections', request);
    return data;
  },

  // Update collection
  update: async (id: number, request: UpdateCollectionRequest) => {
    const { data } = await apiClient.put<Collection>(`/collections/${id}`, request);
    return data;
  },

  // Delete collection
  delete: async (id: number) => {
    await apiClient.delete(`/collections/${id}`);
  },

  // Get samples in a collection (paginated)
  getSamples: async (id: number, skip = 0, limit = 50) => {
    const { data } = await apiClient.get<PaginatedResponse<Sample>>(
      `/collections/${id}/samples`,
      {
        params: { skip, limit },
      }
    );
    return data;
  },

  // Add samples to collection
  addSamples: async (id: number, request: AddSamplesToCollectionRequest) => {
    const { data } = await apiClient.post<{ message: string; added_count: number }>(
      `/collections/${id}/samples`,
      request
    );
    return data;
  },

  // Remove sample from collection
  removeSample: async (collectionId: number, sampleId: number) => {
    await apiClient.delete(`/collections/${collectionId}/samples/${sampleId}`);
  },

  // Evaluate smart collection (returns matching samples count)
  evaluateSmartCollection: async (id: number) => {
    const { data } = await apiClient.post<{ matching_samples: number }>(
      `/collections/${id}/evaluate`
    );
    return data;
  },
};
