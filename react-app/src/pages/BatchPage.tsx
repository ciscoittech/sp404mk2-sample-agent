import { useState } from 'react';
import { useActiveBatches, useBatchHistory, useCancelBatch, useRetryBatch } from '@/hooks/useBatches';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Loader2, Plus, AlertCircle, FileText, Clock, X, RotateCcw } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { BatchDetailsModal } from '@/components/batches/BatchDetailsModal';
import { CreateBatchDialog } from '@/components/batches/CreateBatchDialog';
import type { Batch, BatchStatus } from '@/types/api';

export function BatchPage() {
  const [selectedBatchId, setSelectedBatchId] = useState<string | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [cancelBatchId, setCancelBatchId] = useState<string | null>(null);

  const { data: activeBatches, isLoading: isLoadingActive } = useActiveBatches();
  const { data: historyBatches, isLoading: isLoadingHistory } = useBatchHistory();
  const { mutate: cancelBatch } = useCancelBatch();
  const { mutate: retryBatch } = useRetryBatch();

  const handleSelectBatch = (id: string) => {
    setSelectedBatchId(id);
    setShowDetailsModal(true);
  };

  const handleCancelBatch = (id: string) => {
    setCancelBatchId(id);
  };

  const confirmCancel = () => {
    if (cancelBatchId) {
      cancelBatch(cancelBatchId);
      setCancelBatchId(null);
    }
  };

  const handleRetryBatch = (id: string) => {
    retryBatch(id);
  };

  return (
    <div className="container mx-auto px-4 py-6 max-w-[1800px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold">Batch Processing</h2>
          <p className="text-muted-foreground mt-2">
            Process sample collections with automated analysis
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Batch
        </Button>
      </div>

      {/* Active Batches Section */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-4">Active Processing</h3>
        <ActiveBatchesList
          batches={activeBatches?.items || []}
          isLoading={isLoadingActive}
          onSelectBatch={handleSelectBatch}
          onCancelBatch={handleCancelBatch}
        />
      </div>

      {/* Batch History Section */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Processing History</h3>
        <BatchHistoryTable
          batches={historyBatches?.items || []}
          isLoading={isLoadingHistory}
          onSelectBatch={handleSelectBatch}
          onRetryBatch={handleRetryBatch}
        />
      </div>

      {/* Batch Details Modal */}
      <BatchDetailsModal
        batchId={selectedBatchId}
        open={showDetailsModal}
        onOpenChange={setShowDetailsModal}
      />

      {/* Create Batch Dialog */}
      <CreateBatchDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
      />

      {/* Cancel Confirmation Dialog */}
      <Dialog open={!!cancelBatchId} onOpenChange={() => setCancelBatchId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Batch Processing?</DialogTitle>
            <DialogDescription>
              Are you sure you want to cancel this batch? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCancelBatchId(null)}>
              No, keep processing
            </Button>
            <Button variant="destructive" onClick={confirmCancel}>
              Yes, cancel batch
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Helper function to get status badge variant
function getStatusBadgeVariant(status: BatchStatus): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'completed':
      return 'default';
    case 'processing':
      return 'secondary';
    case 'failed':
      return 'destructive';
    default:
      return 'outline';
  }
}

// Helper function to get status badge color classes
function getStatusBadgeColor(status: BatchStatus): string {
  switch (status) {
    case 'completed':
      return 'bg-green-500/10 text-green-500 border-green-500/20';
    case 'processing':
      return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
    case 'pending':
      return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
    case 'failed':
      return 'bg-red-500/10 text-red-500 border-red-500/20';
    case 'cancelled':
      return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    default:
      return '';
  }
}

// Format duration helper
function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  } else if (seconds < 3600) {
    return `${(seconds / 60).toFixed(1)}m`;
  } else {
    return `${(seconds / 3600).toFixed(1)}h`;
  }
}

// Format date helper
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// Extract collection name from path
function getCollectionName(path: string): string {
  return path.split('/').pop() || path;
}

// Active Batches List Component
interface ActiveBatchesListProps {
  batches: Batch[];
  isLoading: boolean;
  onSelectBatch: (id: string) => void;
  onCancelBatch: (id: string) => void;
}

function ActiveBatchesList({ batches, isLoading, onSelectBatch, onCancelBatch }: ActiveBatchesListProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (batches.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <FileText className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
          <p className="text-muted-foreground text-center">No active batch processes</p>
          <p className="text-sm text-muted-foreground text-center mt-1">
            Create a new batch to start processing samples
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {batches.map((batch) => (
        <BatchCard key={batch.id} batch={batch} onSelect={onSelectBatch} onCancel={onCancelBatch} />
      ))}
    </div>
  );
}

