# Track A - Week 1: UI/UX Development

**Developer Role:** React/TypeScript specialist
**Total Hours:** 35 hours (7 hours/day × 5 days)
**Tech Stack:** React 19, Material-UI v7, Tailwind CSS, TypeScript, Playwright

---

## Task 1: Setup Modernize React Environment (6 hours)
**Monday Morning**

### Objectives
- Install Modernize React TypeScript kit
- Configure Material-UI v7
- Setup dark mode theme
- Validate component library

### Steps

```bash
# 1. Clone Modernize React
git clone https://github.com/codedthemes/modernize-react.git modernize-base
cd modernize-base

# 2. Install dependencies
npm install

# 3. Start dev server (verify it works)
npm run dev
# Expected: http://localhost:5173 opens with Material-UI dashboard

# 4. Explore component structure
ls -la src/components/
# Should show: common/, dashboard/, forms/, layouts/, etc.

# 5. Check Material-UI version
npm list @mui/material
# Should be >= 7.0.0
```

### Configuration

Create `src/theme/darkTheme.ts`:
```typescript
import { createTheme } from '@mui/material/styles';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1FC7FF', // SP-404 cyan
      light: '#4DD9FF',
      dark: '#0099CC',
    },
    secondary: {
      main: '#FF006E',
    },
    background: {
      default: '#0D1117',
      paper: '#161B22',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2.5rem', fontWeight: 700 },
  },
});

export default darkTheme;
```

### Validation Checklist
- ✅ Dev server runs without errors
- ✅ Material-UI v7 installed and loading
- ✅ Dark theme applies globally
- ✅ SP-404 cyan color renders correctly
- ✅ Component library accessible
- ✅ TypeScript strict mode enabled

### Expected Deliverable
- Modernize React configured in `saas-frontend/` directory
- Dark theme applied and verified
- All 770+ Material-UI components available

---

## Task 2: Create Component Catalog (8 hours)
**Monday Afternoon → Tuesday Morning**

### Objectives
- Map Modernize React components to SP-404 features
- Document 15-20 core components
- Create component showcase/storybook
- Ensure type safety

### SP-404 Feature → Component Mapping

| SP-404 Feature | Material-UI Components | Path |
|---|---|---|
| Authentication | TextField, Button, Card | pages/Auth/ |
| Sample List | Table, Avatar, Chip | components/SampleTable/ |
| Sample Upload | FileInput, LinearProgress | components/Upload/ |
| Collections | Accordion, List, Drawer | components/Collections/ |
| Billing | Card, Table, Dialog | pages/Billing/ |
| Settings | Form, Tabs, Switch | pages/Settings/ |

### Component Showcase

Create `src/components/ComponentShowcase.tsx`:
```typescript
import { Box, Paper, Typography, Button, TextField, Card } from '@mui/material';

export function ComponentShowcase() {
  return (
    <Box sx={{ p: 4, bgcolor: 'background.default', minHeight: '100vh' }}>
      <Typography variant="h1" sx={{ mb: 4, color: 'primary.main' }}>
        Component Catalog
      </Typography>

      {/* Input Components */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h3" sx={{ mb: 2 }}>Inputs</Typography>
        <TextField label="Sample Name" variant="outlined" sx={{ mr: 2 }} />
        <TextField label="Description" multiline rows={4} variant="outlined" />
      </Paper>

      {/* Button Components */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h3" sx={{ mb: 2 }}>Buttons</Typography>
        <Button variant="contained" sx={{ mr: 2 }}>Primary</Button>
        <Button variant="outlined">Secondary</Button>
      </Paper>

      {/* Card Components */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h3" sx={{ mb: 2 }}>Cards</Typography>
        <Card sx={{ p: 2 }}>Sample Card Content</Card>
      </Paper>
    </Box>
  );
}
```

### Validation Checklist
- ✅ 15-20 components documented with examples
- ✅ All components work with dark theme
- ✅ TypeScript types exported and available
- ✅ Component props documented
- ✅ Accessibility (a11y) checked
- ✅ WCAG AA color contrast verified

### Expected Deliverable
- Component catalog with 50+ documented components
- Usage examples for each
- Storybook or showcase page

---

## Task 3: Design Dark Mode Theme (7 hours)
**Tuesday Afternoon**

### Objectives
- Configure Material-UI dark theme
- Verify WCAG AA compliance
- Create theme customization guide
- Test all components in dark mode

### Color Palette

```typescript
const colors = {
  primary: '#1FC7FF',      // SP-404 cyan
  primaryLight: '#4DD9FF',
  primaryDark: '#0099CC',
  secondary: '#FF006E',    // SP-404 pink
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  background: '#0D1117',
  surface: '#161B22',
  text: '#E6EAEF',
  textSecondary: '#8B949E',
};
```

### Theme Configuration

Update `src/theme/index.ts`:
```typescript
export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: colors.primary, light: colors.primaryLight },
    secondary: { main: colors.secondary },
    background: { default: colors.background, paper: colors.surface },
    text: {
      primary: colors.text,
      secondary: colors.textSecondary,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '8px',
        },
        contained: {
          background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryDark})`,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: colors.surface,
          backgroundImage: 'none',
        },
      },
    },
  },
});
```

### Accessibility Testing

```bash
# Install accessibility checker
npm install --save-dev @axe-core/react

# Test component accessibility
npm run test:a11y

