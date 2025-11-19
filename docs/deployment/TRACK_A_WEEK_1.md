# Track A Week 1: UI/UX Development

**Duration**: 5 days (35 hours total)
**Focus**: Modernize React TypeScript environment + component catalog + dark theme
**Dependencies**: None (fully standalone)
**Risk**: Low

---

## OVERVIEW

Transform the existing React 19 app to use Modernize React template's Material-UI v7 components while maintaining the SP-404 cyan dark mode theme. Create a component catalog and establish E2E testing infrastructure.

**Current State**:
- React 19 with shadcn/ui components
- Tailwind CSS with custom OKLCH theme
- 63+ existing components
- 13 pages fully functional

**Target State**:
- Modernize React template integrated
- Material-UI v7 components styled with SP-404 theme
- Component catalog documented
- E2E tests running with Playwright
- Responsive AppShell layout

---

## TASK 1: Setup Modernize React TypeScript Environment

**Duration**: 6 hours
**Complexity**: Medium
**Prerequisites**: Node.js 18+, npm 9+

### Objective
Install and configure Modernize React template (TypeScript version) alongside the existing React app, preparing for gradual component migration.

### Step 1.1: Download Modernize React Template (45 min)

```bash
# Navigate to project root
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent

# Create temporary directory for template
mkdir -p temp/modernize-eval

# Download Modernize React TypeScript template
# NOTE: You must have purchased this from AdminMart
# Extract the zip file to temp/modernize-eval/

# Expected structure:
# temp/modernize-eval/
#   ├── package.json
#   ├── src/
#   │   ├── components/
#   │   ├── views/
#   │   └── theme/
#   └── public/
```

**Validation**:
```bash
# Verify template structure
ls -la temp/modernize-eval/src/
# Should show: components, views, theme, layouts, utils

# Check package.json
cat temp/modernize-eval/package.json | grep -E "(react|@mui)"
# Should show React 19+ and @mui/material 7+
```

### Step 1.2: Analyze Template Structure (60 min)

Create an inventory spreadsheet of all Modernize components:

```bash
# Create analysis directory
mkdir -p docs/modernize-analysis

# Generate component list
cd temp/modernize-eval
find src/components -name "*.tsx" -o -name "*.jsx" | sort > ../../docs/modernize-analysis/component-list.txt

# Count components
wc -l ../../docs/modernize-analysis/component-list.txt
# Expected: 770+ components
```

**Create Component Inventory** (`docs/modernize-analysis/COMPONENT_INVENTORY.md`):

```markdown
# Modernize React Component Inventory

## Layout Components (Priority 1)
- [ ] AppShell / MainLayout
- [ ] Sidebar / NavigationDrawer
- [ ] Header / TopBar
- [ ] Footer
- [ ] Breadcrumbs

## Form Components (Priority 2)
- [ ] TextField (Material-UI)
- [ ] Select / Dropdown
- [ ] Checkbox / Switch
- [ ] Radio Buttons
- [ ] Date Picker
- [ ] File Upload

## Data Display (Priority 3)
- [ ] Table / DataGrid
- [ ] Card layouts
- [ ] List / ListItem
- [ ] Accordion
- [ ] Tabs

## Navigation (Priority 4)
- [ ] Sidebar menu
- [ ] Breadcrumbs
- [ ] Pagination
- [ ] Stepper

## Feedback (Priority 5)
- [ ] Alert / Snackbar
- [ ] Dialog / Modal
- [ ] Progress indicators
- [ ] Skeleton loaders

## Total: ~770 components
```

**Validation**:
- ✅ Component inventory file created
- ✅ Components categorized by priority
- ✅ At least 15 components identified for Week 1

### Step 1.3: Install Material-UI Dependencies (30 min)

```bash
# Navigate to react-app
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app

# Install Material-UI core packages
npm install @mui/material@^7.0.0 @emotion/react@^11.14.0 @emotion/styled@^11.14.0

# Install Material-UI icons (770+ icons)
npm install @mui/icons-material@^7.0.0

# Install Material-UI date pickers (for forms)
npm install @mui/x-date-pickers@^7.0.0 dayjs@^1.11.13

# Install Material-UI data grid (for tables)
npm install @mui/x-data-grid@^7.0.0

# Verify installation
npm list @mui/material
# Should show: @mui/material@7.x.x
```

**Validation**:
```bash
# Check package.json
cat package.json | grep "@mui"
# Should show all 4 packages installed

# Test import (temporary test file)
cat > src/test-mui.tsx << 'EOF'
import { Button } from '@mui/material';
import { Home } from '@mui/icons-material';

export default function TestMUI() {
  return <Button startIcon={<Home />}>Test</Button>;
}
EOF

# Run dev server (should compile without errors)
npm run dev
# Visit http://localhost:5173 and check console for errors
```

### Step 1.4: Setup Dual Theme System (2 hours)

Create a parallel Material-UI theme alongside the existing Tailwind theme.

**Create MUI Theme Config** (`src/theme/mui-theme.ts`):

```typescript
import { createTheme, ThemeOptions } from '@mui/material/styles';

// SP-404 color palette (from globals.css)
const sp404Colors = {
  // Primary (Bright Cyan)
  primary: {
    light: '#38B2FF',
    main: '#1FC7FF',
    dark: '#0EA5E9',
    contrastText: '#13151A',
  },
  // Accent (Vibrant Green)
  secondary: {
    light: '#1FD864',
    main: '#15B857',
    dark: '#10A850',
    contrastText: '#13151A',
  },
  // Background (Dark Mode)
  background: {
    default: '#13151A',     // oklch(0.18 0.015 250)
    paper: '#16181F',       // oklch(0.22 0.02 250)
  },
  // Text
  text: {
    primary: '#F8F9FB',     // oklch(0.98 0.005 250)
    secondary: '#657184',   // oklch(0.55 0.015 250)
  },
  // Error
  error: {
    main: '#F04444',        // oklch(0.65 0.22 25)
  },
};

// Dark theme (default for SP-404)
const darkThemeOptions: ThemeOptions = {
  palette: {
    mode: 'dark',
    ...sp404Colors,
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
    button: {
      textTransform: 'none', // Don't uppercase buttons
    },
  },
  shape: {
    borderRadius: 10, // Match --radius: 0.625rem
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          backgroundImage: 'none', // Disable MUI gradient
        },
      },
    },
  },
};

// Light theme (for future use)
const lightThemeOptions: ThemeOptions = {
  palette: {
    mode: 'light',
    primary: {
      main: '#0EA5E9',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#10A850',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FFFFFF',
      paper: '#FFFFFF',
    },
  },
  typography: darkThemeOptions.typography,
  shape: darkThemeOptions.shape,
  components: darkThemeOptions.components,
};

export const darkTheme = createTheme(darkThemeOptions);
export const lightTheme = createTheme(lightThemeOptions);
```

**Update App.tsx to Provide MUI Theme**:

```typescript
// src/App.tsx
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { darkTheme } from './theme/mui-theme';
import { ThemeProvider } from './components/ThemeProvider'; // Existing Tailwind provider

function App() {
  return (
    <MuiThemeProvider theme={darkTheme}>
      <CssBaseline />
      <ThemeProvider defaultTheme="dark" storageKey="sp404-theme">
        {/* Existing app content */}
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <Routes>
              {/* ... existing routes ... */}
            </Routes>
          </BrowserRouter>
        </QueryClientProvider>
      </ThemeProvider>
    </MuiThemeProvider>
  );
}
```

