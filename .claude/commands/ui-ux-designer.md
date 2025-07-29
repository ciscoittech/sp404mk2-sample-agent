# UI/UX Designer Specialist

**Command**: `/ui-ux-designer`

Design specialist for creating intuitive, accessible, and visually appealing interfaces for the SP404MK2 sample management system.

## Expertise Areas

### User Research
- **User Personas**: Producer profiles, workflow analysis
- **Journey Mapping**: Sample discovery to production
- **Usability Testing**: A/B testing, user feedback
- **Analytics**: Behavior tracking, heatmaps

### Visual Design
- **Design Systems**: Component library, style guide
- **Responsive Design**: Mobile-first approach
- **Accessibility**: WCAG 2.1 AA compliance
- **Micro-interactions**: Delightful animations

### Information Architecture
- **Navigation**: Intuitive menu structure
- **Content Hierarchy**: Visual importance
- **Search/Filter**: Faceted search design
- **Data Visualization**: Waveforms, analytics

### Prototyping
- **Wireframes**: Low-fidelity concepts
- **Interactive Prototypes**: Figma, user flows
- **Design Handoff**: Specs for developers
- **Component Documentation**: Usage guidelines

## Design System

### Color Palette
```css
/* Primary Colors - Music Production Theme */
:root {
  /* Dark theme base */
  --color-background: #0a0a0a;
  --color-surface: #1a1a1a;
  --color-surface-raised: #2a2a2a;
  
  /* Accent colors */
  --color-primary: #00ff88;      /* Neon green - active/success */
  --color-secondary: #ff0088;    /* Hot pink - alerts/important */
  --color-tertiary: #00ffff;     /* Cyan - info/highlights */
  
  /* Semantic colors */
  --color-error: #ff4444;
  --color-warning: #ffaa00;
  --color-success: var(--color-primary);
  
  /* Text colors */
  --color-text-primary: #ffffff;
  --color-text-secondary: #aaaaaa;
  --color-text-disabled: #666666;
}

/* Light theme override */
[data-theme="light"] {
  --color-background: #ffffff;
  --color-surface: #f5f5f5;
  --color-text-primary: #1a1a1a;
}
```

### Typography
```css
/* Typography scale */
.text-xs { font-size: 0.75rem; line-height: 1rem; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.text-base { font-size: 1rem; line-height: 1.5rem; }
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }
.text-2xl { font-size: 1.5rem; line-height: 2rem; }

/* Font families */
.font-mono { font-family: 'JetBrains Mono', monospace; }
.font-display { font-family: 'Inter', sans-serif; }

/* Font weights */
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-bold { font-weight: 700; }
```

### Component Patterns

#### Sample Card Design
```html
<!-- Sample card component -->
<div class="sample-card">
  <div class="sample-waveform">
    <!-- Waveform visualization -->
  </div>
  
  <div class="sample-info">
    <h3 class="sample-title">Dusty Break 120</h3>
    <div class="sample-meta">
      <span class="tag">Hip-Hop</span>
      <span class="bpm">120 BPM</span>
      <span class="duration">4.2s</span>
    </div>
  </div>
  
  <div class="sample-actions">
    <button class="btn-icon" aria-label="Play sample">
      <icon-play />
    </button>
    <button class="btn-icon" aria-label="Add to kit">
      <icon-plus />
    </button>
    <button class="btn-icon" aria-label="Analyze vibe">
      <icon-sparkle />
    </button>
  </div>
  
  <div class="vibe-indicator">
    <div class="vibe-energy" style="--energy: 0.8"></div>
    <span class="vibe-mood">Energetic</span>
  </div>
</div>
```

#### Kit Builder Interface
```
┌─────────────────────────────────────┐
│  Kit: Summer Vibes                  │
├─────────────────────────────────────┤
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐          │
│  │ 1 │ │ 2 │ │ 3 │ │ 4 │  Bank A  │
│  └───┘ └───┘ └───┘ └───┘          │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐          │
│  │ 5 │ │ 6 │ │ 7 │ │ 8 │          │
│  └───┘ └───┘ └───┘ └───┘          │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐          │
│  │ 9 │ │10 │ │11 │ │12 │          │
│  └───┘ └───┘ └───┘ └───┘          │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐          │
│  │13 │ │14 │ │15 │ │16 │          │
│  └───┘ └───┘ └───┘ └───┘          │
├─────────────────────────────────────┤
│  Drag samples to pads              │
└─────────────────────────────────────┘
```

### Interaction Patterns

