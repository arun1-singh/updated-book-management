import { test, expect } from './test-setup';

test.describe('Books List Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/'); // Fixed: using relative path
  });

  test('should display books page with correct structure', async ({ page }) => {
    // Check navigation header
    await expect(page.locator('text=Book Management System')).toBeVisible();
    
    // Check create button
    const createButton = page.locator('a.btn.btn-success');
    await expect(createButton).toHaveText('Create Link');
    await expect(createButton).toHaveAttribute('href', '/create');
    
    // Check table headers
    const headers = ['Publisher', 'Book', 'Date', 'cost', 'Actions'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('should load and display books data', async ({ page }) => {
    // Wait for data to load with better selector
    await page.waitForSelector('table.table, h2:has-text("No records")', { timeout: 5000 });
    
    // Check if books are displayed or "No records" message
    const noRecords = page.locator('h2:has-text("No records")');
    const booksTable = page.locator('table.table');
    
    if (await noRecords.isVisible()) {
      await expect(noRecords).toBeVisible();
      await expect(booksTable).not.toBeVisible();
    } else {
      await expect(booksTable).toBeVisible();
      
      // Verify table has rows with data
      const rows = page.locator('table.table tbody tr');
      await expect(rows.first()).toBeVisible();
      
      const rowCount = await rows.count();
      expect(rowCount).toBeGreaterThan(0);
      
      // Check if first row has data
      const firstRowCells = rows.first().locator('td');
      await expect(firstRowCells.nth(0)).not.toBeEmpty(); // Publisher
      await expect(firstRowCells.nth(1)).not.toBeEmpty(); // Book name
      
      // Check action buttons
      await expect(rows.first().locator('button.btn-primary')).toHaveText('Update');
      await expect(rows.first().locator('button.btn-danger')).toHaveText('Delete');
    }
  });

  test('should navigate to create page when create link is clicked', async ({ page }) => {
    await page.click('a.btn.btn-success');
    await expect(page).toHaveURL('/create');
  });

  test('should handle update button click', async ({ page }) => {
    // Wait for books to load
    await page.waitForSelector('table.table tbody tr, h2:has-text("No records")', { timeout: 5000 });
    
    const noRecords = page.locator('h2:has-text("No records")');
    const updateButtons = page.locator('button.btn-primary');
    
    // Only run if books exist
    if (await noRecords.isVisible()) {
      console.log('No books available for update test');
      return;
    }
    
    if (await updateButtons.first().isVisible({ timeout: 3000 })) {
      await updateButtons.first().click();
      // Should navigate to update page
      await expect(page).toHaveURL('/update');
    }
  });

  test('should handle delete button click', async ({ page }) => {
    // Do NOT reload — let test-setup's localStorage token stay intact
    await page.waitForSelector('table.table tbody tr, td:has-text("No records")', { timeout: 5000 });

    const noRecords = page.locator('td:has-text("No records")');
    const deleteButtons = page.locator('button.btn-danger');
    const rows = page.locator('table.table tbody tr');

    if (await noRecords.isVisible()) {
      console.log('No books available for delete test');
      return;
    }

    if (await deleteButtons.first().isVisible({ timeout: 3000 })) {
      const rowsBefore = await rows.count();
      await deleteButtons.first().click();
      // The UI removes the row optimistically — wait for DOM update
      await expect(rows).toHaveCount(rowsBefore - 1, { timeout: 10000 });
    }
  });
});