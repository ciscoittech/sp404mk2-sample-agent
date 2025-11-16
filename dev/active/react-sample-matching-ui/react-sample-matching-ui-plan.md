# SP-404MK2 Sample Matching Application - Implementation Plan

**Project**: Production-Quality React + FastAPI Music Sample Matching Application
**Version**: 1.0
**Date**: 2025-11-15
**Estimated Duration**: 4-6 weeks (120-150 hours)
**Author**: Strategic Plan Architect Agent

---

## 1. EXECUTIVE SUMMARY

### 1.1 Project Overview

This plan outlines the development of a professional-grade music production application that enables producers to discover, analyze, match, and organize audio samples for the Roland SP-404MK2. The application combines a modern React frontend with an existing FastAPI backend to create a polished, production-ready tool that meets professional music production UI/UX standards.

### 1.2 Key Objectives

1. **Professional UI/UX**: Create a music production-grade interface inspired by industry tools like Splice, Ableton, and modern DAWs
2. **Real Audio Integration**: Implement waveform visualization, sample playback, and audio feature display
3. **Sample Matching Intelligence**: Build intelligent sample discovery and kit assembly tools
4. **Performance Excellence**: Achieve fast load times (<2s), smooth animations (60fps), and efficient audio handling
5. **Production Ready**: Deliver a polished, accessible, cross-browser compatible application

### 1.3 Success Metrics

**Audio Functionality (4 points)**
- Sample playback with transport controls
- Waveform visualization with zoom/pan
- Audio feature display (BPM, key, spectral data)
- Matching algorithm visualization

**Visual Polish (3 points)**
- Professional dark theme consistent with music production tools
- Smooth Framer Motion animations (60fps)
- Responsive design (desktop, tablet, mobile)

**Performance (3 points)**
- Initial load time <2 seconds
- Efficient audio file handling (streaming for large files)
- Responsive UI (interactions <100ms)

**Integration (2 points)**
- Reliable FastAPI communication
- Comprehensive error handling
- Real-time WebSocket updates

**Target**: 10/12 minimum for production quality

### 1.4 Timeline Estimate

- **Phase 1**: Foundation & Setup (Week 1) - 20 hours
- **Phase 2**: Core Components (Week 2) - 35 hours
- **Phase 3**: Advanced Features (Week 3) - 35 hours
- **Phase 4**: Integration & Polish (Week 4) - 25 hours
- **Phase 5**: Testing & Deployment (Weeks 5-6) - 20 hours

**Total**: 135 hours over 6 weeks

---

