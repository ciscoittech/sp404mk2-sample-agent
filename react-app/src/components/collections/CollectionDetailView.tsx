import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import {
  ArrowLeft,
  Edit2,
  Sparkles,
  Loader2,
  Trash2,
  Search,
  FolderPlus,
} from 'lucide-react';
import { SampleGrid } from '@/components/samples/SampleGrid';
import { SmartRulesEditor } from './SmartRulesEditor';
import {
  useCollection,
  useCollectionSamplesInfinite,
  useUpdateCollection,
  useRemoveSampleFromCollection,
} from '@/hooks/useCollections';
import { toast } from 'sonner';
import type { Sample } from '@/types/api';
import type { SmartRules } from '@/types/collections';

export function CollectionDetailView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const collectionId = Number(id);

  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editSmartRules, setEditSmartRules] = useState<SmartRules>({});
  const [searchQuery, setSearchQuery] = useState('');

  const { data: collection, isLoading: loadingCollection } = useCollection(collectionId);
  const {
    data: samplesData,
    isLoading: loadingSamples,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useCollectionSamplesInfinite(collectionId);

  const updateCollection = useUpdateCollection();
  const removeSample = useRemoveSampleFromCollection();

  // Flatten paginated samples
  const allSamples = useMemo(() => {
    return samplesData?.pages.flatMap((page) => page.items) || [];
  }, [samplesData]);

  // Filter samples by search
  const filteredSamples = useMemo(() => {
    if (!searchQuery) return allSamples;
    const query = searchQuery.toLowerCase();
    return allSamples.filter(
      (sample) =>
        sample.title.toLowerCase().includes(query) ||
        sample.tags.some((tag) => tag.toLowerCase().includes(query))
    );
  }, [allSamples, searchQuery]);

  const handleEditStart = () => {
    if (!collection) return;
    setEditName(collection.name);
    setEditDescription(collection.description || '');
    setEditSmartRules(collection.smart_rules || {});
    setIsEditing(true);
  };

  const handleEditSave = async () => {
    if (!collection) return;

    try {
      await updateCollection.mutateAsync({
        id: collection.id,
        updates: {
          name: editName.trim() || undefined,
          description: editDescription.trim() || undefined,
          smart_rules: collection.is_smart ? editSmartRules : undefined,
        },
      });

      toast.success('Collection updated');
      setIsEditing(false);
    } catch (error) {
      toast.error('Failed to update collection', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  const handleRemoveSample = async (sampleId: number) => {
    try {
      await removeSample.mutateAsync({
        collectionId,
        sampleId,
      });
      toast.success('Sample removed from collection');
    } catch (error) {
      toast.error('Failed to remove sample', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  const handlePlay = (sample: Sample) => {
    console.log('Play sample:', sample.title);
    // TODO: Integrate with audio player
  };

  const handleAddToKit = (sample: Sample) => {
    console.log('Add to kit:', sample.title);
    // TODO: Integrate with kit builder
  };

  if (loadingCollection) {
    return (
      <div className="container mx-auto px-4 py-6 max-w-[1800px]">
        <Skeleton className="h-8 w-64 mb-6" />
        <div className="space-y-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-12 w-full" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-64" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!collection) {
    return (
      <div className="container mx-auto px-4 py-6 max-w-[1800px]">
        <div className="text-center py-12">
          <p className="text-muted-foreground">Collection not found</p>
          <Button className="mt-4" onClick={() => navigate('/collections')}>
            Back to Collections
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-[1800px]">
      {/* Header */}
      <div className="mb-6">
        <Button variant="ghost" onClick={() => navigate('/collections')} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Collections
        </Button>

        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            {isEditing ? (
              <div className="space-y-4">
                <Input
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  placeholder="Collection name"
                  className="text-2xl font-bold"
                />
                <Input
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  placeholder="Description (optional)"
                />
              </div>
            ) : (
              <>
                <div className="flex items-center gap-3 mb-2">
                  {collection.is_smart && <Sparkles className="h-6 w-6 text-purple-500" />}
                  <h1 className="text-3xl font-bold">{collection.name}</h1>
                </div>
                {collection.description && (
                  <p className="text-muted-foreground">{collection.description}</p>
                )}
              </>
            )}

            <div className="flex flex-wrap gap-2 mt-3">
              <Badge variant="secondary">
                {collection.sample_count} sample{collection.sample_count !== 1 ? 's' : ''}
              </Badge>
              {collection.is_smart && (
                <Badge variant="outline" className="border-purple-500/50 text-purple-400">
                  Smart Collection
                </Badge>
              )}
            </div>
          </div>

          <div className="flex gap-2">
            {isEditing ? (
              <>
                <Button variant="outline" onClick={() => setIsEditing(false)}>
                  Cancel
                </Button>
                <Button onClick={handleEditSave} disabled={updateCollection.isPending}>
                  {updateCollection.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Save'
                  )}
                </Button>
              </>
            ) : (
              <Button variant="outline" onClick={handleEditStart}>
                <Edit2 className="h-4 w-4 mr-2" />
                Edit
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Smart rules display/edit */}
      {collection.is_smart && (
        <>
          <Separator className="my-6" />
          <div className="mb-6">
            {isEditing ? (
              <SmartRulesEditor
                value={editSmartRules}
                onChange={setEditSmartRules}
                collectionId={collection.id}
              />
            ) : (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-500" />
                  Smart Rules
                </h3>
                {collection.smart_rules && Object.keys(collection.smart_rules).length > 0 ? (
                  <div className="rounded-lg bg-muted p-4">
                    <ul className="text-sm space-y-1">
                      {(collection.smart_rules.genres || []).length > 0 && (
                        <li>
                          <span className="font-medium">Genres:</span>{' '}
                          {collection.smart_rules.genres?.join(', ')}
                        </li>
                      )}
                      {(collection.smart_rules.bpm_min || collection.smart_rules.bpm_max) && (
                        <li>
                          <span className="font-medium">BPM:</span> {collection.smart_rules.bpm_min || 20} -{' '}
                          {collection.smart_rules.bpm_max || 200}
                        </li>
                      )}
                      {(collection.smart_rules.tags || []).length > 0 && (
                        <li>
                          <span className="font-medium">Tags:</span>{' '}
                          {collection.smart_rules.tags?.join(', ')}
                        </li>
                      )}
                      {(collection.smart_rules.sample_types || []).length > 0 && (
                        <li>
                          <span className="font-medium">Types:</span>{' '}
                          {collection.smart_rules.sample_types?.join(', ')}
                        </li>
                      )}
                      {collection.smart_rules.min_confidence &&
                        collection.smart_rules.min_confidence > 0 && (
                          <li>
                            <span className="font-medium">Min Confidence:</span>{' '}
                            {collection.smart_rules.min_confidence}%
                          </li>
                        )}
                    </ul>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No rules defined</p>
                )}
              </div>
            )}
          </div>
        </>
      )}

      <Separator className="my-6" />

      {/* Samples section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Samples</h2>
          {!collection.is_smart && (
            <Button variant="outline" size="sm">
              <FolderPlus className="h-4 w-4 mr-2" />
              Add Samples
            </Button>
          )}
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search samples in this collection..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Samples grid */}
        {loadingSamples ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : filteredSamples.length === 0 ? (
          <div className="rounded-lg border border-dashed border-muted-foreground/25 bg-muted/30 p-12 text-center">
            <p className="text-muted-foreground">
              {searchQuery
                ? 'No samples found matching your search'
                : 'No samples in this collection yet'}
            </p>
          </div>
        ) : (
          <>
            <SampleGrid
              samples={filteredSamples}
              onPlay={handlePlay}
              onAddToKit={handleAddToKit}
            />

            {/* Load more */}
            {hasNextPage && (
              <div className="flex justify-center pt-6">
                <Button
                  variant="outline"
                  onClick={() => fetchNextPage()}
                  disabled={isFetchingNextPage}
                >
                  {isFetchingNextPage ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Load More'
                  )}
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
