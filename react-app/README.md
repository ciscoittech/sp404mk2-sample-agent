# SP-404MK2 Sample Matching UI

Professional React application for managing and matching audio samples for the Roland SP-404MK2.

## Features

- 🎵 Sample library with 2,437+ samples
- 🎨 Professional dark theme for music production
- 🎛️ Kit builder with SP-404 pad layout (48 pads)
- 📊 Sample matching visualization
- 🌊 Waveform visualization with wavesurfer.js
- 🔍 Advanced filtering (BPM, key, genre, tags)
- ⬆️ Drag-and-drop upload
- ⚡ Real-time WebSocket updates

## Quick Start

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

## Docker

```bash
docker-compose up
```

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 7
- **Routing**: React Router v7
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **UI Library**: ShadCN UI (Radix + Tailwind)
- **Animation**: Framer Motion
- **Audio**: WaveSurfer.js
- **Validation**: Zod
- **Icons**: Lucide React

## Project Structure

```
src/
├── api/          # API client and backend endpoints
├── components/   # Reusable components
│   ├── ui/       # ShadCN UI components
│   ├── audio/    # Audio player and waveform components
│   ├── samples/  # Sample-related components
│   ├── kits/     # Kit builder components
│   ├── upload/   # File upload components
│   ├── layout/   # Layout components (header, nav, etc.)
│   └── shared/   # Shared utility components
├── features/     # Feature-based modules
├── hooks/        # Custom React hooks
│   └── useWebSocket.ts  # Real-time WebSocket hook
├── lib/          # Utilities and helpers
│   └── performance.ts   # Performance optimization utilities
├── pages/        # Route pages
├── stores/       # State management
├── types/        # TypeScript type definitions
└── App.tsx       # Root component
```

## Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format
```

## Backend Integration

The Vite development server is configured to proxy API requests to the FastAPI backend:

- **API Requests**: `/api/*` → `http://127.0.0.1:8100`
- **WebSocket**: `/ws` → `ws://127.0.0.1:8100`

## Path Aliases

TypeScript path aliases are configured for clean imports:

```typescript
import { SampleCard } from '@/components/samples/SampleCard';
import { useAudioPlayer } from '@/hooks/useAudioPlayer';
import { useWebSocket } from '@/hooks/useWebSocket';
import { debounce } from '@/lib/performance';
```

## Performance

Production build optimizations:
- **Code Splitting**: Vendor, UI, Audio, and Query chunks
- **Lazy Loading**: Heavy components loaded on demand
- **Tree Shaking**: Unused code elimination
- **Minification**: Terser for optimal bundle size
- **Target**: LCP < 300ms, CLS: 0.00

## Docker Deployment

Multi-stage Docker build with Nginx:
- **Builder Stage**: Node 20 Alpine with optimized dependencies
- **Production Stage**: Nginx Alpine with static assets
- **Features**: SPA routing, API proxy, WebSocket support, asset caching

## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

Test utilities provided in `src/test-utils.tsx` with React Query and Router setup.

## License

MIT