## 2. ARCHITECTURE DESIGN

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER (React)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Sample     │  │     Kit      │  │   Audio      │      │
│  │   Browser    │  │   Builder    │  │   Player     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │          State Management (React Query)             │     │
│  │  - Sample cache    - Kit cache    - Audio state    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │         API Client Layer (axios + WebSocket)        │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   API LAYER (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  REST Endpoints:                                             │
│  - GET  /api/v1/samples           (list, filter, search)    │
│  - POST /api/v1/samples           (upload)                  │
│  - GET  /api/v1/samples/{id}      (details)                 │
│  - GET  /api/v1/kits              (list kits)               │
│  - POST /api/v1/kits              (create kit)              │
│  - POST /api/v1/kits/{id}/assign  (assign sample to pad)    │
│  - GET  /api/v1/preferences       (user settings)           │
│                                                               │
│  WebSocket:                                                  │
│  - ws://127.0.0.1:8100/ws         (real-time analysis)      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  BUSINESS LOGIC LAYER                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  - AudioFeaturesService    (librosa analysis)               │
│  - HybridAnalysisService   (AI + audio analysis)            │
│  - KitService              (kit assembly logic)             │
│  - SampleService           (sample CRUD)                    │
│  - SP404ExportService      (hardware export)                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PostgreSQL Database:                                        │
│  - samples (2,328 rows)                                     │
│  - kits                                                      │
│  - kit_samples (pad assignments)                            │
│  - audio_features                                           │
│  - user_preferences                                         │
│                                                               │
│  File Storage:                                              │
│  - /samples     (audio files)                               │
│  - /downloads   (temporary uploads)                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Hierarchy (React)

```
App
├── Layout
│   ├── Header
│   │   ├── Logo
│   │   ├── Navigation
│   │   └── UserMenu
│   ├── Sidebar (optional)
│   └── Footer
│
├── Pages
│   ├── SampleBrowser
│   │   ├── SearchBar
│   │   ├── FilterPanel
│   │   │   ├── GenreFilter
│   │   │   ├── BPMRangeSlider
│   │   │   ├── KeyFilter
│   │   │   └── TagFilter
│   │   ├── SampleGrid
│   │   │   └── SampleCard[]
│   │   │       ├── Waveform (mini)
│   │   │       ├── PlayButton
│   │   │       ├── SampleInfo
│   │   │       └── AddToKitButton
│   │   └── Pagination
│   │
│   ├── SampleDetail
│   │   ├── WaveformViewer (full)
│   │   ├── AudioControls
│   │   │   ├── PlayPauseButton
│   │   │   ├── VolumeSlider
│   │   │   └── PlaybackSpeed
│   │   ├── AudioFeaturesDisplay
│   │   │   ├── BPMBadge
│   │   │   ├── KeyBadge
│   │   │   ├── SpectralGraph
│   │   │   └── HarmonicPercussiveRatio
│   │   ├── AIVibeAnalysis
│   │   │   ├── GenreTags
│   │   │   ├── MoodTags
│   │   │   └── DescriptionText
│   │   └── SimilarSamples
│   │
│   ├── KitBuilder
│   │   ├── KitHeader
│   │   │   ├── KitName (editable)
│   │   │   ├── SaveButton
│   │   │   └── ExportButton
│   │   ├── PadGrid (SP-404 layout)
│   │   │   └── Pad[] (12 pads × 4 banks = 48 pads)
│   │   │       ├── PadNumber
│   │   │       ├── AssignedSample
│   │   │       ├── PlayButton
│   │   │       └── RemoveButton
│   │   ├── SampleRecommendations
│   │   │   └── RecommendedSampleCard[]
│   │   └── BatchOperations
│   │       ├── ClearBankButton
│   │       └── AutoFillButton
│   │
│   ├── UploadSamples
│   │   ├── DropZone
│   │   ├── FileList
│   │   │   └── FilePreview[]
│   │   ├── UploadProgress
│   │   └── AnalysisQueue
│   │
│   └── Settings
│       ├── AIModelSelector
│       ├── AutoAnalysisToggle
│       └── ThemeSelector
│
└── Shared Components
    ├── AudioPlayer (global)
    ├── WaveformVisualizer
    ├── LoadingStates
    │   ├── SkeletonCard
    │   ├── ProgressSpinner
    │   └── ProgressBar
    ├── Modals
    │   ├── ConfirmDialog
    │   └── ErrorDialog
    └── Toast Notifications
```

### 2.3 API Integration Points

**Base URL**: `http://127.0.0.1:8100/api/v1`

#### Samples Endpoints
- `GET /samples` - List samples with pagination, filtering, search
  - Query params: `page`, `limit`, `search`, `genre`, `bpm_min`, `bpm_max`, `key`, `tags`
  - Returns: `{ items: Sample[], total: number, page: number, pages: number }`

- `POST /samples` - Upload new sample
  - Body: `FormData` with file, title, genre, bpm, key, tags
  - Returns: `Sample` with audio features

- `GET /samples/{id}` - Get sample details
  - Returns: Full `Sample` object with audio features and AI analysis

- `GET /samples/{id}/download` - Download sample file
  - Returns: Audio file stream

#### Kits Endpoints
- `GET /kits` - List kits
  - Query params: `skip`, `limit`
  - Returns: `{ items: Kit[], total: number }`

- `POST /kits` - Create new kit
  - Body: `{ name: string, description?: string }`
  - Returns: `Kit`

- `GET /kits/{id}` - Get kit details
  - Returns: `Kit` with pad assignments

- `POST /kits/{id}/assign` - Assign sample to pad
  - Body: `{ sample_id: number, pad_bank: string, pad_number: number }`
  - Returns: `PadAssignment`

- `GET /kits/{id}/recommendations` - Get sample recommendations
  - Returns: `{ recommendations: Sample[] }`

- `GET /kits/{id}/export` - Export kit as ZIP
  - Returns: ZIP file stream

#### Preferences Endpoints
- `GET /preferences` - Get user preferences
  - Returns: `{ ai_model: string, auto_analysis: boolean }`

- `PUT /preferences` - Update preferences
  - Body: `{ ai_model?: string, auto_analysis?: boolean }`
  - Returns: Updated preferences

#### WebSocket
- `ws://127.0.0.1:8100/ws` - Real-time analysis updates
  - Send: `{ action: 'analyze', sample_id: number }`
  - Receive: `{ status: 'analyzing' | 'complete', progress: number, result?: Analysis }`

### 2.4 Data Flow

**Sample Upload Flow**:
```
User → DropZone → FormData → POST /samples
  → Backend: Save file → Extract audio features → Queue AI analysis
  → WebSocket: Real-time progress → Update UI → Display results
```

**Sample Search Flow**:
```
User → SearchBar/Filters → React Query → GET /samples?filters
  → Backend: Query DB → Return paginated results
  → React Query: Cache → Render SampleGrid → Display cards
```

**Kit Building Flow**:
```
User → Drag sample to pad → POST /kits/{id}/assign
  → Backend: Validate pad availability → Save assignment
  → React Query: Invalidate cache → Refetch kit → Update PadGrid
```

**Audio Playback Flow**:
```
User → Click play → Fetch audio URL → Web Audio API
  → Decode audio → Create buffer → Start playback
  → Update waveform cursor → Show playback progress
```

### 2.5 State Management Strategy

**React Query** for server state:
- Sample list cache (5 min stale time)
- Kit list cache (5 min stale time)
- Sample details cache (10 min stale time)
- Optimistic updates for kit assignments
- Background refetching on window focus

**Zustand** for client state (if needed):
- Audio player state (current sample, playback position, volume)
- UI state (selected filters, view mode, theme)
- Upload queue state

**React Context** for:
- Theme provider
- Audio context provider

### 2.6 Audio Handling Architecture

**Web Audio API** for playback:
```typescript
interface AudioManager {
  load(url: string): Promise<AudioBuffer>
  play(buffer: AudioBuffer): void
  pause(): void
  resume(): void
  seek(position: number): void
  setVolume(level: number): void
  getPosition(): number
  onTimeUpdate(callback: (position: number) => void): void
}
```

**wavesurfer.js** for waveform visualization:
- Real-time rendering during playback
- Zoom and pan controls
- Region selection for loop points
- Peak data caching for performance

**File Upload Strategy**:
- Chunked uploads for files >10MB
- Client-side validation (file type, size)
- Progress tracking with cancellation
- Retry logic for failed uploads

---

## 3. PHASE BREAKDOWN

### PHASE 1: Foundation & Setup (Week 1 - 20 hours)

#### Objectives
- Initialize React project with professional tooling
- Configure ShadCN UI with custom design system
- Set up API integration layer
- Establish development workflow

#### Tasks

**1.1 Project Initialization (4 hours)**
- [ ] Create Vite + React + TypeScript project
  - Configure path aliases (@/ for src)
  - Set up ESLint + Prettier
  - Configure Vitest for testing
- [ ] Install core dependencies:
  ```bash
  npm install react-router-dom @tanstack/react-query
  npm install axios zod framer-motion
  npm install wavesurfer.js lucide-react
  ```
- [ ] Set up folder structure:
  ```
  src/
  ├── api/          # API client and endpoints
  ├── components/   # Reusable components
  ├── features/     # Feature-based modules
  ├── hooks/        # Custom React hooks
  ├── lib/          # Utilities and helpers
  ├── pages/        # Route pages
  ├── stores/       # State management
  ├── types/        # TypeScript types
  └── App.tsx
  ```

**1.2 ShadCN UI Setup (4 hours)**
- [ ] Install and configure ShadCN UI:
  ```bash
  npx shadcn-ui@latest init
  ```
- [ ] Install essential components:
  - Button, Card, Dialog, DropdownMenu
  - Input, Label, Select, Slider
  - Table, Tabs, Toast, Tooltip
  - Badge, Progress, Separator
- [ ] Configure Tailwind CSS with custom theme
- [ ] Set up Radix UI primitives

**1.3 Design System Implementation (6 hours)**
- [ ] Create custom color palette (NO purple gradients):
  ```css
  /* Professional music production theme */
  --background: 220 13% 8%;        /* Dark blue-gray */
  --foreground: 210 20% 98%;       /* Off-white */
  --primary: 198 93% 60%;          /* Bright cyan accent */
  --secondary: 217 33% 17%;        /* Darker blue-gray */
  --accent: 142 76% 36%;           /* Vibrant green */
  --destructive: 0 84% 60%;        /* Red */
  --muted: 217 33% 17%;            /* Muted backgrounds */
  --border: 217 33% 20%;           /* Subtle borders */
  ```
- [ ] Define typography scale:
  - Headings: Inter (weights: 400, 600, 700)
  - Body: Inter (weight: 400)
  - Mono: JetBrains Mono (for BPM, technical data)
- [ ] Create spacing tokens (4px base unit)
- [ ] Define shadow system for depth
- [ ] Set up animation tokens (Framer Motion presets)

**1.4 API Integration Layer (4 hours)**
- [ ] Create axios instance with base configuration:
  ```typescript
  // src/api/client.ts
  const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8100/api/v1',
    timeout: 30000,
  });
  ```
- [ ] Implement API endpoint functions:
  - `src/api/samples.ts` - Sample CRUD operations
  - `src/api/kits.ts` - Kit operations
  - `src/api/preferences.ts` - User preferences
- [ ] Set up React Query configuration:
  ```typescript
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000,  // 5 minutes
        retry: 1,
      },
    },
  });
  ```
- [ ] Create TypeScript types from API schemas:
  ```typescript
  // src/types/api.ts
  interface Sample {
    id: number;
    title: string;
    genre?: string;
    bpm?: number;
    musical_key?: string;
    tags: string[];
    duration?: number;
    file_path: string;
    audio_features?: AudioFeatures;
  }
  ```

**1.5 Development Workflow (2 hours)**
- [ ] Create npm scripts:
  ```json
  {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint . --ext ts,tsx"
  }
  ```
- [ ] Set up hot reload for development
- [ ] Configure proxy for API in `vite.config.ts`:
  ```typescript
  export default defineConfig({
    server: {
      proxy: {
        '/api': 'http://127.0.0.1:8100',
        '/ws': {
          target: 'ws://127.0.0.1:8100',
          ws: true,
        },
      },
    },
  });
  ```

#### Deliverables
- Working React development environment
- ShadCN UI configured with custom dark theme
- API client layer ready for integration
- TypeScript types for all API entities

---

### PHASE 2: Core Components (Week 2 - 35 hours)

#### Objectives
- Build primary UI components
- Implement sample browsing and playback
- Create audio player with waveform visualization
- Develop search and filter functionality

#### Tasks

**2.1 Sample Library Interface (10 hours)**

**SampleCard Component (3 hours)**
- [ ] Design card layout:
  - Waveform thumbnail (static image or mini canvas)
  - Sample title and duration
  - BPM and key badges
  - Play button overlay
  - Genre and tags
  - Add to kit button
- [ ] Implement hover effects (Framer Motion):
  ```tsx
  <motion.div
    whileHover={{ scale: 1.02 }}
    transition={{ duration: 0.2 }}
  >
  ```
- [ ] Add loading skeleton state
- [ ] Handle click to navigate to detail view

**SampleGrid Component (3 hours)**
- [ ] Create responsive grid layout:
  - Desktop: 4 columns
  - Tablet: 2-3 columns
  - Mobile: 1 column
- [ ] Implement virtualization for large lists (react-virtual)
- [ ] Add empty state when no samples
- [ ] Show loading state while fetching

**FilterPanel Component (4 hours)**
- [ ] Genre filter (multi-select dropdown)
- [ ] BPM range slider (dual thumb):
  ```tsx
  <Slider
    min={60}
    max={180}
    step={1}
    value={[bpmMin, bpmMax]}
    onValueChange={setBpmRange}
  />
  ```
- [ ] Musical key filter (select)
- [ ] Tag filter (searchable multi-select)
- [ ] Clear all filters button
- [ ] Show active filter count badge
- [ ] Persist filters in URL query params

**2.2 Audio Player with Waveform (12 hours)**

**WaveformVisualizer Component (6 hours)**
- [ ] Integrate wavesurfer.js:
  ```typescript
  import WaveSurfer from 'wavesurfer.js';

  useEffect(() => {
    const ws = WaveSurfer.create({
      container: containerRef.current,
      waveColor: '#4a5568',
      progressColor: '#3b82f6',
      height: 120,
      barWidth: 2,
      responsive: true,
    });

    ws.load(audioUrl);
    return () => ws.destroy();
  }, [audioUrl]);
  ```
- [ ] Add zoom controls (+/- buttons)
- [ ] Implement pan (drag to scroll)
- [ ] Show current playback position cursor
- [ ] Display time markers every 5 seconds
- [ ] Add region selection for loop points

**AudioControls Component (4 hours)**
- [ ] Play/Pause button with icon toggle
- [ ] Volume slider with mute toggle
- [ ] Playback speed selector (0.5x, 1x, 1.5x, 2x)
- [ ] Loop toggle button
- [ ] Time display (current / total duration)
- [ ] Keyboard shortcuts:
  - Space: Play/Pause
  - Left/Right arrows: Seek ±5s
  - Up/Down arrows: Volume ±10%

**Global Audio Player (2 hours)**
- [ ] Create AudioContext provider:
  ```tsx
  const AudioProvider = ({ children }) => {
    const [currentSample, setCurrentSample] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    // ... audio state and methods
  };
  ```
- [ ] Implement play queue management
- [ ] Handle auto-play next sample
- [ ] Show mini player in global header

**2.3 Search and Upload (8 hours)**

**SearchBar Component (3 hours)**
- [ ] Create debounced search input:
  ```tsx
  const debouncedSearch = useDebounce(searchTerm, 300);

  useEffect(() => {
    if (debouncedSearch) {
      fetchSamples({ search: debouncedSearch });
    }
  }, [debouncedSearch]);
  ```
- [ ] Add search suggestions dropdown
- [ ] Show recent searches
- [ ] Clear search button
- [ ] Loading indicator during search

**UploadDropZone Component (5 hours)**
- [ ] Drag-and-drop area with hover state
- [ ] File browser fallback (click to browse)
- [ ] File validation:
  - Allowed types: .wav, .mp3, .flac, .aiff, .m4a
  - Max size: 50MB per file
  - Max files: 20 per batch
- [ ] Show file preview list with thumbnails
- [ ] Upload progress bars for each file
- [ ] Error handling and retry
- [ ] Cancel upload button

**2.4 Pagination and Layout (5 hours)**

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

#### Deliverables
- Functional sample browsing interface
- Working audio player with waveform
- Search and filter system
- File upload with progress tracking

---

### PHASE 3: Advanced Features (Week 3 - 35 hours)

#### Objectives
- Build kit builder interface
- Implement sample matching visualization
- Add batch processing UI
- Create advanced audio controls

#### Tasks

**3.1 Kit Builder Interface (15 hours)**

**PadGrid Component (8 hours)**
- [ ] Create SP-404 pad layout grid:
  - 4 banks (A, B, C, D)
  - 12 pads per bank
  - Total: 48 pads
- [ ] Design pad component:
  ```tsx
  interface PadProps {
    bank: 'A' | 'B' | 'C' | 'D';
    number: 1-12;
    sample?: Sample;
    onAssign: (sample: Sample) => void;
    onRemove: () => void;
  }
  ```
- [ ] Implement drag-and-drop:
  - Drag sample from library to pad
  - Drag sample between pads
  - Visual drop zone indicator
- [ ] Show pad states:
  - Empty (dotted border)
  - Assigned (sample info + play button)
  - Playing (animated border)
- [ ] Add pad controls:
  - Play button
  - Remove button
  - Volume slider (per-pad)
  - Pitch shift controls

**KitHeader Component (3 hours)**
- [ ] Editable kit name (click to edit)
- [ ] Kit description textarea
- [ ] Save button with loading state
- [ ] Export button (downloads ZIP)
- [ ] Share button (public link)
- [ ] Delete kit button (with confirmation)

**SampleRecommendations Component (4 hours)**
- [ ] Fetch recommendations from API
- [ ] Display recommended samples:
  - Similar BPM
  - Matching key
  - Complementary genre
- [ ] Show match score (percentage)
- [ ] One-click assign to empty pad
- [ ] Refresh recommendations button

**3.2 Sample Matching Visualization (8 hours)**

**MatchingVisualization Component (5 hours)**
- [ ] Create radar chart for audio features:
  - BPM compatibility
  - Key harmony
  - Spectral similarity
  - Energy level
  - Genre match
- [ ] Use Recharts library:
  ```tsx
  import { Radar, RadarChart, PolarGrid, PolarAngleAxis } from 'recharts';

  const data = [
    { feature: 'BPM', value: 0.85 },
    { feature: 'Key', value: 0.92 },
    // ...
  ];
  ```
- [ ] Add comparison mode (compare 2 samples)
- [ ] Show detailed breakdown on hover
- [ ] Animate chart on load (Framer Motion)

**SimilarSamples Component (3 hours)**
- [ ] Query API for similar samples:
  ```typescript
  const { data: similar } = useQuery({
    queryKey: ['similar-samples', sampleId],
    queryFn: () => api.getSimilarSamples(sampleId),
  });
  ```
- [ ] Display similar samples grid (4 columns)
- [ ] Show similarity score badge
- [ ] Click to navigate to sample detail
- [ ] Add to kit quick action

**3.3 Batch Processing UI (7 hours)**

**BatchUploadManager (4 hours)**
- [ ] Create batch upload queue:
  ```typescript
  interface BatchItem {
    id: string;
    file: File;
    status: 'pending' | 'uploading' | 'analyzing' | 'complete' | 'error';
    progress: number;
    result?: Sample;
  }
  ```
- [ ] Show overall progress (X/Y files complete)
- [ ] Individual file progress bars
- [ ] Pause/Resume batch upload
- [ ] Cancel individual or entire batch
- [ ] Auto-retry failed uploads (max 3 attempts)

**AnalysisQueueDisplay (3 hours)**
- [ ] Connect to WebSocket for real-time updates
- [ ] Show analysis status per sample:
  - Extracting audio features...
  - Running AI analysis...
  - Complete
- [ ] Display estimated time remaining
- [ ] Show analysis results as they complete
- [ ] Error handling with retry option

**3.4 Advanced Audio Features (5 hours)**

**SpectralGraph Component (3 hours)**
- [ ] Visualize spectral features:
  - Spectral centroid over time
  - Spectral rolloff
  - Spectral bandwidth
- [ ] Use Recharts line chart
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

#### Deliverables
- Fully functional kit builder
- Sample matching visualization
- Batch upload and analysis system
- Advanced audio feature displays

---

### PHASE 4: Integration & Polish (Week 4 - 25 hours)

#### Objectives
- Complete FastAPI endpoint integration
- Implement real-time WebSocket updates
- Optimize performance
- Add accessibility improvements

#### Tasks

**4.1 Complete API Integration (8 hours)**

**Samples API Integration (3 hours)**
- [ ] Implement all sample endpoints:
  - List samples with filters
  - Get sample details
  - Upload new sample
  - Download sample file
  - Delete sample
- [ ] Add error handling for each endpoint
- [ ] Implement retry logic for failed requests
- [ ] Add request/response logging

**Kits API Integration (3 hours)**
- [ ] Implement kit endpoints:
  - List kits
  - Create kit
  - Update kit
  - Delete kit
  - Assign sample to pad
  - Remove sample from pad
  - Get recommendations
  - Export kit as ZIP
- [ ] Handle optimistic updates:
  ```typescript
  const mutation = useMutation({
    mutationFn: assignSampleToPad,
    onMutate: async (newAssignment) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries(['kit', kitId]);

      // Snapshot previous value
      const previousKit = queryClient.getQueryData(['kit', kitId]);

      // Optimistically update
      queryClient.setQueryData(['kit', kitId], (old) => ({
        ...old,
        samples: [...old.samples, newAssignment],
      }));

      return { previousKit };
    },
    onError: (err, newAssignment, context) => {
      // Rollback on error
      queryClient.setQueryData(['kit', kitId], context.previousKit);
    },
  });
  ```

**Preferences API Integration (2 hours)**
- [ ] Load user preferences on app init
- [ ] Update preferences endpoint
- [ ] Sync preferences across components
- [ ] Persist theme selection

**4.2 WebSocket Real-Time Updates (5 hours)**

**WebSocket Client (3 hours)**
- [ ] Create WebSocket hook:
  ```typescript
  const useWebSocket = (url: string) => {
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null);

    useEffect(() => {
      const ws = new WebSocket(url);

      ws.onopen = () => console.log('Connected');
      ws.onmessage = (event) => setLastMessage(event);
      ws.onerror = (error) => console.error('WebSocket error:', error);
      ws.onclose = () => console.log('Disconnected');

      setSocket(ws);

      return () => ws.close();
    }, [url]);

    return { socket, lastMessage };
  };
  ```
- [ ] Handle reconnection on disconnect
- [ ] Implement message queue for offline messages

**Real-Time Analysis Updates (2 hours)**
- [ ] Listen for analysis progress updates
- [ ] Update UI in real-time (progress bars)
- [ ] Show toast notification on completion
- [ ] Handle analysis errors

**4.3 Performance Optimization (6 hours)**

**Code Splitting (2 hours)**
- [ ] Implement lazy loading for routes:
  ```tsx
  const SampleBrowser = lazy(() => import('./pages/SampleBrowser'));
  const KitBuilder = lazy(() => import('./pages/KitBuilder'));
  ```
- [ ] Split large components
- [ ] Analyze bundle size (vite-plugin-bundle-visualizer)
- [ ] Optimize imports (tree shaking)

**Audio Performance (2 hours)**
- [ ] Implement audio file streaming for large files
- [ ] Cache decoded audio buffers
- [ ] Prefetch next sample in queue
- [ ] Use Web Workers for waveform rendering

**Rendering Optimization (2 hours)**
- [ ] Memoize expensive components:
  ```tsx
  const SampleCard = memo(({ sample }) => {
    // Component implementation
  }, (prevProps, nextProps) => {
    return prevProps.sample.id === nextProps.sample.id;
  });
  ```
- [ ] Virtualize long lists (react-virtual)
- [ ] Debounce filter changes
- [ ] Optimize re-renders with React DevTools

**4.4 Accessibility & UX Polish (6 hours)**

**Keyboard Navigation (2 hours)**
- [ ] Add keyboard shortcuts:
  - `/` to focus search
  - `Esc` to close modals
  - `Tab` navigation for all interactive elements
  - Arrow keys for pad grid navigation
- [ ] Show keyboard shortcut hints (tooltip on hover)
- [ ] Create keyboard shortcuts help modal

**ARIA Labels (2 hours)**
- [ ] Add proper ARIA labels to all interactive elements:
  ```tsx
  <button
    aria-label="Play sample"
    aria-pressed={isPlaying}
  >
  ```
- [ ] Use semantic HTML (nav, main, aside, section)
- [ ] Add skip navigation links
- [ ] Ensure focus indicators are visible

**Loading & Error States (2 hours)**
- [ ] Create consistent loading skeletons
- [ ] Implement error boundaries:
  ```tsx
  class ErrorBoundary extends Component {
    componentDidCatch(error, info) {
      // Log error to monitoring service
    }

    render() {
      if (this.state.hasError) {
        return <ErrorFallback />;
      }
      return this.props.children;
    }
  }
  ```
- [ ] Add toast notifications for user actions
- [ ] Show helpful error messages

#### Deliverables
- Fully integrated FastAPI backend
- Real-time WebSocket communication
- Optimized performance (load time <2s)
- Accessible, keyboard-navigable interface

---

### PHASE 5: Testing & Deployment (Weeks 5-6 - 20 hours)

#### Objectives
- Comprehensive E2E testing
- Audio functionality testing
- Performance benchmarking
- Production deployment

#### Tasks

**5.1 E2E Testing with Playwright (8 hours)**

**Sample Browser Tests (3 hours)**
- [ ] Test sample listing:
  ```typescript
  test('loads samples successfully', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await expect(page.locator('.sample-card')).toHaveCount(20);
  });
  ```
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

**5.2 Audio Functionality Testing (4 hours)**

**Manual Audio Tests (2 hours)**
- [ ] Test playback across browsers:
  - Chrome
  - Firefox
  - Safari
  - Edge
- [ ] Test different audio formats:
  - WAV (PCM)
  - MP3 (various bitrates)
  - FLAC
  - AIFF
- [ ] Test large files (>10MB)
- [ ] Test rapid play/pause/seek operations

**Waveform Rendering Tests (2 hours)**
- [ ] Test waveform accuracy against reference
- [ ] Test zoom performance (1x to 10x)
- [ ] Test pan smoothness
- [ ] Test responsiveness (window resize)

**5.3 Performance Benchmarking (4 hours)**

**Load Time Tests (2 hours)**
- [ ] Measure initial page load (<2s target):
  ```bash
  npx lighthouse http://localhost:5173 --view
  ```
- [ ] Test with throttled network (3G, 4G)
- [ ] Measure Time to Interactive (TTI)
- [ ] Measure Largest Contentful Paint (LCP)

**Runtime Performance (2 hours)**
- [ ] Test sample grid scroll performance (60fps)
- [ ] Test audio playback CPU usage (<10%)
- [ ] Test memory usage during long sessions
- [ ] Profile with Chrome DevTools Performance tab

**5.4 Production Deployment (4 hours)**

**Build Configuration (1 hour)**
- [ ] Configure production build:
  ```typescript
  // vite.config.ts
  export default defineConfig({
    build: {
      target: 'es2020',
      minify: 'terser',
      sourcemap: true,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            ui: ['@radix-ui/react-dialog', 'framer-motion'],
            audio: ['wavesurfer.js'],
          },
        },
      },
    },
  });
  ```
- [ ] Enable Brotli compression
- [ ] Set cache headers for static assets

**Docker Deployment (2 hours)**
- [ ] Create multi-stage Dockerfile:
  ```dockerfile
  FROM node:20-alpine AS builder
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build

  FROM nginx:alpine
  COPY --from=builder /app/dist /usr/share/nginx/html
  COPY nginx.conf /etc/nginx/nginx.conf
  EXPOSE 80
  CMD ["nginx", "-g", "daemon off;"]
  ```
- [ ] Configure nginx for SPA routing
- [ ] Set up Docker Compose with backend

**Monitoring & Logging (1 hour)**
- [ ] Set up error tracking (Sentry)
- [ ] Configure analytics (Plausible or similar)
- [ ] Set up performance monitoring
- [ ] Create health check endpoint

#### Deliverables
- 90%+ E2E test coverage
- Performance metrics meeting targets
- Production-ready Docker deployment
- Monitoring and error tracking

---

## 4. DETAILED TASK LIST

### Week 1: Foundation (20 hours)

| Task | Component | Hours | Priority |
|------|-----------|-------|----------|
| Create Vite + React + TS project | Setup | 1 | Critical |
| Install dependencies | Setup | 1 | Critical |
| Set up folder structure | Setup | 1 | Critical |
| Configure ESLint + Prettier | Setup | 1 | Critical |
| Install ShadCN UI | Setup | 2 | Critical |
| Add essential components | Setup | 2 | Critical |
| Create custom color palette | Design | 2 | High |
| Define typography scale | Design | 1 | High |
| Set up spacing & shadows | Design | 1 | High |
| Create animation tokens | Design | 1 | High |
| Create axios client | API | 2 | Critical |
| Implement API endpoints | API | 2 | Critical |
| Set up React Query | API | 1 | Critical |
| Create TypeScript types | API | 2 | High |

### Week 2: Core Components (35 hours)

| Task | Component | Hours | Priority |
|------|-----------|-------|----------|
| Build SampleCard | UI | 3 | Critical |
| Build SampleGrid | UI | 3 | Critical |
| Build FilterPanel | UI | 4 | Critical |
| Integrate wavesurfer.js | Audio | 6 | Critical |
| Build AudioControls | Audio | 4 | Critical |
| Create AudioContext provider | Audio | 2 | High |
| Build SearchBar | UI | 3 | High |
| Build UploadDropZone | UI | 5 | High |
| Build Pagination | UI | 2 | Medium |
| Build Layout components | UI | 3 | Medium |

### Week 3: Advanced Features (35 hours)

| Task | Component | Hours | Priority |
|------|-----------|-------|----------|
| Build PadGrid component | Kit Builder | 8 | Critical |
| Build KitHeader | Kit Builder | 3 | High |
| Build SampleRecommendations | Kit Builder | 4 | High |
| Create MatchingVisualization | Visualization | 5 | Medium |
| Build SimilarSamples | Visualization | 3 | Medium |
| Build BatchUploadManager | Batch | 4 | High |
| Build AnalysisQueueDisplay | Batch | 3 | High |
| Build SpectralGraph | Audio | 3 | Low |
| Build AudioFeaturesDisplay | Audio | 2 | Medium |

### Week 4: Integration & Polish (25 hours)

| Task | Component | Hours | Priority |
|------|-----------|-------|----------|
| Integrate Samples API | Integration | 3 | Critical |
| Integrate Kits API | Integration | 3 | Critical |
| Integrate Preferences API | Integration | 2 | High |
| Create WebSocket client | Integration | 3 | High |
| Add real-time analysis updates | Integration | 2 | High |
| Implement code splitting | Performance | 2 | Medium |
| Optimize audio performance | Performance | 2 | High |
| Optimize rendering | Performance | 2 | High |
| Add keyboard navigation | Accessibility | 2 | Medium |
| Add ARIA labels | Accessibility | 2 | Medium |
| Create loading states | UX | 2 | High |

### Weeks 5-6: Testing & Deployment (20 hours)

| Task | Component | Hours | Priority |
|------|-----------|-------|----------|
| Write Sample Browser tests | Testing | 3 | Critical |
| Write Kit Builder tests | Testing | 3 | Critical |
| Write Audio tests | Testing | 2 | Critical |
| Manual audio testing | Testing | 2 | High |
| Waveform rendering tests | Testing | 2 | Medium |
| Load time benchmarking | Performance | 2 | High |
| Runtime performance testing | Performance | 2 | Medium |
| Configure production build | Deployment | 1 | Critical |
| Create Docker setup | Deployment | 2 | Critical |
| Set up monitoring | Deployment | 1 | Medium |

**Total Estimated Hours**: 135 hours

---

## 5. TECHNICAL SPECIFICATIONS

### 5.1 Frontend Stack

**Core Framework**
- **React** 18.3+ with TypeScript 5.3+
- **Vite** 5.0+ for build tooling
- **React Router** 6.20+ for routing

**UI Components**
- **ShadCN UI** - Radix UI + Tailwind CSS components
- **Framer Motion** 11.0+ - Animations and transitions
- **Lucide React** - Icon library

**State Management**
- **TanStack Query** (React Query) v5 - Server state
- **Zustand** 4.4+ - Client state (if needed)
- **React Context** - Theme and audio providers

**Audio**
- **wavesurfer.js** 7.0+ - Waveform visualization
- **Web Audio API** - Audio playback and processing

**Data Visualization**
- **Recharts** 2.10+ - Charts and graphs

**Forms & Validation**
- **React Hook Form** 7.48+ - Form management
- **Zod** 3.22+ - Schema validation

**HTTP & WebSocket**
- **axios** 1.6+ - HTTP client
- **native WebSocket** - Real-time communication

**Development Tools**
- **ESLint** + **Prettier** - Code quality
- **Vitest** - Unit testing
- **Playwright** - E2E testing
- **TypeScript** - Type safety

### 5.2 Backend Integration

**FastAPI Endpoints** (existing at 127.0.0.1:8100)

```typescript
// Sample endpoints
GET    /api/v1/samples              // List samples (paginated, filtered)
POST   /api/v1/samples              // Upload sample
GET    /api/v1/samples/{id}         // Get sample details
GET    /api/v1/samples/{id}/download // Download audio file
DELETE /api/v1/samples/{id}         // Delete sample

// Kit endpoints
GET    /api/v1/kits                 // List kits
POST   /api/v1/kits                 // Create kit
GET    /api/v1/kits/{id}            // Get kit details
PUT    /api/v1/kits/{id}            // Update kit
DELETE /api/v1/kits/{id}            // Delete kit
POST   /api/v1/kits/{id}/assign     // Assign sample to pad
DELETE /api/v1/kits/{id}/assign/{sample_id} // Remove from pad
GET    /api/v1/kits/{id}/recommendations // Get recommendations
GET    /api/v1/kits/{id}/export     // Export kit as ZIP

// Preferences endpoints
GET    /api/v1/preferences          // Get user preferences
PUT    /api/v1/preferences          // Update preferences

// WebSocket
ws://127.0.0.1:8100/ws              // Real-time analysis updates
```

**Data Models** (TypeScript interfaces)

```typescript
interface Sample {
  id: number;
  user_id: number;
  title: string;
  file_path: string;
  duration?: number;
  genre?: string;
  bpm?: number;
  musical_key?: string;
  tags: string[];
  rating?: number;
  created_at: string;
  updated_at: string;
  audio_features?: AudioFeatures;
  ai_analysis?: AIAnalysis;
}

interface AudioFeatures {
  bpm?: number;
  key?: string;
  scale?: string;
  spectral_centroid?: number;
  spectral_bandwidth?: number;
  spectral_rolloff?: number;
  spectral_flatness?: number;
  zero_crossing_rate?: number;
  rms_energy?: number;
  harmonic_ratio?: number;
  mfcc_mean?: number[];
  mfcc_std?: number[];
  chroma_mean?: number[];
  chroma_std?: number[];
}

interface Kit {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  samples: PadAssignment[];
}

interface PadAssignment {
  kit_id: number;
  sample_id: number;
  pad_bank: 'A' | 'B' | 'C' | 'D';
  pad_number: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
  volume?: number;
  pitch_shift?: number;
  sample: Sample;
}

interface UserPreferences {
  ai_model: 'qwen3-7b' | 'qwen3-235b';
  auto_analysis: boolean;
  theme: 'dark' | 'light';
}
```

### 5.3 Design System

**Color Palette** (Professional Music Production Theme)

```css
/* globals.css */
@layer base {
  :root {
    /* Background */
    --background: 220 13% 8%;        /* #13151A - Deep blue-gray */
    --foreground: 210 20% 98%;       /* #F8F9FB - Off-white */

    /* Primary (Accent) */
    --primary: 198 93% 60%;          /* #1FC7FF - Bright cyan */
    --primary-foreground: 220 13% 8%; /* Dark text on primary */

    /* Secondary */
    --secondary: 217 33% 17%;        /* #1D232E - Darker blue-gray */
    --secondary-foreground: 210 20% 98%;

    /* Accent (Success/Active) */
    --accent: 142 76% 36%;           /* #15B857 - Vibrant green */
    --accent-foreground: 220 13% 8%;

    /* Destructive (Error/Delete) */
    --destructive: 0 84% 60%;        /* #F04444 - Red */
    --destructive-foreground: 210 20% 98%;

    /* Muted */
    --muted: 217 33% 17%;            /* #1D232E - Same as secondary */
    --muted-foreground: 215 16% 47%; /* #657184 - Muted text */

    /* Border */
    --border: 217 33% 20%;           /* #222936 - Subtle border */

    /* Card */
    --card: 217 33% 12%;             /* #16181F - Slightly lighter than bg */
    --card-foreground: 210 20% 98%;

    /* Popover */
    --popover: 217 33% 12%;
    --popover-foreground: 210 20% 98%;

    /* Ring (focus) */
    --ring: 198 93% 60%;             /* Same as primary */

    /* Radius */
    --radius: 0.5rem;                /* 8px default border radius */
  }
}
```

**Typography**

```css
/* Font families */
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Font sizes (16px base) */
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */
--text-4xl: 2.25rem;     /* 36px */

/* Font weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

**Spacing System** (4px base unit)

```css
--spacing-1: 0.25rem;    /* 4px */
--spacing-2: 0.5rem;     /* 8px */
--spacing-3: 0.75rem;    /* 12px */
--spacing-4: 1rem;       /* 16px */
--spacing-5: 1.25rem;    /* 20px */
--spacing-6: 1.5rem;     /* 24px */
--spacing-8: 2rem;       /* 32px */
--spacing-10: 2.5rem;    /* 40px */
--spacing-12: 3rem;      /* 48px */
--spacing-16: 4rem;      /* 64px */
```

**Shadow System**

```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
```

**Animation Tokens**

```typescript
// Framer Motion presets
export const animations = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2 },
  },

  slideUp: {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -20, opacity: 0 },
    transition: { duration: 0.3 },
  },

  scaleIn: {
    initial: { scale: 0.9, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.9, opacity: 0 },
    transition: { duration: 0.2 },
  },

  spring: {
    type: 'spring',
    stiffness: 300,
    damping: 30,
  },
};
```

### 5.4 Component Library Structure

```
src/components/
├── ui/                          # ShadCN UI components
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── dropdown-menu.tsx
│   ├── input.tsx
│   ├── select.tsx
│   ├── slider.tsx
│   ├── table.tsx
│   ├── tabs.tsx
│   ├── toast.tsx
│   └── tooltip.tsx
│
├── audio/                       # Audio-specific components
│   ├── AudioPlayer.tsx          # Global audio player
│   ├── WaveformVisualizer.tsx   # Waveform display
│   ├── AudioControls.tsx        # Play/pause/volume controls
│   ├── SpectralGraph.tsx        # Frequency visualization
│   └── AudioFeaturesDisplay.tsx # BPM, key, etc.
│
├── samples/                     # Sample-related components
│   ├── SampleCard.tsx           # Individual sample card
│   ├── SampleGrid.tsx           # Grid of sample cards
│   ├── SampleDetail.tsx         # Detailed sample view
│   ├── FilterPanel.tsx          # Sample filters
│   └── SearchBar.tsx            # Sample search
│
├── kits/                        # Kit builder components
│   ├── PadGrid.tsx              # SP-404 pad layout
│   ├── Pad.tsx                  # Individual pad
│   ├── KitHeader.tsx            # Kit name/actions
│   └── SampleRecommendations.tsx # AI recommendations
│
├── upload/                      # Upload components
│   ├── DropZone.tsx             # Drag-and-drop area
│   ├── FilePreview.tsx          # File list preview
│   ├── UploadProgress.tsx       # Progress bars
│   └── BatchUploadManager.tsx   # Batch upload queue
│
├── layout/                      # Layout components
│   ├── Header.tsx               # App header
│   ├── Sidebar.tsx              # Sidebar navigation
│   ├── Footer.tsx               # App footer
│   └── PageLayout.tsx           # Page wrapper
│
└── shared/                      # Shared components
    ├── LoadingSkeleton.tsx      # Loading states
    ├── ErrorBoundary.tsx        # Error handling
    ├── EmptyState.tsx           # Empty state UI
    └── Pagination.tsx           # Pagination controls
