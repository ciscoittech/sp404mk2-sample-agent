import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Music,
  Package,
  Upload,
  HardDrive,
  Plus,
  Library,
  Layers,
  TrendingUp,
  Clock,
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { useSamples } from '@/hooks/useSamples';
import { useKits } from '@/hooks/useKits';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Stats card component
interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  isLoading?: boolean;
}

function StatCard({ title, value, icon: Icon, trend, isLoading }: StatCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            <Skeleton className="h-4 w-24" />
          </CardTitle>
          <Skeleton className="h-4 w-4 rounded" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-16 mb-1" />
          <Skeleton className="h-3 w-20" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {trend && (
          <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
            <TrendingUp
              className={`h-3 w-3 ${
                trend.isPositive ? 'text-green-500' : 'text-red-500 rotate-180'
              }`}
            />
            {trend.isPositive ? '+' : ''}
            {trend.value}% from last week
          </p>
        )}
      </CardContent>
    </Card>
  );
}

// Recent activity item
interface ActivityItemProps {
  sample: {
    id: number;
    title: string;
    bpm?: number;
    genre?: string;
    created_at: string;
  };
}

function ActivityItem({ sample }: ActivityItemProps) {
  return (
    <Link
      to={`/samples/${sample.id}`}
      className="flex items-center gap-3 p-3 rounded-lg hover:bg-accent transition-colors"
    >
      <div className="h-10 w-10 rounded bg-primary/10 flex items-center justify-center shrink-0">
        <Music className="h-5 w-5 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate">{sample.title}</p>
        <div className="flex items-center gap-2 mt-1">
          {sample.bpm && (
            <Badge variant="outline" className="text-xs">
              {sample.bpm} BPM
            </Badge>
          )}
          {sample.genre && (
            <Badge variant="outline" className="text-xs">
              {sample.genre}
            </Badge>
          )}
        </div>
      </div>
      <Clock className="h-4 w-4 text-muted-foreground shrink-0" />
    </Link>
  );
}

export function DashboardPage() {
  // Fetch samples and kits
  const { data: samplesData, isLoading: samplesLoading } = useSamples({ limit: 100 });
  const { data: kitsData, isLoading: kitsLoading } = useKits({ limit: 100 });

  // Calculate stats
  const stats = useMemo(() => {
    const now = new Date();
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const fourteenDaysAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);

    const samples = samplesData?.items || [];
    const kits = kitsData?.items || [];

    // Recent uploads (last 7 days)
    const recentSamples = samples.filter(
      (s) => new Date(s.created_at) >= sevenDaysAgo
    );

    // Previous period (7-14 days ago)
    const previousSamples = samples.filter(
      (s) =>
        new Date(s.created_at) >= fourteenDaysAgo &&
        new Date(s.created_at) < sevenDaysAgo
    );

    // Calculate trend
    const trend =
      previousSamples.length > 0
        ? Math.round(
            ((recentSamples.length - previousSamples.length) /
              previousSamples.length) *
              100
          )
        : 100;

    // Calculate storage (rough estimate: 2MB per sample)
    const estimatedStorageMB = samples.length * 2;
    const storageDisplay =
      estimatedStorageMB > 1024
        ? `${(estimatedStorageMB / 1024).toFixed(1)} GB`
        : `${estimatedStorageMB} MB`;

    return {
      totalSamples: samples.length,
      totalKits: kits.length,
      recentUploads: recentSamples.length,
      storage: storageDisplay,
      uploadTrend: {
        value: trend,
        isPositive: trend >= 0,
      },
    };
  }, [samplesData, kitsData]);

  // Get recent samples (last 5)
  const recentSamples = useMemo(() => {
    const samples = samplesData?.items || [];
    return [...samples]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5);
  }, [samplesData]);

  // Generate chart data (last 30 days)
  const chartData = useMemo(() => {
    const samples = samplesData?.items || [];
    const data: { date: string; uploads: number }[] = [];
    const now = new Date();

    // Generate last 30 days
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

      // Count uploads for this day
      const dayStart = new Date(date);
      dayStart.setHours(0, 0, 0, 0);
      const dayEnd = new Date(date);
      dayEnd.setHours(23, 59, 59, 999);

      const uploads = samples.filter((s) => {
        const sampleDate = new Date(s.created_at);
        return sampleDate >= dayStart && sampleDate <= dayEnd;
      }).length;

      data.push({ date: dateStr, uploads });
    }

    return data;
  }, [samplesData]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <p className="text-muted-foreground">
          Welcome back! Here's an overview of your sample library.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Samples"
          value={stats.totalSamples}
          icon={Music}
          isLoading={samplesLoading}
        />
        <StatCard
          title="Total Kits"
          value={stats.totalKits}
          icon={Package}
          isLoading={kitsLoading}
        />
        <StatCard
          title="Recent Uploads"
          value={stats.recentUploads}
          icon={Upload}
          trend={stats.uploadTrend}
          isLoading={samplesLoading}
        />
        <StatCard
          title="Storage Used"
          value={stats.storage}
          icon={HardDrive}
          isLoading={samplesLoading}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity - Takes 2 columns */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest uploaded samples</CardDescription>
          </CardHeader>
          <CardContent>
            {samplesLoading ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center gap-3 p-3">
                    <Skeleton className="h-10 w-10 rounded" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-48" />
                      <Skeleton className="h-3 w-32" />
                    </div>
                  </div>
                ))}
              </div>
            ) : recentSamples.length > 0 ? (
              <div className="space-y-1">
                {recentSamples.map((sample) => (
                  <ActivityItem key={sample.id} sample={sample} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Music className="h-12 w-12 mx-auto mb-2 opacity-20" />
                <p>No samples yet. Upload your first sample to get started!</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Shortcuts to common tasks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button asChild className="w-full justify-start" variant="outline">
              <Link to="/samples?action=upload">
                <Upload className="mr-2 h-4 w-4" />
                Upload New Sample
              </Link>
            </Button>
            <Button asChild className="w-full justify-start" variant="outline">
              <Link to="/kits?action=create">
                <Plus className="mr-2 h-4 w-4" />
                Create New Kit
              </Link>
            </Button>
            <Button asChild className="w-full justify-start" variant="outline">
              <Link to="/samples">
                <Library className="mr-2 h-4 w-4" />
                Browse Sample Library
              </Link>
            </Button>
            <Button asChild className="w-full justify-start" variant="outline">
              <Link to="/kits">
                <Layers className="mr-2 h-4 w-4" />
                View All Kits
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Upload Activity Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Activity</CardTitle>
          <CardDescription>Samples uploaded over the last 30 days</CardDescription>
        </CardHeader>
        <CardContent>
          {samplesLoading ? (
            <Skeleton className="h-[300px] w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="date"
                  className="text-xs"
                  tick={{ fill: 'hsl(var(--muted-foreground))' }}
                />
                <YAxis
                  className="text-xs"
                  tick={{ fill: 'hsl(var(--muted-foreground))' }}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '0.5rem',
                  }}
                  labelStyle={{ color: 'hsl(var(--foreground))' }}
                />
                <Line
                  type="monotone"
                  dataKey="uploads"
                  stroke="hsl(var(--chart-1))"
                  strokeWidth={2}
                  dot={{ fill: 'hsl(var(--chart-1))', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
