/**
 * auth.setup.js — Shared Authentication Helper
 * ================================================
 * Handles login for E2E tests. Every test file imports this
 * to get an authenticated browser session.
 *
 * TEAMS: Update the credentials below with valid test accounts
 * from your PostgreSQL database.
 */

import { expect } from "@playwright/test";

// ── TEST CREDENTIALS ──
// These must be REAL users in your local database.
// Ask your team lead or check the DB dump for valid accounts.
export const TEST_USERS = {
  student: {
    username: "student1",    // CHANGE to a real student username
    password: "student123",  // CHANGE to real password
    role: "student",
  },
  staff: {
    username: "staff1",      // CHANGE to a real staff username
    password: "staff123",    // CHANGE to real password
    role: "staff",
  },
  faculty: {
    username: "faculty1",    // CHANGE to a real faculty username
    password: "faculty123",  // CHANGE to real password
    role: "faculty",
  },
};

/**
 * Login as a specific user role.
 * Called at the start of each test that needs authentication.
 *
 * @param {import('@playwright/test').Page} page
 * @param {"student" | "staff" | "faculty"} role
 */
export async function loginAs(page, role) {
  const user = TEST_USERS[role];
  if (!user) throw new Error(`Unknown role: ${role}`);

  // Navigate to login page
  await page.goto("/accounts/login");

  // Wait for login form to appear
  // The Fusion login has a "landing" view first, click to get to login form
  const loginInput = page.getByPlaceholder(/username/i).or(
    page.locator('input[type="text"]').first()
  );

  // If on landing page, click to get to login form
  const isLanding = await page.locator("text=Enter").isVisible().catch(() => false);
  if (isLanding) {
    await page.keyboard.press("Enter");
    await page.waitForTimeout(500);
  }

  // Fill credentials
  await loginInput.waitFor({ state: "visible", timeout: 10000 });
  await loginInput.fill(user.username);

  const passwordInput = page.getByPlaceholder(/password/i).or(
    page.locator('input[type="password"]').first()
  );
  await passwordInput.fill(user.password);

  // Click login button
  await page.locator('button[type="submit"]').or(
    page.getByRole("button", { name: /sign in|log in|login|authenticate/i })
  ).click();

  // Wait for redirect to dashboard (proves login worked)
  await page.waitForURL("**/dashboard**", { timeout: 15000 });

  // Verify we're on the dashboard
  await expect(page).toHaveURL(/dashboard/);
}

/**
 * Navigate to a specific module page after login.
 * @param {import('@playwright/test').Page} page
 * @param {string} modulePath - e.g., "/examination", "/mess"
 */
export async function navigateToModule(page, modulePath) {
  await page.goto(modulePath);
  await page.waitForLoadState("networkidle");
}
