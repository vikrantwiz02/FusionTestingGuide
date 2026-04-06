// @ts-check
/**
 * Playwright Configuration — Fusion Module E2E Testing
 * ======================================================
 * Tests run against:
 *   - Frontend: http://localhost:5173 (Vite dev server)
 *   - Backend:  http://127.0.0.1:8000 (Django dev server)
 *
 * BOTH SERVERS MUST BE RUNNING before tests execute.
 *
 * RUN MODULE-SPECIFIC TESTS:
 *   npx playwright test e2e/tests/Mess/
 *   npx playwright test e2e/tests/Examination/
 *   npx playwright test e2e/tests/Program_curriculum/
 *
 * RUN ALL MODULES:
 *   npx playwright test e2e/tests/
 */

import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  // Test directory — contains per-module subdirectories
  testDir: "./e2e/tests",

  // Match all .spec.js files in any module subdirectory
  testMatch: "**/*.e2e.spec.js",

  // Maximum time a single test can run
  timeout: 60_000,

  // Retry failed tests once
  retries: 1,

  // Sequential execution (since tests share the same backend state)
  workers: 1,

  // Reporters
  reporter: [
    ["html", { open: "never", outputFolder: "e2e/reports/html" }],
    ["json", { outputFile: "e2e/reports/results.json" }],
    ["list"],
  ],

  // Shared settings
  use: {
    baseURL: "http://localhost:5173",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "on-first-retry",
    viewport: { width: 1280, height: 720 },
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  outputDir: "e2e/reports/test-artifacts",
});
