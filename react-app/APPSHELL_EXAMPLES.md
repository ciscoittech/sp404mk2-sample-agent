# AppShell Customization Examples

## Common Customizations

### 1. Add Badge to Navigation Item

Show notification count or "New" badge:

```tsx
const navigation: NavItem[] = [
  {
    title: 'Samples',
    href: '/samples',
    icon: Music,
    badge: '12',  // ← Shows sample count
  },
  {
    title: 'Kits',
    href: '/kits',
    icon: Grid3x3,
    badge: 'New',  // ← Shows "New" label
  },
];
```

### 2. Add Secondary Navigation Group

Create sections in sidebar:

```tsx
<SidebarContent>
  {/* Main Navigation */}
  <SidebarGroup>
    <SidebarGroupLabel>Main</SidebarGroupLabel>
    <SidebarGroupContent>
      <SidebarMenu>
        {/* Your main nav items */}
      </SidebarMenu>
    </SidebarGroupContent>
  </SidebarGroup>

  {/* Admin Section */}
  <SidebarGroup>
    <SidebarGroupLabel>Admin</SidebarGroupLabel>
    <SidebarGroupContent>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton asChild>
            <Link to="/admin">
              <Shield className="size-4" />
              <span>Admin Panel</span>
            </Link>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarGroupContent>
  </SidebarGroup>
</SidebarContent>
```

### 3. Add Search to Sidebar

Global search in sidebar header:

```tsx
<SidebarHeader>
  <SidebarMenu>
    {/* Logo */}
  </SidebarMenu>

  {/* Add Search */}
  <form>
    <SidebarInput
      type="search"
      placeholder="Search samples..."
      onChange={(e) => handleSearch(e.target.value)}
    />
  </form>
</SidebarHeader>
```

### 4. Dynamic User Profile

Show real user data:

```tsx
const { user } = useAuth();  // Your auth hook

<SidebarFooter>
  <SidebarMenu>
    <SidebarMenuItem>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <SidebarMenuButton size="lg">
            <Avatar className="size-8">
              <AvatarImage src={user.avatar} />
              <AvatarFallback>{user.initials}</AvatarFallback>
            </Avatar>
            <div className="grid flex-1 text-left text-sm leading-tight">
              <span className="truncate font-semibold">
                {user.name}
              </span>
              <span className="truncate text-xs">
                {user.email}
              </span>
            </div>
            <ChevronUp className="ml-auto size-4" />
          </SidebarMenuButton>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem onClick={handleLogout}>
            <LogOut className="mr-2 size-4" />
            Logout
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </SidebarMenuItem>
  </SidebarMenu>
</SidebarFooter>
```

### 5. Add Breadcrumbs to Header

Show navigation path:

```tsx
<header className="sticky top-0...">
  <SidebarTrigger />
  <div className="h-4 w-[1px] bg-border" />

  {/* Add Breadcrumbs */}
  <Breadcrumb>
    <BreadcrumbList>
      <BreadcrumbItem>
        <BreadcrumbLink href="/">Home</BreadcrumbLink>
      </BreadcrumbItem>
      <BreadcrumbSeparator />
      <BreadcrumbItem>
        <BreadcrumbPage>Samples</BreadcrumbPage>
      </BreadcrumbItem>
    </BreadcrumbList>
  </Breadcrumb>

  <div className="flex-1" />
  <ThemeSwitcher />
</header>
```

### 6. Add Workspace Switcher

Switch between projects:

```tsx
<SidebarHeader>
  <SidebarMenu>
    <SidebarMenuItem>
      {/* Workspace Dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <SidebarMenuButton size="lg">
            <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Folder className="size-4" />
            </div>
            <div className="flex-1 text-left">
              <span className="truncate font-semibold">
                {currentWorkspace.name}
              </span>
            </div>
            <ChevronsUpDown className="ml-auto size-4" />
          </SidebarMenuButton>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          {workspaces.map((ws) => (
            <DropdownMenuItem
              key={ws.id}
              onClick={() => switchWorkspace(ws.id)}
            >
              {ws.name}
            </DropdownMenuItem>
          ))}
          <DropdownMenuSeparator />
          <DropdownMenuItem>
            <Plus className="mr-2 size-4" />
            New Workspace
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </SidebarMenuItem>
  </SidebarMenu>
</SidebarHeader>
```

### 7. Add Keyboard Shortcuts Menu

Show available shortcuts:

```tsx
// Add to user dropdown
<DropdownMenuContent>
  <DropdownMenuItem asChild>
    <Link to="/settings">
      <Settings className="mr-2 size-4" />
      Settings
    </Link>
  </DropdownMenuItem>

  {/* Shortcuts Menu */}
  <DropdownMenuItem onClick={openShortcutsDialog}>
    <Keyboard className="mr-2 size-4" />
    Keyboard Shortcuts
    <DropdownMenuShortcut>⌘K</DropdownMenuShortcut>
  </DropdownMenuItem>
</DropdownMenuContent>
```

