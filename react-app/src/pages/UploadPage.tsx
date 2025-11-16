import { PageLayout } from '@/components/layout/PageLayout';

export function UploadPage() {
  return (
    <PageLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold">Upload Samples</h2>
          <p className="text-muted-foreground mt-2">
            Upload and analyze new audio samples
          </p>
        </div>

        <div className="rounded-lg border border-border bg-card p-8 text-center">
          <p className="text-muted-foreground">
            Upload interface will be added here
          </p>
        </div>
      </div>
    </PageLayout>
  );
}
