import { test as baseTest } from '@playwright/test';

// Global setup with page fixture
export const test = baseTest.extend({
  page: async ({ browser }, use) => {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 }
    });
    // Ensure tests run with a logged-in state so routes requiring auth are reachable
    await context.addInitScript(() => {
      try {
        localStorage.setItem('access_token', 'test-token');
      } catch (e) {}
    });
    const page = await context.newPage();

    // Navigate to the app before each test.
    // Reads BASE_URL (set in playwright.config.js and CI workflow) with a
    // sensible fallback. PLAYWRIGHT_BASE_URL is kept as an alias for compat.
    const baseUrl =
      process.env.BASE_URL ||
      process.env.PLAYWRIGHT_BASE_URL ||
      'http://localhost:5173';
    await page.goto(baseUrl);
    
    await use(page);
    
    await context.close();
  },
});

export const expect = test.expect;