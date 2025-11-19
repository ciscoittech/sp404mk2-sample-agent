import { test, expect } from '@playwright/test';

/**
 * TDD RED PHASE: Kit Builder Template Loading Fix
 *
 * This test documents the expected behavior for the Kit Builder page.
 * Currently FAILING because the page displays Usage dashboard content
 * instead of Kit Builder content due to a race condition in template loading.
 *
 * Root Cause: Sidebar's embedded JavaScript executes before page-specific
 * template injection, causing usage content to be displayed.
 *
 * Expected Fix: Extract sidebar initialization to separate module and
 * ensure proper load order.
 */

test.describe('Kit Builder Page - Template Loading Fix (RED → GREEN → REFACTOR)', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to kits page
    await page.goto('/pages/kits.html');

    // Wait for page to fully load
    await page.waitForLoadState('networkidle');

    // Wait for Alpine.js to initialize (used in kit builder)
    await page.waitForFunction(() => window.Alpine !== undefined, { timeout: 5000 });

    // Give template injection time to complete (or fail)
    await page.waitForTimeout(2000);
  });

  test('should display Kit Builder heading, not Usage dashboard', async ({ page }) => {
    // EXPECTED: Kit Builder heading should be visible
    const kitBuilderHeading = page.getByRole('heading', { name: 'Kit Builder', level: 1 });
    await expect(kitBuilderHeading).toBeVisible({ timeout: 5000 });

    // EXPECTED: Kit Builder description should be visible
    const description = page.getByText('Organize your samples into SP-404MK2 kits');
    await expect(description).toBeVisible();

    // EXPECTED: Should NOT show Usage dashboard heading
    const usageHeading = page.getByRole('heading', { name: /API Usage|Usage & Costs/i });
    await expect(usageHeading).not.toBeVisible();
  });

  test('should display New Kit button', async ({ page }) => {
    // EXPECTED: New Kit button should be visible and functional
    const newKitButton = page.getByRole('button', { name: /New Kit/i });
    await expect(newKitButton).toBeVisible({ timeout: 5000 });
  });

  test('should display kit list container with HTMX attributes', async ({ page }) => {
    // EXPECTED: Kit list div should exist in DOM
    const kitList = page.locator('#kit-list');
    await expect(kitList).toBeAttached();

    // EXPECTED: Should have HTMX attributes for loading kits
    const hxGet = await kitList.getAttribute('hx-get');
    expect(hxGet).toBe('/api/v1/kits');

    const hxTrigger = await kitList.getAttribute('hx-trigger');
    expect(hxTrigger).toBe('load');
  });

  test('should display "Your Kits" subheading', async ({ page }) => {
    // EXPECTED: Your Kits heading should be visible
    const yourKitsHeading = page.getByRole('heading', { name: 'Your Kits', level: 2 });
    await expect(yourKitsHeading).toBeVisible({ timeout: 5000 });
  });

  test('should have correct page title', async ({ page }) => {
    // EXPECTED: Browser tab title should be correct
    await expect(page).toHaveTitle('Kit Builder - SP404MK2 Sample Manager');
  });

  test('should not have JavaScript console errors', async ({ page }) => {
    const consoleErrors = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        // Filter out expected Tailwind CDN warning
        if (!msg.text().includes('Tailwind')) {
          consoleErrors.push(msg.text());
        }
      }
    });

    // Reload page to capture all console messages
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // EXPECTED: No JavaScript errors (except Tailwind CDN warning)
    expect(consoleErrors).toHaveLength(0);
  });

  test('should have kits-page class on main container', async ({ page }) => {
    // EXPECTED: Main content should have kits-page class
    const kitsPage = page.locator('.kits-page');
    await expect(kitsPage).toBeAttached();
  });

  test('sidebar should be loaded and contain navigation links', async ({ page }) => {
    // EXPECTED: Sidebar should exist
    const sidebar = page.locator('#sidebar-container');
    await expect(sidebar).toBeAttached();

    // EXPECTED: Should have navigation link to Kits page
    const kitsLink = page.getByRole('link', { name: /Kits|Sample kits/i });
    await expect(kitsLink).toBeVisible();
  });
});
