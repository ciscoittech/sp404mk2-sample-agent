import { useQuery } from '@tanstack/react-query';
import { samplesApi } from '@/api';
import { queryKeys } from '@/lib/queryClient';

export function useSimilarSamples(
  sampleId: number | null,
  options?: { limit?: number }
) {
  return useQuery({
    queryKey: queryKeys.samples.similar(sampleId!),
    queryFn: () => samplesApi.findSimilar(sampleId!, options),
    enabled: !!sampleId,
  });
}