```

---

## 6. RISK ANALYSIS

### 6.1 Technical Risks

**Risk 1: Audio Playback Browser Compatibility**

**Description**: Different browsers have varying support for audio formats and Web Audio API features.

**Impact**: High - Core functionality may not work on all browsers

**Mitigation**:
- Use feature detection to check Web Audio API support
- Provide fallback to HTML5 `<audio>` element
- Test on all major browsers (Chrome, Firefox, Safari, Edge)
- Document supported formats and browsers
- Consider using a library like Howler.js for cross-browser compatibility

**Risk 2: Large File Upload Handling**

**Description**: Uploading large audio files (>50MB) may cause timeouts or memory issues.

**Impact**: Medium - Users with large sample libraries may face issues

**Mitigation**:
- Implement chunked uploads (5MB chunks)
- Add client-side file size validation (max 50MB)
- Show progress bars with ability to cancel
- Use streaming on backend to avoid memory spikes
- Implement retry logic for failed chunks

**Risk 3: Real-time Analysis Performance**

**Description**: Running AI analysis on multiple samples simultaneously may cause backend slowdowns.

**Impact**: Medium - Batch uploads may queue for long periods

**Mitigation**:
- Implement queue system with rate limiting
- Show estimated wait time to users
- Allow users to defer analysis (audio-only mode)
- Use WebSocket to provide real-time progress updates
- Scale backend workers horizontally if needed

**Risk 4: WebSocket Connection Stability**

**Description**: WebSocket connections may drop due to network issues or server restarts.

**Impact**: Medium - Real-time updates may stop working

**Mitigation**:
- Implement automatic reconnection with exponential backoff
- Queue messages during disconnection
- Show connection status indicator in UI
- Fall back to polling if WebSocket unavailable
- Add heartbeat ping/pong to detect stale connections

### 6.2 UX Risks

**Risk 5: Mobile Audio Limitations**

**Description**: iOS Safari has restrictions on audio playback (must be user-initiated).

**Impact**: Medium - Mobile experience may be degraded

**Mitigation**:
- Ensure all audio playback is triggered by user interaction
- Test thoroughly on iOS Safari and mobile Chrome
- Provide clear UI indicators when audio is restricted
- Consider progressive web app (PWA) for better mobile experience
- Document mobile limitations in user guide

**Risk 6: Waveform Rendering Performance**

**Description**: Rendering high-resolution waveforms for many samples may cause lag.

**Impact**: Low-Medium - UI may feel sluggish with large libraries

**Mitigation**:
- Use canvas-based rendering (not SVG)
- Implement virtualization for sample grid
- Lazy-load waveforms as they enter viewport
- Cache rendered waveforms in browser storage
- Use Web Workers for waveform data processing

### 6.3 Integration Risks

**Risk 7: API Response Time**

**Description**: Backend API may be slow for complex queries (many filters, large datasets).

**Impact**: Medium - Users may perceive app as slow

**Mitigation**:
- Implement optimistic UI updates
- Show loading skeletons while fetching
- Use React Query's stale-while-revalidate pattern
- Add pagination to limit response sizes
- Work with backend team to optimize slow queries

**Risk 8: Audio Feature Extraction Accuracy**

**Description**: Librosa may produce inaccurate BPM/key detection for certain samples.

**Impact**: Low - May affect sample matching quality

**Mitigation**:
- Allow users to manually correct BPM and key
- Show confidence scores from audio analysis
- Use AI analysis as secondary validation
- Provide "Report Incorrect" button for feedback
- Document known limitations (e.g., complex polyrhythms)

### 6.4 Deployment Risks

**Risk 9: CORS Configuration**

**Description**: Frontend may face CORS issues when communicating with backend.

**Impact**: High - App won't function if CORS not configured

**Mitigation**:
- Configure FastAPI CORS middleware properly
- Test CORS in production-like environment
- Use proxy in development (vite.config.ts)
- Document CORS requirements for deployment
- Add CORS error handling with helpful messages

**Risk 10: Environment-Specific Bugs**

**Description**: Code may work in development but fail in production build.

**Impact**: Medium - May require hotfixes post-deployment

**Mitigation**:
- Test production build locally before deploying
- Use environment variables for all config
- Enable source maps for debugging
- Set up staging environment identical to production
- Implement comprehensive error tracking (Sentry)

---

## 7. SUCCESS METRICS

### 7.1 Audio Functionality (4 points)

**Sample Playback (1 point)**
- ✅ Users can play/pause samples
- ✅ Volume controls work correctly
- ✅ Playback position updates in real-time
- ✅ Keyboard shortcuts (space, arrows) work

**Waveform Display (1 point)**
- ✅ Waveform renders accurately
- ✅ Zoom and pan controls are smooth (60fps)
- ✅ Current position cursor follows playback
- ✅ Waveform loads within 2 seconds for typical samples

**Audio Feature Display (1 point)**
- ✅ BPM, key, duration displayed correctly
- ✅ Spectral features visualized clearly
- ✅ Harmonic/percussive ratio shown
- ✅ Audio features match backend analysis (90%+ accuracy)

**Matching Accuracy (1 point)**
- ✅ Similar samples have high match scores (>70%)
- ✅ Dissimilar samples have low match scores (<40%)
- ✅ Recommendations are musically relevant
- ✅ Users can find complementary samples quickly

**Target**: 4/4 points

### 7.2 Visual Polish (3 points)

**Professional Appearance (1 point)**
- ✅ UI follows music production design patterns
- ✅ Color palette is cohesive and professional
- ✅ Typography is readable and well-sized
- ✅ No purple gradients or AI agent aesthetics
- ✅ Dark theme is comfortable for long sessions

**Smooth Animations (1 point)**
- ✅ All animations run at 60fps
- ✅ Framer Motion transitions are smooth
- ✅ No janky scrolling or layout shifts
- ✅ Loading states transition gracefully
- ✅ Hover effects are responsive (<100ms)

**Responsive Design (1 point)**
- ✅ Works on desktop (1920x1080, 1366x768)
- ✅ Works on tablet (768x1024)
- ✅ Works on mobile (375x667, 414x896)
- ✅ Touch interactions work on mobile
- ✅ Layout adapts gracefully to different sizes

**Target**: 3/3 points

### 7.3 Performance (3 points)

**Fast Load Times (1 point)**
- ✅ Initial page load <2 seconds
- ✅ Time to Interactive (TTI) <3 seconds
- ✅ Largest Contentful Paint (LCP) <2.5 seconds
- ✅ First Input Delay (FID) <100ms

**Efficient Audio Handling (1 point)**
- ✅ Audio files load progressively (streaming)
- ✅ Decoded buffers are cached
- ✅ CPU usage <10% during playback
- ✅ Memory usage stable during long sessions

**Responsive UI (1 point)**
- ✅ Search results appear within 500ms
- ✅ Filter changes apply instantly (<100ms perceived)
- ✅ Sample grid scrolls smoothly (60fps)
- ✅ Drag-and-drop has no lag

**Target**: 3/3 points

### 7.4 Integration (2 points)

**Reliable FastAPI Communication (1 point)**
- ✅ API requests succeed 99%+ of the time
- ✅ Failed requests retry automatically
- ✅ WebSocket reconnects on disconnect
- ✅ Real-time updates arrive within 1 second
- ✅ Optimistic updates work correctly

**Comprehensive Error Handling (1 point)**
- ✅ Network errors show helpful messages
- ✅ Upload failures offer retry option
- ✅ Invalid data is validated client-side
- ✅ Error boundaries catch React errors
- ✅ Users can recover from errors without refresh

**Target**: 2/2 points

### 7.5 Overall Success Criteria

**Minimum for Production**: 10/12 points (83%)

**Ideal Target**: 12/12 points (100%)

**Priority Order**:
1. Audio Functionality (critical for core value)
2. Performance (critical for user experience)
3. Integration (critical for reliability)
4. Visual Polish (important for professional feel)

---

## 8. PROJECT TIMELINE

### Week 1: Foundation (Nov 18-24)
- **Days 1-2**: Project setup, dependencies, folder structure
- **Days 3-4**: ShadCN UI installation, design system
- **Day 5**: API client layer, TypeScript types

**Checkpoint**: Dev environment running, design system implemented, API client ready

---

### Week 2: Core Components (Nov 25 - Dec 1)
- **Days 1-2**: Sample browsing (SampleCard, SampleGrid, FilterPanel)
- **Days 3-4**: Audio player integration (WaveformVisualizer, AudioControls)
- **Day 5**: Search and upload (SearchBar, DropZone)

**Checkpoint**: Sample browsing works, audio playback functional, uploads succeed

---

### Week 3: Advanced Features (Dec 2-8)
- **Days 1-3**: Kit builder (PadGrid, KitHeader, drag-and-drop)
- **Days 4-5**: Sample matching, batch processing, advanced audio features

**Checkpoint**: Kit builder functional, sample matching works, batch uploads succeed

---

### Week 4: Integration & Polish (Dec 9-15)
- **Days 1-2**: Complete API integration, WebSocket real-time updates
- **Days 3-4**: Performance optimization, code splitting
- **Day 5**: Accessibility improvements, loading states

**Checkpoint**: All features integrated, performance targets met, polish complete

---

### Week 5: Testing (Dec 16-22)
- **Days 1-2**: E2E tests (Playwright)
- **Days 3-4**: Audio functionality testing, cross-browser testing
- **Day 5**: Performance benchmarking

**Checkpoint**: 90%+ test coverage, all browsers tested, performance measured

---

### Week 6: Deployment (Dec 23-29)
- **Days 1-2**: Production build configuration, Docker setup
- **Days 3-4**: Deployment to staging, final QA
- **Day 5**: Production deployment, monitoring setup

**Checkpoint**: App deployed to production, monitoring active, documentation complete

---

## 9. IMPLEMENTATION NOTES

### 9.1 Key Development Principles

**1. Component-First Development**
- Build components in isolation (Storybook optional)
- Test components independently
- Document props and usage
- Ensure accessibility from the start

**2. Progressive Enhancement**
- Start with core functionality (sample browsing, playback)
- Add advanced features incrementally
- Ensure basic functionality works without JavaScript (where possible)
- Graceful degradation for older browsers

**3. Performance by Default**
- Use React.memo() for expensive components
- Implement code splitting at route level
- Lazy-load heavy dependencies (wavesurfer.js)
- Profile regularly with Chrome DevTools

**4. Accessibility First**
- Use semantic HTML
- Add ARIA labels to all interactive elements
- Ensure keyboard navigation works
- Test with screen readers (NVDA, JAWS)

**5. Mobile-First Design**
- Design for mobile screens first
- Use responsive breakpoints consistently
- Test on real devices, not just DevTools
- Optimize touch targets (min 44x44px)

### 9.2 Code Quality Standards

**TypeScript**
- Strict mode enabled
- No `any` types (use `unknown` if needed)
- Explicit return types for functions
- Proper error handling (no silent failures)

**React**
- Functional components only
- Custom hooks for reusable logic
- Proper dependency arrays in useEffect
- Avoid prop drilling (use context or composition)

**CSS/Tailwind**
- Use design tokens (CSS variables)
- Follow BEM naming for custom classes
- Avoid inline styles unless dynamic
- Use Tailwind utilities first, custom CSS as fallback

**Testing**
- Unit tests for utilities and hooks
- Component tests for complex UI logic
- E2E tests for critical user flows
- Aim for 80%+ code coverage

### 9.3 Git Workflow

**Branch Strategy**
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches

**Commit Messages**
```
feat: Add waveform visualization component
fix: Resolve audio playback on Safari
perf: Optimize sample grid rendering
docs: Update API integration guide
```

**Pull Request Process**
1. Create feature branch from `develop`
2. Implement feature with tests
3. Run linter and tests locally
4. Create PR with description and screenshots
5. Request review from team
6. Address feedback and merge

### 9.4 Documentation

**Code Documentation**
- JSDoc comments for all public functions
- README for each major feature
- Inline comments for complex logic

**User Documentation**
- Keyboard shortcuts guide
- Feature tutorials with screenshots
- FAQ for common issues
- Troubleshooting guide

**Developer Documentation**
- Architecture overview
- API integration guide
- Component library docs
- Deployment guide

---

## 10. NEXT STEPS

### Immediate Actions (Week 1)

1. **Review and Approve Plan**
   - Team review of implementation plan
   - Identify any gaps or concerns
   - Finalize timeline and resource allocation

2. **Environment Setup**
   - Set up development machines
   - Install required tools and dependencies
   - Create GitHub repository and project board

3. **Begin Phase 1 Implementation**
   - Initialize Vite + React + TypeScript project
   - Install ShadCN UI and configure theme
   - Create API client layer

### Communication Plan

**Daily Standups**
- Share progress on current tasks
- Identify blockers
- Plan next day's work

**Weekly Reviews**
- Demo completed features
- Review against success metrics
- Adjust plan if needed

**Sprint Retrospectives**
- What went well?
- What could be improved?
- Action items for next sprint

---

## APPENDIX A: Research Sources

### Music Production UI References

1. **Drumhaus** (github.com/mxfng/drumhaus)
   - Browser-based drum machine
   - Curated sample kits with frequency graphs
   - Next.js + Tone.js implementation

2. **Splice Sample Manager**
   - Industry-standard sample browser
   - Waveform previews
   - Tag-based filtering

3. **Ableton Live Browser**
   - Professional music production tool
   - Hierarchical navigation
   - Real-time preview

### Dashboard & Visualization References

1. **Recharts** (recharts.org)
   - React chart library with 3.0 update (2025)
   - Built on D3 and React
   - Declarative, composable charts

2. **Tremor** (tremor.so)
   - 35+ open-source dashboard components
   - Built with Tailwind CSS and Radix UI
   - Production-ready

3. **ApexCharts**
   - Real-time data visualization
   - Wide range of chart types
   - Excellent for monitoring dashboards

### ShadCN + Framer Motion References

1. **Indie UI**
   - Animated components with Framer Motion
   - ShadCN UI integration
   - Modern, responsive designs

2. **Magic UI**
   - 50+ animated components
   - TypeScript, Next.js, Tailwind
   - Copy-paste components

3. **Aceternity UI**
   - Masterclass in UI design
   - Framer Motion + Tailwind + ShadCN
   - Visual effects and animations

---

## APPENDIX B: Color Palette Reference

### Primary Colors

```css
/* Background Shades */
--bg-darker: #0D0F13;    /* HSL(220, 13%, 6%) */
--bg-dark: #13151A;      /* HSL(220, 13%, 8%) */
--bg-medium: #16181F;    /* HSL(217, 33%, 12%) */
--bg-light: #1D232E;     /* HSL(217, 33%, 17%) */

