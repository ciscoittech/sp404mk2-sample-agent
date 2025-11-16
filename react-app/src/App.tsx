import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import { ThemeProvider } from '@/components/ThemeProvider';
import { AppShell } from '@/components/layout/AppShell';
import { DashboardPage } from '@/pages/DashboardPage';
import { SamplesPage } from '@/pages/SamplesPage';
import { KitsPage } from '@/pages/KitsPage';
import { UploadPage } from '@/pages/UploadPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { ComponentsDemo } from '@/pages/ComponentsDemo';
import { ColorsDebugPage } from '@/pages/ColorsDebugPage';
import { AudioPlayerTest } from '@/pages/AudioPlayerTest';
import '@/globals.css';

function App() {
  useEffect(() => {
    // Suppress WaveSurfer AbortErrors - these occur when components unmount during audio loading
    // and are harmless. The library internally aborts fetch requests during cleanup, causing
    // unhandled promise rejections that can't be caught in component-level try/catch blocks.
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      if (
        event.reason?.name === 'AbortError' &&
        (event.reason?.message?.includes('signal is aborted') ||
          event.reason?.message?.includes('aborted'))
      ) {
        event.preventDefault();
        return;
      }
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    return () => window.removeEventListener('unhandledrejection', handleUnhandledRejection);
  }, []);

  return (
    <ThemeProvider defaultTheme="dark" storageKey="sp404-ui-theme">
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppShell>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/samples" element={<SamplesPage />} />
              <Route path="/kits" element={<KitsPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/demo" element={<ComponentsDemo />} />
              <Route path="/debug/colors" element={<ColorsDebugPage />} />
              <Route path="/test/audio" element={<AudioPlayerTest />} />
            </Routes>
          </AppShell>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
