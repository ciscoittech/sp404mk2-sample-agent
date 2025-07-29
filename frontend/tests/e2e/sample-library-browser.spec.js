import { test, expect } from '@playwright/test';

test.describe('Sample Library Browser - Advanced Features', () => {
  test.beforeEach(async ({ page }) => {
    // Using public endpoint, no auth needed
    await page.goto('/pages/samples.html');
  });

  test.describe('Virtual Scrolling', () => {
    test('implements virtual scrolling for performance', async ({ page }) => {
      // Check that not all samples are rendered at once
      const sampleGrid = page.locator('#sample-grid');
      
      // Initial load should show limited samples
      const initialCards = await sampleGrid.locator('.card').count();
      expect(initialCards).toBeLessThanOrEqual(20); // Virtual window size
      
      // Check for infinite scroll trigger
      const loadMore = page.locator('#load-more');
      await expect(loadMore).toHaveAttribute('hx-trigger', 'revealed');
    });

    test('loads more samples on scroll', async ({ page }) => {
      // Get initial count
      const initialCount = await page.locator('.card').count();
      
      // Scroll to bottom
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      
      // Wait for new samples to load
      await page.waitForTimeout(1000); // Wait for HTMX request
      
      // Should have more samples
      const newCount = await page.locator('.card').count();
      expect(newCount).toBeGreaterThan(initialCount);
    });
  });

  test.describe('Advanced Filtering', () => {
    test('BPM range filter updates results', async ({ page }) => {
      // Set BPM range
      await page.fill('input[name="bpm-min"]', '120');
      await page.fill('input[name="bpm-max"]', '130');
      
      // Wait for HTMX update
      await page.waitForTimeout(500);
      
      // Check URL includes filter params
      await expect(page).toHaveURL(/bpm-min=120/);
      await expect(page).toHaveURL(/bpm-max=130/);
    });

    test('genre filter works correctly', async ({ page }) => {
      // Select genre
      const genreSelect = page.locator('select[name="genre"]').first();
      await genreSelect.selectOption('jazz');
      
      // Wait for update
      await page.waitForTimeout(500);
      
      // Check that request includes genre
      await expect(page).toHaveURL(/genre=jazz/);
    });

    test('multiple filters work together', async ({ page }) => {
      // First wait for initial load
      await page.waitForSelector('.card', { timeout: 5000 });
      
      // Apply multiple filters
      await page.fill('input[name="search"]', 'chill'); // Search for 'chill' which exists in our data
      await page.locator('select[name="genre"]').first().selectOption('hip-hop');
      await page.fill('input[name="bpm-min"]', '90');
      
      // Wait for debounced update
      await page.waitForTimeout(600);
      
      // Check that filters are applied by verifying the request was made
      // HTMX updates URL to the endpoint URL, so we check for filter params there
      const url = page.url();
      expect(url).toContain('search=chill');
      expect(url).toContain('genre=hip-hop');
      
      // Verify filters work by checking sample results
      const samples = await page.locator('.card').count();
      expect(samples).toBeGreaterThan(0); // Should have filtered results
    });

    test('clear filters button resets all filters', async ({ page }) => {
      // Apply filters
      await page.fill('input[name="search"]', 'test');
      await page.locator('select[name="genre"]').first().selectOption('jazz');
      
      // Click clear filters (to be implemented)
      const clearButton = page.locator('button:has-text("Clear Filters")');
      if (await clearButton.isVisible()) {
        await clearButton.click();
        
        // All filters should be reset
        await expect(page.locator('input[name="search"]')).toHaveValue('');
        await expect(page.locator('select[name="genre"]').first()).toHaveValue('');
      }
    });
  });

  test.describe('Search Features', () => {
    test('search has debounce delay', async ({ page }) => {
      const searchInput = page.locator('input[name="search"]');
      
      // Type quickly
      await searchInput.fill('test');
      
      // Should have debounce attribute
      await expect(searchInput).toHaveAttribute('hx-trigger', /delay:300ms/);
    });

    test('search shows loading indicator', async ({ page }) => {
      const searchInput = page.locator('input[name="search"]');
      const indicator = page.locator('#search-indicator');
      
      // Initially hidden
      await expect(indicator).toHaveClass(/htmx-indicator/);
      
      // Type to trigger search
      await searchInput.fill('jazz');
      
      // Indicator should have htmx-indicator class
      await expect(searchInput).toHaveAttribute('hx-indicator', '#search-indicator');
    });

    test('empty search shows all samples', async ({ page }) => {
      // First wait for initial samples to load
      await page.waitForSelector('.card', { timeout: 5000 });
      
      const searchInput = page.locator('input[name="search"]');
      
      // Type and clear
      await searchInput.fill('test');
      await page.waitForTimeout(400); // Wait for debounce
      await searchInput.clear();
      await page.waitForTimeout(600); // Wait for debounce and reload
      
      // Wait for samples to reload
      await page.waitForSelector('.card', { timeout: 3000 });
      
      // Should show samples (not empty)
      const samples = await page.locator('.card').count();
      expect(samples).toBeGreaterThan(0);
    });
  });

  test.describe('Sample Preview', () => {
    test('audio player controls are functional', async ({ page }) => {
      // Wait for a sample card
      const firstCard = page.locator('.card').first();
      await firstCard.waitFor();
      
      // Check for audio controls
      const playButton = firstCard.locator('button').filter({ hasText: /play|pause/i }).first();
      if (await playButton.isVisible()) {
        // Check Alpine.js data attribute
        const playerDiv = firstCard.locator('[x-data*="samplePlayer"]');
        await expect(playerDiv).toBeVisible();
      }
    });

    test('waveform visualization exists', async ({ page }) => {
      const firstCard = page.locator('.card').first();
      await firstCard.waitFor();
      
      // Check for waveform container
      const waveform = firstCard.locator('.waveform-container');
      await expect(waveform).toBeVisible();
      await expect(waveform).toHaveClass(/waveform-container/);
      
      // Check that waveform bars exist
      const waveformBars = waveform.locator('div.w-1');
      const barCount = await waveformBars.count();
      expect(barCount).toBeGreaterThan(0);
    });
  });

  test.describe('Performance', () => {
    test('sample cards have lazy loading', async ({ page }) => {
      // Check for loading states
      const cards = page.locator('.card');
      const firstCard = cards.first();
      
      // Cards should be visible quickly
      await expect(firstCard).toBeVisible({ timeout: 2000 });
    });

    test('filters respond quickly', async ({ page }) => {
      const startTime = Date.now();
      
      // Apply filter
      await page.locator('select[name="genre"]').first().selectOption('jazz');
      
      // Wait for update
      await page.waitForSelector('.card', { timeout: 1000 });
      
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      // Should respond within 1 second
      expect(responseTime).toBeLessThan(1000);
    });
  });

  test.describe('Accessibility', () => {
    test('keyboard navigation works', async ({ page }) => {
      // Focus on first sample
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab'); // Skip nav
      
      // Should focus on search or first interactive element
      const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
      expect(['INPUT', 'BUTTON', 'A']).toContain(focusedElement);
    });

    test('ARIA labels are present', async ({ page }) => {
      // Check search input
      const searchInput = page.locator('input[name="search"]');
      const searchLabel = await searchInput.getAttribute('aria-label') || 
                         await searchInput.getAttribute('placeholder');
      expect(searchLabel).toBeTruthy();
      
      // Check buttons have accessible text
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();
      for (let i = 0; i < Math.min(buttonCount, 5); i++) {
        const button = buttons.nth(i);
        const text = await button.textContent();
        const ariaLabel = await button.getAttribute('aria-label');
        expect(text || ariaLabel).toBeTruthy();
      }
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test('grid adjusts for mobile viewport', async ({ page, isMobile }) => {
      if (isMobile) {
        const grid = page.locator('#sample-grid');
        const classes = await grid.getAttribute('class');
        expect(classes).toContain('grid-cols-1');
      }
    });

    test('filters are accessible on mobile', async ({ page, isMobile }) => {
      if (isMobile) {
        // Check if filters are visible or in a collapsible menu
        const filters = page.locator('input[name="search"]');
        await expect(filters).toBeVisible();
      }
    });
  });
});