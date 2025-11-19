import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Loader2 } from 'lucide-react';
import { SmartRulesEditor } from './SmartRulesEditor';
import { useCreateCollection } from '@/hooks/useCollections';
import { toast } from 'sonner';
import type { SmartRules } from '@/types/collections';

interface CreateCollectionModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: (collectionId: number) => void;
}

export function CreateCollectionModal({
  open,
  onOpenChange,
  onSuccess,
}: CreateCollectionModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isSmart, setIsSmart] = useState(false);
  const [smartRules, setSmartRules] = useState<SmartRules>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createCollection = useCreateCollection();

  // Reset form when modal closes
  useEffect(() => {
    if (!open) {
      setName('');
      setDescription('');
      setIsSmart(false);
      setSmartRules({});
      setErrors({});
    }
  }, [open]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!name.trim()) {
      newErrors.name = 'Name is required';
    } else if (name.length > 255) {
      newErrors.name = 'Name must be 255 characters or less';
    }

    if (description.length > 1000) {
      newErrors.description = 'Description must be 1000 characters or less';
    }

    if (isSmart) {
      const hasRules = Object.values(smartRules).some(
        (v) => v !== undefined && (Array.isArray(v) ? v.length > 0 : true)
      );
      if (!hasRules) {
        newErrors.rules = 'Smart collections require at least one rule';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const collection = await createCollection.mutateAsync({
        name: name.trim(),
        description: description.trim() || undefined,
        is_smart: isSmart,
        smart_rules: isSmart ? smartRules : undefined,
      });

      toast.success('Collection created successfully', {
        description: `Created "${collection.name}"`,
      });

      onOpenChange(false);
      onSuccess?.(collection.id);
    } catch (error) {
      toast.error('Failed to create collection', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create New Collection</DialogTitle>
            <DialogDescription>
              Organize your samples into collections. Use smart collections for automatic filtering
              based on rules.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-6">
            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="name">
                Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                placeholder="e.g., Hip-Hop Drums, Jazz Loops"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  setErrors({ ...errors, name: '' });
                }}
                maxLength={255}
                className={errors.name ? 'border-destructive' : ''}
              />
              {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
              <p className="text-xs text-muted-foreground">{name.length}/255 characters</p>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Optional description for this collection"
                value={description}
                onChange={(e) => {
                  setDescription(e.target.value);
                  setErrors({ ...errors, description: '' });
                }}
                maxLength={1000}
                rows={3}
                className={errors.description ? 'border-destructive' : ''}
              />
              {errors.description && (
                <p className="text-sm text-destructive">{errors.description}</p>
              )}
              <p className="text-xs text-muted-foreground">{description.length}/1000 characters</p>
            </div>

            {/* Smart collection toggle */}
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div className="space-y-0.5">
                <Label htmlFor="smart-toggle" className="text-base cursor-pointer">
                  Smart Collection
                </Label>
                <p className="text-sm text-muted-foreground">
                  Automatically filter samples based on rules
                </p>
              </div>
              <Switch
                id="smart-toggle"
                checked={isSmart}
                onCheckedChange={(checked) => {
                  setIsSmart(checked);
                  if (!checked) {
                    setSmartRules({});
                    setErrors({ ...errors, rules: '' });
                  }
                }}
              />
            </div>

            {/* Smart rules editor */}
            {isSmart && (
              <div className="space-y-2">
                <SmartRulesEditor
                  value={smartRules}
                  onChange={(rules) => {
                    setSmartRules(rules);
                    setErrors({ ...errors, rules: '' });
                  }}
                />
                {errors.rules && <p className="text-sm text-destructive">{errors.rules}</p>}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={createCollection.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createCollection.isPending}>
              {createCollection.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Collection'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
