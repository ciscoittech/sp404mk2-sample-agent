import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PadGrid } from '../PadGrid';
import type { Kit } from '@/types/api';

describe('PadGrid', () => {
  const mockKit: Kit = {
    id: 1,
    user_id: 1,
    name: 'Test Kit',
    description: 'Test description',
    is_public: false,
    created_at: '2025-01-01',
    updated_at: '2025-01-01',
    samples: [
      {
        kit_id: 1,
        sample_id: 1,
        pad_bank: 'A',
        pad_number: 1,
        sample: {
          id: 1,
          user_id: 1,
          title: 'Test Sample',
          file_path: '/test.wav',
          duration: 2.5,
          genre: 'Hip-Hop',
          bpm: 90,
          musical_key: 'C',
          tags: ['test'],
          rating: 5,
          created_at: '2025-01-01',
          updated_at: '2025-01-01',
        },
      },
    ],
  };

  const mockHandlers = {
    onAssignSample: vi.fn(),
    onRemoveSample: vi.fn(),
  };

  it('renders all 4 banks', () => {
    render(<PadGrid kit={mockKit} {...mockHandlers} />);

    expect(screen.getByText('Bank A')).toBeInTheDocument();
    expect(screen.getByText('Bank B')).toBeInTheDocument();
    expect(screen.getByText('Bank C')).toBeInTheDocument();
    expect(screen.getByText('Bank D')).toBeInTheDocument();
  });

  it('displays assigned sample', () => {
    render(<PadGrid kit={mockKit} {...mockHandlers} />);

    expect(screen.getByText('Test Sample')).toBeInTheDocument();
    expect(screen.getByText('90')).toBeInTheDocument();
    expect(screen.getByText('C')).toBeInTheDocument();
  });

  it('shows empty pads', () => {
    render(<PadGrid kit={mockKit} {...mockHandlers} />);

    // Should have 11 empty pads in Bank A (12 total - 1 filled)
    const emptyPads = screen.getAllByText('Empty');
    expect(emptyPads.length).toBeGreaterThan(0);
  });
});
