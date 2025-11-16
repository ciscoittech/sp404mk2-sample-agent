# React Sample Matching UI - Task Checklist

**Feature**: Production-Quality React + FastAPI Music Sample Matching Application
**Status**: Planning Complete
**Last Updated**: 2025-11-15

---

## 📋 WEEK 1: FOUNDATION & SETUP (20 hours)

### 1.1 Project Initialization (4 hours)
- [ ] Create Vite + React + TypeScript project
  - [ ] Configure path aliases (@/ for src)
  - [ ] Set up ESLint + Prettier
  - [ ] Configure Vitest for testing
- [ ] Install core dependencies
  - [ ] `npm install react-router-dom @tanstack/react-query`
  - [ ] `npm install axios zod framer-motion`
  - [ ] `npm install wavesurfer.js lucide-react`
- [ ] Set up folder structure (api, components, features, hooks, lib, pages, stores, types)
- [ ] Create npm scripts (dev, build, test, lint)

### 1.2 ShadCN UI Setup (4 hours)
- [ ] Install and configure ShadCN UI (`npx shadcn-ui@latest init`)
- [ ] Install essential components
  - [ ] Button, Card, Dialog, DropdownMenu
  - [ ] Input, Label, Select, Slider
  - [ ] Table, Tabs, Toast, Tooltip
  - [ ] Badge, Progress, Separator
- [ ] Configure Tailwind CSS with custom theme
- [ ] Set up Radix UI primitives

### 1.3 Design System Implementation (6 hours)
- [ ] Create custom color palette (NO purple gradients)
  - [ ] Background: `#13151A` (dark blue-gray)
  - [ ] Primary: `#1FC7FF` (bright cyan)
  - [ ] Accent: `#15B857` (vibrant green)
  - [ ] Define all color tokens in `globals.css`
- [ ] Define typography scale
  - [ ] Headings: Inter (weights: 400, 600, 700)
  - [ ] Body: Inter (weight: 400)
  - [ ] Mono: JetBrains Mono (technical data)
- [ ] Create spacing tokens (4px base unit)
- [ ] Define shadow system for depth
- [ ] Set up animation tokens (Framer Motion presets)

### 1.4 API Integration Layer (4 hours)
- [ ] Create axios instance with base configuration (`src/api/client.ts`)
- [ ] Implement API endpoint functions
  - [ ] `src/api/samples.ts` - Sample CRUD operations
  - [ ] `src/api/kits.ts` - Kit operations
  - [ ] `src/api/preferences.ts` - User preferences
- [ ] Set up React Query configuration
  - [ ] QueryClient with default options
  - [ ] 5-minute stale time for server state
- [ ] Create TypeScript types from API schemas
  - [ ] `src/types/api.ts` - Sample, Kit, AudioFeatures, UserPreferences

### 1.5 Development Workflow (2 hours)
- [ ] Configure Vite dev server with hot reload
- [ ] Set up proxy for API in `vite.config.ts`
  - [ ] `/api` → `http://127.0.0.1:8100`
  - [ ] `/ws` → `ws://127.0.0.1:8100` (WebSocket)
- [ ] Test connection to FastAPI backend
- [ ] Verify TypeScript compilation works

**Week 1 Checkpoint**: ✅ Dev environment running, design system implemented, API client ready

---

## 📋 WEEK 2: CORE COMPONENTS (35 hours)

### 2.1 Sample Library Interface (10 hours)

**SampleCard Component (3 hours)**
- [ ] Design card layout (waveform, title, BPM, key, tags)
- [ ] Implement hover effects (Framer Motion scale: 1.02)
- [ ] Add loading skeleton state
- [ ] Handle click to navigate to detail view
- [ ] Add "Add to Kit" button

**SampleGrid Component (3 hours)**
- [ ] Create responsive grid layout (4 cols desktop, 2-3 tablet, 1 mobile)
- [ ] Implement virtualization for large lists (react-virtual)
- [ ] Add empty state when no samples found
- [ ] Show loading state while fetching
- [ ] Handle pagination

**FilterPanel Component (4 hours)**
- [ ] Genre filter (multi-select dropdown)
- [ ] BPM range slider (dual thumb, 60-180 BPM)
- [ ] Musical key filter (select)
- [ ] Tag filter (searchable multi-select)
- [ ] Clear all filters button
- [ ] Show active filter count badge
- [ ] Persist filters in URL query params

### 2.2 Audio Player with Waveform (12 hours)

