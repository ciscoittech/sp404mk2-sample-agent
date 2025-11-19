import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { FolderPlus, Check, Loader2 } from 'lucide-react';
import { useCollections, useAddSamplesToCollection } from '@/hooks/useCollections';
import { toast } from 'sonner';

interface AddToCollectionMenuProps {
  sampleId: number;
  sampleIds?: number[];
  onSuccess?: () => void;
  variant?: 'ghost' | 'outline' | 'default';
  size?: 'sm' | 'default' | 'lg' | 'icon';
  className?: string;
}

export function AddToCollectionMenu({
  sampleId,
  sampleIds,
  onSuccess,
  variant = 'ghost',
  size = 'icon',
  className,
}: AddToCollectionMenuProps) {
  const [open, setOpen] = useState(false);
  const { data: collections, isLoading: loadingCollections } = useCollections();
  const addSamples = useAddSamplesToCollection();

  const handleAddToCollection = async (collectionId: number, collectionName: string) => {
    const idsToAdd = sampleIds || [sampleId];

    try {
      await addSamples.mutateAsync({
        id: collectionId,
        request: { sample_ids: idsToAdd },
      });

      const count = idsToAdd.length;
      toast.success(
        `Added ${count} sample${count !== 1 ? 's' : ''} to ${collectionName}`,
        {
          duration: 2000,
        }
      );

      setOpen(false);
      onSuccess?.();
    } catch (error) {
      toast.error('Failed to add to collection', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size} className={className}>
          <FolderPlus className="h-4 w-4" />
          {size !== 'icon' && <span className="ml-2">Add to Collection</span>}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>Add to Collection</DropdownMenuLabel>
        <DropdownMenuSeparator />

        {loadingCollections && (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          </div>
        )}

        {!loadingCollections && (!collections || collections.length === 0) && (
          <div className="px-2 py-4 text-center">
            <p className="text-sm text-muted-foreground">No collections yet</p>
            <p className="text-xs text-muted-foreground mt-1">
              Create a collection to organize samples
            </p>
          </div>
        )}

        {!loadingCollections &&
          collections &&
          collections.length > 0 &&
          collections.map((collection) => (
            <DropdownMenuItem
              key={collection.id}
              onClick={() => handleAddToCollection(collection.id, collection.name)}
              disabled={addSamples.isPending || collection.is_smart}
              className="cursor-pointer"
            >
              <div className="flex items-center justify-between w-full">
                <div className="flex flex-col flex-1 min-w-0">
                  <span className="text-sm truncate">{collection.name}</span>
                  {collection.is_smart && (
                    <span className="text-xs text-muted-foreground">Smart (read-only)</span>
                  )}
                </div>
                {addSamples.isPending && (
                  <Loader2 className="h-3 w-3 animate-spin ml-2 flex-shrink-0" />
                )}
              </div>
            </DropdownMenuItem>
          ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