/* Foreground Shades */
--fg-white: #F8F9FB;     /* HSL(210, 20%, 98%) */
--fg-gray: #A8B0C1;      /* HSL(215, 16%, 70%) */
--fg-muted: #657184;     /* HSL(215, 16%, 47%) */

/* Accent Colors */
--cyan: #1FC7FF;         /* HSL(198, 93%, 60%) */
--cyan-dark: #0B8BBD;    /* HSL(198, 93%, 40%) */
--green: #15B857;        /* HSL(142, 76%, 36%) */
--red: #F04444;          /* HSL(0, 84%, 60%) */
--yellow: #F59E0B;       /* HSL(38, 92%, 50%) */
```

### Usage Guidelines

- **Background**: Deep blue-gray for music production aesthetic
- **Primary**: Bright cyan for interactive elements (buttons, links)
- **Accent**: Vibrant green for success states, active elements
- **Destructive**: Red for delete/error states
- **Muted**: Gray tones for disabled states, secondary text

---

## APPENDIX C: Folder Structure

```
sp404mk2-sample-matching-app/
├── public/
│   ├── favicon.ico
│   └── assets/
│       └── images/
├── src/
│   ├── api/
│   │   ├── client.ts
│   │   ├── samples.ts
│   │   ├── kits.ts
│   │   └── preferences.ts
│   ├── components/
│   │   ├── ui/              # ShadCN components
│   │   ├── audio/           # Audio components
│   │   ├── samples/         # Sample components
│   │   ├── kits/            # Kit components
│   │   ├── upload/          # Upload components
│   │   ├── layout/          # Layout components
│   │   └── shared/          # Shared components
│   ├── features/
│   │   ├── sample-browser/
│   │   ├── kit-builder/
│   │   └── upload/
│   ├── hooks/
│   │   ├── useAudioPlayer.ts
│   │   ├── useWebSocket.ts
│   │   ├── useDebounce.ts
│   │   └── useLocalStorage.ts
│   ├── lib/
│   │   ├── audio.ts         # Audio utilities
│   │   ├── utils.ts         # General utilities
│   │   └── constants.ts     # App constants
│   ├── pages/
│   │   ├── SampleBrowser.tsx
│   │   ├── SampleDetail.tsx
│   │   ├── KitBuilder.tsx
│   │   ├── Upload.tsx
│   │   └── Settings.tsx
│   ├── stores/
│   │   ├── audioStore.ts    # Zustand audio store
│   │   └── uiStore.ts       # Zustand UI store
│   ├── types/
│   │   ├── api.ts           # API types
│   │   ├── audio.ts         # Audio types
│   │   └── kit.ts           # Kit types
│   ├── App.tsx
│   ├── main.tsx
│   ├── globals.css
│   └── vite-env.d.ts
├── tests/
│   ├── e2e/                 # Playwright tests
│   ├── unit/                # Vitest unit tests
│   └── fixtures/            # Test fixtures
├── .env.example
├── .eslintrc.cjs
├── .prettierrc
├── docker-compose.yml
├── Dockerfile
├── index.html
├── package.json
├── playwright.config.ts
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── vitest.config.ts
```

---

## CONCLUSION

This implementation plan provides a comprehensive roadmap for building a production-quality music sample matching application. The plan is grounded in research on best practices for music production UI, modern React development, and professional design systems.

**Key Strengths**:
- Realistic timeline (4-6 weeks) based on detailed task breakdown
- Professional design system avoiding AI agent aesthetics
- Comprehensive risk analysis with mitigation strategies
- Clear success metrics (10/12 minimum)
- Production-ready architecture with FastAPI integration

**Next Steps**:
1. Review and approve plan
2. Set up development environment
3. Begin Phase 1 implementation

The plan is designed to be flexible and can be adjusted based on actual progress and emerging requirements. Regular checkpoints at the end of each week will ensure the project stays on track.

---

**Plan Version**: 1.0
**Last Updated**: 2025-11-15
**Status**: Ready for Implementation
