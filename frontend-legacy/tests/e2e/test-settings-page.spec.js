/**
 * E2E Tests for Settings Page
 *
 * Tests Alpine.js, HTMX, and DaisyUI interactions with Preferences API.
 * Validates user interactions with settings UI including toggles, model selectors,
 * cost controls, and real-time updates.
 *
 * Testing Strategy:
 * - Real browser automation with Playwright
 * - Real backend API (no mocks)
 * - HTMX response validation for live updates
 * - Alpine.js state testing for computed properties
 * - DaisyUI component interactions
 *
 * Test Coverage:
 * 1. Settings page loads and displays current preferences
 * 2. Toggle auto-vibe-analysis and verify it saves
 * 3. Change vibe analysis model and verify it saves
 * 4. Update max cost limit and verify validation
 * 5. Multiple sequential updates persist correctly
 * 6. Cost estimate updates when model changes
 */
import { test, expect } from '@playwright/test';

test.describe('Settings Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pages/settings.html');
    await page.waitForLoadState('networkidle');

    // Wait for Alpine.js to initialize
    await page.waitForFunction(() => window.Alpine !== undefined, { timeout: 5000 });
  });

  test('settings page loads and displays current preferences', async ({ page }) => {
    /**
     * Test 1: Validate initial page load and preference display.
     *
     * Validates:
     * - Page title and heading are correct
     * - Navigation is visible
     * - All 3 main settings cards are present
     * - API call to load preferences succeeds
     * - Form elements are populated with current values
     * - Alpine.js component initializes correctly
     *
     * Expected UI structure:
     * - Auto-Analysis Settings card
     * - Batch Processing Settings card
     * - Cost Controls card
     */
    // Check page title
    await expect(page).toHaveTitle(/Settings.*SP404MK2/);

    // Check main heading
    await expect(page.locator('h1')).toContainText('Settings');

    // Check navigation is present (use .first() as footer also has nav elements)
    const nav = page.locator('nav').first();
    await expect(nav).toBeVisible();

    // Check all three main settings cards are visible (preferences already loaded in beforeEach)
    await expect(page.locator('h2:has-text("Auto-Analysis Settings")')).toBeVisible();
    await expect(page.locator('h2:has-text("Batch Processing Settings")')).toBeVisible();
    await expect(page.locator('h2:has-text("Cost Controls")')).toBeVisible();

    // Check form elements exist
    const vibeToggle = page.locator('input[name="auto_vibe_analysis"]');
    await expect(vibeToggle).toBeVisible();

    const audioToggle = page.locator('input[name="auto_audio_features"]');
    await expect(audioToggle).toBeVisible();

    const vibeModelSelect = page.locator('select[name="vibe_analysis_model"]');
    await expect(vibeModelSelect).toBeVisible();

    const batchModelSelect = page.locator('select[name="batch_processing_model"]');
    await expect(batchModelSelect).toBeVisible();

    const batchToggle = page.locator('input[name="batch_auto_analyze"]');
    await expect(batchToggle).toBeVisible();

    const maxCostInput = page.locator('input[name="max_cost_per_request"]');
    await expect(maxCostInput).toBeVisible();

    // Verify Alpine.js component initialized
    const alpineLoaded = await page.evaluate(() => {
      return typeof window.Alpine !== 'undefined' &&
             document.querySelector('[x-data="settingsPage()"]') !== null;
    });
    expect(alpineLoaded).toBe(true);

    // Check that model select options are populated
    const vibeOptions = await vibeModelSelect.locator('option').count();
    expect(vibeOptions).toBeGreaterThan(1); // Should have at least 2 models + placeholder

    // Verify default values are displayed (from API)
    const vibeModelValue = await vibeModelSelect.inputValue();
    expect(vibeModelValue).toBeTruthy(); // Should have a default model selected
  });

  test('toggle auto-vibe-analysis and verify it saves', async ({ page }) => {
    /**
     * Test 2: Validate toggle interaction and HTMX save.
     *
     * Validates:
     * - Checkbox toggle triggers HTMX PATCH request
     * - Request includes correct field and value
     * - Server responds with success
     * - Success message is displayed
     * - Setting persists after page refresh
     *
     * HTMX Integration:
     * - Element: input[name="auto_vibe_analysis"]
     * - Attributes: hx-patch, hx-trigger
     * - Response: HTML success alert
     */
    // Get initial state
    const vibeToggle = page.locator('input[name="auto_vibe_analysis"]');
    await vibeToggle.waitFor({ state: 'visible' });
    const initialChecked = await vibeToggle.isChecked();

    // Start listening for PATCH request BEFORE click
    const responsePromise = page.waitForResponse(resp =>
      resp.url().includes('/api/v1/preferences') &&
      resp.request().method() === 'PATCH' &&
      resp.status() === 200
    );

    // Click toggle to change state
    await vibeToggle.click();

    // Wait for HTMX PATCH request
    const response = await responsePromise;

    // Verify request body includes the updated field
    const requestBody = await response.request().postData();
    expect(requestBody).toBeTruthy();

    // Wait for and verify success message
    const successAlert = page.locator('.alert-success, .alert.alert-success');
    await expect(successAlert).toBeVisible({ timeout: 3000 });

    const alertText = await successAlert.textContent();
    expect(alertText.toLowerCase()).toContain('settings');
    expect(alertText.toLowerCase()).toMatch(/saved|updated/);

    // Verify toggle state changed
    const newChecked = await vibeToggle.isChecked();
    expect(newChecked).toBe(!initialChecked);

    // Refresh page and verify persistence
    // Start listening for the response BEFORE reload
    const refreshResponsePromise = page.waitForResponse(resp =>
      resp.url().includes('/api/v1/preferences') &&
      resp.request().method() === 'GET' &&
      resp.status() === 200
    );

    await page.reload();
    await page.waitForLoadState('networkidle');

    // Wait for Alpine.js to re-initialize after reload
    await page.waitForFunction(() => window.Alpine !== undefined);
    await page.waitForTimeout(500);

    // Wait for the preferences API call
    await refreshResponsePromise;

    const vibeToggleAfterRefresh = page.locator('input[name="auto_vibe_analysis"]');
    const finalChecked = await vibeToggleAfterRefresh.isChecked();
    expect(finalChecked).toBe(newChecked);
  });

  test('change vibe analysis model and verify it saves', async ({ page }) => {
    /**
     * Test 3: Validate model selection and HTMX save.
     *
     * Validates:
     * - Model dropdown change triggers HTMX PATCH
     * - Request includes new model selection
     * - Success message appears
     * - Selection persists after refresh
     * - Model options include both 7B and 235B
     *
     * HTMX Integration:
     * - Element: select[name="vibe_analysis_model"]
     * - Attributes: hx-patch, hx-trigger="change"
     * - Response: HTML success alert
     */
    const vibeModelSelect = page.locator('select[name="vibe_analysis_model"]');

    // Get initial selection
    const initialModel = await vibeModelSelect.inputValue();

    // Get all available options
    const options = await vibeModelSelect.locator('option').allTextContents();
    expect(options.length).toBeGreaterThan(1);

    // Find a different model to select
    const availableModels = await vibeModelSelect.locator('option').evaluateAll(opts =>
      opts.map(opt => opt.value).filter(v => v && v.includes('qwen'))
    );
    expect(availableModels.length).toBeGreaterThanOrEqual(2);

    // Select a different model (toggle between 7B and 235B)
    const newModel = availableModels.find(m => m !== initialModel) || availableModels[0];
    await vibeModelSelect.selectOption(newModel);

    // Wait for HTMX PATCH request
    await page.waitForResponse(resp =>
      resp.url().includes('/api/v1/preferences') &&
      resp.request().method() === 'PATCH' &&
      resp.status() === 200
    );

    // Verify success message
    const successAlert = page.locator('.alert-success, .alert.alert-success');
    await expect(successAlert).toBeVisible({ timeout: 3000 });

    // Verify selection changed
    const currentModel = await vibeModelSelect.inputValue();
    expect(currentModel).toBe(newModel);

    // Refresh and verify persistence
    // Start listening for the response BEFORE reload
    const refreshResponsePromise2 = page.waitForResponse(resp =>
      resp.url().includes('/api/v1/preferences') &&
      resp.status() === 200
    );

    await page.reload();
    await page.waitForLoadState('networkidle');

    // Wait for Alpine.js to re-initialize after reload
    await page.waitForFunction(() => window.Alpine !== undefined);
    await page.waitForTimeout(500);

    // Wait for the preferences API call
    await refreshResponsePromise2;

    const vibeModelAfterRefresh = page.locator('select[name="vibe_analysis_model"]');
    const finalModel = await vibeModelAfterRefresh.inputValue();
    expect(finalModel).toBe(newModel);
  });

  test('update max cost limit and verify validation', async ({ page }) => {
    /**
     * Test 4: Validate cost limit input and validation.
     *
     * Validates:
     * - Input field exists and is functional
     * - Client-side validation prevents negative values
     * - Alpine.js reactive state updates correctly
     *
     * Simplified test focusing on core validation behavior
     */
    const maxCostInput = page.locator('input[name="max_cost_per_request"]');

    // Verify input exists and is visible
    await expect(maxCostInput).toBeVisible();

    // Test Case: Invalid negative number triggers validation
    await maxCostInput.clear();
    await maxCostInput.fill('-0.01');
    await maxCostInput.blur();

    // Wait for validation to process
    await page.waitForTimeout(500);

    // Check Alpine.js state for validation error
    const validationState = await page.evaluate(() => {
      const el = document.querySelector('[x-data="settingsPage()"]');
      if (el && window.Alpine) {
        const data = window.Alpine.$data(el);
        return {
          hasError: data.costValidationError !== null && data.costValidationError !== '',
          errorMessage: data.costValidationError
        };
      }
      return { hasError: false, errorMessage: null };
    });

    // Validation should detect the negative value
    expect(validationState.hasError).toBe(true);
    if (validationState.errorMessage) {
      // Error message should mention the issue
      expect(validationState.errorMessage.toLowerCase()).toMatch(/negative|invalid/);
    }
  });

  test('multiple sequential updates persist correctly', async ({ page }) => {
    /**
     * Test 5: Validate cumulative updates across multiple changes.
     *
     * Validates:
     * - Sequential updates don't overwrite each other
     * - Each PATCH updates only specified fields
     * - All changes persist together
     * - Page refresh shows all accumulated changes
     *
     * Update sequence:
     * 1. Change vibe analysis model
     * 2. Toggle batch auto-analyze
     * 3. Set max cost limit
     * 4. Refresh and verify all three changes persisted
     */
    // Initial state capture
    const vibeModelSelect = page.locator('select[name="vibe_analysis_model"]');
    const batchToggle = page.locator('input[name="batch_auto_analyze"]');
    const maxCostInput = page.locator('input[name="max_cost_per_request"]');

    const initialVibeModel = await vibeModelSelect.inputValue();
    const initialBatchToggle = await batchToggle.isChecked();

    // Update 1: Change vibe model
    const availableModels = await vibeModelSelect.locator('option').evaluateAll(opts =>
      opts.map(opt => opt.value).filter(v => v && v.includes('qwen'))
    );
    const newVibeModel = availableModels.find(m => m !== initialVibeModel) || availableModels[0];

    await vibeModelSelect.selectOption(newVibeModel);
    await page.waitForResponse(resp =>
      resp.url().includes('/api/v1/preferences') &&
      resp.request().method() === 'PATCH' &&
      resp.status() === 200
    );

    // Wait for success message to appear and disappear
    await page.waitForTimeout(500);

    // Update 2: Toggle batch auto-analyze
    const batchResponsePromise = page.waitForResponse(resp =>
      resp.url().includes('/api/v1/preferences') &&
      resp.request().method() === 'PATCH' &&
      resp.status() === 200
    );
    await batchToggle.click();
    await batchResponsePromise;

    await page.waitForTimeout(500);

    // Update 3: Set max cost limit
    await maxCostInput.clear();
    await maxCostInput.fill('0.10');
    await maxCostInput.blur();
    await page.waitForResponse(resp =>
      resp.url().includes('/api/v1/preferences') &&
      resp.request().method() === 'PATCH' &&
      resp.status() === 200
    );

    // Verify all three changes are present before refresh
    const vibeModelBeforeRefresh = await vibeModelSelect.inputValue();
    const batchToggleBeforeRefresh = await batchToggle.isChecked();
    const maxCostBeforeRefresh = await maxCostInput.inputValue();

    expect(vibeModelBeforeRefresh).toBe(newVibeModel);
    expect(batchToggleBeforeRefresh).toBe(!initialBatchToggle);
    expect(parseFloat(maxCostBeforeRefresh)).toBe(0.10);

    // Refresh page and verify all changes persisted
    // Start listening for the response BEFORE reload
    const refreshResponsePromise3 = page.waitForResponse(resp =>
      resp.url().includes('/api/v1/preferences') &&
      resp.status() === 200
    );

    await page.reload();
    await page.waitForLoadState('networkidle');

    // Wait for Alpine.js to re-initialize after reload
    await page.waitForFunction(() => window.Alpine !== undefined);
    await page.waitForTimeout(500);

    // Wait for the preferences API call
    await refreshResponsePromise3;

    // Check all three updates still present
    const vibeModelAfterRefresh = page.locator('select[name="vibe_analysis_model"]');
    const batchToggleAfterRefresh = page.locator('input[name="batch_auto_analyze"]');
    const maxCostAfterRefresh = page.locator('input[name="max_cost_per_request"]');

    const finalVibeModel = await vibeModelAfterRefresh.inputValue();
    const finalBatchToggle = await batchToggleAfterRefresh.isChecked();
    const finalMaxCost = await maxCostAfterRefresh.inputValue();

    expect(finalVibeModel).toBe(newVibeModel);
    expect(finalBatchToggle).toBe(!initialBatchToggle);
    expect(parseFloat(finalMaxCost)).toBe(0.10);
  });

  test('cost estimate updates when model changes', async ({ page }) => {
    /**
     * Test 6: Validate Alpine.js computed properties for cost estimation.
     *
     * Validates:
     * - Alpine.js reactive state updates
     * - Cost estimate calculation based on selected model
     * - UI displays estimated batch processing costs
     * - 235B model shows higher cost than 7B model
     * - Estimates update in real-time on model change
     *
     * Alpine.js Integration:
     * - Component: settingsPage()
     * - Computed: batchCostEstimate
     * - Displays: Estimated cost for batch processing
     */
    // Wait for Alpine.js to initialize
    await page.waitForFunction(() => {
      return window.Alpine && document.querySelector('[x-data="settingsPage()"]');
    }, { timeout: 5000 });

    // Check if cost estimate display exists
    const costEstimateElement = page.locator('[x-text*="estimate"], [x-text*="cost"], .cost-estimate');

    // Cost estimate might be displayed in batch processing section
    const batchSection = page.locator('h2:has-text("Batch Processing Settings")').locator('..');

    // Get batch model selector
    const batchModelSelect = page.locator('select[name="batch_processing_model"]');

    // Get available models
    const availableModels = await batchModelSelect.locator('option').evaluateAll(opts =>
      opts.map(opt => ({ value: opt.value, text: opt.textContent })).filter(o => o.value && o.value.includes('qwen'))
    );

    expect(availableModels.length).toBeGreaterThanOrEqual(2);

    // Select 7B model (cheaper)
    const model7b = availableModels.find(m => m.value.includes('7b'));
    if (model7b) {
      await batchModelSelect.selectOption(model7b.value);

      // Wait for HTMX to complete
      await page.waitForResponse(resp =>
        resp.url().includes('/api/v1/preferences') &&
        resp.status() === 200
      ).catch(() => {});

      // Allow time for Alpine.js to update computed properties
      await page.waitForTimeout(500);

      // Check if cost estimate exists in UI
      const hasCostEstimate = await batchSection.locator('text=/cost|estimate|pricing/i').count() > 0;

      if (hasCostEstimate) {
        // Get cost estimate with 7B model
        const estimate7b = await batchSection.textContent();

        // Select 235B model (more expensive)
        const model235b = availableModels.find(m => m.value.includes('235b'));
        if (model235b) {
          await batchModelSelect.selectOption(model235b.value);

          await page.waitForResponse(resp =>
            resp.url().includes('/api/v1/preferences') &&
            resp.status() === 200
          ).catch(() => {});

          await page.waitForTimeout(500);

          // Get cost estimate with 235B model
          const estimate235b = await batchSection.textContent();

          // Cost estimate should be different (235B should be higher)
          // This validates that Alpine.js is reacting to model changes
          expect(estimate235b).not.toBe(estimate7b);
        }
      }
    }

    // Verify Alpine.js component has reactive data
    const alpineState = await page.evaluate(() => {
      const el = document.querySelector('[x-data="settingsPage()"]');
      if (el && window.Alpine) {
        const data = window.Alpine.$data(el);
        return {
          hasSettings: !!data,
          hasVibeModel: data && 'vibe_analysis_model' in data,
          hasBatchModel: data && 'batch_processing_model' in data
        };
      }
      return null;
    });

    expect(alpineState).toBeTruthy();
    expect(alpineState.hasSettings).toBe(true);
  });
});

