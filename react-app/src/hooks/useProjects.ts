import { useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '@/api/projects';
import { queryKeys } from '@/lib/queryClient';
import type { ProjectBuildRequest } from '@/types/api';
import { toast } from 'sonner';

// Build project from kit
export function useBuildProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: { kitId: number; request: ProjectBuildRequest }) =>
      projectsApi.buildProject(params.kitId, params.request),
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`Project "${data.project_name}" generated successfully!`);
        // Optionally refetch kit data
        queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() });
      } else {
        toast.error(data.error_message || 'Failed to build project');
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message || 'Unknown error';
      toast.error(`Failed to build project: ${message}`);
    },
  });
}

// Download project ZIP
export function useDownloadProject() {
  return useMutation({
    mutationFn: (exportId: string) => projectsApi.downloadProject(exportId),
    onSuccess: (blob: Blob, exportId: string) => {
      // Trigger browser download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `sp404-project-${exportId}.zip`;
      document.body.appendChild(link);
      link.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
      toast.success('Project downloaded successfully');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message || 'Unknown error';
      toast.error(`Download failed: ${message}`);
    },
  });
}
