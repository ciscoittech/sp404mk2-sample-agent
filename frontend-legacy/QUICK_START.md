# 🚀 Quick Start Guide - Building New Pages

## TL;DR - Create a New Page in 3 Steps

```bash
# 1. Copy the template
cp frontend/pages/dashboard.html frontend/pages/my-new-page.html

# 2. Edit the content blocks
# 3. Add to navigation in components/nav.html

# Done! Your page now has:
# ✅ Shared navigation with theme switcher
# ✅ Responsive footer
# ✅ All 8 theme options
# ✅ Alpine.js and HTMX ready
# ✅ Consistent styling
```

---

## 📋 Page Template Anatomy

Every page extends `components/base.html` and has these blocks:

```html
{% extends "components/base.html" %}

{% block title %}My Page - SP404MK2{% endblock %}

{% block head %}
    <!-- Optional: Page-specific CSS or meta tags -->
{% endblock %}

{% block content %}
    <!-- Your page content goes here -->
{% endblock %}

{% block scripts %}
    <!-- Optional: Page-specific JavaScript -->
{% endblock %}
```

---

## 🎨 Using DaisyUI Components

### Cards

```html
<div class="card bg-base-100 shadow-xl">
    <div class="card-body">
        <h2 class="card-title">Card Title</h2>
        <p>Card content here.</p>
        <div class="card-actions justify-end">
            <button class="btn btn-primary">Action</button>
        </div>
    </div>
</div>
```

### Forms

```html
<div class="form-control w-full">
    <label class="label">
        <span class="label-text">Label</span>
        <span class="label-text-alt">Optional hint</span>
    </label>
    <input type="text"
           placeholder="Type here"
           class="input input-bordered w-full"
           required>
    <label class="label">
        <span class="label-text-alt text-error">Error message</span>
    </label>
</div>
```

### Buttons

```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-accent">Accent</button>
<button class="btn btn-ghost">Ghost</button>
<button class="btn btn-outline">Outline</button>

<!-- With icon -->
<button class="btn btn-primary">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
    </svg>
    Add New
</button>
```

### Modals

```html
<button class="btn" onclick="myModal.showModal()">Open Modal</button>

<dialog id="myModal" class="modal">
    <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">Modal Title</h3>
        <p class="py-4">Modal content here...</p>
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

### Stats

```html
<div class="stats shadow">
    <div class="stat">
        <div class="stat-figure text-primary">
            <svg class="w-8 h-8">...</svg>
        </div>
        <div class="stat-title">Total Samples</div>
        <div class="stat-value text-primary">342</div>
        <div class="stat-desc">+12 this week</div>
    </div>
</div>
```

---

## 🔥 Using HTMX

### Load Content on Page Load

```html
<div id="content"
     hx-get="/api/v1/endpoint"
     hx-trigger="load"
     hx-target="#content">
    <div class="loading loading-spinner"></div>
</div>
```

### Form Submission

```html
<form hx-post="/api/v1/endpoint"
      hx-target="#result"
      hx-swap="innerHTML">
    <input type="text" name="field" class="input input-bordered">
    <button type="submit" class="btn btn-primary">
        Submit
        <span class="htmx-indicator loading loading-spinner loading-sm"></span>
    </button>
</form>
<div id="result"></div>
```

### Search with Debounce

```html
<input type="search"
       hx-get="/api/v1/search"
       hx-trigger="keyup changed delay:300ms"
       hx-target="#results"
       placeholder="Search...">
<div id="results"></div>
```

### Polling

```html
<div hx-get="/api/v1/status"
     hx-trigger="load, every 5s"
     hx-swap="innerHTML">
    <!-- Auto-updates every 5 seconds -->
</div>
```

---

## 🎭 Using Alpine.js

### Basic Component

```html
<div x-data="{ open: false }">
    <button @click="open = !open" class="btn">Toggle</button>
    <div x-show="open" class="alert">Content visible when open</div>
</div>
```

### Using Global Components

```html
<!-- Audio Player -->
<div x-data="samplePlayer('/path/to/audio.mp3')">
    <button @click="togglePlay()" class="btn btn-circle">
        <svg x-show="!playing">...</svg>
        <svg x-show="playing">...</svg>
    </button>
    <span x-text="formatTime(currentTime)"></span>
</div>

<!-- Theme Switcher (already included in nav) -->
<!-- Filter Component -->
<div x-data="sampleFilters()">
    <input x-model="search" type="search">
    <button @click="clearFilters()">Clear</button>
</div>
```

---

## 🎨 Theme-Aware Styling

Always use semantic DaisyUI colors - they adapt to all themes:

```html
<!-- Good ✅ -->
<div class="bg-base-100 text-base-content">
    <p class="text-primary">Primary colored text</p>
    <button class="btn btn-secondary">Secondary button</button>
</div>

<!-- Bad ❌ -->
<div class="bg-gray-800 text-white">
    <p class="text-blue-500">This won't adapt to themes!</p>