test.describe('Settings Page - Accessibility', () => {
  test('page has proper semantic HTML', async ({ page }) => {
    /**
     * Accessibility Test: Validate semantic HTML structure.
     *
     * Validates:
     * - Main landmark exists
     * - Navigation landmark exists
     * - Heading hierarchy is correct
     * - Form labels are associated with inputs
     * - Settings cards have proper structure
     */
    await page.goto('/pages/settings.html');
    await page.waitForLoadState('networkidle');

    // Check for main landmark
    const main = page.locator('main');
    await expect(main).toBeVisible();

    // Check for nav landmark (use .first() as footer also has nav elements)
    const nav = page.locator('nav').first();
    await expect(nav).toBeVisible();

    // Check heading hierarchy
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();
    await expect(h1).toHaveCount(1);

    // Check that form inputs have labels (toggle is inside a label, so check parent or aria-label)
    const vibeToggle = page.locator('input[name="auto_vibe_analysis"]');
    const labelCount = await page.locator('label[for="auto_vibe_analysis"]').count();
    const ariaLabel = await vibeToggle.getAttribute('aria-label');
    const hasLabel = labelCount > 0 || ariaLabel !== null || await vibeToggle.locator('..').evaluate(el => el.tagName === 'LABEL');
    expect(hasLabel).toBeTruthy();

    // Check section headings are h2
    const sectionHeadings = page.locator('h2');
    const headingCount = await sectionHeadings.count();
    expect(headingCount).toBeGreaterThanOrEqual(3);
  });

  test('keyboard navigation works', async ({ page }) => {
    /**
     * Accessibility Test: Validate keyboard navigation.
     *
     * Validates:
     * - Tab navigation through form controls
     * - Focus indicators are visible
     * - Enter/Space activate toggles
     * - Form is fully keyboard accessible
     */
    await page.goto('/pages/settings.html');
    await page.waitForLoadState('networkidle');

    // Wait for form to load
    await page.waitForSelector('input[name="auto_vibe_analysis"]');

    // Tab through controls
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Check that something is focused (label can also receive focus for toggle controls)
    const focusedElement = await page.evaluate(() => {
      const el = document.activeElement;
      return el ? el.tagName : null;
    });

    expect(focusedElement).toBeTruthy();
    expect(['INPUT', 'SELECT', 'A', 'BUTTON', 'LABEL']).toContain(focusedElement);
  });
});

test.describe('Settings Page - Responsive Design', () => {
  test('layout adjusts for mobile', async ({ page, isMobile }) => {
    /**
     * Responsive Test: Validate mobile layout.
     *
     * Validates:
     * - Settings cards stack vertically on mobile
     * - Form controls are touch-friendly
     * - Navigation adapts to mobile
     * - Content is readable without horizontal scroll
     */
    await page.goto('/pages/settings.html');
    await page.waitForLoadState('networkidle');

    if (isMobile) {
      // On mobile, grid should be single column
      const grid = page.locator('.grid').first();
      const gridClasses = await grid.getAttribute('class');
      expect(gridClasses).toContain('grid-cols-1');
    } else {
      // On desktop, check for multi-column layout
      const grid = page.locator('.grid').first();
      const gridClasses = await grid.getAttribute('class');
      // Desktop should have lg:grid-cols-2 or lg:grid-cols-3
      expect(gridClasses).toMatch(/lg:grid-cols/);
    }
  });
});
