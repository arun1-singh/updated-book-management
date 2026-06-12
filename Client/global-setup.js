import { chromium } from '@playwright/test';

async function globalSetup() {
  const backendUrl = 'http://localhost:5001';
  const browser = await chromium.launch();

  // ── 1. Health check ────────────────────────────────────────────────────────
  const apiCtx = await browser.newContext();
  const healthRes = await apiCtx.request.get(`${backendUrl}/health`);
  if (!healthRes.ok()) {
    throw new Error(`Backend health check failed: ${healthRes.status()}`);
  }
  console.log('✅ Backend is healthy');

  // ── 2. Login and get real JWT ──────────────────────────────────────────────
  const loginRes = await apiCtx.request.post(`${backendUrl}/login`, {
    data: { username: 'testuser', password: 'Test@1234' },
  });
  if (!loginRes.ok()) {
    throw new Error(`Login failed: ${loginRes.status()} ${await loginRes.text()}`);
  }
  const { access_token } = await loginRes.json();
  await apiCtx.close();

  // ── 3. Open a real page, set localStorage, then capture storage state ──────
  // We must navigate to the app first so localStorage is scoped to the origin.
  const baseUrl = process.env.BASE_URL || 'http://localhost:5173';
  const page = await browser.newPage();
  await page.goto(baseUrl);

  // Write the real JWT directly into localStorage
  await page.evaluate((token) => {
    localStorage.setItem('access_token', token);
  }, access_token);

  // Save the entire storage state (localStorage + cookies) for reuse in tests
  await page.context().storageState({ path: 'auth-state.json' });

  await browser.close();
  console.log('✅ Global setup complete – token saved');
}

export default globalSetup;
