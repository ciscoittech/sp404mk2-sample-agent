import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProjectBuilderDialog } from '../ProjectBuilderDialog';
import * as projectsApi from '@/api/projects';

// Mock the API
vi.mock('@/api/projects', () => ({
  projectsApi: {
    buildProject: vi.fn(),
    downloadProject: vi.fn(),
  },
}));

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('ProjectBuilderDialog', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const defaultProps = {
    kitId: 1,
    kitName: 'Test Kit',
    sampleCount: 12,
    isOpen: true,
    onOpenChange: vi.fn(),
  };

  const renderDialog = (props = {}) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <ProjectBuilderDialog {...defaultProps} {...props} />
      </QueryClientProvider>
    );
  };

  it('renders dialog when isOpen is true', () => {
    renderDialog();
    expect(screen.getByText('Generate SP-404MK2 Project')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    renderDialog({ isOpen: false });
    expect(screen.queryByText('Generate SP-404MK2 Project')).not.toBeInTheDocument();
  });

  it('displays kit information', () => {
    renderDialog();
    expect(screen.getByText(/Test Kit/)).toBeInTheDocument();
    expect(screen.getByText(/12 samples/)).toBeInTheDocument();
  });

  it('has project name input field', () => {
    renderDialog();
    const input = screen.getByLabelText(/Project Name/);
    expect(input).toBeInTheDocument();
  });

  it('has BPM input field', () => {
    renderDialog();
    const input = screen.getByLabelText(/Project BPM/);
    expect(input).toBeInTheDocument();
  });

  it('has format selector', () => {
    renderDialog();
    expect(screen.getByText(/Audio Format/)).toBeInTheDocument();
  });

  it('has bank layout switch', () => {
    renderDialog();
    expect(screen.getByText(/Include Bank Layout/)).toBeInTheDocument();
  });

  describe('Form Validation', () => {
    it('shows error for empty project name', async () => {
      const user = userEvent.setup();
      renderDialog();

      const input = screen.getByLabelText(/Project Name/);
      await user.type(input, 'test');
      await user.clear(input);

      expect(screen.getByText(/Project name is required/)).toBeInTheDocument();
    });

    it('shows error for project name too long', async () => {
      const user = userEvent.setup();
      renderDialog();

      const input = screen.getByLabelText(/Project Name/);
      await user.type(input, 'a'.repeat(32)); // Exceeds 31 char limit

      expect(screen.getByText(/must be 1-31 characters/)).toBeInTheDocument();
    });

    it('shows error for invalid BPM (too low)', async () => {
      const user = userEvent.setup();
      renderDialog();

      const input = screen.getByLabelText(/Project BPM/);
      await user.type(input, '10');

      expect(screen.getByText(/must be between 20 and 300/)).toBeInTheDocument();
    });

    it('shows error for invalid BPM (too high)', async () => {
      const user = userEvent.setup();
      renderDialog();

      const input = screen.getByLabelText(/Project BPM/);
      await user.type(input, '400');

      expect(screen.getByText(/must be between 20 and 300/)).toBeInTheDocument();
    });

    it('accepts valid BPM', async () => {
      const user = userEvent.setup();
      renderDialog();

      const input = screen.getByLabelText(/Project BPM/);
      await user.type(input, '120');

      expect(screen.queryByText(/must be between/)).not.toBeInTheDocument();
    });

    it('allows empty BPM (auto-detect)', () => {
      renderDialog();
      const input = screen.getByLabelText(/Project BPM/);
      expect(input).toHaveValue(null);
    });
  });

  describe('Form Submission', () => {
    it('disables submit button when form is invalid', () => {
      renderDialog();
      const submitButton = screen.getByRole('button', { name: /Generate Project/i });
      expect(submitButton).toBeDisabled();
    });

    it('enables submit button when form is valid', async () => {
      const user = userEvent.setup();
      renderDialog();

      const input = screen.getByLabelText(/Project Name/);
      await user.type(input, 'MyProject');

      const submitButton = screen.getByRole('button', { name: /Generate Project/i });
      expect(submitButton).toBeEnabled();
    });

    it('shows loading state during submission', async () => {
      const user = userEvent.setup();
      vi.mocked(projectsApi.projectsApi.buildProject).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderDialog();

      const nameInput = screen.getByLabelText(/Project Name/);
      await user.type(nameInput, 'MyProject');

      const submitButton = screen.getByRole('button', { name: /Generate Project/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Building project/)).toBeInTheDocument();
      });
    });

    it('shows success view on successful build', async () => {
      const user = userEvent.setup();
      const mockResult = {
        success: true,
        export_id: '123',
        project_name: 'MyProject',
        sample_count: 12,
        file_size_bytes: 5242880,
        download_url: '/api/v1/projects/download/123',
      };

      vi.mocked(projectsApi.projectsApi.buildProject).mockResolvedValue(mockResult);

      renderDialog();

      const nameInput = screen.getByLabelText(/Project Name/);
      await user.type(nameInput, 'MyProject');

      const submitButton = screen.getByRole('button', { name: /Generate Project/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Project generated successfully/)).toBeInTheDocument();
      });

      expect(screen.getByText('MyProject')).toBeInTheDocument();
      expect(screen.getByText('12')).toBeInTheDocument();
      expect(screen.getByText(/5.00 MB/)).toBeInTheDocument();
    });

    it('shows error view on failed build', async () => {
      const user = userEvent.setup();
      const mockResult = {
        success: false,
        sample_count: 0,
        file_size_bytes: 0,
        error_message: 'Kit has no samples',
      };

      vi.mocked(projectsApi.projectsApi.buildProject).mockResolvedValue(mockResult);

      renderDialog();

      const nameInput = screen.getByLabelText(/Project Name/);
      await user.type(nameInput, 'MyProject');

      const submitButton = screen.getByRole('button', { name: /Generate Project/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to build project/)).toBeInTheDocument();
      });

      expect(screen.getByText('Kit has no samples')).toBeInTheDocument();
    });
  });

  describe('Download Functionality', () => {
    it('shows download button after successful build', async () => {
      const user = userEvent.setup();
      const mockResult = {
        success: true,
        export_id: '123',
        project_name: 'MyProject',
        sample_count: 12,
        file_size_bytes: 5242880,
        download_url: '/api/v1/projects/download/123',
      };

      vi.mocked(projectsApi.projectsApi.buildProject).mockResolvedValue(mockResult);

      renderDialog();

      const nameInput = screen.getByLabelText(/Project Name/);
      await user.type(nameInput, 'MyProject');

      const submitButton = screen.getByRole('button', { name: /Generate Project/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Download Project/i })).toBeInTheDocument();
      });
    });

    it('triggers download when download button is clicked', async () => {
      const user = userEvent.setup();
      const mockBlob = new Blob(['test'], { type: 'application/zip' });

      const mockBuildResult = {
        success: true,
        export_id: '123',
        project_name: 'MyProject',
        sample_count: 12,
        file_size_bytes: 5242880,
        download_url: '/api/v1/projects/download/123',
      };

      vi.mocked(projectsApi.projectsApi.buildProject).mockResolvedValue(mockBuildResult);
      vi.mocked(projectsApi.projectsApi.downloadProject).mockResolvedValue(mockBlob);

      // Mock URL.createObjectURL
      global.URL.createObjectURL = vi.fn(() => 'blob:test');
      global.URL.revokeObjectURL = vi.fn();

      renderDialog();

      const nameInput = screen.getByLabelText(/Project Name/);
      await user.type(nameInput, 'MyProject');

      const submitButton = screen.getByRole('button', { name: /Generate Project/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Download Project/i })).toBeInTheDocument();
      });

      const downloadButton = screen.getByRole('button', { name: /Download Project/i });
      await user.click(downloadButton);

      await waitFor(() => {
        expect(projectsApi.projectsApi.downloadProject).toHaveBeenCalledWith('123');
      });
    });
  });

  describe('Error Recovery', () => {
    it('shows retry button on error', async () => {
      const user = userEvent.setup();
      const mockResult = {
        success: false,
        sample_count: 0,
        file_size_bytes: 0,
        error_message: 'Test error',
      };

      vi.mocked(projectsApi.projectsApi.buildProject).mockResolvedValue(mockResult);

      renderDialog();

      const nameInput = screen.getByLabelText(/Project Name/);
      await user.type(nameInput, 'MyProject');

      const submitButton = screen.getByRole('button', { name: /Generate Project/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Try Again/i })).toBeInTheDocument();
      });
    });

    it('returns to form view when retry is clicked', async () => {
      const user = userEvent.setup();
      const mockResult = {
        success: false,
        sample_count: 0,
        file_size_bytes: 0,
        error_message: 'Test error',
      };

      vi.mocked(projectsApi.projectsApi.buildProject).mockResolvedValue(mockResult);

      renderDialog();

      const nameInput = screen.getByLabelText(/Project Name/);
      await user.type(nameInput, 'MyProject');

      const submitButton = screen.getByRole('button', { name: /Generate Project/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Try Again/i })).toBeInTheDocument();
      });

      const retryButton = screen.getByRole('button', { name: /Try Again/i });
      await user.click(retryButton);

      expect(screen.getByLabelText(/Project Name/)).toBeInTheDocument();
    });
  });

  describe('Dialog Controls', () => {
    it('calls onOpenChange when cancel is clicked', async () => {
      const user = userEvent.setup();
      const onOpenChange = vi.fn();
      renderDialog({ onOpenChange });

      const cancelButton = screen.getByRole('button', { name: /Cancel/i });
      await user.click(cancelButton);

      expect(onOpenChange).toHaveBeenCalledWith(false);
    });

    it('resets form state when dialog is closed and reopened', async () => {
      const user = userEvent.setup();
      const { rerender } = renderDialog();

      const nameInput = screen.getByLabelText(/Project Name/);
      await user.type(nameInput, 'MyProject');

      // Close dialog
      rerender(
        <QueryClientProvider client={queryClient}>
          <ProjectBuilderDialog {...defaultProps} isOpen={false} />
        </QueryClientProvider>
      );

      // Reopen dialog
      rerender(
        <QueryClientProvider client={queryClient}>
          <ProjectBuilderDialog {...defaultProps} isOpen={true} />
        </QueryClientProvider>
      );

      const newNameInput = screen.getByLabelText(/Project Name/);
      expect(newNameInput).toHaveValue('');
    });
  });
});
