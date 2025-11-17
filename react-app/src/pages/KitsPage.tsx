import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PageLayout } from '@/components/layout/PageLayout';
import { PadGrid, SampleBrowser } from '@/components/kits';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useKits, useCreateKit, useAssignSample, useRemoveSample } from '@/hooks/useKits';
import type { Sample } from '@/types/api';
import { Plus, Loader2, Download, MoreVertical, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

const SELECTED_KIT_STORAGE_KEY = 'sp404mk2_selected_kit';

export function KitsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedKit, setSelectedKitState] = useState<number | undefined>(() => {
    // Initialize from URL params or localStorage
    const kitIdParam = searchParams.get('kit');
    if (kitIdParam) {
      const id = parseInt(kitIdParam, 10);
      if (!isNaN(id)) return id;
    }
    const stored = localStorage.getItem(SELECTED_KIT_STORAGE_KEY);
    if (stored) {
      const id = parseInt(stored, 10);
      if (!isNaN(id)) return id;
    }
    return undefined;
  });
  const [newKitName, setNewKitName] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  // Persist selectedKit to both localStorage and URL params
  const setSelectedKit = useCallback((kitId: number | undefined) => {
    console.log('[STATE] Updating selectedKit:', { kitId, timestamp: new Date().toISOString() });
    setSelectedKitState(kitId);
    if (kitId !== undefined) {
      localStorage.setItem(SELECTED_KIT_STORAGE_KEY, kitId.toString());
      setSearchParams({ kit: kitId.toString() });
    } else {
      localStorage.removeItem(SELECTED_KIT_STORAGE_KEY);
      setSearchParams({});
    }
  }, [setSearchParams]);

  const { data: kits, isLoading } = useKits();
  const createKit = useCreateKit();
  const assignSample = useAssignSample();
  const removeSample = useRemoveSample();

  // Validate selectedKit when kits load - clear if kit no longer exists
  useEffect(() => {
    if (!kits?.items) return;
    if (selectedKit && !kits.items.find(k => k.id === selectedKit)) {
      console.log('[STATE] Selected kit no longer exists, clearing selection');
      setSelectedKit(undefined);
    }
  }, [kits?.items, selectedKit, setSelectedKit]);

  const currentKit = kits?.items?.find((k) => k.id === selectedKit);

  const handleCreateKit = async () => {
    if (!newKitName.trim()) return;

    try {
      const kit = await createKit.mutateAsync({ name: newKitName });
      setSelectedKit(kit.id);
      setNewKitName('');
      setIsCreateDialogOpen(false);
      toast.success('Kit created successfully');
    } catch (error) {
      toast.error('Failed to create kit');
      console.error('Error creating kit:', error);
    }
  };

  const handleAssignSample = async (
    padBank: string,
    padNumber: number,
    sample: Sample
  ) => {
    if (!selectedKit) {
      toast.error('Please select a kit first');
      return;
    }

    try {
      await assignSample.mutateAsync({
        kitId: selectedKit,
        assignment: {
          sample_id: sample.id,
          pad_bank: padBank as 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J',
          pad_number: padNumber,
        },
      });
      toast.success(`Assigned "${sample.title}" to pad ${padBank}${padNumber}`);
    } catch (error) {
      toast.error('Failed to assign sample');
      console.error('Error assigning sample:', error);
    }
  };

  const handleRemoveSample = async (padBank: string, padNumber: number) => {
    if (!selectedKit) return;

    try {
      await removeSample.mutateAsync({
        kitId: selectedKit,
        padBank,
        padNumber,
      });
      toast.success(`Removed sample from pad ${padBank}${padNumber}`);
    } catch (error) {
      toast.error('Failed to remove sample');
      console.error('Error removing sample:', error);
    }
  };

  if (isLoading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="h-[calc(100vh-4rem)] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold">Kit Builder</h2>
              <p className="text-muted-foreground mt-1">
                Build SP-404MK2 kits with drag-and-drop
              </p>
            </div>

            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  New Kit
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Kit</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 pt-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Kit Name</label>
                    <Input
                      placeholder="Enter kit name..."
                      value={newKitName}
                      onChange={(e) => setNewKitName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleCreateKit();
                      }}
                    />
                  </div>
                  <Button
                    onClick={handleCreateKit}
                    disabled={!newKitName.trim() || createKit.isPending}
                    className="w-full"
                  >
                    {createKit.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      'Create Kit'
                    )}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Kit selector */}
          {kits && kits.items.length > 0 && (
            <>
              <Separator className="my-4" />
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Active Kit:</span>
                <div className="flex gap-2 flex-wrap">
                  {kits.items.map((kit) => (
                    <div key={kit.id} className="relative">
                      <Button
                        type="button"
                        variant={selectedKit === kit.id ? 'default' : 'outline'}
                        onClick={() => {
                          console.log('[KIT] Kit button clicked: kitId=', kit.id, 'kitName=', kit.name, 'timestamp=', new Date().toISOString());
                          setSelectedKit(kit.id);
                        }}
                        className="pr-8"
                      >
                        {kit.name}
                      </Button>
                      {selectedKit === kit.id && (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6 absolute right-1 top-1/2 -translate-y-1/2"
                            >
                              <MoreVertical className="h-3 w-3" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent>
                            <DropdownMenuItem>
                              <Download className="h-4 w-4 mr-2" />
                              Export
                            </DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive">
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Main content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Pad Grid */}
          <div className="flex-1 p-6 overflow-auto">
            {currentKit ? (
              <PadGrid
                kit={currentKit}
                onAssignSample={handleAssignSample}
                onRemoveSample={handleRemoveSample}
              />
            ) : (
              <div className="h-full flex items-center justify-center">
                <div className="text-center max-w-md">
                  <h3 className="text-lg font-semibold mb-2">No Kit Selected</h3>
                  <p className="text-muted-foreground mb-4">
                    {kits?.items.length
                      ? 'Select a kit from the list above to start building'
                      : 'Create your first kit to get started'}
                  </p>
                  {!kits?.items.length && (
                    <Button onClick={() => setIsCreateDialogOpen(true)}>
                      <Plus className="h-4 w-4 mr-2" />
                      Create First Kit
                    </Button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Sample Browser Sidebar */}
          {currentKit && (
            <div className="w-96 flex-shrink-0">
              <SampleBrowser onAddToKit={(sample) => {
                // Quick add to first available pad
                const firstEmptyPad = findFirstEmptyPad();
                if (firstEmptyPad) {
                  handleAssignSample(firstEmptyPad.bank, firstEmptyPad.number, sample);
                } else {
                  toast.warning('All pads are full. Drag sample onto a pad to replace.');
                }
              }} />
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );

  function findFirstEmptyPad() {
    if (!currentKit) return null;

    const banks = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'] as const;
    for (const bank of banks) {
      for (let number = 1; number <= 16; number++) {
        const assignment = currentKit.samples.find(
          (a) => a.pad_bank === bank && a.pad_number === number
        );
        if (!assignment) {
          return { bank, number };
        }
      }
    }
    return null;
  }
}
