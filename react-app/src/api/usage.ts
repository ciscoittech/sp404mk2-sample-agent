/**
 * API Client for Usage & Cost Tracking
 *
 * Provides functions to fetch API usage metrics, cost data,
 * budget status, and activity logs from the backend.
 */

import { apiClient } from './client';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

export interface UsageSummary {
  total_cost: number;
  total_tokens: number;
  input_tokens: number;
  output_tokens: number;
  call_count: number;
  by_operation: Record<string, { cost: number; count: number }>;
  by_model: Record<string, { cost: number; tokens: number; count: number }>;
}

export interface BudgetStatus {
  status: 'ok' | 'warning' | 'exceeded';
  warnings: string[];
  monthly: {
    used: number;
    limit: number;
    percentage: number;
    remaining: number;
  };
  daily: {
    tokens_used: number;
    tokens_limit: number;
    percentage: number;
    tokens_remaining: number;
  };
}

export interface DailyUsage {
  date: string;
  cost: number;
  tokens: number;
}

export interface ApiCall {
  id: number;
  model: string;
  operation: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  total_cost: number;
  created_at: string;
  sample_id: number | null;
  batch_id: string | null;
}

export interface PublicUsageSummaryResponse {
  summary: UsageSummary;
  budget: BudgetStatus;
}

export interface DailyUsageResponse {
  days: number;
  data: DailyUsage[];
}

export interface RecentCallsResponse {
  limit: number;
  count: number;
  calls: ApiCall[];
}

export interface ModelStats {
  name: string;
  count: number;
  tokens: number;
  cost: number;
  avgCost: number;
}

// ============================================================================
// Public Endpoints (No Authentication Required)
// ============================================================================

/**
 * Get usage summary for public/demo user
 * Returns combined summary and budget data
 */
export async function getPublicUsageSummary(): Promise<PublicUsageSummaryResponse> {
  const response = await apiClient.get<PublicUsageSummaryResponse>('/public/usage/summary');
  return response.data;
}

/**
 * Get daily usage totals for last N days (public)
 */
export async function getPublicDailyUsage(days: number = 30): Promise<DailyUsageResponse> {
  const response = await apiClient.get<DailyUsageResponse>('/public/usage/daily', {
    params: { days }
  });
  return response.data;
}

/**
 * Get recent API calls (public)
 */
export async function getPublicRecentCalls(limit: number = 50): Promise<RecentCallsResponse> {
  const response = await apiClient.get<RecentCallsResponse>('/public/usage/recent', {
    params: { limit }
  });
  return response.data;
}

// ============================================================================
// Authenticated Endpoints
// ============================================================================

/**
 * Get usage summary for authenticated user
 * Supports optional date range filtering
 */
export async function getUsageSummary(
  startDate?: Date,
  endDate?: Date
): Promise<UsageSummary> {
  const params: Record<string, string> = {};
  if (startDate) params.start_date = startDate.toISOString();
  if (endDate) params.end_date = endDate.toISOString();

  const response = await apiClient.get<UsageSummary>('/usage/summary', { params });
  return response.data;
}

/**
 * Get daily usage totals for last N days
 */
export async function getDailyUsage(days: number = 30): Promise<DailyUsageResponse> {
  const response = await apiClient.get<DailyUsageResponse>('/usage/daily', {
    params: { days }
  });
  return response.data;
}

/**
 * Get current budget status
 */
export async function getBudgetStatus(): Promise<BudgetStatus> {
  const response = await apiClient.get<BudgetStatus>('/usage/budget');
  return response.data;
}

/**
 * Get recent API calls
 */
export async function getRecentCalls(limit: number = 50): Promise<RecentCallsResponse> {
  const response = await apiClient.get<RecentCallsResponse>('/usage/recent', {
    params: { limit }
  });
  return response.data;
}

/**
 * Export usage data as CSV
 * Downloads file directly to browser
 */
export async function exportUsageCSV(startDate?: Date, endDate?: Date): Promise<void> {
  const params: Record<string, string> = {};
  if (startDate) params.start_date = startDate.toISOString();
  if (endDate) params.end_date = endDate.toISOString();

  const response = await apiClient.get('/usage/export', {
    params,
    responseType: 'blob'
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `openrouter_usage_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Transform summary data to get model statistics list
 * Sorted by cost (highest first)
 */
export function getModelStatsList(summary: UsageSummary): ModelStats[] {
  return Object.entries(summary.by_model)
    .map(([name, data]) => ({
      name,
      count: data.count,
      tokens: data.tokens,
      cost: data.cost,
      avgCost: data.count > 0 ? data.cost / data.count : 0
    }))
    .sort((a, b) => b.cost - a.cost);
}

/**
 * Get top model by cost
 */
export function getTopModel(summary: UsageSummary): ModelStats | null {
  const models = getModelStatsList(summary);
  return models.length > 0 ? models[0] : null;
}

/**
 * Format cost as currency string
 */
export function formatCost(cost: number): string {
  return `$${cost.toFixed(4)}`;
}

/**
 * Format large numbers with commas
 */
export function formatNumber(num: number): string {
  return num.toLocaleString();
}

/**
 * Format percentage with 1 decimal place
 */
export function formatPercentage(percentage: number): string {
  return `${(percentage * 100).toFixed(1)}%`;
}

/**
 * Get budget status color class
 */
export function getBudgetStatusColor(percentage: number): string {
  if (percentage < 0.5) return 'text-green-500';
  if (percentage < 0.8) return 'text-yellow-500';
  return 'text-red-500';
}

/**
 * Get budget progress bar color class
 */
export function getBudgetProgressColor(percentage: number): string {
  if (percentage < 0.5) return 'bg-green-500';
  if (percentage < 0.8) return 'bg-yellow-500';
  return 'bg-red-500';
}
