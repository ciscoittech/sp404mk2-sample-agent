import { apiClient } from './client';
import type { Batch, BatchListResponse, BatchCreateRequest, BatchProgress } from '@/types/api';

export const batchesApi = {
  // List batches with filters
  list: async (params?: {
    page?: number;
    limit?: number;
    status?: string;
  }) => {
    const { data } = await apiClient.get<BatchListResponse>('/public/batch/', { params });
    return data;
  },

  // Get batch by ID
  getById: async (id: string) => {
    const { data } = await apiClient.get<Batch>(`/public/batch/${id}`);
    return data;
  },

  // Create new batch
  create: async (request: BatchCreateRequest) => {
    const formData = new FormData();
    formData.append('collection_path', request.collection_path);
    if (request.batch_size) {
      formData.append('batch_size', String(request.batch_size));
    }
    if (request.options) {
      // Add each option as a form field
      Object.entries(request.options).forEach(([key, value]) => {
        formData.append(key, String(value));
      });
    }
    const { data } = await apiClient.post<Batch>('/public/batch/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Cancel batch
  cancel: async (id: string) => {
    const { data } = await apiClient.post(`/public/batch/${id}/cancel`);
    return data;
  },

  // Retry batch
  retry: async (id: string) => {
    const { data } = await apiClient.post<Batch>(`/public/batch/${id}/retry`);
    return data;
  },

  // Import batch results to samples
  import: async (id: string) => {
    const { data } = await apiClient.post<{ status: string; imported_count: number }>(
      `/public/batch/${id}/import`
    );
    return data;
  },

  // Get export download URL
  getExportUrl: (id: string) => {
    return `${apiClient.defaults.baseURL}/public/batch/${id}/export`;
  },
};
