import { useEffect, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { useBatch, useImportBatch } from '@/hooks/useBatches';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Loader2, AlertCircle, Download, Upload, Wifi, WifiOff, CheckCircle } from 'lucide-react';
import type { Batch, BatchProgress, BatchStatus } from '@/types/api';
import { batchesApi } from '@/api';

interface BatchDetailsModalProps {
  batchId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BatchDetailsModal({ batchId, open, onOpenChange }: BatchDetailsModalProps) {
  const { data: batch, isLoading } = useBatch(batchId);
  const { mutate: importBatch, isPending: isImporting } = useImportBatch();
  const [wsProgress, setWsProgress] = useState<BatchProgress | null>(null);
  const [importResult, setImportResult] = useState<{ success: boolean; message: string } | null>(null);

  // WebSocket URL (only connect when modal is open and batch is processing)
  const wsUrl = batch && (batch.status === 'processing' || batch.status === 'pending')
    ? `ws://localhost:8100/api/v1/batch/${batch.id}/progress`
    : null;

  const { isConnected } = useWebSocket(wsUrl || '', {
    onMessage: (message) => {
      if (message.type === 'progress' && message.data) {
        setWsProgress(message.data);
      }
    },
    reconnect: true,
  });

  // Reset WebSocket progress when modal closes
  useEffect(() => {
    if (!open) {
      setWsProgress(null);
    }
  }, [open]);

  const handleImport = () => {
    if (!batch) return;
    setImportResult(null);
    importBatch(batch.id, {
      onSuccess: (data) => {
        setImportResult({
          success: true,
          message: `Successfully imported ${data.imported_count} samples!`,
        });
      },
      onError: (error: any) => {
        setImportResult({
          success: false,
          message: error.response?.data?.detail || 'Failed to import batch results',
        });
      },
    });
  };

  const handleDownload = () => {
    if (!batch) return;
    const url = batchesApi.getExportUrl(batch.id);
    window.open(url, '_blank');
  };

  if (isLoading) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent>
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  if (!batch) return null;

  // Use WebSocket data if available, otherwise use API data
  const displayData = wsProgress || batch;
  const progress = wsProgress?.percentage ?? batch.progress_percentage;

  const getStatusBadgeColor = (status: BatchStatus): string => {
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
  };

  const formatDuration = (start?: string, end?: string): string => {
    if (!start || !end) return '--';
    const duration = (new Date(end).getTime() - new Date(start).getTime()) / 1000;
    if (duration < 60) return `${Math.round(duration)}s`;
    if (duration < 3600) return `${(duration / 60).toFixed(1)}m`;
    return `${(duration / 3600).toFixed(1)}h`;
  };

  const successRate = batch.processed_samples > 0
    ? ((batch.success_count / batch.processed_samples) * 100).toFixed(1)
    : '--';

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle>Batch Details</DialogTitle>
            {(batch.status === 'processing' || batch.status === 'pending') && (
              <div className="flex items-center gap-2 text-xs">
                {isConnected ? (
                  <>
                    <Wifi className="h-3 w-3 text-green-500" />
                    <span className="text-green-500">Live</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-3 w-3 text-gray-500" />
                    <span className="text-gray-500">Offline</span>
                  </>
                )}
              </div>
            )}
          </div>
        </DialogHeader>

        <div className="space-y-4">
          {/* Status and Progress */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Badge className={getStatusBadgeColor(batch.status)}>{batch.status}</Badge>
              <span className="text-sm font-medium">{progress.toFixed(1)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
            <div className="text-sm text-muted-foreground">
              {displayData.processed_samples}/{displayData.total_samples} samples processed
            </div>
            {wsProgress?.current_sample && (
              <div className="text-xs text-muted-foreground">
                Current: {wsProgress.current_sample}
              </div>
            )}
            {wsProgress?.eta_minutes && (
              <div className="text-xs text-muted-foreground">
                ETA: {wsProgress.eta_minutes.toFixed(1)} minutes
              </div>
            )}
          </div>

          <Separator />

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-muted-foreground">Status:</span>
              <div className="font-medium mt-1">
                <Badge className={getStatusBadgeColor(batch.status)}>{batch.status}</Badge>
              </div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Samples:</span>
              <div className="font-medium mt-1">
                {batch.processed_samples}/{batch.total_samples}
              </div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Success Rate:</span>
              <div className="font-medium mt-1">{successRate}%</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Duration:</span>
              <div className="font-medium mt-1">
                {formatDuration(batch.started_at, batch.completed_at)}
              </div>
            </div>
          </div>

          {/* Error Log */}
          {batch.error_log && batch.error_log.length > 0 && (
            <>
              <Separator />
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <div className="font-semibold mb-2">Errors:</div>
                  <ul className="text-sm space-y-1">
                    {batch.error_log.map((error, idx) => (
                      <li key={idx}>{error}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            </>
          )}

          {/* Options */}
          {batch.options && Object.keys(batch.options).length > 0 && (
            <>
              <Separator />
              <div>
                <div className="text-sm font-medium mb-2">Options</div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {Object.entries(batch.options).map(([key, value]) => (
                    <div key={key}>
                      <span className="text-muted-foreground capitalize">
                        {key.replace(/_/g, ' ')}:
                      </span>
                      <span className="font-medium ml-2">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Import Result Alert */}
          {importResult && (
            <>
              <Separator />
              <Alert variant={importResult.success ? 'default' : 'destructive'}>
                {importResult.success ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <AlertDescription>{importResult.message}</AlertDescription>
              </Alert>
            </>
          )}
        </div>

        <DialogFooter>
          <div className="flex gap-2 w-full">
            {batch.export_path && (
              <>
                <Button
                  variant="outline"
                  onClick={handleDownload}
                  className="flex-1"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Results
                </Button>
                <Button
                  onClick={handleImport}
                  disabled={isImporting || batch.status !== 'completed'}
                  className="flex-1"
                >
                  {isImporting ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Upload className="h-4 w-4 mr-2" />
                  )}
                  Import to Samples
                </Button>
              </>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
