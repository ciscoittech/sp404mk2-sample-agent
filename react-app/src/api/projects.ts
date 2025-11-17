import { apiClient } from './client';
import type { ProjectBuildRequest, ProjectBuildResult } from '@/types/api';

export const projectsApi = {
  // Build SP-404MK2 project from kit
  buildProject: async (kitId: number, request: ProjectBuildRequest) => {
    const { data } = await apiClient.post<ProjectBuildResult>(
      `/projects/from-kit/${kitId}`,
      request
    );
    return data;
  },

  // Download generated project ZIP
  downloadProject: async (exportId: string) => {
    const { data } = await apiClient.get<Blob>(
      `/projects/download/${exportId}`,
      { responseType: 'blob' }
    );
    return data;
  },
};