### 8. Add Active Sample Counter

Show currently selected samples:

```tsx
const { selectedSamples } = useSelection();

<SidebarFooter>
  {/* Selection Counter */}
  {selectedSamples.length > 0 && (
    <div className="p-2">
      <div className="rounded-lg bg-primary/10 p-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-primary font-medium">
            {selectedSamples.length} selected
          </span>
          <Button size="sm" variant="ghost" onClick={clearSelection}>
            Clear
          </Button>
        </div>
      </div>
    </div>
  )}

  {/* User Profile */}
  <SidebarMenu>
    {/* ... */}
  </SidebarMenu>
</SidebarFooter>
```

### 9. Add Quick Actions

Floating action button in sidebar:

```tsx
<SidebarContent>
  <SidebarGroup>
    {/* Navigation items */}
  </SidebarGroup>

  {/* Quick Actions */}
  <SidebarGroup className="mt-auto">
    <SidebarGroupContent>
      <Button className="w-full" asChild>
        <Link to="/upload">
          <Upload className="mr-2 size-4" />
          Upload Sample
        </Link>
      </Button>
    </SidebarGroupContent>
  </SidebarGroup>
</SidebarContent>
```

### 10. Add Sub-Navigation

Nested menu items:

```tsx
<SidebarMenuItem>
  <Collapsible defaultOpen className="group/collapsible">
    <CollapsibleTrigger asChild>
      <SidebarMenuButton>
        <Music className="size-4" />
        <span>Samples</span>
        <ChevronRight className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-90" />
      </SidebarMenuButton>
    </CollapsibleTrigger>
    <CollapsibleContent>
      <SidebarMenuSub>
        <SidebarMenuSubItem>
          <SidebarMenuSubButton asChild>
            <Link to="/samples/drums">
              <span>Drums</span>
            </Link>
          </SidebarMenuSubButton>
        </SidebarMenuSubItem>
        <SidebarMenuSubItem>
          <SidebarMenuSubButton asChild>
            <Link to="/samples/bass">
              <span>Bass</span>
            </Link>
          </SidebarMenuSubButton>
        </SidebarMenuSubItem>
      </SidebarMenuSub>
    </CollapsibleContent>
  </Collapsible>
</SidebarMenuItem>
```

## Advanced Examples

### 11. Storage Usage Indicator

Show disk space usage:

```tsx
const { used, total } = useStorage();
const percentage = (used / total) * 100;

<SidebarFooter>
  <div className="p-2 space-y-2">
    <div className="text-xs text-sidebar-foreground/70">
      Storage: {used}GB / {total}GB
    </div>
    <Progress value={percentage} className="h-1" />
  </div>

  <SidebarMenu>
    {/* User profile */}
  </SidebarMenu>
</SidebarFooter>
```

### 12. Recent Items

Show recently accessed samples:

```tsx
const { recentSamples } = useRecent();

<SidebarContent>
  {/* Main navigation */}

  <SidebarGroup>
    <SidebarGroupLabel>Recent</SidebarGroupLabel>
    <SidebarGroupContent>
      <SidebarMenu>
        {recentSamples.map((sample) => (
          <SidebarMenuItem key={sample.id}>
            <SidebarMenuButton asChild size="sm">
              <Link to={`/samples/${sample.id}`}>
                <Music className="size-3" />
                <span className="truncate">{sample.title}</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarGroupContent>
  </SidebarGroup>
</SidebarContent>
```

### 13. Favorites Section

Pin favorite samples:

```tsx
const { favorites } = useFavorites();

<SidebarContent>
  <SidebarGroup>
    <SidebarGroupLabel>
      <Star className="mr-2 size-4" />
      Favorites
    </SidebarGroupLabel>
    <SidebarGroupContent>
      <SidebarMenu>
        {favorites.map((item) => (
          <SidebarMenuItem key={item.id}>
            <SidebarMenuButton asChild size="sm">
              <Link to={item.href}>
                <item.icon className="size-3" />
                <span>{item.title}</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarGroupContent>
  </SidebarGroup>

  {/* Main navigation */}
</SidebarContent>
```

### 14. Command Palette Integration

Quick access to all features:

```tsx
// Add to header
const [open, setOpen] = useState(false);

useEffect(() => {
  const down = (e: KeyboardEvent) => {
    if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      setOpen((open) => !open);
    }
  };
  document.addEventListener('keydown', down);
  return () => document.removeEventListener('keydown', down);
}, []);

<header>
  {/* ... */}

  <Button
    variant="outline"
    className="relative h-8 w-48 justify-start text-sm"
    onClick={() => setOpen(true)}
  >
    <Search className="mr-2 size-4" />
    <span className="inline-flex">Search...</span>
    <kbd className="ml-auto text-xs">⌘K</kbd>
  </Button>

  <CommandDialog open={open} onOpenChange={setOpen}>
    {/* Command palette content */}
  </CommandDialog>
</header>
```