# Verify color contrast
# Use WebAIM: https://webaim.org/resources/contrastchecker/
# Primary (#1FC7FF) on background (#0D1117): 10.5:1 ✅
# Text (#E6EAEF) on background (#0D1117): 15.1:1 ✅
```

### Validation Checklist
- ✅ Dark theme applies to all components
- ✅ Text contrast meets WCAG AA (4.5:1 minimum)
- ✅ Interactive elements have :focus styles
- ✅ No hard-coded colors (all use theme)
- ✅ Theme switching works (if light mode needed)
- ✅ No broken components in dark mode

### Expected Deliverable
- Complete Material-UI dark theme
- All components tested and working
- Accessibility audit passed

---

## Task 4: Create AppShell Layout (7 hours)
**Wednesday Morning**

### Objectives
- Build responsive AppShell component
- Implement navigation drawer
- Create responsive layout system
- Setup routing structure

### AppShell Structure

Create `src/components/layout/AppShell.tsx`:
```typescript
import { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Breadcrumbs,
  Container,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';

export function AppShell({ children }: { children: React.ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  const toggleDrawer = () => setDrawerOpen(!drawerOpen);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton onClick={toggleDrawer} edge="start" color="inherit">
            {drawerOpen ? <CloseIcon /> : <MenuIcon />}
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1, ml: 2 }}>
            SP-404 SaaS
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={toggleDrawer}
        sx={{
          width: 280,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 280,
            marginTop: '64px',
          },
        }}
      >
        {/* Navigation Items */}
        <Box sx={{ p: 2 }}>
          <Typography variant="h6">Menu</Typography>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: '64px' }}>
        <Container maxWidth="lg">
          <Breadcrumbs sx={{ mb: 3 }}>
            {/* Breadcrumb items */}
          </Breadcrumbs>
          {children}
        </Container>
      </Box>
    </Box>
  );
}
```

### Layout Features
- ✅ Responsive drawer (mobile/desktop)
- ✅ App bar with branding
- ✅ Breadcrumb navigation
- ✅ Main content area with padding
- ✅ Footer (optional)

### Validation Checklist
- ✅ Mobile: Drawer collapses, hamburger menu shows
- ✅ Desktop: Drawer visible, full navigation
- ✅ Responsive: Tested at 320px, 768px, 1920px widths
- ✅ Navigation functional (routing works)
- ✅ Accessible: ARIA labels present
- ✅ Dark mode: Theme applied correctly

### Expected Deliverable
- AppShell component integrated into app
- Responsive navigation working
- Routing structure in place

---

## Task 5: Setup Testing Infrastructure (7 hours)
**Thursday → Friday Morning**

### Objectives
- Install Playwright E2E testing
- Create 10+ test scenarios
- Setup CI/CD for automated testing
- Ensure test coverage

### Playwright Setup

```bash
# 1. Install Playwright
npm install -D @playwright/test

# 2. Create test configuration
npx playwright install

# 3. Create first test
mkdir tests
touch tests/sample.spec.ts
```

### Test Examples

Create `tests/sample.spec.ts`:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Sample Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should display sample list', async ({ page }) => {
    const sampleTable = page.locator('table');
    await expect(sampleTable).toBeVisible();

    const rows = page.locator('tbody tr');
    expect(await rows.count()).toBeGreaterThan(0);
  });

  test('should open sample details on click', async ({ page }) => {
    const firstSample = page.locator('tbody tr').first();
    await firstSample.click();

    const detailsModal = page.locator('[role="dialog"]');
    await expect(detailsModal).toBeVisible();
  });

  test('should upload new sample', async ({ page }) => {
    await page.click('button:has-text("Upload")');

    const uploadInput = page.locator('input[type="file"]');
    await uploadInput.setInputFiles('test-audio.wav');

    await page.click('button:has-text("Upload")');

    const success = page.locator('text=Upload successful');
    await expect(success).toBeVisible();
  });
});
```

### Run Tests

```bash
# Run all tests
npm run test

# Run with UI
npm run test:ui

# Run specific test
npm run test tests/sample.spec.ts

# Run in debug mode
npm run test:debug
```

### Validation Checklist
- ✅ 10+ test scenarios created
- ✅ All tests passing
- ✅ Test coverage > 80% for new components
- ✅ CI/CD pipeline configured (GitHub Actions)
- ✅ Mobile responsive tests passing
- ✅ Dark mode tests passing

### Expected Deliverable
- Automated test suite (10+ tests)
- CI/CD pipeline configured
- Test reports generated

---

## Daily Deliverables

| Day | Task | Deliverable |
|-----|------|------------|
| Mon | Task 1 | Modernize React running, dark theme applied |
| Tue | Task 2 | 20 components documented with examples |
| Wed | Task 3 | Dark theme finalized, accessibility verified |
| Wed | Task 4 | AppShell layout responsive and working |
| Thu-Fri | Task 5 | 10+ E2E tests passing, CI/CD ready |

---

## Integration with Track B

### Wednesday 12:00 PM
- Track B confirms backend health check
- You test CORS with backend

### Thursday 3:00 PM
- Track B provides API endpoints
- You create API client and test data loading

### Friday 3:00 PM
- Deploy React build to Track B VPS
- Run full E2E test through browser

---

## Success Criteria for Week 1

- ✅ Modernize React fully configured
- ✅ Material-UI v7 dark theme working
- ✅ 20+ components tested and documented
- ✅ AppShell responsive on all devices
- ✅ 10+ E2E tests passing
- ✅ TypeScript strict mode, zero errors
- ✅ WCAG AA accessibility compliant
- ✅ Ready for production deployment Friday

---

## Resources

- Modernize React: `modernize-react/docs/`
- Material-UI v7: https://mui.com/material-ui/
- Playwright: https://playwright.dev/docs/intro
- Component catalog in this doc above
