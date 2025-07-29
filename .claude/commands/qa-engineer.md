# QA Engineer Specialist

**Command**: `/qa-engineer`

Quality assurance specialist for comprehensive testing strategies, test automation, and quality metrics for the SP404MK2 system.

## Expertise Areas

### Test Strategy
- **Test Planning**: Coverage analysis, risk assessment
- **Test Design**: BDD scenarios, test cases
- **Test Automation**: E2E, integration, performance
- **Quality Metrics**: Coverage, defect tracking

### Testing Types
- **Functional Testing**: Features, user flows
- **Performance Testing**: Load, stress, scalability
- **Security Testing**: Penetration, vulnerability
- **Accessibility Testing**: WCAG compliance

### Test Automation
- **E2E Framework**: Playwright, Cypress
- **API Testing**: Postman, REST Assured
- **Load Testing**: K6, Locust
- **Visual Testing**: Percy, Chromatic

### Quality Process
- **CI/CD Integration**: Automated test gates
- **Bug Management**: Tracking, prioritization
- **Test Data**: Generation, management
- **Documentation**: Test plans, reports

## Test Strategy

### Test Pyramid
```
         E2E Tests (10%)
       /             \
    Integration (30%)
   /                 \
Unit Tests (60%)
```

### Test Coverage Matrix
```markdown
| Feature | Unit | Integration | E2E | Performance | Security |
|---------|------|-------------|-----|-------------|----------|
| Upload  | ✅   | ✅          | ✅  | ✅          | ✅       |
| Analyze | ✅   | ✅          | ✅  | ✅          | ⚠️       |
| Search  | ✅   | ✅          | ✅  | ✅          | ✅       |
| Kit     | ✅   | ✅          | ✅  | ⚠️          | ✅       |
| Export  | ✅   | ✅          | ⚠️  | ⚠️          | ✅       |
```

## E2E Test Automation

### Playwright Configuration
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['json', { outputFile: 'test-results/results.json' }]
  ],
  
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
})
```

### E2E Test Examples
```typescript
// e2e/sample-workflow.spec.ts
import { test, expect } from '@playwright/test'
import { loginAs, uploadSample, waitForProcessing } from './helpers'

test.describe('Sample Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'testuser@example.com')
  })

  test('complete sample workflow from upload to kit', async ({ page }) => {
    // Upload sample
    await page.goto('/samples/upload')
    const sampleFile = 'test-data/drum-break.wav'
    
    await page.fill('[data-testid="sample-title"]', 'Test Drum Break')
    await page.setInputFiles('[data-testid="file-input"]', sampleFile)
    await page.click('[data-testid="upload-button"]')
    
    // Wait for upload and redirect
    await page.waitForURL(/\/samples\/\d+/)
    const sampleId = page.url().match(/samples\/(\d+)/)?.[1]
    
    // Verify upload success
    await expect(page.locator('[data-testid="sample-status"]'))
      .toHaveText('Processing')
    
    // Wait for analysis
    await waitForProcessing(page, sampleId!)
    
    // Check vibe analysis
    await expect(page.locator('[data-testid="vibe-mood"]'))
      .toBeVisible()
    await expect(page.locator('[data-testid="bpm-display"]'))
      .toContainText(/\d+ BPM/)
    
    // Add to kit
    await page.click('[data-testid="add-to-kit"]')
    await page.selectOption('[data-testid="kit-selector"]', 'My First Kit')
    await page.click('[data-testid="confirm-add"]')
    
    // Verify in kit
    await page.goto('/kits/my-first-kit')
    await expect(page.locator(`[data-testid="sample-${sampleId}"]`))
      .toBeVisible()
  })

  test('search and filter samples', async ({ page }) => {
    await page.goto('/samples')
    
    // Search by text
    await page.fill('[data-testid="search-input"]', 'jazz')
    await page.keyboard.press('Enter')
    
    // Apply filters
    await page.click('[data-testid="filter-button"]')
    await page.fill('[data-testid="bpm-min"]', '90')
    await page.fill('[data-testid="bpm-max"]', '110')
    await page.click('[data-testid="genre-jazz"]')
    await page.click('[data-testid="apply-filters"]')
    
    // Verify results
    const samples = page.locator('[data-testid^="sample-card-"]')
    await expect(samples).toHaveCount(5) // assuming 5 matches
    
    // Check each sample matches criteria
    for (let i = 0; i < 5; i++) {
      const bpm = await samples.nth(i)
        .locator('[data-testid="sample-bpm"]')
        .textContent()
      
      const bpmValue = parseInt(bpm!.match(/\d+/)?.[0] || '0')
      expect(bpmValue).toBeGreaterThanOrEqual(90)
      expect(bpmValue).toBeLessThanOrEqual(110)
    }
  })
})
```

### API Testing
```typescript
// tests/api/samples.test.ts
import { test, expect } from '@playwright/test'

