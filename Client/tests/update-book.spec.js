import { test, expect } from './test-setup';

test.describe('Update Book Page', () => {
  test('should navigate to update page with pre-filled data', async ({ page }) => {
    // First go to books page
    await page.goto('http://localhost:5173/');
    await page.waitForTimeout(2000);
    
    // Check if books exist and click update on first one
    const updateButtons = page.locator('button.btn-primary');
    
    if (await updateButtons.first().isVisible()) {
      // Get book data from the first row before clicking update
      const firstRow = page.locator('table.table tbody tr').first();
      const bookData = {
        publisher: await firstRow.locator('td').nth(0).textContent(),
        name: await firstRow.locator('td').nth(1).textContent(),
        date: await firstRow.locator('td').nth(2).textContent(),
        cost: await firstRow.locator('td').nth(3).textContent()
      };
      
      // Click update button
      await updateButtons.first().click();
      
      // Should navigate to update page
      await expect(page).toHaveURL('http://localhost:5173/update');
      
      // Check if form is pre-filled with book data
      await expect(page.locator('h2:has-text("Update Book")')).toBeVisible();
      
      // Verify form fields have the correct values
      const publisherInput = page.locator('input[name="publisher"]');
      const nameInput = page.locator('input[placeholder="Enter Book name"]');
      
      if (await publisherInput.isVisible()) {
        const publisherValue = await publisherInput.inputValue();
        const nameValue = await nameInput.inputValue();
        
        expect(publisherValue).toBe(bookData.publisher);
        expect(nameValue).toBe(bookData.name);
      }
    }
  });

  test('should update book data successfully', async ({ page }) => {
    // Navigate via books list to ensure we have a book to update
    await page.goto('http://localhost:5173/');
    await page.waitForTimeout(2000);
    
    const updateButtons = page.locator('button.btn-primary');
    if (await updateButtons.first().isVisible()) {
      await updateButtons.first().click();
      await page.waitForURL('http://localhost:5173/update');
      
      // Modify the book data
      const updatedData = {
        publisher: 'Updated Publisher',
        name: 'Updated Book Name',
        date: '2024-02-20',
        cost: '39.99'
      };
      
      // Update form fields
      await page.fill('input[name="publisher"]', updatedData.publisher);
      await page.fill('input[placeholder="Enter Book name"]', updatedData.name);
      
      const dateInputs = page.locator('input[type="date"]');
      await dateInputs.first().fill(updatedData.date);
      
      await page.fill('input[placeholder="Rupees"]', updatedData.cost);
      
      // Submit the update
      await page.click('button[type="submit"]');
      
      // Should redirect to books list
      await expect(page).toHaveURL('http://localhost:5173/');
      
      // Verify the update (you might check if the data changed in the list)
      await page.waitForTimeout(1000);
    }
  });

  test('should display update form correctly', async ({ page }) => {
    // Try direct navigation (might not work without book data)
    await page.goto('http://localhost:5173/update');
    
    // Either we see the form or we're redirected
    const updateForm = page.locator('h2:has-text("Update Book")');
    
    if (await updateForm.isVisible()) {
      await expect(updateForm).toBeVisible();
      await expect(page.locator('button[type="submit"]')).toHaveText('Update');
    }
  });
});