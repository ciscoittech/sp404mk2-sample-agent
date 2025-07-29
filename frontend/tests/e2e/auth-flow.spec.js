import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.skip('login and view samples', async ({ page }) => {
    // Skip - login page not implemented yet
    // This test will be enabled when authentication UI is built
  });
  
  test('filters work with public API', async ({ page }) => {
    // Go directly to samples page (using public API, no login needed)
    await page.goto('/pages/samples.html');
    
    // Wait for initial load
    await page.waitForSelector('.card', { timeout: 10000 });
    
    // Set up response promise before filling the input
    const responsePromise = page.waitForResponse(resp => 
      resp.url().includes('/api/v1/public/samples/') && 
      resp.url().includes('bpm-min=120')
    );
    
    // Test BPM filter
    const bpmInput = page.locator('input[name="bpm-min"]');
    await bpmInput.fill('120');
    // Trigger change event since HTMX listens to change not input
    await bpmInput.blur(); // This triggers the change event
    
    // Wait for the response
    const response = await responsePromise;
    expect(response.status()).toBe(200);
  });
});