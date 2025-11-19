/**
 * UsagePage - API Usage & Cost Tracking Dashboard
 *
 * Displays comprehensive usage metrics, cost breakdowns, budget status,
 * and activity logs for OpenRouter API usage.
 */

import { useState } from 'react';
import { RefreshCw, Download, DollarSign, Hash, TrendingUp, Cpu, AlertTriangle, AlertCircle } from 'lucide-react';
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { useUsagePageData, useBudgetAlert, useTopModel, useModelList } from '@/hooks/useUsage';
import { exportUsageCSV, formatCost, formatNumber, formatPercentage } from '@/api/usage';

// Chart colors
const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444'];

export function UsagePage() {
  const [days, setDays] = useState(30);
  const [recentLimit, setRecentLimit] = useState(50);

  // Fetch all usage data
  const {
    summaryData,
    budgetData,
    dailyData,
    recentCalls,
    isLoading,
    hasError,
    refetchAll
  } = useUsagePageData(days, recentLimit);

  // Budget alert state
  const budgetAlert = useBudgetAlert();

  // Top model
  const topModel = useTopModel();

  // Model list
  const modelList = useModelList();

  // Handle CSV export
  const handleExport = async () => {
    try {
      await exportUsageCSV();
    } catch (error) {
      console.error('Failed to export CSV:', error);
    }
  };

  // Handle manual refresh
  const handleRefresh = () => {
    refetchAll();
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">OpenRouter API Usage & Costs</h1>
            <p className="text-muted-foreground">Track your AI model spending and token usage</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleRefresh} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button onClick={handleExport} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </div>
      </div>

      {/* Budget Alerts */}
      {budgetAlert.showAlert && (
        <Alert variant={budgetAlert.isExceeded ? 'destructive' : 'default'} className="mb-6">
          {budgetAlert.isExceeded ? (
            <AlertCircle className="h-4 w-4" />
          ) : (
            <AlertTriangle className="h-4 w-4" />
          )}
          <AlertTitle>{budgetAlert.isExceeded ? 'Budget Exceeded!' : 'Budget Warning'}</AlertTitle>
          <AlertDescription>
            {budgetAlert.warnings.join(', ')}
          </AlertDescription>
        </Alert>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {/* Total Cost Card */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Total Spend (Month)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-10 w-32" />
            ) : (
              <>
                <div className="text-3xl font-bold">
                  {formatCost(summaryData?.total_cost || 0)}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {formatNumber(summaryData?.call_count || 0)} API calls
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Tokens Used Card */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Hash className="h-4 w-4" />
              Tokens Used
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-10 w-32" />
            ) : (
              <>
                <div className="text-3xl font-bold">
                  {formatNumber(summaryData?.total_tokens || 0)}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {formatNumber(summaryData?.input_tokens || 0)} in / {formatNumber(summaryData?.output_tokens || 0)} out
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Budget Status Card */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Budget Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-10 w-32" />
            ) : (
              <>
                <div className={`text-3xl font-bold ${
                  (budgetData?.monthly.percentage || 0) > 0.8 ? 'text-red-500' : ''
                }`}>
                  ${budgetData?.monthly.remaining.toFixed(2) || '0.00'}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {formatPercentage(budgetData?.monthly.percentage || 0)} of budget used
                </p>
                <div className="mt-2 w-full bg-secondary h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      (budgetData?.monthly.percentage || 0) < 0.5
                        ? 'bg-green-500'
                        : (budgetData?.monthly.percentage || 0) < 0.8
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${((budgetData?.monthly.percentage || 0) * 100)}%` }}
                  />
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Top Model Card */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Cpu className="h-4 w-4" />
              Top Model
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-10 w-32" />
            ) : (
              <>
                <div className="text-xl font-bold truncate" title={topModel.name}>
                  {topModel.name}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {formatCost(topModel.cost)} • {topModel.count} calls
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Operation Breakdown Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Cost Breakdown by Operation</CardTitle>
            <CardDescription>Distribution of API costs across different operations</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : summaryData && Object.keys(summaryData.by_operation).length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={Object.entries(summaryData.by_operation).map(([name, data]) => ({
                      name,
                      value: data.cost,
                      count: data.count
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {Object.keys(summaryData.by_operation).map((_, index) => (
                      <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatCost(Number(value))} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                No operation data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Daily Cost Trend Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Daily Cost (Last {days} Days)</CardTitle>
            <CardDescription>Track spending trends over time</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : dailyData && dailyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis
                    dataKey="date"
                    className="text-xs"
                    tick={{ fill: 'hsl(var(--muted-foreground))' }}
                  />
                  <YAxis
                    className="text-xs"
                    tick={{ fill: 'hsl(var(--muted-foreground))' }}
                    tickFormatter={(value) => `$${value.toFixed(2)}`}
                  />
                  <Tooltip
                    formatter={(value) => formatCost(Number(value))}
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '6px'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="cost"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6' }}
                    name="Cost (USD)"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                No daily data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Model Comparison Table */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Model Comparison</CardTitle>
          <CardDescription>Detailed breakdown of usage by model</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : modelList.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Model</TableHead>
                    <TableHead className="text-right">Calls</TableHead>
                    <TableHead className="text-right">Tokens</TableHead>
                    <TableHead className="text-right">Cost</TableHead>
                    <TableHead className="text-right">Avg Cost/Call</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {modelList.map((model) => (
                    <TableRow key={model.name}>
                      <TableCell className="font-mono text-xs">{model.name}</TableCell>
                      <TableCell className="text-right">{formatNumber(model.count)}</TableCell>
                      <TableCell className="text-right">{formatNumber(model.tokens)}</TableCell>
                      <TableCell className="text-right">{formatCost(model.cost)}</TableCell>
                      <TableCell className="text-right">{formatCost(model.avgCost)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No model data available
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent API Calls */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Recent API Calls (Last {recentLimit})</CardTitle>
          <CardDescription>Detailed log of recent API usage</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : recentCalls && recentCalls.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Model</TableHead>
                    <TableHead>Operation</TableHead>
                    <TableHead className="text-right">Tokens (in/out)</TableHead>
                    <TableHead className="text-right">Cost</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentCalls.map((call) => (
                    <TableRow key={call.id}>
                      <TableCell className="text-xs">
                        {new Date(call.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell className="text-xs font-mono">{call.model}</TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="text-xs">
                          {call.operation}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs text-right">
                        {formatNumber(call.total_tokens)}
                        <span className="text-muted-foreground ml-1">
                          ({formatNumber(call.input_tokens)}/{formatNumber(call.output_tokens)})
                        </span>
                      </TableCell>
                      <TableCell className="text-xs text-right">
                        {formatCost(call.total_cost)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No recent API calls
            </div>
          )}
        </CardContent>
      </Card>

      {/* Error State */}
      {hasError && (
        <Alert variant="destructive" className="mt-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error Loading Usage Data</AlertTitle>
          <AlertDescription>
            Failed to load usage data. Please try refreshing the page.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

export default UsagePage;
