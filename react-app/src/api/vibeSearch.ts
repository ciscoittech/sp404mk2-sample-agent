import { apiClient } from './client';
import type {
  VibeSearchResponse,
  VibeSearchFilters,
  VibeSearchResult,
} from '@/types/api';

export interface VibeSearchRequest {
  query: string;
  limit?: number;
  filters?: VibeSearchFilters;
}

export const vibeSearchApi = {
  /**
   * Search samples by natural language vibe query
   */
  search: async (request: VibeSearchRequest): Promise<VibeSearchResponse> => {
    const params = new URLSearchParams({
      query: request.query,
      limit: String(request.limit || 20),
      ...(request.filters?.bpm_min && { bpm_min: String(request.filters.bpm_min) }),
      ...(request.filters?.bpm_max && { bpm_max: String(request.filters.bpm_max) }),
      ...(request.filters?.genre && { genre: request.filters.genre }),
      ...(request.filters?.energy_min && { energy_min: String(request.filters.energy_min) }),
      ...(request.filters?.energy_max && { energy_max: String(request.filters.energy_max) }),
    });

    const { data } = await apiClient.get<VibeSearchResponse>(
      `/search/vibe?${params.toString()}`
    );
    return data;
  },

  /**
   * Find samples similar to a specific sample
   */
  findSimilar: async (
    sampleId: number,
    limit = 10
  ): Promise<VibeSearchResult[]> => {
    const { data } = await apiClient.get<{ results: VibeSearchResult[] }>(
      `/search/similar/${sampleId}?limit=${limit}`
    );
    return data.results;
  },
};
