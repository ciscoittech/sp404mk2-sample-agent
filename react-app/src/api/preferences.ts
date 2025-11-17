import { apiClient } from './client';
import type { UserPreferences, Model, ModelsResponse } from '@/types/api';

export const preferencesApi = {
  // Get user preferences
  get: async () => {
    const { data } = await apiClient.get<UserPreferences>('/preferences');
    return data;
  },

  // Update user preferences
  update: async (preferences: Partial<UserPreferences>) => {
    const { data } = await apiClient.patch<UserPreferences>('/preferences', preferences);
    return data;
  },

  // Get available models
  getModels: async () => {
    const { data } = await apiClient.get<ModelsResponse>('/preferences/models');
    return data.models;
  },
};
