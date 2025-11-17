import { useState } from 'react';
import { useBuildProject, useDownloadProject } from '@/hooks/useProjects';
import type { ProjectBuildRequest, ProjectBuildResult } from '@/types/api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Loader2, Download, Zap, CheckCircle2, AlertCircle } from 'lucide-react';

interface ProjectBuilderDialogProps {
  kitId: number;
  kitName: string;
  sampleCount: number;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

type ViewState = 'form' | 'loading' | 'success' | 'error';

export function ProjectBuilderDialog({
  kitId,
  kitName,
  sampleCount,
  isOpen,
  onOpenChange,
}: ProjectBuilderDialogProps) {
  // Form state
  const [projectName, setProjectName] = useState('');
  const [projectBpm, setProjectBpm] = useState<string>('');
  const [audioFormat, setAudioFormat] = useState<'wav' | 'aiff'>('wav');
  const [includeBankLayout, setIncludeBankLayout] = useState(false);

  // View state
  const [viewState, setViewState] = useState<ViewState>('form');
  const [buildResult, setBuildResult] = useState<ProjectBuildResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');

  // Mutations
  const buildProject = useBuildProject();
  const downloadProject = useDownloadProject();

  // Validation
  const validateProjectName = (name: string): string | null => {
    if (!name.trim()) return 'Project name is required';
    if (name.length < 1 || name.length > 31) return 'Name must be 1-31 characters';
    if (!/^[\x00-\x7F]*$/.test(name)) return 'Only ASCII characters allowed';
    return null;
  };

  const validateBpm = (bpm: string): string | null => {
    if (!bpm.trim()) return null; // Optional
    const num = parseFloat(bpm);
    if (isNaN(num)) return 'BPM must be a number';
    if (num < 20 || num > 300) return 'BPM must be between 20 and 300';
    return null;
  };

  const isFormValid = (): boolean => {
    return validateProjectName(projectName) === null && validateBpm(projectBpm) === null;
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!isFormValid()) return;

    const request: ProjectBuildRequest = {
      project_name: projectName.trim(),
      project_bpm: projectBpm.trim() ? parseFloat(projectBpm) : null,
      audio_format: audioFormat,
      include_bank_layout: includeBankLayout,
    };

    setViewState('loading');
    setErrorMessage('');

    try {
      const result = await buildProject.mutateAsync({ kitId, request });
      setBuildResult(result);

      if (result.success) {
        setViewState('success');
      } else {
        setViewState('error');
        setErrorMessage(result.error_message || 'Unknown error occurred');
      }
    } catch (error: any) {
      setViewState('error');
      setErrorMessage(error.response?.data?.detail || error.message || 'Failed to build project');
    }
  };

  // Handle download
  const handleDownload = async () => {
    if (!buildResult?.export_id) return;

    try {
      await downloadProject.mutateAsync(buildResult.export_id);
      // Close dialog after successful download
      setTimeout(() => {
        handleClose();
      }, 1000);
    } catch (error) {
      // Error already handled by mutation
      console.error('Download failed:', error);
    }
  };

  // Handle retry
  const handleRetry = () => {
    setViewState('form');
    setErrorMessage('');
    setBuildResult(null);
  };

