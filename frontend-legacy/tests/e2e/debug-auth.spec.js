import { test, expect } from '@playwright/test';

test('sample loading with public API', async ({ page }) => {
  // Using public API - no authentication needed
  await page.goto('/pages/samples.html');
  
  // Wait for any network activity to settle
  await page.waitForLoadState('networkidle');
  
  // Wait for samples to load
  await page.waitForSelector('.card', { timeout: 5000 });
  
  // Check if there are any sample cards
  const cards = await page.locator('.card').count();
  console.log('Number of cards found:', cards);
  
  // Check for any error messages
  const errorMessages = await page.locator('.error, .alert-error').count();
  if (errorMessages > 0) {
    console.log('Error messages found on page');
  }
  
  expect(cards).toBeGreaterThan(0);
});