**WaveformVisualizer Component (6 hours)**
- [ ] Integrate wavesurfer.js
  - [ ] Create WaveSurfer instance
  - [ ] Configure waveColor, progressColor, height
- [ ] Add zoom controls (+/- buttons)
- [ ] Implement pan (drag to scroll)
- [ ] Show current playback position cursor
- [ ] Display time markers every 5 seconds
- [ ] Add region selection for loop points
- [ ] Handle destroy on unmount

**AudioControls Component (4 hours)**
- [ ] Play/Pause button with icon toggle
- [ ] Volume slider with mute toggle
- [ ] Playback speed selector (0.5x, 1x, 1.5x, 2x)
- [ ] Loop toggle button
- [ ] Time display (current / total duration)
- [ ] Keyboard shortcuts (Space, Left/Right arrows, Up/Down arrows)

**Global Audio Player (2 hours)**
- [ ] Create AudioContext provider
- [ ] Manage audio state (current sample, playback position, volume)
- [ ] Implement play queue management
- [ ] Handle auto-play next sample
- [ ] Show mini player in global header

### 2.3 Search and Upload (8 hours)

**SearchBar Component (3 hours)**
- [ ] Create debounced search input (300ms delay)
- [ ] Add search suggestions dropdown
- [ ] Show recent searches
- [ ] Clear search button
- [ ] Loading indicator during search

**UploadDropZone Component (5 hours)**
- [ ] Drag-and-drop area with hover state
- [ ] File browser fallback (click to browse)
- [ ] File validation (type: .wav/.mp3/.flac/.aiff/.m4a, size: <50MB, max 20 files)
- [ ] Show file preview list with thumbnails
- [ ] Upload progress bars for each file
- [ ] Error handling and retry logic
- [ ] Cancel upload button

### 2.4 Pagination and Layout (5 hours)

**Pagination Component (2 hours)**
- [ ] Page number buttons
- [ ] Previous/Next buttons
- [ ] Jump to page input
- [ ] Show total items and current range
- [ ] Items per page selector (20, 50, 100)

**Layout Components (3 hours)**
- [ ] Header with logo and navigation
- [ ] Sidebar for filters (collapsible on mobile)
- [ ] Footer with links and credits
- [ ] Breadcrumb navigation
- [ ] Mobile responsive navigation menu

**Week 2 Checkpoint**: ✅ Sample browsing functional, audio playback works, uploads succeed

---

## 📋 WEEK 3: ADVANCED FEATURES (35 hours)

### 3.1 Kit Builder Interface (15 hours)

**PadGrid Component (8 hours)**
- [ ] Create SP-404 pad layout grid (4 banks × 12 pads = 48 pads)
- [ ] Design Pad component
  - [ ] Props: bank (A/B/C/D), number (1-12), sample, onAssign, onRemove
  - [ ] Empty state (dotted border)
  - [ ] Assigned state (sample info + play button)
  - [ ] Playing state (animated border)
- [ ] Implement drag-and-drop
  - [ ] Drag sample from library to pad
  - [ ] Drag sample between pads
  - [ ] Visual drop zone indicator
- [ ] Add pad controls (play, remove, volume slider, pitch shift)

**KitHeader Component (3 hours)**
- [ ] Editable kit name (click to edit)
- [ ] Kit description textarea
- [ ] Save button with loading state
- [ ] Export button (downloads ZIP)
- [ ] Share button (public link)
- [ ] Delete kit button (with confirmation)

**SampleRecommendations Component (4 hours)**
- [ ] Fetch recommendations from API
- [ ] Display recommended samples (similar BPM, matching key, complementary genre)
- [ ] Show match score (percentage)
- [ ] One-click assign to empty pad
- [ ] Refresh recommendations button

### 3.2 Sample Matching Visualization (8 hours)

**MatchingVisualization Component (5 hours)**
- [ ] Create radar chart for audio features (Recharts)
  - [ ] BPM compatibility
  - [ ] Key harmony
  - [ ] Spectral similarity
  - [ ] Energy level
  - [ ] Genre match
- [ ] Add comparison mode (compare 2 samples)
- [ ] Show detailed breakdown on hover
- [ ] Animate chart on load (Framer Motion)

**SimilarSamples Component (3 hours)**
- [ ] Query API for similar samples
- [ ] Display similar samples grid (4 columns)
- [ ] Show similarity score badge
- [ ] Click to navigate to sample detail
- [ ] Add to kit quick action

### 3.3 Batch Processing UI (7 hours)