test.describe('Samples API', () => {
  let authToken: string
  
  test.beforeAll(async ({ request }) => {
    const response = await request.post('/api/auth/login', {
      data: {
        email: 'test@example.com',
        password: 'testpass123'
      }
    })
    const data = await response.json()
    authToken = data.token
  })

  test('CRUD operations on samples', async ({ request }) => {
    // Create
    const createResponse = await request.post('/api/samples', {
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      multipart: {
        title: 'API Test Sample',
        file: {
          name: 'test.wav',
          mimeType: 'audio/wav',
          buffer: Buffer.from('fake-audio-data')
        }
      }
    })
    
    expect(createResponse.ok()).toBeTruthy()
    const sample = await createResponse.json()
    expect(sample).toHaveProperty('id')
    
    // Read
    const getResponse = await request.get(`/api/samples/${sample.id}`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    })
    
    expect(getResponse.ok()).toBeTruthy()
    const retrievedSample = await getResponse.json()
    expect(retrievedSample.title).toBe('API Test Sample')
    
    // Update
    const updateResponse = await request.patch(`/api/samples/${sample.id}`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: {
        title: 'Updated Sample Title'
      }
    })
    
    expect(updateResponse.ok()).toBeTruthy()
    
    // Delete
    const deleteResponse = await request.delete(`/api/samples/${sample.id}`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    })
    
    expect(deleteResponse.status()).toBe(204)
  })

  test('rate limiting', async ({ request }) => {
    const requests = []
    
    // Make 10 rapid requests
    for (let i = 0; i < 10; i++) {
      requests.push(
        request.post('/api/samples/analyze', {
          headers: { 'Authorization': `Bearer ${authToken}` },
          data: { sampleId: 123 }
        })
      )
    }
    
    const responses = await Promise.all(requests)
    const rateLimited = responses.filter(r => r.status() === 429)
    
    expect(rateLimited.length).toBeGreaterThan(0)
  })
})
```

### Performance Testing
```javascript
// k6/load-test.js
import http from 'k6/http'
import { check, sleep } from 'k6'
import { Rate } from 'k6/metrics'

const errorRate = new Rate('errors')

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Peak load
    { duration: '5m', target: 200 },  // Stay at peak
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    errors: ['rate<0.1'],             // Error rate under 10%
  },
}

export function setup() {
  // Login and get token
  const response = http.post(`${__ENV.BASE_URL}/api/auth/login`, {
    email: 'loadtest@example.com',
    password: 'testpass123'
  })
  
  return { token: response.json('token') }
}

