import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useUploadSample } from '@/hooks/useSamples';

export function UploadDropZone() {
  const [files, setFiles] = useState<File[]>([]);
  const uploadMutation = useUploadSample();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.flac', '.aiff', '.m4a'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    maxFiles: 20,
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadFile = async (file: File) => {
    try {
      await uploadMutation.mutateAsync({ file });
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <div className="space-y-4">
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
          <p>Drop the files here...</p>
        ) : (
          <div>
            <p className="text-lg font-medium">Drag & drop audio files here</p>
            <p className="text-sm text-muted-foreground mt-2">
              or click to browse (WAV, MP3, FLAC, AIFF, M4A)
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Max 50MB per file, up to 20 files
            </p>
          </div>
        )}
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">Files to Upload ({files.length})</h3>
          {files.map((file, index) => (
            <div key={index} className="flex items-center gap-3 p-3 bg-card rounded-lg border">
              <File className="h-4 w-4 text-muted-foreground" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              {uploadMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeFile(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          ))}

          <Button
            onClick={() => files.forEach(uploadFile)}
            disabled={uploadMutation.isPending}
            className="w-full"
          >
            {uploadMutation.isPending ? 'Uploading...' : 'Upload All Files'}
          </Button>
        </div>
      )}
    </div>
  );
}
