# 🎨 SP404MK2 Theme System & Component Architecture

## Overview

This guide documents the complete theme system and shared component architecture for the SP404MK2 Sample Manager frontend. The system provides:

- **8 Curated Themes** - Light, dark, and specialty themes optimized for music production
- **Shared Components** - DRY principle with reusable navigation, headers, and UI elements
- **Theme Persistence** - User preferences saved in localStorage
- **Responsive Design** - Mobile-first with SP-404MK2 hardware inspiration
- **Easy Extensibility** - Simple patterns for adding new pages and components

---

## 🎨 Theme Palette

### Selected Themes

We've curated 8 themes that work well for a music production tool:

| Theme | Type | Description | Use Case |
|-------|------|-------------|----------|
| **dark** | Dark | Clean professional dark (default dark) | Late night sessions |
| **light** | Light | Soft light with good contrast (default light) | Daytime work |
| **synthwave** | Dark | Retro 80s neon aesthetic | Creative inspiration |
| **dracula** | Dark | Popular developer theme | Developer-friendly |
| **cyberpunk** | Dark | High-contrast futuristic | High energy sessions |
| **business** | Dark | Sleek corporate dark | Professional use |
| **lofi** | Light | Muted pastel tones | Chill vibes |
| **forest** | Dark | Natural green tones | Calm focus |

### Default Behavior

- **Light Mode Default**: `light` theme
- **Dark Mode Default**: `dark` theme (prefers-color-scheme: dark)
- **Persistence**: Last selected theme saved to localStorage
- **System Preference**: Respects OS dark mode setting on first visit

---

## 📁 File Structure

```
frontend/
├── components/
│   ├── base.html              # Base layout template (extends all pages)
│   ├── nav.html               # Main navigation bar
│   ├── theme-switcher.html    # Theme selector component
│   ├── footer.html            # Shared footer
│   └── sample-card.html       # Sample card component
├── pages/
│   ├── samples.html           # Sample library (uses base template)
│   ├── kits.html              # Kit builder
│   ├── batch.html             # Batch processing
│   └── vibe-analysis.html     # AI analysis
├── static/
│   ├── css/
│   │   ├── main.css           # Custom styles
│   │   └── themes.css         # Theme-specific overrides
│   └── js/
│       ├── theme.js           # Theme switching logic
│       ├── components.js      # Alpine.js components
│       └── filters.js         # HTMX filter utils
├── index.html                 # Landing page
└── THEME_SYSTEM_GUIDE.md      # This file
```

---

## 🏗️ Architecture Pattern

### 1. Base Template System

All pages extend `components/base.html`:

```html
<!-- components/base.html -->
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <!-- CDN imports -->
    <!-- Theme system -->
    <!-- Page-specific head content -->
    {% block head %}{% endblock %}
</head>
<body>
    <!-- Shared Navigation -->
    {% include 'components/nav.html' %}

    <!-- Page Content -->
    <main id="main-content" class="container mx-auto p-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Shared Footer -->
    {% include 'components/footer.html' %}

    <!-- Global Scripts -->
    {% block scripts %}{% endblock %}
</body>
</html>
```

### 2. Page Template Pattern

New pages extend the base:

```html
<!-- pages/my-new-page.html -->
{% extends "components/base.html" %}

{% block head %}
    <title>My Page - SP404MK2</title>
{% endblock %}

{% block content %}
    <h1>My Page Content</h1>
    <!-- Your content here -->
{% endblock %}

{% block scripts %}
    <script>
        // Page-specific Alpine.js components
    </script>
{% endblock %}
```

### 3. Component Inclusion

Reusable components are included:

```html
{% include 'components/theme-switcher.html' %}
{% include 'components/sample-card.html' with sample=sample_data %}
```

---

## 🎨 Theme Switching Implementation

### JavaScript Logic