  // Handle close
  const handleClose = () => {
    setViewState('form');
    setProjectName('');
    setProjectBpm('');
    setAudioFormat('wav');
    setIncludeBankLayout(false);
    setBuildResult(null);
    setErrorMessage('');
    onOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-500" />
            Generate SP-404MK2 Project
          </DialogTitle>
        </DialogHeader>

        {/* FORM VIEW */}
        {viewState === 'form' && (
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <div className="text-sm text-muted-foreground">
                Kit: <span className="font-medium text-foreground">{kitName}</span>
                {' · '}
                {sampleCount} sample{sampleCount !== 1 ? 's' : ''}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="project-name">Project Name *</Label>
              <Input
                id="project-name"
                placeholder="MyProject"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                maxLength={31}
                className={validateProjectName(projectName) ? 'border-red-500' : ''}
              />
              {projectName && validateProjectName(projectName) && (
                <p className="text-xs text-red-500">{validateProjectName(projectName)}</p>
              )}
              <p className="text-xs text-muted-foreground">1-31 ASCII characters</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="project-bpm">Project BPM (optional)</Label>
              <Input
                id="project-bpm"
                type="number"
                placeholder="Auto-detect from samples"
                value={projectBpm}
                onChange={(e) => setProjectBpm(e.target.value)}
                min={20}
                max={300}
                className={projectBpm && validateBpm(projectBpm) ? 'border-red-500' : ''}
              />
              {projectBpm && validateBpm(projectBpm) && (
                <p className="text-xs text-red-500">{validateBpm(projectBpm)}</p>
              )}
              <p className="text-xs text-muted-foreground">20-300 BPM, leave blank for auto-detect</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="audio-format">Audio Format</Label>
              <Select value={audioFormat} onValueChange={(v) => setAudioFormat(v as 'wav' | 'aiff')}>
                <SelectTrigger id="audio-format">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="wav">WAV (48kHz/16-bit)</SelectItem>
                  <SelectItem value="aiff">AIFF (48kHz/16-bit)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="bank-layout">Include Bank Layout</Label>
                <p className="text-xs text-muted-foreground">
                  Add bank configuration metadata
                </p>
              </div>
              <Switch
                id="bank-layout"
                checked={includeBankLayout}
                onCheckedChange={setIncludeBankLayout}
              />
            </div>
          </div>
        )}

        {/* LOADING VIEW */}
        {viewState === 'loading' && (
          <div className="flex flex-col items-center justify-center py-12 space-y-4">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
            <div className="text-center space-y-2">
              <p className="font-medium">Building project...</p>
              <p className="text-sm text-muted-foreground">
                Converting samples and generating PADCONF.BIN
              </p>
            </div>
          </div>
        )}

        {/* SUCCESS VIEW */}
        {viewState === 'success' && buildResult && (
          <div className="space-y-4 py-4">
            <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
              <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400 flex-shrink-0" />
              <div className="space-y-1">
                <p className="font-medium text-green-900 dark:text-green-100">
                  Project generated successfully!
                </p>
                <p className="text-sm text-green-700 dark:text-green-300">
                  {buildResult.project_name}
                </p>
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Samples:</span>
                <span className="font-medium">{buildResult.sample_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">File size:</span>
                <span className="font-medium">
                  {(buildResult.file_size_bytes / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Export ID:</span>
                <span className="font-mono text-xs">{buildResult.export_id}</span>
              </div>
            </div>

            <Button
              onClick={handleDownload}
              disabled={downloadProject.isPending}
              className="w-full"
              size="lg"
            >
              {downloadProject.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Downloading...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Download Project ZIP
                </>
              )}
            </Button>
          </div>
        )}

        {/* ERROR VIEW */}
        {viewState === 'error' && (
          <div className="space-y-4 py-4">
            <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-950 rounded-lg border border-red-200 dark:border-red-800">
              <AlertCircle className="h-6 w-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="font-medium text-red-900 dark:text-red-100">
                  Failed to build project
                </p>
                <p className="text-sm text-red-700 dark:text-red-300">
                  {errorMessage || 'An unknown error occurred'}
                </p>
              </div>
            </div>

            <Button onClick={handleRetry} className="w-full" variant="outline">
              Try Again
            </Button>
          </div>
        )}

        {/* FOOTER */}
        {viewState === 'form' && (
          <DialogFooter>
            <Button variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={!isFormValid() || buildProject.isPending}
            >
              {buildProject.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Building...
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4 mr-2" />
                  Generate Project
                </>
              )}
            </Button>
          </DialogFooter>
        )}

        {viewState === 'success' && (
          <DialogFooter>
            <Button variant="outline" onClick={handleClose}>
              Close
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );
}
