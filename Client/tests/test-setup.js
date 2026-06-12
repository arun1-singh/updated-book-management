import { test as baseTest } from '@playwright/test';
import fs from 'fs';
import path from 'path';

/**
 * Custom page fixture that:
 *  1. Uses the real auth token saved by global-setup (auth-state.json)
 *     so axios picks it up via App.jsx's useEffect and JWT-protected
 *     endpoints (create, delete, update) work correctly.
 *  2. Falls back to a no-auth context when auth-state.json is missing
 *     (local dev without running global setup first).
 */
export const test = baseTest.extend({
  page: async ({ browser }, use) => {
    // Resolve auth-state.json relative to the Client/ directory
    const authStatePath = path.resolve(process.cwd(), 'auth-state.json');
    const hasAuthState = fs.existsSync(authStatePath);

    const contextOptions = {
      viewport: { width: 1280, height: 720 },
    };

    // Use the storage state saved by global-setup when available.
    // This gives the browser context the real access_token in localStorage
    // so axios.defaults.headers.common['Authorization'] is set correctly.
    if (hasAuthState) {
      contextOptions.storageState = authStatePath;
    }

    const context = await browser.newContext(contextOptions);

    const page = await context.newPage();

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