```javascript
// static/js/theme.js
const THEMES = {
    light: ['light', 'lofi'],
    dark: ['dark', 'synthwave', 'dracula', 'cyberpunk', 'business', 'forest']
};

const ALL_THEMES = ['light', 'dark', 'synthwave', 'dracula', 'cyberpunk', 'business', 'lofi', 'forest'];

// Initialize theme from localStorage or system preference
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const defaultTheme = savedTheme || (prefersDark ? 'dark' : 'light');
    setTheme(defaultTheme);
}

// Apply theme
function setTheme(themeName) {
    if (!ALL_THEMES.includes(themeName)) {
        console.warn(`Invalid theme: ${themeName}`);
        return;
    }
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem('theme', themeName);

    // Dispatch event for other components
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: themeName } }));
}

// Get current theme
function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'dark';
}

// Toggle between light and dark mode
function toggleDarkMode() {
    const current = getCurrentTheme();
    const isLight = THEMES.light.includes(current);
    const newTheme = isLight ? 'dark' : 'light';
    setTheme(newTheme);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initTheme);

// Listen for system theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light');
    }
});
```

### Alpine.js Component

```javascript
// Theme switcher Alpine component
function themeSwitcher() {
    return {
        currentTheme: 'dark',
        themes: [
            { name: 'light', label: 'Light', icon: '☀️' },
            { name: 'dark', label: 'Dark', icon: '🌙' },
            { name: 'synthwave', label: 'Synthwave', icon: '🌆' },
            { name: 'dracula', label: 'Dracula', icon: '🧛' },
            { name: 'cyberpunk', label: 'Cyberpunk', icon: '🤖' },
            { name: 'business', label: 'Business', icon: '💼' },
            { name: 'lofi', label: 'Lo-fi', icon: '🎵' },
            { name: 'forest', label: 'Forest', icon: '🌲' }
        ],

        init() {
            this.currentTheme = getCurrentTheme();
            window.addEventListener('themeChanged', (e) => {
                this.currentTheme = e.detail.theme;
            });
        },

        selectTheme(themeName) {
            setTheme(themeName);
        },

        isDark() {
            return !['light', 'lofi'].includes(this.currentTheme);
        }
    }
}
```

---

## 🎨 Theme-Specific Styling

### Custom CSS Overrides

```css
/* static/css/themes.css */

/* SP-404MK2 Custom Colors (applied to all themes) */
:root {
    --sp404-orange: #FF6B00;
    --sp404-cyan: #00D9FF;
    --sp404-red: #FF0033;
    --sp404-green: #00FF66;
}

/* Synthwave enhancements */
[data-theme="synthwave"] {
    --waveform-glow: 0 0 10px #FF00FF;
}

[data-theme="synthwave"] .sample-card:hover {
    box-shadow: 0 0 20px rgba(255, 0, 255, 0.5);
}

/* Cyberpunk enhancements */
[data-theme="cyberpunk"] {
    --grid-color: #00FFFF;
}

[data-theme="cyberpunk"] .pad-button:active {
    box-shadow: 0 0 15px currentColor;
}

/* Forest enhancements */
[data-theme="forest"] .waveform-progress {
    background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
}

/* Business professional tweaks */
[data-theme="business"] .navbar {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
```

---

## 🧩 Component Library

### Navigation Bar

**File**: `components/nav.html`

```html
<nav class="navbar bg-base-200 shadow-lg">
    <div class="flex-1">
        <a class="btn btn-ghost text-xl" href="/">
            <span class="text-primary">SP404</span>MK2
        </a>
    </div>

    <!-- Desktop Menu -->
    <div class="flex-none hidden md:flex">
        <ul class="menu menu-horizontal px-1">
            <li><a href="/pages/samples.html" hx-boost="true">📀 Samples</a></li>
            <li><a href="/pages/kits.html" hx-boost="true">🎛️ Kits</a></li>
            <li><a href="/pages/batch.html" hx-boost="true">⚡ Batch</a></li>
            <li><a href="/pages/vibe-analysis.html" hx-boost="true">🎵 Vibe</a></li>
        </ul>
    </div>

    <!-- Theme Switcher -->
    <div class="flex-none">
        {% include 'components/theme-switcher.html' %}
    </div>

    <!-- Mobile Menu -->
    <div class="flex-none md:hidden">
        <button class="btn btn-square btn-ghost" onclick="mobileMenu.showModal()">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
        </button>
    </div>
</nav>

<!-- Mobile Menu Modal -->
<dialog id="mobileMenu" class="modal modal-bottom md:hidden">
    <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">Menu</h3>
        <ul class="menu menu-lg">
            <li><a href="/pages/samples.html">📀 Samples</a></li>
            <li><a href="/pages/kits.html">🎛️ Kits</a></li>
            <li><a href="/pages/batch.html">⚡ Batch</a></li>
            <li><a href="/pages/vibe-analysis.html">🎵 Vibe</a></li>
        </ul>
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>
```