#### Drag & Drop
```javascript
// Visual feedback for drag operations
.dragging {
  opacity: 0.5;
  cursor: grabbing;
}

.drop-zone {
  border: 2px dashed var(--color-primary);
  background: rgba(0, 255, 136, 0.1);
}

.drop-zone.active {
  background: rgba(0, 255, 136, 0.2);
  animation: pulse 0.5s ease-in-out;
}
```

#### Loading States
```html
<!-- Skeleton loader for sample grid -->
<div class="sample-grid-skeleton">
  <div class="skeleton-card" v-for="i in 12">
    <div class="skeleton-waveform"></div>
    <div class="skeleton-text w-3/4"></div>
    <div class="skeleton-text w-1/2"></div>
  </div>
</div>

<!-- Progress indicator for batch processing -->
<div class="batch-progress">
  <div class="progress-bar" :style="{ width: `${progress}%` }">
    <span class="progress-text">{{processed}} / {{total}}</span>
  </div>
  <div class="progress-samples">
    <div v-for="sample in samples" 
         :class="['sample-dot', sample.status]">
    </div>
  </div>
</div>
```

### Mobile Responsiveness

#### Breakpoints
```css
/* Mobile-first breakpoints */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

#### Touch Gestures
```javascript
// Swipe to delete
const gesture = {
  onSwipeLeft: () => showDeleteConfirm(),
  onSwipeRight: () => showSampleDetails(),
  onLongPress: () => enterSelectionMode()
}
```

### Accessibility Guidelines

#### Focus Management
```css
/* Visible focus indicators */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Skip navigation */
.skip-nav {
  position: absolute;
  left: -9999px;
}

.skip-nav:focus {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 999;
}
```

#### ARIA Labels
```html
<!-- Accessible sample player -->
<div role="region" aria-label="Sample player">
  <button aria-label="Play Dusty Break 120" 
          aria-pressed="false">
    <icon-play />
  </button>
  <div role="slider" 
       aria-label="Sample position"
       aria-valuemin="0"
       aria-valuemax="100"
       aria-valuenow="45">
  </div>
</div>
```

### User Flows

#### Sample Discovery Flow
```
Home → Browse Samples → Filter/Search → Sample Details → Add to Kit
  ↓                         ↓
Analytics            Vibe Analysis → Similar Samples
```

#### Kit Building Flow
```
My Kits → New Kit → Drag Samples → Arrange Pads → Test/Preview → Export
            ↓           ↓
      Import Existing  Sample Library
```

### Data Visualization

#### Waveform Display
```svg
<!-- Optimized waveform rendering -->
<svg class="waveform" viewBox="0 0 1000 100">
  <path d="M0,50 L10,30 L20,70..." 
        stroke="var(--color-primary)"
        fill="none" />
  <rect class="playhead" 
        x="450" y="0" 
        width="2" height="100" />
</svg>
```

#### Vibe Visualization
```html
<!-- Circular vibe meter -->
<div class="vibe-meter">
  <svg viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="45" 
            class="vibe-track" />
    <circle cx="50" cy="50" r="45" 
            class="vibe-fill"
            style="--energy: 0.75" />
  </svg>
  <div class="vibe-label">
    <span class="mood">Chill</span>
    <span class="energy">75%</span>
  </div>
</div>
```

### Animation Guidelines

#### Micro-interactions
```css
/* Button feedback */
.btn:active {
  transform: scale(0.98);
  transition: transform 0.1s ease;
}

/* Card hover */
.sample-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 255, 136, 0.2);
  transition: all 0.2s ease;
}

/* Smooth transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
```

### Design Handoff

#### Component Specs
```yaml
SampleCard:
  dimensions:
    width: 280px
    height: 180px
    padding: 16px
    borderRadius: 8px
  
  colors:
    background: var(--color-surface)
    hover: var(--color-surface-raised)
    border: transparent
    
  spacing:
    titleMargin: 8px
    metaGap: 8px
    actionGap: 4px
```

#### Figma Integration
- Component library with auto-layout
- Design tokens synchronized
- Interactive prototypes
- Developer annotations

## Integration Points

### With Frontend Developer
- Component specifications
- Animation timing
- Responsive breakpoints
- Accessibility requirements

### With Full-Stack Developer
- Data requirements
- Loading states
- Error handling
- Performance constraints

### With Product Manager
- User stories
- Feature prioritization
- Success metrics
- A/B test design

## Success Metrics

- Task completion rate > 90%
- Error rate < 5%
- Time to first meaningful action < 30s
- Accessibility score 100%
- User satisfaction > 4.5/5
- Mobile usage > 40%