**BatchUploadManager (4 hours)**
- [ ] Create batch upload queue
  - [ ] Track status (pending, uploading, analyzing, complete, error)
  - [ ] Track progress per file
- [ ] Show overall progress (X/Y files complete)
- [ ] Individual file progress bars
- [ ] Pause/Resume batch upload
- [ ] Cancel individual or entire batch
- [ ] Auto-retry failed uploads (max 3 attempts)

**AnalysisQueueDisplay (3 hours)**
- [ ] Connect to WebSocket for real-time updates
- [ ] Show analysis status per sample (extracting features, running AI, complete)
- [ ] Display estimated time remaining
- [ ] Show analysis results as they complete
- [ ] Error handling with retry option

### 3.4 Advanced Audio Features (5 hours)

**SpectralGraph Component (3 hours)**
- [ ] Visualize spectral features (Recharts line chart)
  - [ ] Spectral centroid over time
  - [ ] Spectral rolloff
  - [ ] Spectral bandwidth
- [ ] Add zoom controls
- [ ] Show frequency ranges (bass, mid, treble)

**AudioFeaturesDisplay Component (2 hours)**
- [ ] BPM badge with confidence indicator
- [ ] Key badge with scale (major/minor)
- [ ] Duration display (mm:ss)
- [ ] Sample rate and bit depth
- [ ] Harmonic/percussive ratio visualization
- [ ] Energy level meter
- [ ] Genre tags with confidence scores

**Week 3 Checkpoint**: ✅ Kit builder functional, sample matching works, batch uploads succeed

---

## 📋 WEEK 4: INTEGRATION & POLISH (25 hours)

### 4.1 Complete API Integration (8 hours)

**Samples API Integration (3 hours)**
- [ ] Implement all sample endpoints
  - [ ] List samples with filters
  - [ ] Get sample details
  - [ ] Upload new sample
  - [ ] Download sample file
  - [ ] Delete sample
- [ ] Add error handling for each endpoint
- [ ] Implement retry logic for failed requests
- [ ] Add request/response logging

**Kits API Integration (3 hours)**
- [ ] Implement kit endpoints
  - [ ] List kits
  - [ ] Create kit
  - [ ] Update kit
  - [ ] Delete kit
  - [ ] Assign sample to pad
  - [ ] Remove sample from pad
  - [ ] Get recommendations
  - [ ] Export kit as ZIP
- [ ] Handle optimistic updates (cancel queries, snapshot, update, rollback on error)

**Preferences API Integration (2 hours)**
- [ ] Load user preferences on app init
- [ ] Update preferences endpoint
- [ ] Sync preferences across components
- [ ] Persist theme selection

### 4.2 WebSocket Real-Time Updates (5 hours)

**WebSocket Client (3 hours)**
- [ ] Create WebSocket hook
  - [ ] Connect to `ws://127.0.0.1:8100/ws`
  - [ ] Handle open, message, error, close events
- [ ] Handle reconnection on disconnect (exponential backoff)
- [ ] Implement message queue for offline messages

**Real-Time Analysis Updates (2 hours)**
- [ ] Listen for analysis progress updates
- [ ] Update UI in real-time (progress bars)
- [ ] Show toast notification on completion
- [ ] Handle analysis errors

### 4.3 Performance Optimization (6 hours)

**Code Splitting (2 hours)**
- [ ] Implement lazy loading for routes (React.lazy)
- [ ] Split large components
- [ ] Analyze bundle size (vite-plugin-bundle-visualizer)
- [ ] Optimize imports (tree shaking)

**Audio Performance (2 hours)**
- [ ] Implement audio file streaming for large files
- [ ] Cache decoded audio buffers
- [ ] Prefetch next sample in queue
- [ ] Use Web Workers for waveform rendering

**Rendering Optimization (2 hours)**
- [ ] Memoize expensive components (React.memo)
- [ ] Virtualize long lists (react-virtual)
- [ ] Debounce filter changes
- [ ] Optimize re-renders with React DevTools

### 4.4 Accessibility & UX Polish (6 hours)

**Keyboard Navigation (2 hours)**
- [ ] Add keyboard shortcuts (/, Esc, Tab, Arrow keys)
- [ ] Show keyboard shortcut hints (tooltip on hover)
- [ ] Create keyboard shortcuts help modal

**ARIA Labels (2 hours)**
- [ ] Add proper ARIA labels to all interactive elements
- [ ] Use semantic HTML (nav, main, aside, section)
- [ ] Add skip navigation links
- [ ] Ensure focus indicators are visible

