# AppShell Architecture

## Component Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ SidebarProvider (Context & Keyboard Shortcuts)                 │
│                                                                 │
│ ┌──────────────┬──────────────────────────────────────────────┐│
│ │              │ SidebarInset (Main Content Area)             ││
│ │              │                                              ││
│ │   Sidebar    │ ┌──────────────────────────────────────────┐││
│ │   (Left)     │ │ Header (Sticky Top Bar)                  │││
│ │              │ │  ├─ SidebarTrigger                       │││
│ │ ┌──────────┐ │ │  ├─ Page Title (Auto-detected)          │││
│ │ │  Header  │ │ │  └─ ThemeSwitcher                       │││
│ │ │  SP-404  │ │ └──────────────────────────────────────────┘││
│ │ │  Logo    │ │                                              ││
│ │ └──────────┘ │ ┌──────────────────────────────────────────┐││
│ │              │ │ Main Content (Scrollable)                │││
│ │ ┌──────────┐ │ │                                          │││
│ │ │          │ │ │  {children}                              │││
│ │ │   Nav    │ │ │  (Page Components Rendered Here)         │││
│ │ │  Items   │ │ │                                          │││
│ │ │          │ │ │                                          │││
│ │ │ • Home   │ │ │                                          │││
│ │ │ • Sample │ │ │                                          │││
│ │ │ • Kits   │ │ │                                          │││
│ │ │ • Upload │ │ │                                          │││
│ │ │ • Setting│ │ │                                          │││
│ │ │          │ │ │                                          │││
│ │ └──────────┘ │ │                                          │││
│ │              │ │                                          │││
│ │              │ │                                          │││
│ │ ┌──────────┐ │ │                                          │││
│ │ │  Footer  │ │ │                                          │││
│ │ │  User    │ │ │                                          │││
│ │ │ Profile  │ │ │                                          │││
│ │ │ Dropdown │ │ │                                          │││
│ │ └──────────┘ │ └──────────────────────────────────────────┘││
│ │              │                                              ││
│ │ SidebarRail  │                                              ││
│ └──────────────┴──────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Responsive Behavior

### Desktop (≥768px)

**Expanded Mode (Default)**
```
┌─────────┬──────────────────────────────┐
│ Sidebar │ Main Content                 │
│ 16rem   │ Flexible width               │
│         │                              │
│ [Logo]  │ [Header Bar]                 │
│ Home    │ [Page Content]               │
│ Samples │                              │
│ Kits    │                              │
│ Upload  │                              │
│ Settings│                              │
│         │                              │
│ [User]  │                              │
└─────────┴──────────────────────────────┘
```

**Collapsed Mode (Icon Only)**
```
┌──┬─────────────────────────────────────┐
│S │ Main Content                        │
│i │ Flexible width                      │
│d │                                     │
│e │ [Header Bar]                        │
│b │ [Page Content]                      │
│a │                                     │
│r │                                     │
│  │                                     │
│3 │                                     │
│r │                                     │
│e │                                     │
│m │                                     │
│  │                                     │
│U │                                     │
└──┴─────────────────────────────────────┘
```

### Mobile (<768px)

**Closed State**
```
┌─────────────────────────────────────────┐
│ [☰] Dashboard          [Theme]          │ Header
├─────────────────────────────────────────┤
│                                         │
│                                         │
│          Full-width Content             │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

**Open State (Sheet Drawer)**
```
┌───────────────────┬─────────────────────┐
│ Sidebar Sheet     │ Dimmed Backdrop     │
│ 18rem wide        │                     │
│                   │                     │
│ [Logo]            │                     │
│ Home              │                     │
│ Samples           │                     │
│ Kits              │                     │
│ Upload            │                     │
│ Settings          │                     │
│                   │                     │
│ [User Profile]    │                     │
│                   │                     │
└───────────────────┴─────────────────────┘
```

## State Management

### SidebarProvider Context

```typescript
interface SidebarContextProps {
  state: "expanded" | "collapsed"
  open: boolean
  setOpen: (open: boolean) => void
  openMobile: boolean
  setOpenMobile: (open: boolean) => void
  isMobile: boolean
  toggleSidebar: () => void
}
```

### State Flow

```
User Action (Click/Keyboard)
       ↓
