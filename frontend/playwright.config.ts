import { defineConfig, devices } from '@playwright/test'

const dbPath = `/tmp/tisket-e2e-${process.pid}.db`
const databaseUrl = `sqlite:////${dbPath.replace(/^\//, '')}`

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:4173',
    trace: 'retain-on-failure',
    ...devices['Desktop Chrome'],
  },
  webServer: [
    {
      command: `DATABASE_URL=${databaseUrl} APP_ENV=test ALLOWED_ORIGINS=http://127.0.0.1:4173 uv run alembic upgrade head && DATABASE_URL=${databaseUrl} APP_ENV=test ALLOWED_ORIGINS=http://127.0.0.1:4173 uv run uvicorn app.main:app --host 127.0.0.1 --port 8001`,
      cwd: '../backend',
      url: 'http://127.0.0.1:8001/health',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: 'npm run build && npm run preview -- --host 127.0.0.1 --port 4173',
      cwd: '.',
      url: 'http://127.0.0.1:4173',
      env: { VITE_API_URL: 'http://127.0.0.1:8001' },
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
})
