import { memo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Folder, Sparkles, Trash2, ArrowRight } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import type { Collection } from '@/types/collections';

interface CollectionCardProps {
  collection: Collection;
  onDelete?: (id: number) => Promise<void>;
  onView?: (id: number) => void;
}

function CollectionCardComponent({ collection, onDelete, onView }: CollectionCardProps) {
  const navigate = useNavigate();
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleView = () => {
    if (onView) {
      onView(collection.id);
    } else {
      navigate(`/collections/${collection.id}`);
    }
  };

  const handleDelete = async () => {
    if (!onDelete) return;

    setIsDeleting(true);
    try {
      await onDelete(collection.id);
      setShowDeleteDialog(false);
    } catch (error) {
      console.error('Failed to delete collection:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <Card className="group hover:border-primary/50 transition-all duration-200 hover:shadow-lg">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-start gap-2 flex-1 min-w-0">
              {collection.is_smart ? (
                <Sparkles className="h-5 w-5 text-purple-500 flex-shrink-0 mt-0.5" />
              ) : (
                <Folder className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
              )}
              <div className="flex-1 min-w-0">
                <CardTitle className="text-base truncate" title={collection.name}>
                  {collection.name}
                </CardTitle>
                {collection.description && (
                  <p
                    className="text-xs text-muted-foreground mt-1 line-clamp-2"
                    title={collection.description}
                  >
                    {collection.description}
                  </p>
                )}
              </div>
            </div>
            {onDelete && (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity text-destructive"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowDeleteDialog(true);
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardHeader>

        <CardContent className="space-y-3">
          {/* Badges */}
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary" className="font-mono">
              {collection.sample_count} sample{collection.sample_count !== 1 ? 's' : ''}
            </Badge>
            {collection.is_smart && (
              <Badge variant="outline" className="border-purple-500/50 text-purple-400">
                Smart Collection
              </Badge>
            )}
          </div>

          {/* View button */}
          <Button
            variant="outline"
            size="sm"
            className="w-full group-hover:bg-primary group-hover:text-primary-foreground transition-colors"
            onClick={handleView}
          >
            View Collection
            <ArrowRight className="h-3 w-3 ml-2" />
          </Button>
        </CardContent>
      </Card>

      {/* Delete confirmation dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Collection</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{collection.name}"? This action cannot be undone.
              {collection.sample_count > 0 && (
                <span className="block mt-2 text-orange-500">
                  Note: This will not delete the {collection.sample_count} sample
                  {collection.sample_count !== 1 ? 's' : ''} in this collection, only the
                  collection itself.
                </span>
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)} disabled={isDeleting}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

// Skeleton loader for loading state
export function CollectionCardSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start gap-2">
          <Skeleton className="h-5 w-5 rounded flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-full" />
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex gap-2">
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-5 w-24" />
        </div>
        <Skeleton className="h-9 w-full" />
      </CardContent>
    </Card>
  );
}

export const CollectionCard = memo(CollectionCardComponent);