toggleSidebar()
       ↓
isMobile Check
       ↓
   ┌───┴───┐
   ↓       ↓
Desktop  Mobile
setOpen  setOpenMobile
   ↓       ↓
Collapse Sheet Open
Icon Mode Animation
```

## CSS Custom Properties

### Sidebar Widths

```css
--sidebar-width: 16rem         /* Expanded sidebar */
--sidebar-width-mobile: 18rem  /* Mobile sheet */
--sidebar-width-icon: 3rem     /* Collapsed icon-only */
```

### Theme Colors (Dark Mode)

```css
--sidebar: oklch(0.22 0.02 250)                  /* Background */
--sidebar-foreground: oklch(0.98 0.005 250)      /* Text */
--sidebar-primary: oklch(0.75 0.15 210)          /* Cyan accent */
--sidebar-accent: oklch(0.28 0.02 250)           /* Hover state */
--sidebar-border: oklch(0.30 0.02 250)           /* Borders */
```

## Component Props

### AppShell

```typescript
interface AppShellProps {
  children: ReactNode;  // Page content to render
}
```

### Navigation Item

```typescript
interface NavItem {
  title: string;        // Display name
  href: string;         // Route path
  icon: LucideIcon;     // Icon component
  badge?: string;       // Optional badge text
}
```

## Key Features

### 1. Active Route Detection

```typescript
const isActive = (href: string) => {
  if (href === '/') {
    return location.pathname === '/';
  }
  return location.pathname.startsWith(href);
};
```

### 2. Keyboard Shortcuts

- **Cmd/Ctrl + B**: Toggle sidebar
- Handled by `SidebarProvider` context

### 3. Collapsible Variants

- **offcanvas**: Sidebar slides off-screen (mobile behavior)
- **icon**: Sidebar collapses to icon-only mode (default)
- **none**: Sidebar cannot be collapsed

### 4. Layout Variants

- **sidebar**: Standard fixed sidebar (default)
- **floating**: Floating sidebar with padding
- **inset**: Inset sidebar with rounded corners (used)

## Animation & Transitions

### Sidebar Toggle

```css
transition: [width] duration-200 ease-linear
```

### Active State

```css
transition: colors
background: sidebar-accent
color: primary (cyan)
font-weight: medium
```

### Header Backdrop Blur

```css
background: background/95
backdrop-blur
supports-[backdrop-filter]: background/60
```

## Integration Points

### 1. React Router

Uses `useLocation()` hook for active route detection:

```typescript
const location = useLocation();
const active = location.pathname === href;
```

### 2. Theme System

Integrates with existing `ThemeSwitcher` component:

```tsx
<ThemeSwitcher />
```

### 3. Navigation

Uses React Router `Link` components:

```tsx
<Link to={item.href}>
  {/* Navigation content */}
</Link>
```

## Performance Considerations

### Optimizations

1. **Context Memoization**: Sidebar context values are memoized
2. **CSS Transitions**: Hardware-accelerated transform animations
3. **Conditional Rendering**: Mobile sheet only renders on mobile
4. **Lazy State Updates**: Debounced resize handlers

### Bundle Size

- Sidebar component: ~8KB (gzipped)
- Dependencies: Radix UI primitives (already in project)
- Total added: ~10KB to bundle

## Accessibility Features

### ARIA Labels

- `<SidebarTrigger>`: "Toggle Sidebar"
- `<SheetTitle>`: "Sidebar" (screen reader only)
- Active nav items: `data-active="true"`

### Keyboard Navigation

- Tab through navigation items
- Enter/Space to activate
- Escape to close mobile sheet
- Cmd/Ctrl + B to toggle

### Focus Management

- Focus trap in mobile sheet
- Visible focus indicators
- Logical tab order

## Future Enhancements

### Potential Additions

1. **Breadcrumbs**: Add breadcrumb navigation in header
2. **Search**: Global search in sidebar header
3. **Notifications**: Badge counts on nav items
4. **Favorites**: Pin frequently used pages
5. **Workspace Switcher**: Multiple workspaces/projects
6. **Recent Items**: Quick access to recent samples/kits

### API for Custom Nav

```typescript
// Future: Allow passing navigation as prop
<AppShell navigation={customNavItems}>
  {children}
</AppShell>
```
