/**
 * uc.e2e.spec.js — Use Case E2E Tests (TEMPLATE)
 * ==================================================
 * REAL browser → REAL frontend → REAL backend → REAL database
 * No mocks. Full stack integration.
 *
 * HOW TO USE:
 *   1. Copy this file for your module
 *   2. Replace EXAMPLE tests with your actual UC tests
 *   3. Update loginAs() role and module URLs for your module
 *
 * NAMING CONVENTION (required for CSV report generation):
 *   test("UC-1-HP-01: <description>")
 *   test("UC-1-AP-01: <description>")
 *   test("UC-1-EX-01: <description>")
 *
 * The test ID prefix (UC-1-HP-01) is parsed by the CSV reporter
 * to generate Sheet 5, 6, and 7 automatically.
 */

import { test, expect } from "@playwright/test";
import { loginAs, navigateToModule } from "../helpers/auth.setup.js";

// ═══════════════════════════════════════════════════════
// UC-EXAMPLE: Login Use Case (DELETE and replace with yours)
// ═══════════════════════════════════════════════════════

test.describe("UC-1: User Login", () => {

  test("UC-1-HP-01: Student logs in with valid credentials", async ({ page }) => {
    // Navigate to login page
    await page.goto("/accounts/login");

    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // This test IS the login flow — if loginAs succeeds, login works
    await loginAs(page, "student");

    // Verify dashboard is visible
    await expect(page).toHaveURL(/dashboard/);

    // Take screenshot as evidence
    await page.screenshot({
      path: "e2e/reports/evidence/UC-1-HP-01_dashboard.png",
      fullPage: true,
    });
  });

  test("UC-1-AP-01: Staff user logs in (different role)", async ({ page }) => {
    await loginAs(page, "staff");
    await expect(page).toHaveURL(/dashboard/);

    await page.screenshot({
      path: "e2e/reports/evidence/UC-1-AP-01_staff_dashboard.png",
    });
  });

  test("UC-1-EX-01: Login fails with wrong password", async ({ page }) => {
    await page.goto("/accounts/login");

    // Get to the login form
    await page.keyboard.press("Enter");
    await page.waitForTimeout(500);

    // Fill wrong credentials
    const usernameInput = page.locator('input[type="text"]').first();
    await usernameInput.waitFor({ state: "visible", timeout: 10000 });
    await usernameInput.fill("fakeuser");
    await page.locator('input[type="password"]').first().fill("wrongpassword");

    // Click login
    await page.locator('button[type="submit"]').or(
      page.getByRole("button", { name: /sign in|log in|login/i })
    ).click();

    // Should not redirect to dashboard
    await page.waitForTimeout(2000);
    await expect(page).not.toHaveURL(/dashboard/);

    // Should show error notification
    // (Fusion shows orange notification with "ACCESS DENIED")
    await page.screenshot({
      path: "e2e/reports/evidence/UC-1-EX-01_login_failed.png",
    });
  });
});

// ═══════════════════════════════════════════════════════
// YOUR MODULE'S USE CASES — Replace examples below
// ═══════════════════════════════════════════════════════
//
// test.describe("UC-2: Submit Feedback", () => {
//
//   test.beforeEach(async ({ page }) => {
//     // Login before each test
//     await loginAs(page, "student");
//     // Navigate to your module
//     await navigateToModule(page, "/mess");
//   });
//
//   test("UC-2-HP-01: Student submits feedback successfully", async ({ page }) => {
//     // Click "Feedback" tab
//     await page.click("text=Feedback");
//
//     // Fill feedback form
//     await page.fill('[name="description"]', "Food quality is great today");
//     await page.selectOption('[name="feedback_type"]', "food");
//
//     // Submit
//     await page.click('button:has-text("Submit")');
//
//     // Verify success notification
//     await expect(page.locator("text=Feedback submitted")).toBeVisible();
//
//     // Screenshot as evidence
//     await page.screenshot({
//       path: "e2e/reports/evidence/UC-2-HP-01_feedback_submitted.png",
//     });
//   });
//
//   test("UC-2-AP-01: Different feedback types work", async ({ page }) => {
//     await page.click("text=Feedback");
//     await page.fill('[name="description"]', "Bathroom needs cleaning");
//     await page.selectOption('[name="feedback_type"]', "cleanliness");
//     await page.click('button:has-text("Submit")');
//     await expect(page.locator("text=Feedback submitted")).toBeVisible();
//   });
//
//   test("UC-2-EX-01: Empty description shows error", async ({ page }) => {
//     await page.click("text=Feedback");
//     // Don't fill description
//     await page.click('button:has-text("Submit")');
//     await expect(page.locator("text=required")).toBeVisible();
//   });
// });