**Validation**:
```bash
# Run dev server
npm run dev

# Open browser DevTools and check:
# 1. No MUI theme errors in console
# 2. Inspect <body> and see MUI theme classes
# 3. Background color should be #13151A (dark mode)

# Test with a Material-UI button
cat > src/pages/MUITestPage.tsx << 'EOF'
import { Box, Button, Typography } from '@mui/material';
import { Home } from '@mui/icons-material';

export default function MUITestPage() {
  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h1">MUI Theme Test</Typography>
      <Button variant="contained" startIcon={<Home />}>
        Primary Button
      </Button>
      <Button variant="contained" color="secondary">
        Secondary Button
      </Button>
    </Box>
  );
}
EOF

# Add route to test page
# Visit http://localhost:5173/mui-test
# Buttons should be cyan (#1FC7FF) and green (#15B857)
```

### Step 1.5: Configure TypeScript Path Aliases (30 min)

Ensure TypeScript recognizes both Material-UI and existing component paths.

**Update `tsconfig.app.json`**:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@mui/*": ["./node_modules/@mui/*"],
      "@theme/*": ["./src/theme/*"]
    }
  },
  "include": ["src"]
}
```

**Validation**:
```bash
# Run TypeScript compiler
npm run build
# Should complete without errors

# Test import in a component
cat > src/test-paths.tsx << 'EOF'
import { Button } from '@mui/material';
import { AppShell } from '@/components/layout/AppShell';
import { darkTheme } from '@theme/mui-theme';

// No TypeScript errors if paths are configured correctly
EOF
```

### Step 1.6: Document Setup (1 hour)

Create comprehensive setup documentation.

**Create Setup Guide** (`docs/modernize-analysis/SETUP_GUIDE.md`):

```markdown
# Modernize React + Material-UI Setup

## Installation Summary
- Material-UI v7.x
- Emotion (CSS-in-JS)
- MUI Icons (770+ icons)
- MUI X Data Grid
- MUI X Date Pickers

## Theme Configuration
- Primary: Cyan (#1FC7FF)
- Secondary: Green (#15B857)
- Dark mode default
- Border radius: 10px
- Typography: System fonts

## Path Aliases
- `@/*` → `src/*`
- `@components/*` → `src/components/*`
- `@mui/*` → `node_modules/@mui/*`
- `@theme/*` → `src/theme/*`

## Quick Start
\`\`\`bash
npm install
npm run dev
\`\`\`

## Testing MUI Theme
Visit `/mui-test` to see themed buttons and components.

## Troubleshooting
- **Emotion errors**: Ensure `@emotion/react` and `@emotion/styled` are installed
- **Theme not applied**: Check `App.tsx` wraps with `MuiThemeProvider`
- **Icon errors**: Install `@mui/icons-material`
```

**Validation Checklist**:
- ✅ Material-UI v7 installed
- ✅ SP-404 cyan theme configured
- ✅ Dark mode working
- ✅ TypeScript paths resolve
- ✅ Dev server runs without errors
- ✅ Documentation complete

**Time Estimate**: 6 hours (45min + 60min + 30min + 2hr + 30min + 1hr)

---

## TASK 2: Create Component Catalog for SP-404 Features

**Duration**: 8 hours
**Complexity**: Medium
**Prerequisites**: Task 1 complete

### Objective
Map existing React components to Modernize Material-UI components, identifying which components to migrate and in what order.

### Step 2.1: Inventory Existing Components (2 hours)

Create a comprehensive list of all current components.

```bash
# Navigate to react-app
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app

# Generate component tree
find src/components -name "*.tsx" | sort > ../docs/modernize-analysis/existing-components.txt

# Count by category
echo "Layout: $(find src/components/layout -name "*.tsx" | wc -l)"
echo "Samples: $(find src/components/samples -name "*.tsx" | wc -l)"
echo "Kits: $(find src/components/kits -name "*.tsx" | wc -l)"
echo "Audio: $(find src/components/audio -name "*.tsx" | wc -l)"
echo "UI: $(find src/components/ui -name "*.tsx" | wc -l)"
```

**Create Existing Component Matrix** (`docs/modernize-analysis/EXISTING_COMPONENTS.md`):

```markdown
# Current React Component Inventory

## Layout Components (6 components)
| Component | Purpose | Dependencies | Lines |
|-----------|---------|--------------|-------|
| AppShell | Main app layout with sidebar | shadcn/ui sidebar | 240 |
| Header | Top navigation bar | Lucide icons | 60 |
| PageLayout | Page wrapper with breadcrumbs | React Router | 45 |

## Sample Components (12 components)
| Component | Purpose | Dependencies | Lines |
|-----------|---------|--------------|-------|
| SampleCard | Sample metadata display | shadcn/ui card | 180 |
| SampleGrid | Grid of sample cards | React Query | 120 |
| FilterPanel | Sample filtering UI | shadcn/ui select | 210 |
| PinnedSamplesSection | Pinned samples display | Zustand | 95 |

## Kit Components (6 components)
| Component | Purpose | Dependencies | Lines |
|-----------|---------|--------------|-------|
| PadGrid | SP-404 16-pad layout | DnD | 156 |
| Pad | Single pad component | Audio context | 89 |
| ProjectBuilderDialog | Export project dialog | shadcn/ui dialog | 187 |

## Audio Components (4 components)
| Component | Purpose | Dependencies | Lines |
|-----------|---------|--------------|-------|
| SamplePlayer | Audio playback | WaveSurfer.js | 145 |
| WaveformVisualizer | Waveform display | WaveSurfer.js | 198 |
| AudioControls | Play/pause controls | Audio context | 78 |

## UI Components (35 shadcn/ui components)
button, card, dialog, dropdown-menu, input, select, slider, table, tabs, etc.

## Total: 63 components, ~4,500 lines of code
```

**Validation**:
- ✅ All components inventoried
- ✅ Dependencies identified
- ✅ Line counts documented

### Step 2.2: Map to Material-UI Components (3 hours)

Create a migration mapping from existing components to Material-UI equivalents.

**Create Migration Matrix** (`docs/modernize-analysis/MIGRATION_MATRIX.md`):

```markdown
# Component Migration Matrix

## Priority 1: Layout (Week 1)
| Existing | Material-UI Replacement | Effort | Notes |
|----------|-------------------------|--------|-------|
| AppShell | Drawer + AppBar + Box | Medium | Use MUI permanent drawer |
| Header | AppBar + Toolbar | Low | Direct replacement |
| PageLayout | Container + Breadcrumbs | Low | MUI has Breadcrumbs component |

**Week 1 Target**: Migrate 3 layout components

## Priority 2: Forms (Week 2)
| Existing | Material-UI Replacement | Effort | Notes |
|----------|-------------------------|--------|-------|
| shadcn/ui Input | TextField | Low | MUI TextField is more feature-rich |
| shadcn/ui Select | Select + MenuItem | Low | MUI native select |
| shadcn/ui Slider | Slider | Low | Direct replacement |
| shadcn/ui Switch | Switch | Low | Direct replacement |

**Week 2 Target**: Migrate 10 form components

## Priority 3: Data Display (Week 3)
| Existing | Material-UI Replacement | Effort | Notes |
|----------|-------------------------|--------|-------|
| SampleCard | Card + CardContent | Medium | Add MUI styling |
| SampleGrid | Grid2 + Card | Medium | Use MUI Grid2 (v7 feature) |
| shadcn/ui Table | DataGrid (MUI X) | High | Powerful but complex |

**Week 3 Target**: Migrate 5 data display components

## Priority 4: Navigation (Week 4)
| Existing | Material-UI Replacement | Effort | Notes |
|----------|-------------------------|--------|-------|
| Sidebar menu | List + ListItem + Collapse | Medium | MUI nested lists |
| Breadcrumbs | Breadcrumbs + Link | Low | Direct replacement |
| Tabs | Tabs + Tab | Low | Direct replacement |

**Week 4 Target**: Migrate 4 navigation components

## Priority 5: Feedback (Week 5)
| Existing | Material-UI Replacement | Effort | Notes |
|----------|-------------------------|--------|-------|
| sonner (toast) | Snackbar + Alert | Medium | MUI built-in notifications |
| shadcn/ui Dialog | Dialog + DialogContent | Low | Similar API |
| shadcn/ui Progress | LinearProgress | Low | Direct replacement |

**Week 5 Target**: Migrate 5 feedback components

## Components to Keep (No Migration)
| Component | Reason |
|-----------|--------|
| WaveformVisualizer | Custom WaveSurfer.js integration |
| SamplePlayer | Audio-specific logic |
| PadGrid | SP-404 specific layout |
| AudioControls | Custom audio API |

## Total Migration: ~25 components over 5 weeks
```

**Validation**:
- ✅ Migration path for each component defined
- ✅ Effort estimates documented
- ✅ Week-by-week targets set

### Step 2.3: Create Component Showcase Page (2 hours)

Build a live demo page showcasing Material-UI components with SP-404 theme.

**Create Component Showcase** (`src/pages/ComponentShowcase.tsx`):

```typescript
import { Box, Container, Typography, Stack, Paper } from '@mui/material';
import { Button } from '@mui/material';
import { TextField } from '@mui/material';
import { Select, MenuItem } from '@mui/material';
import { Slider } from '@mui/material';
import { Switch, FormControlLabel } from '@mui/material';
import { Chip } from '@mui/material';
import { Alert } from '@mui/material';
import { LinearProgress } from '@mui/material';
import { Card, CardContent, CardActions } from '@mui/material';
import { Home, Music, Settings } from '@mui/icons-material';

export default function ComponentShowcase() {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h2" gutterBottom>
        Material-UI Component Showcase
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        SP-404 cyan theme applied to Material-UI v7 components
      </Typography>

      {/* Buttons */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>Buttons</Typography>
        <Stack direction="row" spacing={2}>
          <Button variant="contained">Primary</Button>
          <Button variant="contained" color="secondary">Secondary</Button>
          <Button variant="outlined">Outlined</Button>
          <Button variant="text">Text</Button>
          <Button variant="contained" startIcon={<Home />}>With Icon</Button>
        </Stack>
      </Paper>

      {/* Form Inputs */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>Form Inputs</Typography>
        <Stack spacing={2}>
          <TextField label="Sample Name" variant="outlined" fullWidth />
          <Select defaultValue="jazz" fullWidth>
            <MenuItem value="jazz">Jazz</MenuItem>
            <MenuItem value="hiphop">Hip-Hop</MenuItem>
            <MenuItem value="electronic">Electronic</MenuItem>
          </Select>
          <Slider defaultValue={30} aria-label="BPM" />
          <FormControlLabel control={<Switch defaultChecked />} label="Auto-analyze" />
        </Stack>
      </Paper>

      {/* Cards */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>Cards</Typography>
        <Card>
          <CardContent>
            <Typography variant="h6">Sample Card</Typography>
            <Typography variant="body2" color="text.secondary">
              BPM: 120 | Key: C minor | Genre: Jazz
            </Typography>
          </CardContent>
          <CardActions>
            <Button size="small">Play</Button>
            <Button size="small">Add to Kit</Button>
          </CardActions>
        </Card>
      </Paper>

      {/* Feedback */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>Feedback</Typography>
        <Stack spacing={2}>
          <Alert severity="success">Sample analyzed successfully</Alert>
          <Alert severity="error">Failed to load audio file</Alert>
          <Alert severity="info">Processing 5 samples...</Alert>
          <LinearProgress />
          <LinearProgress variant="determinate" value={60} />
        </Stack>
      </Paper>

      {/* Icons */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>Icons</Typography>
        <Stack direction="row" spacing={2}>
          <Home />
          <Music />
          <Settings />
          <Chip icon={<Music />} label="Jazz" />
          <Chip icon={<Music />} label="Hip-Hop" color="primary" />
        </Stack>
      </Paper>
    </Container>
  );
}
```

**Add Route**:

```typescript
// src/App.tsx
import ComponentShowcase from './pages/ComponentShowcase';

<Routes>
  {/* Existing routes */}
  <Route path="/component-showcase" element={<ComponentShowcase />} />
</Routes>
```

**Validation**:
```bash
# Run dev server
npm run dev

# Visit http://localhost:5173/component-showcase
# Verify:
# - Primary buttons are cyan (#1FC7FF)
# - Secondary buttons are green (#15B857)
# - Background is dark (#13151A)
# - All components render without errors
```

### Step 2.4: Document Component API (1 hour)

Create usage documentation for each Material-UI component.

**Create Component API Guide** (`docs/modernize-analysis/COMPONENT_API.md`):

```markdown
# Material-UI Component API Reference

## Button
\`\`\`typescript
import { Button } from '@mui/material';

<Button variant="contained">Primary</Button>
<Button variant="contained" color="secondary">Secondary</Button>
<Button variant="outlined">Outlined</Button>
<Button startIcon={<Icon />}>With Icon</Button>
\`\`\`

**Props**: variant, color, size, startIcon, endIcon, disabled, onClick

## TextField
\`\`\`typescript
import { TextField } from '@mui/material';

<TextField label="Sample Name" variant="outlined" fullWidth />
<TextField type="number" label="BPM" defaultValue={120} />
\`\`\`

**Props**: label, variant, type, defaultValue, onChange, error, helperText

## Card
\`\`\`typescript
import { Card, CardContent, CardActions } from '@mui/material';

<Card>
  <CardContent>
    <Typography variant="h6">Title</Typography>
  </CardContent>
  <CardActions>
    <Button>Action</Button>
  </CardActions>
</Card>
\`\`\`

**Props**: elevation, variant, sx

## Select
\`\`\`typescript
import { Select, MenuItem } from '@mui/material';

<Select value={genre} onChange={(e) => setGenre(e.target.value)}>
  <MenuItem value="jazz">Jazz</MenuItem>
  <MenuItem value="hiphop">Hip-Hop</MenuItem>
</Select>
\`\`\`

**Props**: value, onChange, fullWidth, label, displayEmpty

## DataGrid (MUI X)
\`\`\`typescript
import { DataGrid } from '@mui/x-data-grid';

<DataGrid
  rows={samples}
  columns={columns}
  pageSize={25}
  checkboxSelection
/>
\`\`\`

**Props**: rows, columns, pageSize, loading, onRowClick

[Continue for all 15-20 components...]
```

**Validation**:
- ✅ API documented for 15+ components
- ✅ Code examples provided
- ✅ Common props listed

**Time Estimate**: 8 hours (2hr + 3hr + 2hr + 1hr)

---

## TASK 3: Design Dark Mode Color Palette (SP-404 Cyan Theme)

**Duration**: 7 hours
**Complexity**: Medium
**Prerequisites**: Task 1 complete

### Objective
Create a comprehensive SP-404-branded dark mode color system for Material-UI, extending the existing Tailwind OKLCH theme.

### Step 3.1: Extract Current Theme Colors (1 hour)

Document all existing colors from `globals.css`.

**Create Color Palette Document** (`docs/modernize-analysis/COLOR_PALETTE.md`):

```markdown
# SP-404 Color Palette (OKLCH → Hex)

## Primary: Bright Cyan
- Light: `oklch(0.80 0.15 210)` → `#38B2FF`
- Main: `oklch(0.75 0.15 210)` → `#1FC7FF`
- Dark: `oklch(0.60 0.15 210)` → `#0EA5E9`
- Contrast: `oklch(0.18 0.015 250)` → `#13151A`

## Secondary: Vibrant Green
- Light: `oklch(0.70 0.19 150)` → `#1FD864`
- Main: `oklch(0.65 0.19 150)` → `#15B857`
- Dark: `oklch(0.55 0.19 150)` → `#10A850`
- Contrast: `oklch(0.18 0.015 250)` → `#13151A`

## Background
- Default: `oklch(0.18 0.015 250)` → `#13151A` (deep blue-gray)
- Paper: `oklch(0.22 0.02 250)` → `#16181F` (card background)
- Elevated: `oklch(0.26 0.02 250)` → `#1A1E26` (modal backgrounds)

## Text
- Primary: `oklch(0.98 0.005 250)` → `#F8F9FB` (off-white)
- Secondary: `oklch(0.55 0.015 250)` → `#657184` (muted)
- Disabled: `oklch(0.40 0.015 250)` → `#3D4654`

## Error
- Main: `oklch(0.65 0.22 25)` → `#F04444`
- Light: `oklch(0.75 0.22 25)` → `#FF6B6B`
- Dark: `oklch(0.55 0.22 25)` → `#DC2626`

## Warning
- Main: `oklch(0.70 0.20 60)` → `#F59E0B`
- Light: `oklch(0.80 0.20 60)` → `#FFC454`
- Dark: `oklch(0.60 0.20 60)` → `#D97706`

## Success
- Main: `#15B857` (same as secondary green)
- Light: `#1FD864`
- Dark: `#10A850`

## Info
- Main: `#1FC7FF` (same as primary cyan)
- Light: `#38B2FF`
- Dark: `#0EA5E9`

## Border & Divider
- Border: `oklch(0.30 0.02 250)` → `#222936`
- Divider: `oklch(0.25 0.02 250)` → `#1A202C`

## Chart Colors (Data Visualization)
1. Cyan: `#1FC7FF`
2. Green: `#15B857`
3. Purple: `oklch(0.60 0.18 280)` → `#A855F7` (data viz only)
4. Yellow: `oklch(0.70 0.20 60)` → `#FFC454`
5. Red: `#F04444`
```

**Validation**:
- ✅ All colors documented
- ✅ OKLCH to Hex conversions verified
- ✅ Contrast ratios meet WCAG AA (4.5:1 minimum)

### Step 3.2: Create Material-UI Theme Variables (2 hours)

Extend the MUI theme with comprehensive color tokens.

**Update `src/theme/mui-theme.ts`**:

```typescript
import { createTheme, ThemeOptions, alpha } from '@mui/material/styles';

// SP-404 color tokens
const colors = {
  // Primary (Bright Cyan)
  cyan: {
    50: '#E0F7FF',
    100: '#B3EAFF',
    200: '#80DCFF',
    300: '#4DCFFF',
    400: '#26C4FF',
    500: '#1FC7FF', // Main
    600: '#0EA5E9', // Dark
    700: '#0284C7',
    800: '#0369A1',
    900: '#075985',
  },
  // Secondary (Vibrant Green)
  green: {
    50: '#E6F9EE',
    100: '#C0F0D4',
    200: '#96E7B8',
    300: '#6CDD9C',
    400: '#4DD687',
    500: '#15B857', // Main
    600: '#10A850', // Dark
    700: '#0D8F45',
    800: '#0A763A',
    900: '#065A2C',
  },
  // Neutral (Blue-gray)
  neutral: {
    50: '#F8F9FB',
    100: '#E9ECF0',
    200: '#D3D9E2',
    300: '#B0B9C9',
    400: '#8B96A8',
    500: '#657184', // Text secondary
    600: '#4A5468',
    700: '#3D4654', // Text disabled
    800: '#2B3240',
    900: '#13151A', // Background default
  },
  // Background
  background: {
    default: '#13151A',
    paper: '#16181F',
    elevated: '#1A1E26',
  },
};

const darkThemeOptions: ThemeOptions = {
  palette: {
    mode: 'dark',
    primary: {
      main: colors.cyan[500],
      light: colors.cyan[300],
      dark: colors.cyan[600],
      contrastText: colors.neutral[900],
    },
    secondary: {
      main: colors.green[500],
      light: colors.green[300],
      dark: colors.green[600],
      contrastText: colors.neutral[900],
    },
    error: {
      main: '#F04444',
      light: '#FF6B6B',
      dark: '#DC2626',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#F59E0B',
      light: '#FFC454',
      dark: '#D97706',
      contrastText: colors.neutral[900],
    },
    info: {
      main: colors.cyan[500],
      light: colors.cyan[300],
      dark: colors.cyan[600],
      contrastText: colors.neutral[900],
    },
    success: {
      main: colors.green[500],
      light: colors.green[300],
      dark: colors.green[600],
      contrastText: colors.neutral[900],
    },
    background: {
      default: colors.background.default,
      paper: colors.background.paper,
    },
    text: {
      primary: colors.neutral[50],
      secondary: colors.neutral[500],
      disabled: colors.neutral[700],
    },
    divider: alpha(colors.neutral[500], 0.12),
    action: {
      active: colors.neutral[50],
      hover: alpha(colors.cyan[500], 0.08),
      selected: alpha(colors.cyan[500], 0.16),
      disabled: colors.neutral[700],
      disabledBackground: alpha(colors.neutral[700], 0.12),
      focus: alpha(colors.cyan[500], 0.12),
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      lineHeight: 1.2,
      letterSpacing: '-0.01562em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.00833em',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
      lineHeight: 1.6,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.43,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.66,
    },
  },
  shape: {
    borderRadius: 10,
  },
  spacing: 8, // 8px base spacing unit
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          padding: '8px 16px',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
        containedPrimary: {
          backgroundColor: colors.cyan[500],
          color: colors.neutral[900],
          '&:hover': {
            backgroundColor: colors.cyan[600],
          },
        },
        containedSecondary: {
          backgroundColor: colors.green[500],
          color: colors.neutral[900],
          '&:hover': {
            backgroundColor: colors.green[600],
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          backgroundImage: 'none',
          backgroundColor: colors.background.paper,
          border: `1px solid ${alpha(colors.neutral[500], 0.12)}`,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
            '& fieldset': {
              borderColor: alpha(colors.neutral[500], 0.23),
            },
            '&:hover fieldset': {
              borderColor: alpha(colors.neutral[500], 0.4),
            },
            '&.Mui-focused fieldset': {
              borderColor: colors.cyan[500],
            },
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
        elevation1: {
          boxShadow: `0px 2px 4px ${alpha(colors.neutral[900], 0.25)}`,
        },
        elevation2: {
          boxShadow: `0px 4px 8px ${alpha(colors.neutral[900], 0.30)}`,
        },
      },
    },
  },
};

export const darkTheme = createTheme(darkThemeOptions);
export const lightTheme = createTheme(lightThemeOptions);

// Export color tokens for use in components
export { colors };
```

**Validation**:
```bash
# Test theme in ComponentShowcase
npm run dev
# Visit /component-showcase
# Verify:
# - Buttons use cyan/green colors
# - Cards have paper background (#16181F)
# - Text is readable (off-white on dark)
# - Borders are subtle blue-gray
```

### Step 3.3: Create Theme Switcher Component (2 hours)

Build a Material-UI version of the theme switcher.

**Create MUI Theme Switcher** (`src/components/MuiThemeSwitcher.tsx`):

```typescript
import { IconButton, Tooltip } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

export function MuiThemeSwitcher() {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const toggleTheme = () => {
    // Future: Toggle between dark and light
    console.log('Theme toggle clicked');
  };

  return (
    <Tooltip title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}>
      <IconButton onClick={toggleTheme} color="inherit">
        {isDark ? <Brightness7 /> : <Brightness4 />}
      </IconButton>
    </Tooltip>
  );
}
```

**Validation**:
- ✅ Theme switcher renders
- ✅ Icons display correctly
- ✅ Tooltip shows on hover

### Step 3.4: Document Theme Usage (1 hour)

Create comprehensive theme usage guide.

**Create Theme Guide** (`docs/modernize-analysis/THEME_GUIDE.md`):

```markdown
# SP-404 Theme Usage Guide