// Batch Card Component
interface BatchCardProps {
  batch: Batch;
  onSelect: (id: string) => void;
  onCancel: (id: string) => void;
}

function BatchCard({ batch, onSelect, onCancel }: BatchCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between mb-2">
          <CardTitle className="text-base font-medium truncate flex-1 cursor-pointer" onClick={() => onSelect(batch.id)}>
            {getCollectionName(batch.collection_path)}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge className={getStatusBadgeColor(batch.status)}>
              {batch.status}
            </Badge>
            {batch.status === 'processing' && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={(e) => {
                  e.stopPropagation();
                  onCancel(batch.id);
                }}
              >
                <X className="h-4 w-4 text-destructive" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent onClick={() => onSelect(batch.id)} className="cursor-pointer">
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              {batch.processed_samples}/{batch.total_samples} samples
            </span>
            <span className="font-medium">{batch.progress_percentage.toFixed(1)}%</span>
          </div>

          <Progress value={batch.progress_percentage} className="h-2" />

          {batch.error_count > 0 && (
            <div className="flex items-center gap-2 text-xs text-red-500">
              <AlertCircle className="h-3 w-3" />
              <span>{batch.error_count} errors occurred</span>
            </div>
          )}

          <div className="flex items-center gap-2 text-xs text-muted-foreground pt-2">
            <Clock className="h-3 w-3" />
            <span>Started: {formatDate(batch.created_at)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Batch History Table Component
interface BatchHistoryTableProps {
  batches: Batch[];
  isLoading: boolean;
  onSelectBatch: (id: string) => void;
  onRetryBatch: (id: string) => void;
}

function BatchHistoryTable({ batches, isLoading, onSelectBatch, onRetryBatch }: BatchHistoryTableProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (batches.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <FileText className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
          <p className="text-muted-foreground text-center">No completed batches yet</p>
          <p className="text-sm text-muted-foreground text-center mt-1">
            Process some sample collections to see history here
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="text-left p-4 font-medium">Collection</th>
                <th className="text-left p-4 font-medium">Status</th>
                <th className="text-left p-4 font-medium">Samples</th>
                <th className="text-left p-4 font-medium">Success Rate</th>
                <th className="text-left p-4 font-medium">Duration</th>
                <th className="text-left p-4 font-medium">Created</th>
                <th className="text-left p-4 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {batches.map((batch) => (
                <BatchHistoryRow key={batch.id} batch={batch} onSelect={onSelectBatch} onRetry={onRetryBatch} />
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

// Batch History Row Component
interface BatchHistoryRowProps {
  batch: Batch;
  onSelect: (id: string) => void;
  onRetry: (id: string) => void;
}

function BatchHistoryRow({ batch, onSelect, onRetry }: BatchHistoryRowProps) {
  const successRate = batch.processed_samples > 0
    ? ((batch.processed_samples - batch.error_count) / batch.processed_samples) * 100
    : 0;

  const getSuccessRateColor = (rate: number): string => {
    if (rate >= 80) return 'text-green-500';
    if (rate >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <tr className="border-b hover:bg-muted/50 transition-colors">
      <td className="p-4">
        <div className="font-medium">{getCollectionName(batch.collection_path)}</div>
        <div className="text-xs text-muted-foreground truncate max-w-xs">
          {batch.collection_path}
        </div>
      </td>
      <td className="p-4">
        <Badge className={getStatusBadgeColor(batch.status)}>
          {batch.status}
        </Badge>
      </td>
      <td className="p-4">
        {batch.processed_samples}/{batch.total_samples}
      </td>
      <td className="p-4">
        {batch.processed_samples > 0 ? (
          <span className={getSuccessRateColor(successRate)}>
            {successRate.toFixed(1)}%
          </span>
        ) : (
          '--'
        )}
      </td>
      <td className="p-4">
        {batch.completed_at && batch.started_at
          ? formatDuration(
              (new Date(batch.completed_at).getTime() - new Date(batch.started_at).getTime()) / 1000
            )
          : '--'}
      </td>
      <td className="p-4 text-sm text-muted-foreground">
        {formatDate(batch.created_at)}
      </td>
      <td className="p-4">
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => onSelect(batch.id)}>
            Details
          </Button>
          {batch.status === 'failed' && (
            <Button variant="outline" size="sm" onClick={() => onRetry(batch.id)}>
              <RotateCcw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          )}
        </div>
      </td>
    </tr>
  );
}

export default BatchPage;