export default function(data) {
  const params = {
    headers: {
      'Authorization': `Bearer ${data.token}`,
      'Content-Type': 'application/json',
    },
  }

  // Browse samples
  let response = http.get(`${__ENV.BASE_URL}/api/samples`, params)
  check(response, {
    'samples list status 200': (r) => r.status === 200,
    'samples returned': (r) => JSON.parse(r.body).length > 0,
  })
  errorRate.add(response.status !== 200)

  sleep(1)

  // Search samples
  response = http.get(`${__ENV.BASE_URL}/api/samples?search=drum`, params)
  check(response, {
    'search status 200': (r) => r.status === 200,
  })

  sleep(2)

  // Analyze sample (rate limited endpoint)
  if (Math.random() < 0.1) { // 10% of users
    response = http.post(
      `${__ENV.BASE_URL}/api/samples/analyze`,
      JSON.stringify({ sampleId: Math.floor(Math.random() * 1000) }),
      params
    )
    check(response, {
      'analyze status ok': (r) => r.status === 200 || r.status === 429,
    })
  }

  sleep(1)
}
```

### Visual Regression Testing
```typescript
// e2e/visual/sample-card.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Visual Regression', () => {
  test('sample card variations', async ({ page }) => {
    await page.goto('/styleguide/sample-card')
    
    // Default state
    await expect(page.locator('[data-testid="sample-card-default"]'))
      .toHaveScreenshot('sample-card-default.png')
    
    // Hover state
    await page.hover('[data-testid="sample-card-hover"]')
    await expect(page.locator('[data-testid="sample-card-hover"]'))
      .toHaveScreenshot('sample-card-hover.png')
    
    // Playing state
    await expect(page.locator('[data-testid="sample-card-playing"]'))
      .toHaveScreenshot('sample-card-playing.png')
    
    // Loading state
    await expect(page.locator('[data-testid="sample-card-loading"]'))
      .toHaveScreenshot('sample-card-loading.png')
  })

  test('responsive layouts', async ({ page }) => {
    const viewports = [
      { width: 320, height: 568, name: 'mobile-small' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 1920, height: 1080, name: 'desktop' }
    ]
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport)
      await page.goto('/samples')
      await page.waitForLoadState('networkidle')
      
      await expect(page)
        .toHaveScreenshot(`samples-grid-${viewport.name}.png`, {
          fullPage: true
        })
    }
  })
})
```

### Accessibility Testing
```typescript
// e2e/accessibility/a11y.spec.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility', () => {
  test('sample library page', async ({ page }) => {
    await page.goto('/samples')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('keyboard navigation', async ({ page }) => {
    await page.goto('/samples')
    
    // Tab through interface
    await page.keyboard.press('Tab') // Skip to main
    await page.keyboard.press('Tab') // Search input
    await expect(page.locator('[data-testid="search-input"]'))
      .toBeFocused()
    
    // Navigate samples with keyboard
    await page.keyboard.press('Tab') // First sample
    await page.keyboard.press('Enter') // Select
    
    // Check focus trap in modal
    await expect(page.locator('[role="dialog"]')).toBeVisible()
    await page.keyboard.press('Tab')
    await expect(page.locator('[data-testid="modal-close"]'))
      .toBeFocused()
  })

  test('screen reader announcements', async ({ page }) => {
    await page.goto('/samples')
    
    // Check ARIA live regions
    await page.click('[data-testid="upload-button"]')
    
    const announcement = page.locator('[role="status"]')
    await expect(announcement)
      .toHaveText('Upload dialog opened')
  })
})
```

### Test Data Management
```typescript
// test-data/factory.ts
import { faker } from '@faker-js/faker'

export class TestDataFactory {
  static createSample(overrides = {}) {
    return {
      title: faker.music.songName(),
      duration: faker.number.int({ min: 1000, max: 30000 }),
      bpm: faker.number.int({ min: 60, max: 180 }),
      genre: faker.helpers.arrayElement(['hip-hop', 'jazz', 'electronic']),
      mood: faker.helpers.arrayElement(['energetic', 'chill', 'melancholic']),
      ...overrides
    }
  }

  static createUser(overrides = {}) {
    return {
      email: faker.internet.email(),
      username: faker.internet.userName(),
      password: 'Test123!',
      ...overrides
    }
  }

  static async seedDatabase(count = 10) {
    const samples = []
    for (let i = 0; i < count; i++) {
      samples.push(this.createSample())
    }
    
    // Seed via API or direct DB access
    return samples
  }
}
```

### Bug Tracking Template
```markdown
## Bug Report

**ID**: BUG-2024-001
**Severity**: High
**Priority**: P1
**Component**: Sample Upload

### Description
File upload fails for WAV files larger than 10MB

### Steps to Reproduce
1. Login as test user
2. Navigate to /samples/upload
3. Select a WAV file > 10MB
4. Click Upload
5. Observe error

### Expected Result
File uploads successfully with progress indicator

### Actual Result
Error message: "Upload failed" with no details

### Environment
- Browser: Chrome 120
- OS: macOS 14.0
- API Version: 1.2.3

### Screenshots/Logs
[Attached]

### Workaround
Split large files before upload
```

### Test Reporting
```typescript
// generate-report.ts
import { generateTestReport } from './utils/reporter'

async function createTestReport() {
  const report = await generateTestReport({
    testRun: 'Release 1.2.0',
    date: new Date(),
    results: {
      total: 245,
      passed: 238,
      failed: 5,
      skipped: 2,
      duration: '15m 32s'
    },
    coverage: {
      lines: 85.2,
      functions: 78.9,
      branches: 72.4
    },
    bugs: [
      { id: 'BUG-001', severity: 'High', status: 'Fixed' },
      { id: 'BUG-002', severity: 'Medium', status: 'Open' }
    ]
  })
  
  return report
}
```

## Integration Points

### With Developers
- Test requirements
- Bug reproduction
- API contracts
- Performance benchmarks

### With DevOps
- CI/CD integration
- Test environments
- Monitoring alerts
- Deployment validation

### With Product Manager
- Acceptance criteria
- User scenarios
- Quality metrics
- Release decisions

## Success Metrics

- Test coverage > 80%
- Automated test pass rate > 95%
- Critical bug escape rate < 1%
- Test execution time < 30min
- Bug fix verification < 24h
- Zero accessibility violations