## Importing Theme
\`\`\`typescript
import { useTheme } from '@mui/material/styles';
import { colors } from '@theme/mui-theme';

const theme = useTheme();
\`\`\`

## Using Theme Colors in Components
\`\`\`typescript
import { Box } from '@mui/material';

<Box sx={{ bgcolor: 'background.paper', color: 'text.primary' }}>
  Content
</Box>
\`\`\`

## Custom Component Styling
\`\`\`typescript
<Button
  sx={{
    bgcolor: 'primary.main',
    color: 'primary.contrastText',
    '&:hover': {
      bgcolor: 'primary.dark',
    },
  }}
>
  Custom Button
</Button>
\`\`\`

## Accessing Color Tokens
\`\`\`typescript
import { colors } from '@theme/mui-theme';

<Box sx={{ backgroundColor: colors.cyan[500] }}>
  Direct color access
</Box>
\`\`\`

## Alpha Transparency
\`\`\`typescript
import { alpha } from '@mui/material/styles';

<Box sx={{ bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1) }}>
  Transparent cyan background
</Box>
\`\`\`

## Responsive Typography
\`\`\`typescript
<Typography
  variant="h1"
  sx={{
    fontSize: { xs: '1.5rem', md: '2.5rem' },
  }}
>
  Responsive heading
</Typography>
\`\`\`

## Best Practices
1. Use theme tokens (`primary.main`) instead of hardcoded colors
2. Use `sx` prop for component-specific styling
3. Leverage theme spacing: `sx={{ p: 2, m: 3 }}` (2×8px, 3×8px)
4. Use alpha() for transparent overlays
5. Test in both dark and light modes (future)
```

