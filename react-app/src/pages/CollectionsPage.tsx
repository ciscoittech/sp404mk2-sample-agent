import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Plus, Loader2, FolderOpen } from 'lucide-react';
import { CollectionCard, CollectionCardSkeleton } from '@/components/collections/CollectionCard';
import { CreateCollectionModal } from '@/components/collections/CreateCollectionModal';
import { useCollections, useDeleteCollection } from '@/hooks/useCollections';
import { toast } from 'sonner';

export function CollectionsPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'manual' | 'smart'>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: collections, isLoading, error } = useCollections();
  const deleteCollection = useDeleteCollection();

  // Filter collections
  const filteredCollections = useMemo(() => {
    if (!collections) return [];

    let filtered = collections;

    // Filter by type
    if (filterType === 'manual') {
      filtered = filtered.filter((c) => !c.is_smart);
    } else if (filterType === 'smart') {
      filtered = filtered.filter((c) => c.is_smart);
    }

    // Filter by search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.name.toLowerCase().includes(query) ||
          c.description?.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [collections, filterType, searchQuery]);

  // Count by type
  const counts = useMemo(() => {
    if (!collections) return { all: 0, manual: 0, smart: 0 };
    return {
      all: collections.length,
      manual: collections.filter((c) => !c.is_smart).length,
      smart: collections.filter((c) => c.is_smart).length,
    };
  }, [collections]);

  const handleDelete = async (id: number) => {
    try {
      await deleteCollection.mutateAsync(id);
      toast.success('Collection deleted');
    } catch (error) {
      toast.error('Failed to delete collection', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  const handleView = (id: number) => {
    navigate(`/collections/${id}`);
  };

  const handleCreateSuccess = (collectionId: number) => {
    navigate(`/collections/${collectionId}`);
  };

  return (
    <div className="container mx-auto px-4 py-6 max-w-[1800px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold">Collections</h2>
          <p className="text-muted-foreground mt-2">
            Organize samples into thematic groups
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          Create Collection
        </Button>
      </div>

      {/* Search and filters */}
      <div className="space-y-4 mb-6">
        {/* Search bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search collections..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Type filter tabs */}
        <Tabs value={filterType} onValueChange={(v) => setFilterType(v as typeof filterType)}>
          <TabsList>
            <TabsTrigger value="all" className="gap-2">
              All
              {counts.all > 0 && (
                <Badge variant="secondary" className="ml-1">
                  {counts.all}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="manual" className="gap-2">
              Manual
              {counts.manual > 0 && (
                <Badge variant="secondary" className="ml-1">
                  {counts.manual}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="smart" className="gap-2">
              Smart
              {counts.smart > 0 && (
                <Badge variant="secondary" className="ml-1">
                  {counts.smart}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Content states */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <CollectionCardSkeleton key={i} />
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4">
          <p className="text-sm text-destructive">
            Error loading collections: {error.message}
          </p>
        </div>
      )}

      {!isLoading && !error && collections && collections.length === 0 && (
        <div className="rounded-lg border border-dashed border-muted-foreground/25 bg-muted/30 p-12 text-center">
          <FolderOpen className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">No collections yet</h3>
          <p className="text-muted-foreground mb-4">
            Create your first collection to organize your samples
          </p>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Collection
          </Button>
        </div>
      )}

      {!isLoading && !error && filteredCollections.length === 0 && collections && collections.length > 0 && (
        <div className="rounded-lg border border-dashed border-muted-foreground/25 bg-muted/30 p-12 text-center">
          <p className="text-muted-foreground">
            No collections found matching your filters
          </p>
        </div>
      )}

      {!isLoading && !error && filteredCollections.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCollections.map((collection) => (
            <CollectionCard
              key={collection.id}
              collection={collection}
              onDelete={handleDelete}
              onView={handleView}
            />
          ))}
        </div>
      )}

      {/* Create modal */}
      <CreateCollectionModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
        onSuccess={handleCreateSuccess}
      />
    </div>
  );
}
