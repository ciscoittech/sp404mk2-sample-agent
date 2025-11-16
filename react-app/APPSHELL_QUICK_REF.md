# AppShell Quick Reference

## Installation Complete ✓

The AppShell component is ready to use. Follow these steps to integrate it.

## 1-Minute Integration

### Step 1: Update App.tsx

```tsx
import { AppShell } from '@/components/layout/AppShell';

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="sp404-ui-theme">
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppShell>  {/* ← Add this wrapper */}
            <Routes>
              {/* Your routes */}
            </Routes>
          </AppShell>  {/* ← Close wrapper */}
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
```

### Step 2: Remove PageLayout from Pages

```tsx
// BEFORE
export function SamplesPage() {
  return (
    <PageLayout>  {/* ← Remove this */}
      <div className="space-y-6">
        {/* content */}
      </div>
    </PageLayout>  {/* ← Remove this */}
  );
}

// AFTER
export function SamplesPage() {
  return (
    <div className="space-y-6">
      {/* content */}
    </div>
  );
}
```

### Step 3: Test

```bash
npm run dev
```

**Expected Result:**
- Collapsible sidebar on left
- Navigation items with icons
- Active route highlighted in cyan
- Mobile responsive (sheet drawer)
- Theme switcher in header
- User profile dropdown in footer

## Navigation Items

Currently configured:

| Icon | Title | Route | Description |
|------|-------|-------|-------------|
| Home | Dashboard | `/` | Main dashboard |
| Music | Samples | `/samples` | Sample library |
| Grid3x3 | Kits | `/kits` | Kit builder |
| Upload | Upload | `/upload` | Upload samples |
| Settings | Settings | `/settings` | User settings |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd + B` (Mac) | Toggle sidebar |
| `Ctrl + B` (Windows/Linux) | Toggle sidebar |

## Customization Points

### Add Navigation Item

Edit `src/components/layout/AppShell.tsx`:

```tsx
const navigation: NavItem[] = [
  // Existing items...
  {
    title: 'Analytics',
    href: '/analytics',
    icon: BarChart,
    badge: '3',  // Optional
  },
];
```

### Change User Info

Edit footer section in `AppShell.tsx`:

```tsx
<span className="truncate font-semibold">Your Name</span>
<span className="truncate text-xs">Pro Plan</span>
```

### Modify Sidebar Behavior

```tsx
<SidebarProvider defaultOpen={true}>  {/* Start expanded */}
  <Sidebar
    collapsible="icon"    {/* "icon" | "offcanvas" | "none" */}
    variant="inset"       {/* "sidebar" | "floating" | "inset" */}
  >
```

## Responsive Breakpoints

| Screen Size | Behavior |
|-------------|----------|
| < 768px | Mobile sheet drawer |
| ≥ 768px | Desktop sidebar (collapsible) |

## Theme Colors

### Dark Mode (Default)
- Background: Deep blue-gray `#13151A`
- Sidebar: Card background `#16181F`
- Primary: Bright cyan `#1FC7FF`
- Active state: Cyan accent

### Light Mode
- Background: White `#FFFFFF`
- Sidebar: Off-white `#F8F9FB`
- Primary: Darker cyan `#0EA5E9`
- Active state: Cyan accent

## Component Structure

```
AppShell
├── Sidebar
│   ├── Header (Logo + Title)
│   ├── Content (Navigation Menu)
│   └── Footer (User Profile)
└── SidebarInset
    ├── Header (Page Title + Theme)
    └── Main (Your Page Content)
```

## Common Issues

### Sidebar not visible
✓ Check `SidebarProvider` wraps everything
✓ Verify sidebar CSS variables in `globals.css`

### Active route not highlighting
✓ Ensure route paths match navigation `href` exactly
✓ Check `useLocation()` hook is working

### Mobile sheet not opening
✓ Test at <768px width
✓ Verify `use-mobile` hook is installed

### Build errors
✓ Run `npx shadcn@latest add sidebar`
✓ Run `npx shadcn@latest add dropdown-menu`

## File Locations

| File | Purpose |
|------|---------|
| `src/components/layout/AppShell.tsx` | Main component |
| `src/components/ui/sidebar.tsx` | Sidebar primitives |
| `src/hooks/use-mobile.ts` | Mobile detection |
| `src/globals.css` | Theme variables |

## Next Steps

1. ✅ Build succeeded
2. ⏳ Update App.tsx to use AppShell
3. ⏳ Remove PageLayout from pages
4. ⏳ Test in browser
5. ⏳ Customize navigation items
6. ⏳ Update user profile info

## Support

See full documentation:
- `APPSHELL_INTEGRATION.md` - Complete integration guide
- `APPSHELL_ARCHITECTURE.md` - Technical architecture details

## Example Implementation

Full working example in:
```
src/components/layout/AppShell.tsx
```

The component is production-ready and follows shadcn/ui best practices.