**Validation**:
- ✅ Theme guide complete
- ✅ Code examples provided
- ✅ Best practices documented

### Step 3.5: Validate Accessibility (1 hour)

Ensure all color combinations meet WCAG AA standards.

**Create Contrast Report** (`docs/modernize-analysis/CONTRAST_REPORT.md`):

```markdown
# Accessibility Contrast Report

## Primary Colors
| Foreground | Background | Ratio | WCAG AA | WCAG AAA |
|------------|------------|-------|---------|----------|
| #1FC7FF (cyan) | #13151A (bg) | 8.2:1 | ✅ Pass | ✅ Pass |
| #FFFFFF (white) | #1FC7FF (cyan) | 4.6:1 | ✅ Pass | ❌ Fail |
| #13151A (dark) | #1FC7FF (cyan) | 8.2:1 | ✅ Pass | ✅ Pass |

## Secondary Colors
| Foreground | Background | Ratio | WCAG AA | WCAG AAA |
|------------|------------|-------|---------|----------|
| #15B857 (green) | #13151A (bg) | 5.4:1 | ✅ Pass | ✅ Pass |
| #13151A (dark) | #15B857 (green) | 5.4:1 | ✅ Pass | ✅ Pass |

## Text Colors
| Foreground | Background | Ratio | WCAG AA | WCAG AAA |
|------------|------------|-------|---------|----------|
| #F8F9FB (text) | #13151A (bg) | 14.1:1 | ✅ Pass | ✅ Pass |
| #657184 (muted) | #13151A (bg) | 4.9:1 | ✅ Pass | ❌ Fail |
| #F8F9FB (text) | #16181F (paper) | 13.2:1 | ✅ Pass | ✅ Pass |

## Recommendations
- ✅ All primary/secondary colors meet WCAG AA
- ✅ Primary text colors meet WCAG AAA
- ⚠️ Secondary text could be brighter for AAA
- ✅ Button colors have sufficient contrast

## Tools Used
- WebAIM Contrast Checker
- Chrome DevTools Accessibility Panel
```

