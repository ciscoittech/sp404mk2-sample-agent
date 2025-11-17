import { apiClient } from './client';
import type { Sample, PaginatedResponse } from '@/types/api';

export const samplesApi = {
  // List samples with filters
  list: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    genre?: string;
    bpm_min?: number;
    bpm_max?: number;
    key?: string;
    tags?: string[];
  }) => {
    const { data } = await apiClient.get<PaginatedResponse<Sample>>('/public/samples/', { params });
    return data;
  },

  // Get sample by ID
  getById: async (id: number) => {
    const { data } = await apiClient.get<Sample>(`/samples/${id}`);
    return data;
  },

  // Upload sample
  upload: async (file: File, metadata?: Partial<Sample>) => {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      Object.entries(metadata).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          // Convert arrays to JSON strings for form submission
          const stringValue = Array.isArray(value) ? JSON.stringify(value) : String(value);
          formData.append(key, stringValue);
        }
      });
    }
    const { data } = await apiClient.post<Sample>('/public/samples/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Update sample
  update: async (id: number, updates: Partial<Sample>) => {
    const { data } = await apiClient.patch<Sample>(`/samples/${id}`, updates);
    return data;
  },

  // Delete sample
  delete: async (id: number) => {
    await apiClient.delete(`/samples/${id}`);
  },

  // Analyze sample with AI
  analyze: async (id: number) => {
    const { data } = await apiClient.post<Sample>(`/samples/${id}/analyze`);
    return data;
  },

  // Get audio features
  getAudioFeatures: async (id: number) => {
    const { data } = await apiClient.get(`/samples/${id}/audio-features`);
    return data;
  },
};
