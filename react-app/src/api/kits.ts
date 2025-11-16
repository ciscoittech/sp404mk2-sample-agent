import { apiClient } from './client';
import type { Kit, PadAssignment } from '@/types/api';

export const kitsApi = {
  // List kits
  list: async (params?: { skip?: number; limit?: number }) => {
    const { data } = await apiClient.get<{ items: Kit[]; total: number }>('/kits', { params });
    return data;
  },

  // Get kit by ID
  getById: async (id: number) => {
    const { data } = await apiClient.get<Kit>(`/kits/${id}`);
    return data;
  },

  // Create kit
  create: async (kit: { name: string; description?: string; is_public?: boolean }) => {
    const { data } = await apiClient.post<Kit>('/kits', kit);
    return data;
  },

  // Update kit
  update: async (id: number, updates: { name?: string; description?: string; is_public?: boolean }) => {
    const { data } = await apiClient.patch<Kit>(`/kits/${id}`, updates);
    return data;
  },

  // Delete kit
  delete: async (id: number) => {
    await apiClient.delete(`/kits/${id}`);
  },

  // Assign sample to pad
  assignSample: async (
    kitId: number,
    assignment: {
      sample_id: number;
      pad_bank: 'A' | 'B' | 'C' | 'D';
      pad_number: number;
      volume?: number;
      pitch_shift?: number;
    }
  ) => {
    const { data } = await apiClient.post<PadAssignment>(`/kits/${kitId}/assign`, assignment);
    return data;
  },

  // Remove sample from pad
  removeSample: async (kitId: number, padBank: string, padNumber: number) => {
    await apiClient.delete(`/kits/${kitId}/pads/${padBank}/${padNumber}`);
  },

  // Export kit
  export: async (id: number) => {
    const { data } = await apiClient.get(`/kits/${id}/export`, {
      responseType: 'blob',
    });
    return data;
  },

  // Build kit with AI
  buildWithAI: async (prompt: string) => {
    const { data } = await apiClient.post<Kit>('/kits/build', { prompt });
    return data;
  },
};
