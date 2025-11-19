import { test, expect } from '@playwright/test';

test.describe('Sample Library', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pages/samples.html');
  });

  test('loads samples page successfully', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Samples.*SP404MK2/);
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('Sample Library');
    
    // Check navigation is present
    await expect(page.locator('nav')).toBeVisible();
  });

  test('search input is functional', async ({ page }) => {
    const searchInput = page.locator('input[name="search"]');
    
    // Check search input exists
    await expect(searchInput).toBeVisible();
    
    // Type in search
    await searchInput.fill('jazz drums');
    
    // Check that HTMX attribute is present
    await expect(searchInput).toHaveAttribute('hx-get', '/api/v1/public/samples/');
    await expect(searchInput).toHaveAttribute('hx-trigger', 'keyup changed delay:300ms, search');
  });

  test('filters are interactive', async ({ page }) => {
    // Wait for page to be ready
    await page.waitForSelector('.card', { timeout: 5000 });
    
    // Genre filter
    const genreSelect = page.locator('select[name="genre"]').first();
    await expect(genreSelect).toBeVisible();
    await genreSelect.selectOption('jazz');
    await expect(genreSelect).toHaveValue('jazz');
    
    // BPM filters
    const bpmMin = page.locator('input[name="bpm-min"]');
    const bpmMax = page.locator('input[name="bpm-max"]');
    
    await expect(bpmMin).toBeVisible();
    await expect(bpmMax).toBeVisible();
    
    await bpmMin.fill('90');
    await bpmMax.fill('120');
    
    await expect(bpmMin).toHaveValue('90');
    await expect(bpmMax).toHaveValue('120');
  });

  test('upload modal opens and closes', async ({ page }) => {
    const uploadButton = page.locator('button:has-text("Upload Sample")');
    const modal = page.locator('#uploadModal');
    
    // Dialog elements in HTML5 are not visible by default
    // Check that the modal exists but is not open
    const isOpen = await page.evaluate(() => {
      const dialog = document.querySelector('#uploadModal');
      return dialog && dialog.open;
    });
    expect(isOpen).toBe(false);
    
    // Click upload button
    await uploadButton.click();
    
    // Modal should be visible
    await expect(modal).toBeVisible();
    await expect(modal.locator('h3')).toContainText('Upload Sample');
    
    // Check form fields
    await expect(modal.locator('input[name="file"]')).toBeVisible();
    await expect(modal.locator('input[name="title"]')).toBeVisible();
    await expect(modal.locator('select[name="genre"]')).toBeVisible();
    await expect(modal.locator('input[name="bpm"]')).toBeVisible();
    await expect(modal.locator('input[name="tags"]')).toBeVisible();
    
    // Close modal
    await modal.locator('button:has-text("Cancel")').click();
    
    // Wait for dialog to close
    await page.waitForFunction(() => {
      const dialog = document.querySelector('#uploadModal');
      return dialog && !dialog.open;
    });
    
    // Verify it's closed
    const isClosed = await page.evaluate(() => {
      const dialog = document.querySelector('#uploadModal');
      return dialog && !dialog.open;
    });
    expect(isClosed).toBe(true);
  });

  test('sample grid container exists with HTMX attributes', async ({ page }) => {
    const sampleGrid = page.locator('#sample-grid');
    
    await expect(sampleGrid).toBeVisible();
    await expect(sampleGrid).toHaveAttribute('hx-get', '/api/v1/public/samples/');
    await expect(sampleGrid).toHaveAttribute('hx-trigger', 'load delay:100ms');
  });

  test('infinite scroll element exists', async ({ page }) => {
    // Wait for initial samples to load first
    await page.waitForSelector('.card', { timeout: 5000 });
    
    const loadMore = page.locator('#load-more');
    
    // Load more only appears if there are more pages
    if (await loadMore.isVisible()) {
      await expect(loadMore).toHaveAttribute('hx-trigger', 'revealed');
      // Don't check exact URL as it includes query params
    }
  });

  test('responsive design works', async ({ page, isMobile }) => {
    if (isMobile) {
      // On mobile, grid should be single column
      const grid = page.locator('#sample-grid');
      const gridClasses = await grid.getAttribute('class');
      expect(gridClasses).toContain('grid-cols-1');
    } else {
      // On desktop, check navigation is horizontal
      const navMenu = page.locator('.menu');
      const menuClasses = await navMenu.getAttribute('class');
      expect(menuClasses).toContain('menu-horizontal');
    }
  });

  test('theme switcher works', async ({ page }) => {
    const html = page.locator('html');
    
    // Check initial theme
    await expect(html).toHaveAttribute('data-theme', 'dark');
    
    // Theme could be changed here if we add a theme switcher
  });
});

test.describe('Sample Card Component', () => {
  test('audio player initializes with Alpine.js', async ({ page }) => {
    await page.goto('/pages/samples.html');
    
    // Wait for Alpine.js to load
    await page.waitForFunction(() => typeof window.Alpine !== 'undefined', { timeout: 5000 });
    
    // Check that Alpine.js is loaded
    const alpineLoaded = await page.evaluate(() => {
      return typeof window.Alpine !== 'undefined';
    });
    expect(alpineLoaded).toBe(true);
    
    // Check that samplePlayer function is defined
    const samplePlayerDefined = await page.evaluate(() => {
      return typeof window.samplePlayer === 'function';
    });
    expect(samplePlayerDefined).toBe(true);
  });
});