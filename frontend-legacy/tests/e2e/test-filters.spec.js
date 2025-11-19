import { test, expect } from '@playwright/test';

test.describe('Filter Tests', () => {
  test.beforeEach(async ({ page }) => {
    // No authentication needed - using public API
    await page.goto('/pages/samples.html');
  });

  test('samples load on page', async ({ page }) => {
    // Wait for initial loading spinner to disappear
    await page.waitForSelector('.loading', { state: 'hidden', timeout: 5000 });
    
    // Wait for sample cards to appear
    await page.waitForSelector('.card', { timeout: 5000 });
    
    const cards = await page.locator('.card').count();
    expect(cards).toBeGreaterThan(0);
  });

  test('BPM filter sends request with correct params', async ({ page }) => {
    // Set BPM range
    await page.fill('input[name="bpm-min"]', '120');
    await page.fill('input[name="bpm-max"]', '130');
    
    // Verify filter request was made with both parameters
    const response = await page.waitForResponse(resp => {
      const url = resp.url();
      return url.includes('/api/v1/public/samples/') && 
             url.includes('bpm-min=120') &&
             url.includes('bpm-max=130');
    }, { timeout: 2000 });
    
    expect(response.status()).toBe(200);
  });
});