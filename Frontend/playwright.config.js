// @ts-check
/**
 * Playwright Configuration — Fusion E2E Testing
 * ================================================
 * This config runs tests against:
 *   - Frontend: http://localhost:5173 (Vite dev server)
 *   - Backend:  http://127.0.0.1:8000 (Django dev server)
 *
 * BOTH SERVERS MUST BE RUNNING before tests execute.
 * See the run_e2e.sh script for automated startup.
 */

import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  // Where E2E test files live
  testDir: "./e2e",

  // Maximum time a single test can run
  timeout: 60_000,

  // Retry failed tests once
  retries: 1,

  // Run tests in parallel (disable for debugging)
  workers: 1,

  // Reporter: generates HTML report + console output
  reporter: [
    ["html", { open: "never", outputFolder: "e2e/reports/html" }],
    ["json", { outputFile: "e2e/reports/results.json" }],
    ["list"],
  ],

  // Shared settings for all tests
  use: {
    // Base URL of frontend
    baseURL: "http://localhost:5173",

    // Auto-capture screenshots on failure
    screenshot: "only-on-failure",

    // Record video on failure
    video: "retain-on-failure",

    // Capture trace on first retry (for debugging)
    trace: "on-first-retry",

    // Browser viewport
    viewport: { width: 1280, height: 720 },
  },

  // Test projects (browsers)
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  // Output directory for screenshots, videos, traces
  outputDir: "e2e/reports/test-artifacts",
});
