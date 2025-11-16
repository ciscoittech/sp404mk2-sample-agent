import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { preferencesApi } from '@/api';
import { queryKeys } from '@/lib/queryClient';
import type { UserPreferences } from '@/types/api';

// Get user preferences
export function usePreferences() {
  return useQuery({
    queryKey: queryKeys.preferences.all,
    queryFn: () => preferencesApi.get(),
  });
}

// Update preferences
export function useUpdatePreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (preferences: Partial<UserPreferences>) => preferencesApi.update(preferences),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.preferences.all });
    },
  });
}