**Validation**:
```bash
# Install contrast checker (optional)
npm install --save-dev axe-core

# Run automated accessibility tests
# (Future: Integrate with Playwright tests)
```

**Time Estimate**: 7 hours (1hr + 2hr + 2hr + 1hr + 1hr)

---

## TASK 4: Create AppShell Layout Base Component

**Duration**: 7 hours
**Complexity**: Medium
**Prerequisites**: Tasks 1-3 complete

### Objective
Build a responsive Material-UI layout component to replace the existing shadcn/ui AppShell, featuring a collapsible sidebar, top app bar, and responsive navigation.

### Step 4.1: Design AppShell Structure (1 hour)

Plan the layout architecture.

**Create AppShell Spec** (`docs/modernize-analysis/APPSHELL_SPEC.md`):

```markdown
# AppShell Layout Specification

## Requirements
1. **Responsive**: Mobile (drawer), tablet (mini drawer), desktop (permanent drawer)
2. **Collapsible sidebar**: Toggle between expanded/collapsed states
3. **Top app bar**: Search, notifications, theme switcher, user menu
4. **Navigation**: Support nested menu items
5. **Breadcrumbs**: Show current page hierarchy
6. **Footer**: Copyright, version, links

## Layout Structure
\`\`\`
┌─────────────────────────────────────────────┐
│ App Bar (64px height)                       │
│ [Menu] [Breadcrumbs] [Search] [Theme] [User]│
├───────┬─────────────────────────────────────┤
│       │                                     │
│ Side  │ Main Content Area                   │
│ bar   │                                     │
│       │                                     │
│ 240px │ (dynamic width)                     │
│       │                                     │
├───────┴─────────────────────────────────────┤
│ Footer (optional)                           │
└─────────────────────────────────────────────┘
\`\`\`

## Breakpoints
- **xs**: 0-599px (mobile, temporary drawer)
- **sm**: 600-899px (tablet, mini drawer)
- **md**: 900-1199px (desktop, permanent drawer)
- **lg**: 1200-1535px (large desktop)
- **xl**: 1536px+ (extra large)

## Component Hierarchy
\`\`\`
<AppShell>
  ├── <AppBar> (top navigation)
  │   ├── <Toolbar>
  │   ├── <IconButton> (menu toggle)
  │   ├── <Breadcrumbs>
  │   ├── <Search>
  │   ├── <ThemeSwitcher>
  │   └── <UserMenu>
  ├── <Drawer> (sidebar)
  │   ├── <DrawerHeader> (logo, title)
  │   ├── <List> (navigation items)
  │   └── <Divider>
  └── <Box> (main content)
      ├── {children}
      └── <Footer> (optional)
\`\`\`

## Navigation Items (from existing AppShell)
1. Dashboard (/)
2. Samples (/samples)
3. Collections (/collections)
4. Kits (/kits)
5. Batches (/batches)
6. Upload (/upload)
7. Usage (/usage)
8. Settings (/settings)
```

