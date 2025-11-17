import { PageLayout } from '@/components/layout/PageLayout';
import { useUploadSample } from '@/hooks/useSamples';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Upload, X } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import type { AxiosError } from 'axios';

const GENRES = [
  'Hip-Hop',
  'Trap',
  'Jazz',
  'Soul',
  'Electronic',
  'House',
  'Drum & Bass',
  'Lo-Fi',
  'Ambient',
  'Funk',
  'Disco',
  'R&B',
  'Techno',
  'Dubstep',
];

const MUSICAL_KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

export function UploadPage() {
  const uploadMutation = useUploadSample();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    genre: '',
    bpm: '',
    musical_key: '',
    tags: '',
  });

  // Dropzone setup
  const onDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      toast.success('File selected');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.flac', '.aiff', '.m4a', '.ogg'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    maxFiles: 1,
  });

  const validateForm = (): boolean => {
    if (!formData.title.trim()) {
      toast.error('Title is required');
      return false;
    }
    if (formData.title.length > 255) {
      toast.error('Title must be 255 characters or less');
      return false;
    }
    if (formData.bpm) {
      const bpm = parseFloat(formData.bpm);
      if (isNaN(bpm) || bpm < 40 || bpm > 200) {
        toast.error('BPM must be between 40 and 200');
        return false;
      }
    }
    return true;
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file');
      return;
    }

    if (!validateForm()) return;

    const metadata = {
      title: formData.title,
      genre: formData.genre || undefined,
      bpm: formData.bpm ? parseFloat(formData.bpm) : undefined,
      musical_key: formData.musical_key || undefined,
      tags: formData.tags ? formData.tags.split(',').map((t) => t.trim()) : undefined,
    };

    uploadMutation.mutate({ file: selectedFile, metadata });
  };

  // Handle upload success
  useEffect(() => {
    if (uploadMutation.isSuccess) {
      toast.success('Sample uploaded successfully!');
      setSelectedFile(null);
      setFormData({
        title: '',
        genre: '',
        bpm: '',
        musical_key: '',
        tags: '',
      });
    }
  }, [uploadMutation.isSuccess]);

  // Handle upload error
  useEffect(() => {
    if (uploadMutation.isError) {
      const error = uploadMutation.error as AxiosError;
      const message = error.response?.data?.detail || 'Upload failed';
      toast.error(String(message));
    }
  }, [uploadMutation.isError]);

  return (
    <PageLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold">Upload Samples</h2>
          <p className="text-muted-foreground mt-2">
            Upload and analyze new audio samples
          </p>
        </div>

        {/* Upload Drop Zone */}
        <Card className="p-8">
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
              transition-colors duration-200
              ${isDragActive ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/50'}
            `}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            {isDragActive ? (
              <p className="text-lg font-medium">Drop the file here...</p>
            ) : (
              <div>
                <p className="text-lg font-medium">Drag & drop audio file here</p>
                <p className="text-sm text-muted-foreground mt-2">
                  or click to browse (WAV, MP3, FLAC, AIFF, M4A, OGG)
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Max 50MB per file
                </p>
              </div>
            )}
          </div>

          {selectedFile && (
            <div className="mt-4 flex items-center gap-3 p-3 bg-muted rounded-lg border">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{selectedFile.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSelectedFile(null)}
                disabled={uploadMutation.isPending}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}
        </Card>

        {/* Metadata Form */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Sample Information</h3>

          <div className="space-y-4">
            {/* Title */}
            <div>
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                placeholder="Enter sample title"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value.slice(0, 255) })
                }
                disabled={uploadMutation.isPending}
                maxLength={255}
              />
              <p className="text-xs text-muted-foreground mt-1">
                {formData.title.length}/255 characters
              </p>
            </div>

            {/* Genre */}
            <div>
              <Label htmlFor="genre">Genre (optional)</Label>
              <Select
                value={formData.genre}
                onValueChange={(value) =>
                  setFormData({ ...formData, genre: value })
                }
                disabled={uploadMutation.isPending}
              >
                <SelectTrigger id="genre">
                  <SelectValue placeholder="Select a genre" />
                </SelectTrigger>
                <SelectContent>
                  {GENRES.map((g) => (
                    <SelectItem key={g} value={g}>
                      {g}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* BPM */}
            <div>
              <Label htmlFor="bpm">BPM (optional)</Label>
              <Input
                id="bpm"
                type="number"
                placeholder="Enter BPM (40-200)"
                value={formData.bpm}
                onChange={(e) =>
                  setFormData({ ...formData, bpm: e.target.value })
                }
                disabled={uploadMutation.isPending}
                min="40"
                max="200"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Valid range: 40-200 BPM
              </p>
            </div>

            {/* Musical Key */}
            <div>
              <Label htmlFor="key">Musical Key (optional)</Label>
              <Select
                value={formData.musical_key}
                onValueChange={(value) =>
                  setFormData({ ...formData, musical_key: value })
                }
                disabled={uploadMutation.isPending}
              >
                <SelectTrigger id="key">
                  <SelectValue placeholder="Select a key" />
                </SelectTrigger>
                <SelectContent>
                  {MUSICAL_KEYS.map((k) => (
                    <SelectItem key={k} value={k}>
                      {k}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Tags */}
            <div>
              <Label htmlFor="tags">Tags (optional)</Label>
              <Textarea
                id="tags"
                placeholder="Enter tags separated by commas (e.g., drums, loop, vintage)"
                value={formData.tags}
                onChange={(e) =>
                  setFormData({ ...formData, tags: e.target.value })
                }
                disabled={uploadMutation.isPending}
                rows={3}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Comma-separated tags to organize your samples
              </p>
            </div>
          </div>
        </Card>

        {/* Upload Button */}
        <Button
          onClick={handleUpload}
          disabled={!selectedFile || uploadMutation.isPending}
          className="w-full h-10"
          size="lg"
        >
          {uploadMutation.isPending ? 'Uploading...' : 'Upload Sample'}
        </Button>
      </div>
    </PageLayout>
  );
}
