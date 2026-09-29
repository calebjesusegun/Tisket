import { expect, test } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'

test('create a note with tags', async ({ page }) => {
  await page.goto('/notes/new')
  await page.getByLabel('Title').fill('E2E release notes')
  await page.getByLabel('Content (Markdown)').fill('## Release\n\nChecklist for release day.')
  await page.getByLabel('Tags').fill('e2e-release')
  await page.getByRole('button', { name: 'Add' }).click()
  await page.getByRole('button', { name: 'Create note' }).click()
  await expect(page.getByRole('heading', { name: 'Edit note' })).toBeVisible()
  await expect(page.getByText('#e2e-release')).toBeVisible()
  await page.goto('/notes')
  const screenshot = resolve(process.cwd(), '../docs/screenshots/notes.png')
  await mkdir(dirname(screenshot), { recursive: true })
  await page.screenshot({ path: screenshot, fullPage: true })
})