### Theme Switcher Component

**File**: `components/theme-switcher.html`

```html
<div x-data="themeSwitcher()" class="dropdown dropdown-end">
    <label tabindex="0" class="btn btn-ghost btn-circle" aria-label="Change theme">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path x-show="isDark()" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
            <path x-show="!isDark()" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
        </svg>
    </label>

    <ul tabindex="0" class="dropdown-content z-50 menu p-2 shadow-lg bg-base-100 rounded-box w-52 mt-4">
        <li class="menu-title">
            <span>Choose Theme</span>
        </li>
        <template x-for="theme in themes" :key="theme.name">
            <li>
                <a @click="selectTheme(theme.name)"
                   :class="{ 'active': currentTheme === theme.name }">
                    <span x-text="theme.icon"></span>
                    <span x-text="theme.label"></span>
                    <svg x-show="currentTheme === theme.name" class="w-4 h-4 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                    </svg>
                </a>
            </li>
        </template>

        <div class="divider my-1"></div>

        <li>
            <a @click="toggleDarkMode()">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"/>
                </svg>
                Quick Toggle Dark/Light
            </a>
        </li>
    </ul>
</div>
```

### Footer Component

**File**: `components/footer.html`

```html
<footer class="footer footer-center p-10 bg-base-200 text-base-content mt-12">
    <nav class="grid grid-flow-col gap-4">
        <a class="link link-hover" href="/pages/samples.html">Samples</a>
        <a class="link link-hover" href="/pages/kits.html">Kits</a>
        <a class="link link-hover" href="/pages/batch.html">Batch</a>
        <a class="link link-hover" href="https://github.com/yourusername/sp404mk2-sample-agent" target="_blank">GitHub</a>
    </nav>
    <aside>
        <p class="text-sm opacity-70">
            SP404MK2 Sample Manager &copy; 2025 - AI-Powered Sample Collection
        </p>
    </aside>
</footer>
```

---

## 🎨 Color System Design

### DaisyUI Semantic Colors

All themes use these semantic color names:

| Color Variable | Purpose | Example |
|----------------|---------|---------|
| `primary` | Main brand color | Buttons, links, accents |
| `secondary` | Supporting color | Alternative actions |
| `accent` | Highlights | Tags, badges, special items |
| `neutral` | Text and borders | Body text, dividers |
| `base-100` | Background | Main content area |
| `base-200` | Card background | Cards, panels |
| `base-300` | Hover states | Interactive elements |
| `info` | Informational | Info messages |
| `success` | Positive actions | Confirmations, completed |
| `warning` | Caution | Warnings, alerts |
| `error` | Errors | Error messages, delete |

### Usage Example

```html
<!-- Good: Uses semantic colors -->
<button class="btn btn-primary">Upload</button>
<div class="bg-base-200 p-4">Card content</div>
<span class="text-base-content/70">Secondary text</span>

<!-- Avoid: Hard-coded colors -->
<button class="bg-blue-500">Upload</button>
<div class="bg-gray-800 p-4">Card content</div>
```

---

## 📱 Responsive Design Patterns

### Mobile-First Grid System

```html
<!-- Responsive grid pattern -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    <!-- Content adapts from 1→2→3→4 columns -->
</div>
```

### Mobile Navigation

- **Desktop**: Horizontal menu in navbar
- **Mobile**: Bottom drawer or hamburger menu
- **Breakpoint**: `md` (768px)

### Touch-Friendly Sizing

```css
/* Minimum touch target: 44x44px */
.btn { min-height: 44px; min-width: 44px; }
```

