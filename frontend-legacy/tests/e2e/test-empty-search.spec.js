import { test, expect } from '@playwright/test';

test('debug empty search issue', async ({ page }) => {
  await page.goto('/pages/samples.html');
  
  // Wait for initial load
  await page.waitForSelector('.card', { timeout: 5000 });
  const initialCount = await page.locator('.card').count();
  console.log('Initial sample count:', initialCount);
  
  // Type in search
  await page.fill('input[name="search"]', 'test');
  await page.waitForTimeout(400);
  
  // Clear search
  await page.fill('input[name="search"]', '');
  await page.waitForTimeout(400);
  
  // Check what happens
  const afterClearCount = await page.locator('.card').count();
  console.log('After clear count:', afterClearCount);
  
  // Check if loading spinner is visible (there might be multiple)
  const loadingSpinners = await page.locator('.loading').count();
  console.log('Loading spinners count:', loadingSpinners);
  
  // Check network activity
  const response = await page.waitForResponse(resp => 
    resp.url().includes('/api/v1/public/samples/') && 
    resp.status() === 200,
    { timeout: 2000 }
  ).catch(() => null);
  
  if (response) {
    const data = await response.json();
    console.log('Response data items:', data.items?.length || 0);
  }
  
  expect(afterClearCount).toBeGreaterThan(0);
});