### 15. Notifications Panel

Show system notifications:

```tsx
const { notifications } = useNotifications();
const unreadCount = notifications.filter(n => !n.read).length;

// Add to header
<header>
  {/* ... */}

  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <Button variant="ghost" size="icon" className="relative">
        <Bell className="size-4" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 size-4 rounded-full bg-destructive text-[10px] font-medium text-destructive-foreground flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" className="w-80">
      <DropdownMenuLabel>Notifications</DropdownMenuLabel>
      <DropdownMenuSeparator />
      {notifications.map((notif) => (
        <DropdownMenuItem key={notif.id}>
          {notif.message}
        </DropdownMenuItem>
      ))}
    </DropdownMenuContent>
  </DropdownMenu>
</header>
```

## Pro Tips

### 1. Conditional Navigation Items

Show items based on user role:

```tsx
const navigation = useMemo(() => {
  const baseNav = [
    { title: 'Home', href: '/', icon: Home },
    { title: 'Samples', href: '/samples', icon: Music },
  ];

  if (user.role === 'admin') {
    baseNav.push({
      title: 'Admin',
      href: '/admin',
      icon: Shield,
    });
  }

  return baseNav;
}, [user.role]);
```

### 2. Persist Sidebar State

Save collapse state to localStorage:

```tsx
const [sidebarOpen, setSidebarOpen] = useState(() => {
  const saved = localStorage.getItem('sidebar-open');
  return saved ? JSON.parse(saved) : true;
});

useEffect(() => {
  localStorage.setItem('sidebar-open', JSON.stringify(sidebarOpen));
}, [sidebarOpen]);

<SidebarProvider
  open={sidebarOpen}
  onOpenChange={setSidebarOpen}
>
```

### 3. Animated Badge

Pulse animation for new items:

```tsx
<span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-primary px-1.5 text-xs font-medium text-primary-foreground animate-pulse">
  New
</span>
```

### 4. Tooltip on Collapsed

Show full title on hover when collapsed:

```tsx
<SidebarMenuButton
  asChild
  isActive={active}
  tooltip={item.title}  // ← Automatically shows on collapse
>
```

### 5. Custom Hover Effects

Enhanced hover states:

```tsx
<SidebarMenuButton
  asChild
  className={cn(
    'transition-all duration-200',
    'hover:translate-x-1',  // Slide on hover
    active && 'border-l-2 border-primary'  // Active border
  )}
>
```

## Full Example: Production-Ready AppShell

```tsx
export function AppShell({ children }: AppShellProps) {
  const location = useLocation();
  const { user } = useAuth();
  const { notifications } = useNotifications();
  const { selectedSamples } = useSelection();
  const [commandOpen, setCommandOpen] = useState(false);

  // Command palette shortcut
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setCommandOpen(true);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  return (
    <SidebarProvider defaultOpen>
      <Sidebar collapsible="icon" variant="inset">
        <SidebarHeader>
          {/* Logo + Workspace Switcher */}
          <WorkspaceSwitcher />
          {/* Search */}
          <SidebarInput type="search" placeholder="Search..." />
        </SidebarHeader>

        <SidebarContent>
          {/* Main Navigation */}
          <NavigationGroup />

          {/* Recent Items */}
          <RecentItems />

          {/* Quick Actions */}
          <QuickActions />
        </SidebarContent>

        <SidebarFooter>
          {/* Selection Counter */}
          {selectedSamples.length > 0 && (
            <SelectionCounter count={selectedSamples.length} />
          )}

          {/* Storage Indicator */}
          <StorageIndicator />

          {/* User Profile */}
          <UserProfile user={user} />
        </SidebarFooter>

        <SidebarRail />
      </Sidebar>

      <SidebarInset>
        <header className="sticky top-0...">
          <SidebarTrigger />
          <Breadcrumb />
          <div className="flex-1" />
          {/* Command Palette Trigger */}
          <CommandTrigger onClick={() => setCommandOpen(true)} />
          {/* Notifications */}
          <NotificationBell notifications={notifications} />
          {/* Theme Switcher */}
          <ThemeSwitcher />
        </header>

        <main className="flex flex-1 flex-col gap-4 p-4">
          {children}
        </main>
      </SidebarInset>

      {/* Command Palette */}
      <CommandDialog open={commandOpen} onOpenChange={setCommandOpen}>
        <CommandPalette />
      </CommandDialog>
    </SidebarProvider>
  );
}
```

This provides a foundation for building a world-class music production application UI!