**Loading & Error States (2 hours)**
- [ ] Create consistent loading skeletons
- [ ] Implement error boundaries
- [ ] Add toast notifications for user actions
- [ ] Show helpful error messages

**Week 4 Checkpoint**: ✅ All features integrated, performance targets met, polish complete

---

## 📋 WEEKS 5-6: TESTING & DEPLOYMENT (20 hours)

### 5.1 E2E Testing with Playwright (8 hours)

**Sample Browser Tests (3 hours)**
- [ ] Test sample listing (loads 20 samples)
- [ ] Test search functionality
- [ ] Test filters (genre, BPM, key, tags)
- [ ] Test pagination
- [ ] Test sample detail navigation

**Kit Builder Tests (3 hours)**
- [ ] Test kit creation
- [ ] Test drag-and-drop sample assignment
- [ ] Test pad removal
- [ ] Test kit export
- [ ] Test recommendations display

**Audio Tests (2 hours)**
- [ ] Test audio playback start/stop
- [ ] Test volume controls
- [ ] Test waveform interaction
- [ ] Test keyboard shortcuts

### 5.2 Audio Functionality Testing (4 hours)

**Manual Audio Tests (2 hours)**
- [ ] Test playback across browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test different audio formats (WAV, MP3, FLAC, AIFF)
- [ ] Test large files (>10MB)
- [ ] Test rapid play/pause/seek operations

**Waveform Rendering Tests (2 hours)**
- [ ] Test waveform accuracy against reference
- [ ] Test zoom performance (1x to 10x)
- [ ] Test pan smoothness
- [ ] Test responsiveness (window resize)

### 5.3 Performance Benchmarking (4 hours)

**Load Time Tests (2 hours)**
- [ ] Measure initial page load (<2s target)
  - [ ] Run Lighthouse (`npx lighthouse http://localhost:5173 --view`)
- [ ] Test with throttled network (3G, 4G)
- [ ] Measure Time to Interactive (TTI)
- [ ] Measure Largest Contentful Paint (LCP)

**Runtime Performance (2 hours)**
- [ ] Test sample grid scroll performance (60fps)
- [ ] Test audio playback CPU usage (<10%)
- [ ] Test memory usage during long sessions
- [ ] Profile with Chrome DevTools Performance tab

### 5.4 Production Deployment (4 hours)

**Build Configuration (1 hour)**
- [ ] Configure production build (vite.config.ts)
  - [ ] Target: es2020
  - [ ] Minify: terser
  - [ ] Sourcemap: true
  - [ ] Manual chunks (vendor, ui, audio)
- [ ] Enable Brotli compression
- [ ] Set cache headers for static assets

**Docker Deployment (2 hours)**
- [ ] Create multi-stage Dockerfile (Node builder + nginx)
- [ ] Configure nginx for SPA routing
- [ ] Set up Docker Compose with backend
- [ ] Test Docker build locally

**Monitoring & Logging (1 hour)**
- [ ] Set up error tracking (Sentry)
- [ ] Configure analytics (Plausible or similar)
- [ ] Set up performance monitoring
- [ ] Create health check endpoint

**Weeks 5-6 Checkpoint**: ✅ 90%+ test coverage, performance meets targets, production deployed

---

## 📊 PROGRESS TRACKER

**Overall Progress**: 0/135 hours (0%)

### By Phase
- [ ] Week 1: Foundation (0/20 hours) - 0%
- [ ] Week 2: Core Components (0/35 hours) - 0%
- [ ] Week 3: Advanced Features (0/35 hours) - 0%
- [ ] Week 4: Integration & Polish (0/25 hours) - 0%
- [ ] Weeks 5-6: Testing & Deployment (0/20 hours) - 0%

### Success Metrics Status
- [ ] Audio Functionality: 0/4 points
- [ ] Visual Polish: 0/3 points
- [ ] Performance: 0/3 points
- [ ] Integration: 0/2 points

**Target**: 10/12 minimum for production quality
**Current**: 0/12

---

## 🎯 NEXT IMMEDIATE TASKS

1. [ ] Initialize Vite + React + TypeScript project
2. [ ] Install ShadCN UI and configure custom theme
3. [ ] Create API client layer
4. [ ] Define TypeScript types from backend models
5. [ ] Set up folder structure

---

**Task List Version**: 1.0
**Last Updated**: 2025-11-15
**Status**: Ready to begin Week 1 implementation