</div>
```

### Semantic Color Variables

- `primary` - Main brand color
- `secondary` - Supporting color
- `accent` - Highlights
- `base-100` - Main background
- `base-200` - Card/panel background
- `base-300` - Hover states
- `base-content` - Text color
- `info`, `success`, `warning`, `error` - Status colors

---

## 📱 Responsive Design

Use Tailwind's responsive prefixes:

```html
<!-- Mobile-first approach -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    <!-- 1 column mobile, 2 tablet, 3 desktop, 4 wide -->
</div>

<h1 class="text-2xl md:text-3xl lg:text-4xl">
    <!-- Smaller on mobile, larger on desktop -->
</h1>

<div class="hidden md:block">
    <!-- Hidden on mobile, visible on desktop -->
</div>

<div class="md:hidden">
    <!-- Visible on mobile, hidden on desktop -->
</div>
```

### Breakpoints

- `sm`: 640px (mobile landscape)
- `md`: 768px (tablet)
- `lg`: 1024px (desktop)
- `xl`: 1280px (large desktop)
- `2xl`: 1536px (wide desktop)

---

## 🧪 Testing Your Page

### 1. Visual Test

1. Start dev server: `npm run dev`
2. Open http://localhost:5173/pages/your-page.html
3. Test on mobile (Chrome DevTools → Device Toolbar)
4. Try all 8 themes (use theme switcher in nav)

### 2. Write E2E Test

```javascript
// frontend/tests/e2e/my-page.spec.js
import { test, expect } from '@playwright/test';

test.describe('My New Page', () => {
    test('should load successfully', async ({ page }) => {
        await page.goto('/pages/my-new-page.html');

        // Check title
        await expect(page).toHaveTitle(/My New Page/);

        // Check heading
        const heading = page.locator('h1');
        await expect(heading).toContainText('My New Page');
    });

    test('should be responsive', async ({ page }) => {
        // Desktop
        await page.setViewportSize({ width: 1920, height: 1080 });
        await page.goto('/pages/my-new-page.html');
        // Test desktop layout

        // Mobile
        await page.setViewportSize({ width: 375, height: 667 });
        // Test mobile layout
    });

    test('should work with all themes', async ({ page }) => {
        await page.goto('/pages/my-new-page.html');

        const themes = ['dark', 'light', 'synthwave', 'cyberpunk'];
        for (const theme of themes) {
            await page.evaluate((t) => setTheme(t), theme);
            await page.waitForTimeout(100);
            // Verify page looks good
        }
    });
});
```

### 3. Run Tests

```bash
npm run test:e2e                # Run all tests
npm run test:e2e:ui             # Interactive UI mode
npx playwright test my-page     # Run specific test
```

---

## 🎯 Common Patterns

### Page Header

```html
<div class="mb-8">
    <h1 class="text-3xl md:text-4xl font-bold mb-2">Page Title</h1>
    <p class="text-base-content/70">Brief description</p>
</div>
```

### Loading State

```html
<div id="content" hx-get="/api/data" hx-trigger="load">
    <div class="flex justify-center items-center p-12">
        <span class="loading loading-spinner loading-lg"></span>
    </div>
</div>
```

### Empty State

```html
<div class="hero min-h-[400px]">
    <div class="hero-content text-center">
        <div class="max-w-md">
            <svg class="w-24 h-24 mx-auto mb-4 opacity-30">...</svg>
            <h2 class="text-2xl font-bold mb-2">No Items Found</h2>
            <p class="text-base-content/70 mb-6">
                Get started by creating your first item.
            </p>
            <button class="btn btn-primary">Create Item</button>
        </div>
    </div>
</div>
```

### Error State

```html
<div class="alert alert-error">
    <svg class="w-6 h-6">...</svg>
    <span>Error message here</span>
</div>
```

### Success Message

```html
<div class="alert alert-success">
    <svg class="w-6 h-6">...</svg>
    <span>Success message here</span>
</div>
```

---

## 🎨 Keyboard Shortcuts

- **Ctrl+Shift+T**: Cycle through themes
- Themes persist in localStorage automatically

---

## 📚 Resources

- **DaisyUI Components**: https://daisyui.com/components/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **HTMX Docs**: https://htmx.org/docs/
- **Alpine.js Guide**: https://alpinejs.dev/start-here

---

## 🐛 Troubleshooting

### Page doesn't extend base template

**Error**: `TemplateNotFound: components/base.html`

**Fix**: Make sure you're using Jinja2 syntax:
```html
{% extends "components/base.html" %}
```

### Theme not applying

**Fix**: Check `data-theme` attribute on `<html>`:
```javascript
// In browser console
console.log(document.documentElement.getAttribute('data-theme'));
```

### HTMX not working

**Fix**: Check browser console for errors. Common issues:
- Wrong endpoint URL
- Missing `hx-target`
- CORS issues (use Vite proxy)

### Alpine.js component not initializing

**Fix**: Make sure function is defined in `components.js` or inline before use:
```html
<script>
function myComponent() {
    return { /* ... */ };
}
</script>
<div x-data="myComponent()">...</div>
```

---

**Happy Building! 🎉**

For detailed documentation, see [THEME_SYSTEM_GUIDE.md](./THEME_SYSTEM_GUIDE.md)