**Validation**:
- ✅ Layout structure defined
- ✅ Responsive breakpoints planned
- ✅ Component hierarchy mapped

### Step 4.2: Build Drawer Component (2 hours)

Create the sidebar navigation drawer.

**Create MUI Drawer** (`src/components/layout/MuiDrawer.tsx`):

```typescript
import { Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Divider, Box, Typography } from '@mui/material';
import { Home, Music, FolderOpen, Grid3x3, Layers, Upload, DollarSign, Settings } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const drawerWidth = 240;

interface NavItem {
  title: string;
  href: string;
  icon: React.ElementType;
}

const navigation: NavItem[] = [
  { title: 'Dashboard', href: '/', icon: Home },
  { title: 'Samples', href: '/samples', icon: Music },
  { title: 'Collections', href: '/collections', icon: FolderOpen },
  { title: 'Kits', href: '/kits', icon: Grid3x3 },
  { title: 'Batches', href: '/batches', icon: Layers },
  { title: 'Upload', href: '/upload', icon: Upload },
  { title: 'Usage', href: '/usage', icon: DollarSign },
  { title: 'Settings', href: '/settings', icon: Settings },
];

interface MuiDrawerProps {
  open: boolean;
  onClose: () => void;
  variant?: 'temporary' | 'permanent' | 'persistent';
}

export function MuiDrawer({ open, onClose, variant = 'permanent' }: MuiDrawerProps) {
  const location = useLocation();

  const isActive = (href: string) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  const drawerContent = (
    <>
      {/* Drawer Header */}
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: 2,
            bgcolor: 'primary.main',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'primary.contrastText',
          }}
        >
          <Music size={20} />
        </Box>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
            SP-404
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Sample Manager
          </Typography>
        </Box>
      </Box>

      <Divider />

      {/* Navigation List */}
      <List sx={{ pt: 2 }}>
        {navigation.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <ListItem key={item.href} disablePadding sx={{ px: 1 }}>
              <ListItemButton
                component={Link}
                to={item.href}
                selected={active}
                sx={{
                  borderRadius: 2,
                  mb: 0.5,
                  '&.Mui-selected': {
                    bgcolor: 'action.selected',
                    color: 'primary.main',
                    '& .MuiListItemIcon-root': {
                      color: 'primary.main',
                    },
                    '&:hover': {
                      bgcolor: 'action.selected',
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <Icon size={20} />
                </ListItemIcon>
                <ListItemText primary={item.title} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </>
  );

  return (
    <Drawer
      variant={variant}
      open={open}
      onClose={onClose}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          bgcolor: 'background.paper',
          borderRight: '1px solid',
          borderColor: 'divider',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
}
```

**Validation**:
```bash
# Test drawer in isolation
npm run dev
# Create test page to render drawer
# Verify:
# - Drawer renders at 240px width
# - Navigation items are clickable
# - Active state highlights correctly (cyan)
# - Icons and text are visible
```

### Step 4.3: Build App Bar Component (2 hours)

Create the top navigation bar.

**Create MUI App Bar** (`src/components/layout/MuiAppBar.tsx`):

```typescript
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Box,
  Breadcrumbs,
  Link as MuiLink,
} from '@mui/material';
import { Menu, Home } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { MuiThemeSwitcher } from '../MuiThemeSwitcher';

const drawerWidth = 240;

interface MuiAppBarProps {
  onMenuClick: () => void;
  open: boolean;
}

export function MuiAppBar({ onMenuClick, open }: MuiAppBarProps) {
  const location = useLocation();

  // Generate breadcrumbs from pathname
  const pathnames = location.pathname.split('/').filter((x) => x);

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        bgcolor: 'background.paper',
        color: 'text.primary',
        boxShadow: 1,
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Toolbar>
        {/* Menu Toggle */}
        <IconButton
          color="inherit"
          aria-label="open drawer"
          onClick={onMenuClick}
          edge="start"
          sx={{ mr: 2, display: { md: 'none' } }}
        >
          <Menu size={20} />
        </IconButton>

        {/* Breadcrumbs */}
        <Breadcrumbs aria-label="breadcrumb" sx={{ flexGrow: 1 }}>
          <MuiLink
            component={Link}
            to="/"
            underline="hover"
            color="inherit"
            sx={{ display: 'flex', alignItems: 'center' }}
          >
            <Home size={16} style={{ marginRight: 4 }} />
            Dashboard
          </MuiLink>
          {pathnames.map((value, index) => {
            const to = `/${pathnames.slice(0, index + 1).join('/')}`;
            const isLast = index === pathnames.length - 1;
            const label = value.charAt(0).toUpperCase() + value.slice(1);

            return isLast ? (
              <Typography key={to} color="text.primary">
                {label}
              </Typography>
            ) : (
              <MuiLink
                key={to}
                component={Link}
                to={to}
                underline="hover"
                color="inherit"
              >
                {label}
              </MuiLink>
            );
          })}
        </Breadcrumbs>

        {/* Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <MuiThemeSwitcher />
        </Box>
      </Toolbar>
    </AppBar>
  );
}
```

**Validation**:
- ✅ App bar renders at top
- ✅ Menu button shows on mobile
- ✅ Breadcrumbs generate correctly
- ✅ Theme switcher functional

### Step 4.4: Combine into AppShell Layout (1 hour)

Create the complete layout component.

**Create MUI AppShell** (`src/components/layout/MuiAppShell.tsx`):

