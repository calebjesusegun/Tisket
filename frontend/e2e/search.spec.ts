import { expect, test } from '@playwright/test'

test('search tasks and notes and render highlighted matches', async ({ page }) => {
  await page.goto('/tasks')
  await page.getByRole('button', { name: 'New task' }).click()
  await page.getByLabel('Title').fill('E2E constellation keyword')
  await page.getByRole('button', { name: 'Create task' }).click()
  await page.getByRole('searchbox', { name: 'Search tasks and notes' }).fill('constellation')
  await page.getByRole('search').getByRole('searchbox').press('Enter')
  await expect(page.getByRole('heading', { name: 'Search' })).toBeVisible()
  await expect(page.locator('mark', { hasText: 'constellation' })).toBeVisible()
})
