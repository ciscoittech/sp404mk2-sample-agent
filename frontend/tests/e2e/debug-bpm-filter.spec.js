import { test, expect } from '@playwright/test';

test('BPM filter sends correct request', async ({ page }) => {
  await page.goto('/pages/samples.html');
  await page.waitForSelector('.card', { timeout: 5000 });
  
  // Set up response promise before filling the input
  const responsePromise = page.waitForResponse(resp => 
    resp.url().includes('/api/v1/public/samples/') && 
    resp.url().includes('bpm-min=90')
  );
  
  // Fill BPM min
  const bpmMin = page.locator('input[name="bpm-min"]');
  await bpmMin.fill('90');
  
  // Wait for the value to be set
  await expect(bpmMin).toHaveValue('90');
  
  // Trigger change event
  await bpmMin.blur();
  
  // Verify filter request was made
  const response = await responsePromise;
  expect(response.status()).toBe(200);
});