---

## 🚀 Creating New Pages

### Step-by-Step Guide

#### 1. Create Page File

```bash
touch frontend/pages/my-new-page.html
```

#### 2. Use Base Template

```html
{% extends "components/base.html" %}

{% block head %}
    <title>My New Page - SP404MK2</title>
    <!-- Page-specific meta tags or CSS -->
{% endblock %}

{% block content %}
    <div class="my-new-page">
        <!-- Page header -->
        <div class="mb-8">
            <h1 class="text-3xl font-bold mb-2">My New Page</h1>
            <p class="text-base-content/70">Page description goes here</p>
        </div>

        <!-- Main content -->
        <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
                <h2 class="card-title">Section Title</h2>
                <p>Your content here...</p>

                <!-- Use DaisyUI components -->
                <div class="card-actions justify-end">
                    <button class="btn btn-primary">Action</button>
                </div>
            </div>
        </div>
    </div>
{% endblock %}

{% block scripts %}
    <script>
        // Alpine.js components specific to this page
        function myPageComponent() {
            return {
                data: [],
                loading: false,

                init() {
                    this.loadData();
                },

                async loadData() {
                    this.loading = true;
                    // Fetch data
                    this.loading = false;
                }
            }
        }
    </script>
{% endblock %}
```

#### 3. Add to Navigation

Edit `components/nav.html`:

```html
<li><a href="/pages/my-new-page.html" hx-boost="true">🎯 My Page</a></li>
```

#### 4. Add Backend Route (if needed)

Edit `backend/app/main.py`:

```python
from fastapi.responses import HTMLResponse

@app.get("/pages/my-new-page.html", response_class=HTMLResponse)
async def my_new_page():
    return templates.TemplateResponse("pages/my-new-page.html", {
        "request": request
    })
```

#### 5. Add E2E Test

Create `frontend/tests/e2e/my-new-page.spec.js`:

```javascript
import { test, expect } from '@playwright/test';

test.describe('My New Page', () => {
    test('should load page successfully', async ({ page }) => {
        await page.goto('/pages/my-new-page.html');

        // Check title
        await expect(page).toHaveTitle(/My New Page/);

        // Check main heading
        const heading = page.locator('h1');
        await expect(heading).toContainText('My New Page');
    });

    test('should respect theme', async ({ page }) => {
        await page.goto('/pages/my-new-page.html');

        // Check theme attribute
        const html = page.locator('html');
        const theme = await html.getAttribute('data-theme');
        expect(['light', 'dark']).toContain(theme);
    });
});
```

---

## 🎨 UI/UX Design Patterns

### 1. Page Header Pattern

```html
<div class="mb-8">
    <h1 class="text-3xl font-bold mb-2">Page Title</h1>
    <p class="text-base-content/70">Brief description of page purpose</p>
</div>
```

### 2. Card Pattern

```html
<div class="card bg-base-100 shadow-xl">
    <div class="card-body">
        <h2 class="card-title">Card Title</h2>
        <p>Card content goes here.</p>
        <div class="card-actions justify-end">
            <button class="btn btn-primary">Action</button>
        </div>
    </div>
</div>
```

### 3. Form Pattern

```html
<form hx-post="/api/endpoint" hx-target="#result">
    <div class="form-control w-full">
        <label class="label">
            <span class="label-text">Field Label</span>
        </label>
        <input type="text"
               name="field_name"
               placeholder="Enter value..."
               class="input input-bordered w-full"
               required>
        <label class="label">
            <span class="label-text-alt text-base-content/50">Helper text</span>
        </label>
    </div>

    <div class="form-control mt-6">
        <button type="submit" class="btn btn-primary">
            Submit
            <span class="htmx-indicator loading loading-spinner loading-sm"></span>
        </button>
    </div>
</form>

<div id="result"></div>
```

### 4. Filter Panel Pattern

