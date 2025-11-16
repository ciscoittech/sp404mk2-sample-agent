import { PageLayout } from '@/components/layout/PageLayout';

export function SettingsPage() {
  return (
    <PageLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold">Settings</h2>
          <p className="text-muted-foreground mt-2">
            Configure your preferences
          </p>
        </div>

        <div className="rounded-lg border border-border bg-card p-8 text-center">
          <p className="text-muted-foreground">
            Settings interface will be added here
          </p>
        </div>
      </div>
    </PageLayout>
  );
}
