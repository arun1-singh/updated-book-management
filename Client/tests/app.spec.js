import { test, expect } from './test-setup';

test.describe('App Navigation', () => {
  test('should render navigation header', async ({ page }) => {
    await expect(page.locator('text=Book Management System')).toBeVisible();
    await expect(page.locator('.d-flex.justify-content-center.py-2')).toBeVisible();
  });

  test('should have correct routing setup', async ({ page }) => {
    // Verify initial route is books list (using relative path)
    await expect(page).toHaveURL('/');
    
    // Check if main routes are accessible
    await page.goto('/create');
    await expect(page).toHaveURL('/create');
    
    await page.goto('/');
    await expect(page).toHaveURL('/');
  });

  test('should maintain navigation header across all pages', async ({ page }) => {
    // Check header on books page
    await expect(page.locator('text=Book Management System')).toBeVisible();
    
    // Check header on create page
    await page.goto('/create');
    await expect(page.locator('text=Book Management System')).toBeVisible();
    
    // Check header on update page (if accessible)
    await page.goto('/');
    await expect(page.locator('text=Book Management System')).toBeVisible();
  });

  test('should have all routes defined in App.jsx', async ({ page }) => {
    // Test home route
    await page.goto('/');
    await expect(page.locator('a.btn.btn-success')).toBeVisible(); // Create button
    
    // Test create route
    await page.goto('/create');
    await expect(page.locator('h2:has-text("Add a Book")')).toBeVisible();
    
    // Test that navigation works between routes
    await page.goto('/');
    await page.click('a.btn.btn-success');
    await expect(page).toHaveURL('/create');
  });
});