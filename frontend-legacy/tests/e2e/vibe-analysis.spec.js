import { test, expect } from '@playwright/test';

test.describe('Real-time Vibe Analysis', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pages/vibe-analysis.html');
  });

  test('page loads with sample selector', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Vibe Analysis.*SP404MK2/);
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('Vibe Analysis');
    
    // Check sample selector exists
    const sampleSelect = page.locator('#sample-select');
    await expect(sampleSelect).toBeVisible();
    
    // Wait for samples to load
    await page.waitForFunction(() => {
      const select = document.getElementById('sample-select');
      return select && select.options.length > 1;
    }, { timeout: 5000 });
    
    // Verify samples loaded
    const optionCount = await sampleSelect.locator('option').count();
    expect(optionCount).toBeGreaterThan(1);
  });

  test('analyze button enables when sample selected', async ({ page }) => {
    const sampleSelect = page.locator('#sample-select');
    const analyzeBtn = page.locator('#analyze-btn');
    
    // Initially disabled
    await expect(analyzeBtn).toBeDisabled();
    
    // Wait for samples and select one
    await page.waitForFunction(() => {
      const select = document.getElementById('sample-select');
      return select && select.options.length > 1;
    });
    
    await sampleSelect.selectOption({ index: 1 });
    
    // Button should be enabled
    await expect(analyzeBtn).toBeEnabled();
  });

  test('analysis container shows when analysis starts', async ({ page }) => {
    const analysisContainer = page.locator('#analysis-container');
    
    // Initially hidden
    await expect(analysisContainer).toHaveClass(/hidden/);
    
    // Select sample and start analysis
    await page.waitForFunction(() => {
      const select = document.getElementById('sample-select');
      return select && select.options.length > 1;
    });
    
    await page.locator('#sample-select').selectOption({ index: 1 });
    await page.locator('#analyze-btn').click();
    
    // Container should be visible
    await expect(analysisContainer).not.toHaveClass(/hidden/);
  });

  test('WebSocket connection updates progress', async ({ page }) => {
    // Set up WebSocket message listener
    const wsMessages = [];
    page.on('websocket', ws => {
      ws.on('framereceived', frame => {
        if (frame.payload) {
          try {
            const data = JSON.parse(frame.payload.toString());
            wsMessages.push(data);
          } catch (e) {
            // Not JSON, ignore
          }
        }
      });
    });
    
    // Start analysis
    await page.waitForFunction(() => {
      const select = document.getElementById('sample-select');
      return select && select.options.length > 1;
    });
    
    await page.locator('#sample-select').selectOption({ index: 1 });
    await page.locator('#analyze-btn').click();
    
    // Wait for WebSocket connection
    await page.waitForSelector('#ws-container:not(.hidden)', { timeout: 5000 });
    
    // Check progress bar updates
    const progressBar = page.locator('#progress-bar');
    await expect(progressBar).toBeVisible();
    
    // Wait for some progress
    await page.waitForFunction(() => {
      const progress = document.getElementById('progress-bar');
      return progress && parseInt(progress.value) > 0;
    }, { timeout: 10000 });
    
    // Check that progress steps are updating
    const activeSteps = await page.locator('.progress-step.active').count();
    expect(activeSteps).toBeGreaterThan(0);
  });

  test('energy meter animates with data', async ({ page }) => {
    // Start analysis
    await page.waitForFunction(() => {
      const select = document.getElementById('sample-select');
      return select && select.options.length > 1;
    });
    
    await page.locator('#sample-select').selectOption({ index: 1 });
    await page.locator('#analyze-btn').click();
    
    // Wait for energy indicator to move
    const energyIndicator = page.locator('#energy-indicator');
    await expect(energyIndicator).toBeVisible();
    
    // Check that it moves from default position
    await page.waitForFunction(() => {
      const indicator = document.getElementById('energy-indicator');
      return indicator && indicator.style.left !== '50%';
    }, { timeout: 10000 });
    
    // Check energy value updates
    const energyValue = page.locator('#energy-value');
    await expect(energyValue).not.toHaveText('-');
  });

  test('mood visualization displays results', async ({ page }) => {
    // Start analysis
    await page.waitForFunction(() => {
      const select = document.getElementById('sample-select');
      return select && select.options.length > 1;
    });
    
    await page.locator('#sample-select').selectOption({ index: 1 });
    await page.locator('#analyze-btn').click();
    
    // Wait for mood label to update
    const moodLabel = page.locator('#mood-label');
    await page.waitForFunction(() => {
      const label = document.getElementById('mood-label');
      return label && label.textContent !== '-';
    }, { timeout: 10000 });
    
    // Check mood is one of expected values
    const mood = await moodLabel.textContent();
    const validMoods = ['energetic', 'melancholic', 'aggressive', 'chill', 'mysterious', 'uplifting'];
    expect(validMoods).toContain(mood);
    
    // Check confidence is displayed
    const confidence = page.locator('#mood-confidence');
    await expect(confidence).toContainText('confidence');
  });

  test('texture tags appear after analysis', async ({ page }) => {
    // Start analysis
    await page.waitForFunction(() => {
      const select = document.getElementById('sample-select');
      return select && select.options.length > 1;
    });
    
    await page.locator('#sample-select').selectOption({ index: 1 });
    await page.locator('#analyze-btn').click();
    
    // Wait for texture tags
    await page.waitForSelector('.texture-tag', { timeout: 10000 });
    
    // Should have multiple texture tags
    const tagCount = await page.locator('.texture-tag').count();
    expect(tagCount).toBeGreaterThan(0);
    
    // Tags should have floating animation
    const firstTag = page.locator('.texture-tag').first();
    await expect(firstTag).toHaveCSS('animation-name', 'float');
  });

  test('complete analysis shows all results', async ({ page }) => {
    // Start analysis
    await page.waitForFunction(() => {
      const select = document.getElementById('sample-select');
      return select && select.options.length > 1;
    });
    
    await page.locator('#sample-select').selectOption({ index: 1 });
    await page.locator('#analyze-btn').click();
    
    // Wait for completion
    await page.waitForFunction(() => {
      const progress = document.getElementById('progress-bar');
      return progress && progress.value === '100';
    }, { timeout: 15000 });
    
    // Check all results are populated
    await expect(page.locator('#result-bpm')).not.toHaveText('-');
    await expect(page.locator('#result-key')).not.toHaveText('-');
    await expect(page.locator('#result-genres')).not.toHaveText('-');
    
    // Progress should show complete
    await expect(page.locator('#progress-text')).toContainText('complete');
  });

  test.describe('Mobile Responsiveness', () => {
    test('layout adjusts for mobile', async ({ page, isMobile }) => {
      if (isMobile) {
        // Check grid becomes single column
        const grid = page.locator('.grid').first();
        const classes = await grid.getAttribute('class');
        expect(classes).toContain('grid-cols-1');
      }
    });
  });

  test.describe('Accessibility', () => {
    test('page has proper ARIA labels', async ({ page }) => {
      // Check select has label
      const select = page.locator('#sample-select');
      const selectLabel = await page.locator('label[for="sample-select"]').count() ||
                         await select.getAttribute('aria-label');
      expect(selectLabel).toBeTruthy();
      
      // Check progress has proper role
      const progress = page.locator('#progress-bar');
      await expect(progress).toHaveAttribute('role', 'progressbar');
    });
    
    test('keyboard navigation works', async ({ page }) => {
      // Tab through controls
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Should focus on sample select
      const focusedElement = await page.evaluate(() => document.activeElement?.id);
      expect(['sample-select', 'analyze-btn']).toContain(focusedElement);
    });
  });
});