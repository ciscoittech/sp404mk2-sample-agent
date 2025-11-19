import { test, expect } from '@playwright/test';

test('samples page shows samples without auth check', async ({ page }) => {
  // Skip auth for now - just check if page loads
  await page.goto('/pages/samples.html');
  
  // Check that the page loaded
  await expect(page.locator('h1')).toHaveText('Sample Library');
  
  // The grid should exist
  const grid = await page.locator('#sample-grid');
  await expect(grid).toBeVisible();
});