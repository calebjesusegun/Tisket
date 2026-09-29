import { expect, test } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'

test('create a task from the full task form', async ({ page }) => {
  await page.goto('/tasks')
  await page.getByRole('button', { name: 'New task' }).click()
  await page.getByLabel('Title').fill('E2E quarterly planning')
  await page.getByLabel('Description').fill('Plan the next release')
  await page.getByRole('button', { name: 'Create task' }).click()
  await expect(page.getByText('E2E quarterly planning')).toBeVisible()
  const screenshot = resolve(process.cwd(), '../docs/screenshots/tasks.png')
  await mkdir(dirname(screenshot), { recursive: true })
  await page.screenshot({ path: screenshot, fullPage: true })
})