```html
<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
    <div class="form-control">
        <input type="search"
               name="search"
               placeholder="Search..."
               class="input input-bordered"
               hx-get="/api/items"
               hx-trigger="keyup changed delay:300ms"
               hx-target="#results">
    </div>

    <div class="form-control">
        <select name="category"
                class="select select-bordered"
                hx-get="/api/items"
                hx-trigger="change"
                hx-target="#results">
            <option value="">All Categories</option>
            <option value="cat1">Category 1</option>
        </select>
    </div>

    <div class="form-control">
        <button class="btn btn-primary">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Add New
        </button>
    </div>
</div>

<div id="results" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Results load here -->
</div>
```

### 5. Modal Pattern

```html
<button class="btn" onclick="myModal.showModal()">Open Modal</button>

<dialog id="myModal" class="modal">
    <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">Modal Title</h3>

        <p class="py-4">Modal content goes here.</p>

        <div class="modal-action">
            <button type="button" class="btn" onclick="myModal.close()">Cancel</button>
            <button type="submit" class="btn btn-primary">Confirm</button>
        </div>
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>
```

### 6. Loading State Pattern

```html
<div id="content"
     hx-get="/api/data"
     hx-trigger="load"
     hx-indicator="#loading">

    <div id="loading" class="htmx-indicator">
        <div class="flex justify-center items-center p-12">
            <span class="loading loading-spinner loading-lg"></span>
        </div>
    </div>
</div>
```

### 7. Empty State Pattern

```html
<div class="hero min-h-[400px]">
    <div class="hero-content text-center">
        <div class="max-w-md">
            <svg class="w-24 h-24 mx-auto mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
            </svg>
            <h2 class="text-2xl font-bold mb-2">No Items Found</h2>
            <p class="text-base-content/70 mb-6">
                Get started by uploading your first sample.
            </p>
            <button class="btn btn-primary">Upload Sample</button>
        </div>
    </div>
</div>
```

---

## 🧪 Testing New Pages

### Test Checklist

- [ ] Page loads without errors
- [ ] Theme switcher works
- [ ] Mobile responsive layout
- [ ] HTMX requests work
- [ ] Alpine.js components initialize
- [ ] Accessibility (ARIA labels, keyboard nav)
- [ ] Loading states display correctly
- [ ] Error handling works

### Run Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run specific test file
npx playwright test my-new-page.spec.js

# Debug mode
npm run test:e2e:debug

# UI mode
npm run test:e2e:ui
```

---

## 🎨 Design Tokens

### Spacing Scale

```
xs:  0.25rem  (4px)
sm:  0.5rem   (8px)
md:  1rem     (16px)
lg:  1.5rem   (24px)
xl:  2rem     (32px)
2xl: 3rem     (48px)
```

### Border Radius

```
none:    0
sm:      0.125rem
DEFAULT: 0.25rem
md:      0.375rem
lg:      0.5rem
xl:      0.75rem
2xl:     1rem
full:    9999px
```

### Typography

```
text-xs:   0.75rem    (12px)
text-sm:   0.875rem   (14px)
text-base: 1rem       (16px)
text-lg:   1.125rem   (18px)
text-xl:   1.25rem    (20px)
text-2xl:  1.5rem     (24px)
text-3xl:  1.875rem   (30px)
text-4xl:  2.25rem    (36px)
```

---

## 🚀 Quick Reference

### Common Tasks

**Add new page**:
1. Create `pages/my-page.html` extending `base.html`
2. Add to `components/nav.html`
3. Create E2E test

**Add new component**:
1. Create `components/my-component.html`
2. Include in pages with `{% include 'components/my-component.html' %}`

**Change theme**:
- User: Click theme switcher in navbar
- Developer: Modify `ALL_THEMES` array in `theme.js`

**Add custom theme**:
1. Add theme name to `ALL_THEMES`
2. Add to `themes` array in `themeSwitcher()` component
3. Add theme-specific CSS in `themes.css`

---

## 📚 Resources

- [DaisyUI Documentation](https://daisyui.com/)
- [Tailwind CSS Docs](https://tailwindcss.com/)
- [HTMX Documentation](https://htmx.org/)
- [Alpine.js Guide](https://alpinejs.dev/)
- [Playwright Testing](https://playwright.dev/)

---

*Last Updated: 2025-01-13*
*Version: 1.0.0*