```typescript
import { useState } from 'react';
import { Box, Toolbar } from '@mui/material';
import { MuiDrawer } from './MuiDrawer';
import { MuiAppBar } from './MuiAppBar';

interface MuiAppShellProps {
  children: React.ReactNode;
}

export function MuiAppShell({ children }: MuiAppShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <MuiAppBar onMenuClick={handleDrawerToggle} open={mobileOpen} />

      {/* Drawer - Mobile (temporary) */}
      <Box sx={{ display: { xs: 'block', md: 'none' } }}>
        <MuiDrawer
          open={mobileOpen}
          onClose={handleDrawerToggle}
          variant="temporary"
        />
      </Box>

      {/* Drawer - Desktop (permanent) */}
      <Box sx={{ display: { xs: 'none', md: 'block' } }}>
        <MuiDrawer open={true} onClose={() => {}} variant="permanent" />
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { xs: '100%', md: `calc(100% - 240px)` },
        }}
      >
        <Toolbar /> {/* Spacer for fixed app bar */}
        {children}
      </Box>
    </Box>
  );
}
```

**Validation**:
```bash
# Replace AppShell in App.tsx temporarily
import { MuiAppShell } from './components/layout/MuiAppShell';

# Run dev server
npm run dev

# Test:
# - Mobile: Menu button shows, drawer slides in
# - Desktop: Permanent drawer, no menu button
# - Navigation: Clicking items navigates correctly
# - Breadcrumbs: Update on navigation
```

### Step 4.5: Add Responsive Behavior (1 hour)

Implement advanced responsive features.

**Enhance MuiDrawer with Mini Variant**:

```typescript
// Add mini variant for tablet sizes
<Drawer
  variant={variant}
  open={open}
  onClose={onClose}
  sx={{
    width: open ? drawerWidth : 56,
    flexShrink: 0,
    '& .MuiDrawer-paper': {
      width: open ? drawerWidth : 56,
      overflowX: 'hidden',
      transition: (theme) =>
        theme.transitions.create('width', {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
    },
  }}
>
  {drawerContent}
</Drawer>
```

**Add Collapse Toggle Button**:

```typescript
// In MuiDrawer.tsx, add toggle button
<IconButton onClick={onToggle} sx={{ alignSelf: 'flex-end', mr: 1 }}>
  {open ? <ChevronLeft /> : <ChevronRight />}
</IconButton>
```

**Validation**:
- ✅ Drawer collapses to 56px on tablet
- ✅ Icons remain visible when collapsed
- ✅ Smooth transition animation
- ✅ Toggle button works

**Time Estimate**: 7 hours (1hr + 2hr + 2hr + 1hr + 1hr)

---

## TASK 5: Setup Testing Infrastructure (E2E)

**Duration**: 7 hours
**Complexity**: Medium
**Prerequisites**: Tasks 1-4 complete

### Objective
Install and configure Playwright for end-to-end testing of Material-UI components and user workflows.

### Step 5.1: Install Playwright (1 hour)

```bash
# Navigate to react-app
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app

# Install Playwright
npm install --save-dev @playwright/test@^1.52.0

# Install browsers
npx playwright install chromium webkit firefox

# Verify installation
npx playwright --version
# Should show: Version 1.52.0
```

**Create Playwright Config** (`playwright.config.ts`):

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

**Validation**:
```bash
# Run sample test
npx playwright test --project=chromium
# Should complete without errors
```

### Step 5.2: Create Test Utilities (1 hour)

Build reusable test helpers.

**Create Test Helpers** (`e2e/helpers.ts`):

```typescript
import { Page, expect } from '@playwright/test';

export async function loginAsTestUser(page: Page) {
  // Future: Implement authentication
  await page.goto('/');
}

export async function navigateTo(page: Page, route: string) {
  await page.goto(route);
  await page.waitForLoadState('networkidle');
}

export async function clickNavItem(page: Page, label: string) {
  await page.click(`nav >> text="${label}"`);
  await page.waitForLoadState('networkidle');
}

export async function waitForMuiComponent(page: Page, selector: string) {
  await page.waitForSelector(selector, { state: 'visible' });
}

export async function verifyMuiTheme(page: Page) {
  // Check that MUI theme is applied
  const bgColor = await page.evaluate(() => {
    return window.getComputedStyle(document.body).backgroundColor;
  });
  expect(bgColor).toContain('19, 21, 26'); // RGB of #13151A
}
```

**Validation**:
- ✅ Helper functions defined
- ✅ Type-safe with TypeScript

### Step 5.3: Write Layout Tests (2 hours)

Test AppShell responsive behavior.

**Create Layout Tests** (`e2e/layout.spec.ts`):

```typescript
import { test, expect } from '@playwright/test';
import { navigateTo, verifyMuiTheme } from './helpers';

test.describe('AppShell Layout', () => {
  test('should render drawer on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1200, height: 800 });
    await navigateTo(page, '/');

    // Drawer should be visible
    const drawer = page.locator('[role="navigation"]');
    await expect(drawer).toBeVisible();

    // Should have width of 240px
    const drawerBox = await drawer.boundingBox();
    expect(drawerBox?.width).toBe(240);
  });

  test('should hide drawer on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await navigateTo(page, '/');

    // Drawer should be hidden initially
    const drawer = page.locator('[role="navigation"]');
    await expect(drawer).not.toBeVisible();

    // Menu button should be visible
    const menuButton = page.locator('[aria-label="open drawer"]');
    await expect(menuButton).toBeVisible();
  });

  test('should toggle drawer on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await navigateTo(page, '/');

    // Click menu button
    const menuButton = page.locator('[aria-label="open drawer"]');
    await menuButton.click();

    // Drawer should slide in
    const drawer = page.locator('[role="navigation"]');
    await expect(drawer).toBeVisible();

    // Click outside to close
    await page.click('body', { position: { x: 350, y: 100 } });
    await expect(drawer).not.toBeVisible();
  });

  test('should highlight active nav item', async ({ page }) => {
    await navigateTo(page, '/samples');

    // "Samples" nav item should have active styling
    const samplesNav = page.locator('nav >> text="Samples"');
    await expect(samplesNav).toHaveClass(/Mui-selected/);
  });

  test('should update breadcrumbs on navigation', async ({ page }) => {
    await navigateTo(page, '/samples');

    // Breadcrumbs should show: Home > Samples
    const breadcrumbs = page.locator('[aria-label="breadcrumb"]');
    await expect(breadcrumbs).toContainText('Dashboard');
    await expect(breadcrumbs).toContainText('Samples');
  });

  test('should apply dark theme', async ({ page }) => {
    await navigateTo(page, '/');
    await verifyMuiTheme(page);

    // Check primary button color
    const button = page.locator('button:has-text("Primary")').first();
    const bgColor = await button.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    expect(bgColor).toContain('31, 199, 255'); // RGB of #1FC7FF
  });
});
```

**Validation**:
```bash
# Run layout tests
npx playwright test layout.spec.ts --project=chromium

# Check report
npx playwright show-report
```

### Step 5.4: Write Component Tests (2 hours)

Test Material-UI components.

**Create Component Tests** (`e2e/components.spec.ts`):

