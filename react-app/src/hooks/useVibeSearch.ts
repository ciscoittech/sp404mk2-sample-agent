import { useMutation, useQuery } from '@tanstack/react-query';
import { vibeSearchApi, type VibeSearchRequest } from '@/api/vibeSearch';
import type { VibeSearchResponse, VibeSearchResult } from '@/types/api';

export function useVibeSearch() {
  return useMutation({
    mutationFn: (request: VibeSearchRequest) => vibeSearchApi.search(request),
    onSuccess: (data: VibeSearchResponse) => {
      console.log(
        `Vibe search completed: found ${data.count} results in ${data.execution_time_ms}ms`
      );
    },
    onError: (error: any) => {
      console.error('Vibe search failed:', error.message || error);
    },
  });
}

export function useSimilarSamples(sampleId: number | null, limit = 10) {
  return useQuery({
    queryKey: ['similar-samples', sampleId, limit],
    queryFn: () => vibeSearchApi.findSimilar(sampleId!, limit),
    enabled: sampleId !== null,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
