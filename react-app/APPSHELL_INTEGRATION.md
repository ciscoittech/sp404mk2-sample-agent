# AppShell Component - Integration Guide

## Overview

The `AppShell` component provides a professional sidebar layout for the SP-404 Sample Manager UI. It includes:

- Collapsible sidebar with icon-only mode
- Mobile-responsive (Sheet on mobile)
- Active route highlighting with cyan accent
- User profile dropdown
- Theme switcher integration
- Keyboard shortcut (Cmd/Ctrl + B to toggle)

## Quick Start

### Option 1: Wrap All Routes in App.tsx (Recommended)

Replace the current `PageLayout` usage with `AppShell` at the root level:

```tsx
// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import { ThemeProvider } from '@/components/ThemeProvider';
import { AppShell } from '@/components/layout/AppShell';
import { SamplesPage } from '@/pages/SamplesPage';
import { KitsPage } from '@/pages/KitsPage';
import { UploadPage } from '@/pages/UploadPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { ComponentsDemo } from '@/pages/ComponentsDemo';
import '@/globals.css';

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="sp404-ui-theme">
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppShell>
            <Routes>
              <Route path="/" element={<SamplesPage />} />
              <Route path="/samples" element={<SamplesPage />} />
              <Route path="/kits" element={<KitsPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/demo" element={<ComponentsDemo />} />
            </Routes>
          </AppShell>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
```

### Option 2: Update Individual Pages

Remove `PageLayout` wrapper from each page component:

```tsx
// BEFORE (src/pages/SamplesPage.tsx)
import { PageLayout } from '@/components/layout/PageLayout';

export function SamplesPage() {
  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Page content */}
      </div>
    </PageLayout>
  );
}

// AFTER
export function SamplesPage() {
  return (
    <div className="space-y-6">
      {/* Page content */}
    </div>
  );
}
```

## Features

### 1. Sidebar Navigation

Navigation items are defined in the AppShell component:

```tsx
const navigation: NavItem[] = [
  { title: 'Dashboard', href: '/', icon: Home },
  { title: 'Samples', href: '/samples', icon: Music },
  { title: 'Kits', href: '/kits', icon: Grid3x3 },
  { title: 'Upload', href: '/upload', icon: Upload },
  { title: 'Settings', href: '/settings', icon: Settings },
];
```

### 2. Active Route Highlighting

The component automatically highlights the active route with:
- Cyan accent color
- Bold font weight
- Enhanced icon color

### 3. Collapsible Sidebar

- **Desktop**: Click the rail on the right edge or use the trigger button
- **Mobile**: Automatically converts to a Sheet drawer
- **Keyboard**: Press `Cmd + B` (Mac) or `Ctrl + B` (Windows/Linux)

### 4. User Profile Dropdown

Located in the footer with:
- User name and plan display
- Quick access to Settings
- Quick access to Upload

### 5. Top Header Bar

Shows:
- Sidebar toggle button
- Current page title (auto-detected from route)
- Theme switcher

## Customization

### Add Navigation Items

Edit the `navigation` array in `AppShell.tsx`:

```tsx
const navigation: NavItem[] = [
  // ... existing items
  {
    title: 'Analytics',
    href: '/analytics',
    icon: BarChart,
    badge: 'New', // Optional badge
  },
];
```

### Modify User Profile

Update the footer section:

```tsx
<div className="grid flex-1 text-left text-sm leading-tight">
  <span className="truncate font-semibold">Your Name</span>
  <span className="truncate text-xs text-sidebar-foreground/70">
    Pro Plan
  </span>
</div>
```

### Change Sidebar Behavior

Modify the `SidebarProvider` props:

```tsx
<SidebarProvider
  defaultOpen={true}  // Start expanded/collapsed
>
```

Modify the `Sidebar` props:

```tsx
<Sidebar
  collapsible="icon"     // "icon" | "offcanvas" | "none"
  variant="inset"        // "sidebar" | "floating" | "inset"
  side="left"            // "left" | "right"
>
```

## Layout Grid

The AppShell uses the shadcn/ui Sidebar component which handles the responsive grid automatically:

- **Collapsed**: 3rem icon-only sidebar
- **Expanded**: 16rem full sidebar
- **Mobile**: Full-width sheet drawer

## Theme Support

The component fully supports the dark/light theme with proper colors:

- **Dark Mode**: Deep blue-gray background with cyan accents
- **Light Mode**: Clean white background with darker cyan

Theme variables are defined in `globals.css`:

```css
.dark {
  --sidebar: oklch(0.22 0.02 250);           /* Dark background */
  --sidebar-primary: oklch(0.75 0.15 210);   /* Cyan accent */
  --sidebar-accent: oklch(0.28 0.02 250);    /* Hover state */
}
```

## Accessibility

- Proper ARIA labels
- Keyboard navigation support
- Focus indicators
- Semantic HTML structure
- Screen reader announcements

## Migration Checklist

- [ ] Update `App.tsx` to use `AppShell` instead of individual `PageLayout` wrappers
- [ ] Remove `PageLayout` imports from all page components
- [ ] Remove `<PageLayout>` wrappers from all page components
- [ ] Update page content to use `space-y-6` or similar spacing
- [ ] Test sidebar collapse/expand on desktop
- [ ] Test mobile sheet drawer
- [ ] Test keyboard shortcut (Cmd/Ctrl + B)
- [ ] Verify active route highlighting works
- [ ] Test theme switching
- [ ] Verify user dropdown functionality

## Browser Support

Works in all modern browsers that support:
- CSS Grid
- CSS Custom Properties
- Flexbox
- Backdrop Filter (for header blur effect)

## Performance

- Minimal re-renders (uses React Context efficiently)
- Smooth animations with CSS transitions
- No layout shift when toggling sidebar
- Optimized for mobile touch interactions

## Troubleshooting

### Sidebar not showing

Ensure all required components are installed:
```bash
npx shadcn@latest add sidebar
```

### Active route not highlighting

Check that your route paths match the `navigation` array `href` values exactly.

### Theme not working

Verify `ThemeProvider` wraps the entire app and sidebar CSS variables are defined in `globals.css`.

### Mobile sheet not opening

The mobile trigger is automatic based on screen size. Test at mobile breakpoints (<768px).
