/**
 * Custom React Query Hooks for Usage & Cost Tracking
 *
 * Provides hooks for fetching usage data with automatic caching,
 * refetching, and error handling via React Query.
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import {
  getPublicUsageSummary,
  getPublicDailyUsage,
  getPublicRecentCalls,
  getUsageSummary,
  getDailyUsage,
  getBudgetStatus,
  getRecentCalls,
  PublicUsageSummaryResponse,
  DailyUsageResponse,
  RecentCallsResponse,
  UsageSummary,
  BudgetStatus
} from '@/api/usage';

// ============================================================================
// Public Hooks (No Authentication Required)
// ============================================================================

/**
 * Fetch public usage summary (demo user)
 * Auto-refreshes every 30 seconds to match HTMX behavior
 */
export function usePublicUsageSummary(): UseQueryResult<PublicUsageSummaryResponse> {
  return useQuery({
    queryKey: ['usage', 'public', 'summary'],
    queryFn: getPublicUsageSummary,
    refetchInterval: 30000, // 30 seconds
    staleTime: 25000, // Consider stale after 25 seconds
  });
}

/**
 * Fetch public daily usage data
 * Auto-refreshes every 30 seconds
 */
export function usePublicDailyUsage(days: number = 30): UseQueryResult<DailyUsageResponse> {
  return useQuery({
    queryKey: ['usage', 'public', 'daily', days],
    queryFn: () => getPublicDailyUsage(days),
    refetchInterval: 30000,
    staleTime: 25000,
  });
}

/**
 * Fetch public recent API calls
 * Auto-refreshes every 30 seconds
 */
export function usePublicRecentCalls(limit: number = 50): UseQueryResult<RecentCallsResponse> {
  return useQuery({
    queryKey: ['usage', 'public', 'recent', limit],
    queryFn: () => getPublicRecentCalls(limit),
    refetchInterval: 30000,
    staleTime: 25000,
  });
}

// ============================================================================
// Authenticated Hooks
// ============================================================================

/**
 * Fetch usage summary for authenticated user
 * Supports optional date range filtering
 */
export function useUsageSummary(
  startDate?: Date,
  endDate?: Date
): UseQueryResult<UsageSummary> {
  return useQuery({
    queryKey: ['usage', 'summary', startDate?.toISOString(), endDate?.toISOString()],
    queryFn: () => getUsageSummary(startDate, endDate),
    refetchInterval: 30000,
    staleTime: 25000,
  });
}

/**
 * Fetch daily usage totals
 */
export function useDailyUsage(days: number = 30): UseQueryResult<DailyUsageResponse> {
  return useQuery({
    queryKey: ['usage', 'daily', days],
    queryFn: () => getDailyUsage(days),
    refetchInterval: 30000,
    staleTime: 25000,
  });
}

/**
 * Fetch budget status
 */
export function useBudgetStatus(): UseQueryResult<BudgetStatus> {
  return useQuery({
    queryKey: ['usage', 'budget'],
    queryFn: getBudgetStatus,
    refetchInterval: 30000,
    staleTime: 25000,
  });
}

/**
 * Fetch recent API calls
 */
export function useRecentCalls(limit: number = 50): UseQueryResult<RecentCallsResponse> {
  return useQuery({
    queryKey: ['usage', 'recent', limit],
    queryFn: () => getRecentCalls(limit),
    refetchInterval: 30000,
    staleTime: 25000,
  });
}

// ============================================================================
// Combined Hooks for UsagePage
// ============================================================================

/**
 * Fetch all usage data needed for the UsagePage
 * Returns all queries with loading/error states
 */
export function useUsagePageData(days: number = 30, recentLimit: number = 50) {
  const summary = usePublicUsageSummary();
  const daily = usePublicDailyUsage(days);
  const recent = usePublicRecentCalls(recentLimit);

  return {
    summary,
    daily,
    recent,
    // Aggregate loading state
    isLoading: summary.isLoading || daily.isLoading || recent.isLoading,
    // Aggregate error state
    hasError: summary.isError || daily.isError || recent.isError,
    // Individual data
    summaryData: summary.data?.summary,
    budgetData: summary.data?.budget,
    dailyData: daily.data?.data,
    recentCalls: recent.data?.calls,
    // Refetch all
    refetchAll: () => {
      summary.refetch();
      daily.refetch();
      recent.refetch();
    }
  };
}

/**
 * Hook specifically for the budget alert banner
 * Only fetches budget data
 */
export function useBudgetAlert() {
  const { data } = usePublicUsageSummary();

  return {
    status: data?.budget.status || 'ok',
    warnings: data?.budget.warnings || [],
    showAlert: data?.budget.status === 'warning' || data?.budget.status === 'exceeded',
    isWarning: data?.budget.status === 'warning',
    isExceeded: data?.budget.status === 'exceeded'
  };
}

// ============================================================================
// Utility Hooks
// ============================================================================

/**
 * Get top model from summary data
 */
export function useTopModel() {
  const { data } = usePublicUsageSummary();

  if (!data?.summary.by_model) {
    return { name: '-', cost: 0, count: 0 };
  }

  const models = Object.entries(data.summary.by_model);
  if (models.length === 0) {
    return { name: '-', cost: 0, count: 0 };
  }

  const [name, modelData] = models.reduce((max, current) =>
    current[1].cost > max[1].cost ? current : max
  );

  return {
    name,
    cost: modelData.cost,
    count: modelData.count,
    tokens: modelData.tokens
  };
}

/**
 * Get model list sorted by cost
 */
export function useModelList() {
  const { data } = usePublicUsageSummary();

  if (!data?.summary.by_model) {
    return [];
  }

  return Object.entries(data.summary.by_model)
    .map(([name, modelData]) => ({
      name,
      count: modelData.count,
      tokens: modelData.tokens,
      cost: modelData.cost,
      avgCost: modelData.count > 0 ? modelData.cost / modelData.count : 0
    }))
    .sort((a, b) => b.cost - a.cost);
}
