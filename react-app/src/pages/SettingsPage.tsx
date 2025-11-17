import { PageLayout } from '@/components/layout/PageLayout';
import { usePreferences, useUpdatePreferences } from '@/hooks/usePreferences';
import { preferencesApi } from '@/api/preferences';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import type { UserPreferences, Model } from '@/types/api';
import type { AxiosError } from 'axios';

export function SettingsPage() {
  const { data: preferences, isLoading } = usePreferences();
  const updateMutation = useUpdatePreferences();
  const [formData, setFormData] = useState<Partial<UserPreferences>>({});
  const [models, setModels] = useState<Model[]>([]);

  // Load preferences when they arrive
  useEffect(() => {
    if (preferences) {
      setFormData(preferences);
    }
  }, [preferences]);

  // Load available models
  useEffect(() => {
    preferencesApi.getModels().then(setModels).catch((error) => {
      console.error('Failed to load models:', error);
      toast.error('Failed to load available models');
    });
  }, []);

  const validateForm = (): boolean => {
    if (formData.max_cost_per_request !== undefined) {
      if (formData.max_cost_per_request <= 0) {
        toast.error('Max cost must be positive number');
        return false;
      }
    }

    // Required fields
    if (!formData.vibe_analysis_model) {
      toast.error('Please select a vibe analysis model');
      return false;
    }

    if (!formData.batch_processing_model) {
      toast.error('Please select a batch processing model');
      return false;
    }

    if (!formData.default_export_format) {
      toast.error('Please select export format');
      return false;
    }

    if (!formData.default_export_organization) {
      toast.error('Please select organization strategy');
      return false;
    }

    return true;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    // Only send fields that differ from original
    const updates = Object.entries(formData).reduce((acc, [key, value]) => {
      if (preferences && preferences[key as keyof UserPreferences] !== value) {
        acc[key as keyof UserPreferences] = value;
      }
      return acc;
    }, {} as Partial<UserPreferences>);

    if (Object.keys(updates).length === 0) {
      toast.info('No changes to save');
      return;
    }

    updateMutation.mutate(updates);
  };

  // Handle save success
  useEffect(() => {
    if (updateMutation.isSuccess) {
      toast.success('Settings saved successfully!');
    }
  }, [updateMutation.isSuccess]);

  // Handle save error
  useEffect(() => {
    if (updateMutation.isError) {
      const error = updateMutation.error as AxiosError;
      const message = error.response?.data?.detail || 'Failed to save settings';
      toast.error(String(message));
    }
  }, [updateMutation.isError]);

  if (isLoading) {
    return (
      <PageLayout>
        <div className="flex justify-center items-center h-64">
          <p className="text-muted-foreground">Loading preferences...</p>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold">Preferences</h2>
          <p className="text-muted-foreground mt-2">
            Manage your sample analysis and export settings
          </p>
        </div>

        {/* AI Analysis Settings */}
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">AI Analysis Settings</h3>

          <div className="space-y-4">
            {/* Vibe Analysis Model */}
            <div>
              <Label htmlFor="vibe-model">Vibe Analysis Model</Label>
              <Select
                value={formData.vibe_analysis_model}
                onValueChange={(value) =>
                  setFormData({
                    ...formData,
                    vibe_analysis_model: value as 'qwen3-7b' | 'qwen3-235b',
                  })
                }
                disabled={updateMutation.isPending || isLoading}
              >
                <SelectTrigger id="vibe-model">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {models.map((m) => (
                    <SelectItem key={m.id} value={m.id}>
                      {m.name} (~${m.cost_per_sample}/sample)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground mt-1">
                Model used to analyze vibe and style of samples
              </p>
            </div>

            {/* Auto Vibe Analysis */}
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="auto-vibe">Automatically analyze samples on upload</Label>
                <p className="text-sm text-muted-foreground">
                  Analyzes vibe/style when new samples are uploaded
                </p>
              </div>
              <Switch
                id="auto-vibe"
                checked={formData.auto_vibe_analysis || false}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, auto_vibe_analysis: checked })
                }
                disabled={updateMutation.isPending || isLoading}
              />
            </div>

            {/* Max Cost */}
            <div>
              <Label htmlFor="max-cost">Maximum cost per analysis (optional)</Label>
              <Input
                id="max-cost"
                type="number"
                step="0.001"
                placeholder="Leave empty for unlimited"
                value={formData.max_cost_per_request || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    max_cost_per_request: e.target.value ? parseFloat(e.target.value) : undefined,
                  })
                }
                disabled={updateMutation.isPending || isLoading}
              />
              <p className="text-sm text-muted-foreground mt-1">
                Prevents unexpectedly high costs. Leave blank for no limit.
              </p>
            </div>
          </div>
        </Card>

        {/* Audio Processing Settings */}
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">Audio Processing Settings</h3>

          <div className="space-y-4">
            {/* Auto Audio Features */}
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="auto-features">Auto-extract audio features</Label>
                <p className="text-sm text-muted-foreground">
                  Detects BPM, musical key, and spectral features
                </p>
              </div>
              <Switch
                id="auto-features"
                checked={formData.auto_audio_features || false}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, auto_audio_features: checked })
                }
                disabled={updateMutation.isPending || isLoading}
              />
            </div>

            {/* Batch Processing Model */}
            <div>
              <Label htmlFor="batch-model">Batch Processing Model</Label>
              <Select
                value={formData.batch_processing_model}
                onValueChange={(value) =>
                  setFormData({
                    ...formData,
                    batch_processing_model: value as 'qwen3-7b' | 'qwen3-235b',
                  })
                }
                disabled={updateMutation.isPending || isLoading}
              >
                <SelectTrigger id="batch-model">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {models.map((m) => (
                    <SelectItem key={m.id} value={m.id}>
                      {m.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground mt-1">
                Model used when processing multiple samples at once
              </p>
            </div>

            {/* Batch Auto Analyze */}
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="batch-auto">Auto-analyze batch uploads</Label>
                <p className="text-sm text-muted-foreground">
                  Processes all samples in batch immediately
                </p>
              </div>
              <Switch
                id="batch-auto"
                checked={formData.batch_auto_analyze || false}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, batch_auto_analyze: checked })
                }
                disabled={updateMutation.isPending || isLoading}
              />
            </div>
          </div>
        </Card>

        {/* Export Settings */}
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">Export Preferences</h3>

          <div className="space-y-4">
            {/* Export Format */}
            <div>
              <Label htmlFor="export-format">Default Export Format</Label>
              <Select
                value={formData.default_export_format}
                onValueChange={(value) =>
                  setFormData({
                    ...formData,
                    default_export_format: value as 'wav' | 'aiff',
                  })
                }
                disabled={updateMutation.isPending || isLoading}
              >
                <SelectTrigger id="export-format">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="wav">WAV (Universal, smaller file size)</SelectItem>
                  <SelectItem value="aiff">AIFF (Higher quality, larger file size)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Organization Strategy */}
            <div>
              <Label htmlFor="org-strategy">Organization Strategy</Label>
              <Select
                value={formData.default_export_organization}
                onValueChange={(value) =>
                  setFormData({
                    ...formData,
                    default_export_organization: value as
                      | 'flat'
                      | 'genre'
                      | 'bpm'
                      | 'kit',
                  })
                }
                disabled={updateMutation.isPending || isLoading}
              >
                <SelectTrigger id="org-strategy">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="flat">Flat (All samples in one folder)</SelectItem>
                  <SelectItem value="genre">By Genre (Separate folder per genre)</SelectItem>
                  <SelectItem value="bpm">By BPM (Grouped by tempo ranges)</SelectItem>
                  <SelectItem value="kit">By Kit (Organized into sample kits)</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground mt-1">
                How to organize exported samples
              </p>
            </div>

            {/* Sanitize Filenames */}
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="sanitize">Auto-sanitize filenames</Label>
                <p className="text-sm text-muted-foreground">
                  Removes special characters for SP-404MK2 compatibility
                </p>
              </div>
              <Switch
                id="sanitize"
                checked={formData.auto_sanitize_filenames || false}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, auto_sanitize_filenames: checked })
                }
                disabled={updateMutation.isPending || isLoading}
              />
            </div>
          </div>
        </Card>

        {/* Save Button */}
        <Button
          onClick={handleSave}
          disabled={updateMutation.isPending || isLoading}
          className="w-full h-10"
          size="lg"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </PageLayout>
  );
}
