import { test as baseTest } from '@playwright/test';

// Global setup with page fixture
export const test = baseTest.extend({
  page: async ({ browser }, use) => {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 }
    });
    const page = await context.newPage();
    
    // Navigate to the app before each test
    await page.goto('http://localhost:5173');
    
    await use(page);
    
    await context.close();
  },
});

export const expect = test.expect;