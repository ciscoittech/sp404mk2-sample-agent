import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useCreateBatch } from '@/hooks/useBatches';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import type { BatchCreateRequest } from '@/types/api';

interface CreateBatchDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function CreateBatchDialog({ open, onOpenChange, onSuccess }: CreateBatchDialogProps) {
  const { mutate: createBatch, isPending } = useCreateBatch();
  const [formData, setFormData] = useState<BatchCreateRequest>({
    collection_path: '',
    batch_size: 5,
    options: {
      vibe_analysis: true,
      groove_analysis: false,
      era_detection: false,
    },
  });
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setResult(null);

    // Validation
    if (!formData.collection_path) {
      setResult({
        success: false,
        message: 'Please enter a collection path',
      });
      return;
    }

    createBatch(formData, {
      onSuccess: () => {
        setResult({
          success: true,
          message: 'Batch processing started successfully!',
        });
        // Reset form after delay
        setTimeout(() => {
          setFormData({
            collection_path: '',
            batch_size: 5,
            options: {
              vibe_analysis: true,
              groove_analysis: false,
              era_detection: false,
            },
          });
          setResult(null);
          onOpenChange(false);
          onSuccess?.();
        }, 2000);
      },
      onError: (error: any) => {
        setResult({
          success: false,
          message: error.response?.data?.detail || 'Failed to create batch',
        });
      },
    });
  };

  const handleOptionChange = (key: string, value: boolean) => {
    setFormData((prev) => ({
      ...prev,
      options: {
        ...prev.options,
        [key]: value,
      },
    }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Create New Batch</DialogTitle>
          <DialogDescription>
            Start processing a collection of samples with automated analysis.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Collection Path */}
          <div className="space-y-2">
            <Label htmlFor="collection_path">
              Collection Path <span className="text-red-500">*</span>
            </Label>
            <Input
              id="collection_path"
              placeholder="/path/to/sample/collection"
              value={formData.collection_path}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, collection_path: e.target.value }))
              }
              disabled={isPending}
              required
            />
            <p className="text-xs text-muted-foreground">
              Absolute path to the directory containing audio samples
            </p>
          </div>

          {/* Batch Size */}
          <div className="space-y-2">
            <Label htmlFor="batch_size">Batch Size</Label>
            <Input
              id="batch_size"
              type="number"
              min="1"
              max="10"
              value={formData.batch_size}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, batch_size: parseInt(e.target.value) }))
              }
              disabled={isPending}
            />
            <p className="text-xs text-muted-foreground">
              Number of samples to process concurrently (1-10)
            </p>
          </div>

          {/* Processing Options */}
          <div className="space-y-3">
            <Label>Processing Options</Label>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="vibe_analysis"
                  checked={formData.options?.vibe_analysis ?? true}
                  onChange={(e) => handleOptionChange('vibe_analysis', e.target.checked)}
                  disabled={isPending}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <label
                  htmlFor="vibe_analysis"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Vibe Analysis
                </label>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="groove_analysis"
                  checked={formData.options?.groove_analysis ?? false}
                  onChange={(e) => handleOptionChange('groove_analysis', e.target.checked)}
                  disabled={isPending}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <label
                  htmlFor="groove_analysis"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Groove Analysis
                </label>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="era_detection"
                  checked={formData.options?.era_detection ?? false}
                  onChange={(e) => handleOptionChange('era_detection', e.target.checked)}
                  disabled={isPending}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <label
                  htmlFor="era_detection"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Era Detection
                </label>
              </div>
            </div>
          </div>

          {/* Result Alert */}
          {result && (
            <Alert variant={result.success ? 'default' : 'destructive'}>
              {result.success ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              <AlertDescription>{result.message}</AlertDescription>
            </Alert>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isPending}>
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Batch'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