```typescript
import { test, expect } from '@playwright/test';
import { navigateTo } from './helpers';

test.describe('Material-UI Components', () => {
  test('should render primary button with cyan color', async ({ page }) => {
    await navigateTo(page, '/component-showcase');

    const button = page.locator('button:has-text("Primary")');
    await expect(button).toBeVisible();

    const bgColor = await button.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    expect(bgColor).toContain('31, 199, 255'); // #1FC7FF
  });

  test('should render secondary button with green color', async ({ page }) => {
    await navigateTo(page, '/component-showcase');

    const button = page.locator('button:has-text("Secondary")');
    await expect(button).toBeVisible();

    const bgColor = await button.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    expect(bgColor).toContain('21, 184, 87'); // #15B857
  });

  test('should render text field with proper styling', async ({ page }) => {
    await navigateTo(page, '/component-showcase');

    const textField = page.locator('input[aria-label="Sample Name"]');
    await expect(textField).toBeVisible();

    // Focus should apply cyan border
    await textField.focus();
    await page.waitForTimeout(300); // Wait for focus animation

    const input = textField.locator('..');
    const borderColor = await input.evaluate((el) => {
      return window.getComputedStyle(el).borderColor;
    });
    expect(borderColor).toContain('31, 199, 255'); // Cyan focus
  });

  test('should render card with paper background', async ({ page }) => {
    await navigateTo(page, '/component-showcase');

    const card = page.locator('.MuiCard-root').first();
    await expect(card).toBeVisible();

    const bgColor = await card.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    expect(bgColor).toContain('22, 24, 31'); // #16181F
  });

  test('should render alert with proper colors', async ({ page }) => {
    await navigateTo(page, '/component-showcase');

    const successAlert = page.locator('.MuiAlert-standardSuccess');
    await expect(successAlert).toBeVisible();
    await expect(successAlert).toContainText('Sample analyzed successfully');

    const errorAlert = page.locator('.MuiAlert-standardError');
    await expect(errorAlert).toBeVisible();
    await expect(errorAlert).toContainText('Failed to load audio file');
  });
});
```

**Validation**:
```bash
# Run component tests
npx playwright test components.spec.ts --project=chromium
npx playwright show-report
```

### Step 5.5: Setup CI Integration (1 hour)

Prepare tests for continuous integration.

**Create GitHub Actions Workflow** (`.github/workflows/playwright.yml`):

```yaml
name: Playwright Tests

on:
  push:
    branches: [main, feat/track-a-week1]
  pull_request:
    branches: [main]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - name: Install dependencies
        run: cd react-app && npm ci
      - name: Install Playwright Browsers
        run: cd react-app && npx playwright install --with-deps
      - name: Run Playwright tests
        run: cd react-app && npx playwright test
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: react-app/playwright-report/
          retention-days: 30
```

**Update package.json Scripts**:

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:report": "playwright show-report"
  }
}
```

**Validation**:
```bash
# Run all tests
npm run test:e2e

# Open interactive UI
npm run test:e2e:ui

# Generate report
npm run test:e2e:report
```

**Time Estimate**: 7 hours (1hr + 1hr + 2hr + 2hr + 1hr)

---

## DELIVERABLES CHECKLIST

### Task 1: Setup Modernize React Environment
- [ ] Material-UI v7 installed and configured
- [ ] MUI theme created with SP-404 cyan colors
- [ ] TypeScript paths configured
- [ ] Dev server runs without errors
- [ ] Documentation: SETUP_GUIDE.md

### Task 2: Component Catalog
- [ ] Existing components inventoried (63 components)
- [ ] Migration matrix created (25 components mapped)
- [ ] Component showcase page built
- [ ] API reference documented (15+ components)

### Task 3: Dark Mode Theme
- [ ] Color palette documented (OKLCH → Hex)
- [ ] MUI theme variables configured
- [ ] Theme switcher component created
- [ ] Accessibility validated (WCAG AA)
- [ ] Documentation: THEME_GUIDE.md

### Task 4: AppShell Layout
- [ ] MuiDrawer component built
- [ ] MuiAppBar component built
- [ ] MuiAppShell layout component built
- [ ] Responsive behavior implemented
- [ ] Mobile drawer functional

### Task 5: Testing Infrastructure
- [ ] Playwright installed and configured
- [ ] Test helpers created
- [ ] Layout tests written (5+ scenarios)
- [ ] Component tests written (5+ scenarios)
- [ ] CI workflow configured

---

## VALIDATION GATES

Before marking Week 1 complete, verify:

### Functional
- ✅ Dev server starts: `npm run dev` completes without errors
- ✅ MUI theme applied: Primary buttons are cyan (#1FC7FF)
- ✅ AppShell renders: Sidebar and app bar visible
- ✅ Navigation works: Clicking nav items changes routes
- ✅ Mobile responsive: Drawer slides in on mobile
- ✅ Tests pass: `npm run test:e2e` shows 10+ passing tests

### Code Quality
- ✅ TypeScript: No errors in `npm run build`
- ✅ Linting: No errors in `npm run lint`
- ✅ Components: Follow Material-UI patterns
- ✅ Theme: Uses SP-404 color tokens
- ✅ Accessibility: WCAG AA contrast ratios

### Documentation
- ✅ SETUP_GUIDE.md: Installation steps documented
- ✅ COMPONENT_INVENTORY.md: 15-20 components listed
- ✅ MIGRATION_MATRIX.md: Migration path defined
- ✅ THEME_GUIDE.md: Color usage documented
- ✅ CONTRAST_REPORT.md: Accessibility validated

### Integration
- ✅ Can connect to existing backend API
- ✅ React Query hooks work with FastAPI
- ✅ WebSocket connections functional
- ✅ Audio player components still work

---

## TIME TRACKING

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| Task 1: Setup | 6 hrs | | |
| Task 2: Catalog | 8 hrs | | |
| Task 3: Theme | 7 hrs | | |
| Task 4: AppShell | 7 hrs | | |
| Task 5: Testing | 7 hrs | | |
| **Total** | **35 hrs** | | |

---

## TROUBLESHOOTING

### Material-UI Theme Not Applied
**Issue**: Components render with default MUI theme
**Solution**:
1. Verify `MuiThemeProvider` wraps `App`
2. Check `darkTheme` is imported correctly
3. Inspect browser DevTools for theme class names

### TypeScript Path Errors
**Issue**: Cannot resolve `@/components/*`
**Solution**:
1. Check `tsconfig.app.json` has correct `paths`
2. Restart TypeScript server in VS Code
3. Run `npm run build` to verify

### Playwright Tests Fail
**Issue**: Tests timeout or elements not found
**Solution**:
1. Ensure dev server is running
2. Increase timeout in `playwright.config.ts`
3. Add `await page.waitForLoadState('networkidle')`

### Drawer Not Responsive
**Issue**: Drawer doesn't collapse on mobile
**Solution**:
1. Check breakpoint in `sx={{ display: { xs: 'block', md: 'none' } }}`
2. Verify viewport size in browser DevTools
3. Test with Playwright mobile devices

---

## NEXT STEPS (Week 2)

After Week 1 completion:
1. Migrate 10+ shadcn/ui components to Material-UI
2. Implement sample library browser with DataGrid
3. Build authentication UI components
4. Add 20+ E2E test scenarios
5. Optimize bundle size and lazy loading

**Track B Integration**: Connect to staging API server deployed by Track B.
