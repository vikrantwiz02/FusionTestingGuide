/**
 * br.e2e.spec.js — Business Rule E2E Tests (TEMPLATE)
 * =====================================================
 * Tests that constraints, validations, and permissions
 * are enforced in the real running system.
 *
 * NAMING CONVENTION:
 *   test("BR-1-V-01: <valid case>")
 *   test("BR-1-I-01: <invalid case>")
 */

import { test, expect } from "@playwright/test";
import { loginAs, navigateToModule } from "../helpers/auth.setup.js";

// ═══════════════════════════════════════════════════════
// BR-EXAMPLE: Authentication Required (DELETE and replace)
// ═══════════════════════════════════════════════════════

test.describe("BR-1: Authentication Required for Module Access", () => {

  test("BR-1-V-01: Authenticated user can access module page", async ({ page }) => {
    // Login first
    await loginAs(page, "student");

    // Navigate to module
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/dashboard/);

    await page.screenshot({
      path: "e2e/reports/evidence/BR-1-V-01_authenticated_access.png",
    });
  });

  test("BR-1-I-01: Unauthenticated user is redirected to login", async ({ page }) => {
    // Try to access dashboard without login
    await page.goto("/dashboard");

    // Should be redirected to login page
    await page.waitForTimeout(2000);
    await expect(page).toHaveURL(/login|accounts/);

    await page.screenshot({
      path: "e2e/reports/evidence/BR-1-I-01_redirect_to_login.png",
    });
  });
});

// ═══════════════════════════════════════════════════════
// YOUR MODULE'S BUSINESS RULES
// ═══════════════════════════════════════════════════════
//
// test.describe("BR-2: Casual Leave Duration Constraint (3-5 days)", () => {
//
//   test.beforeEach(async ({ page }) => {
//     await loginAs(page, "student");
//     await navigateToModule(page, "/mess");
//     await page.click("text=Apply Leave");
//   });
//
//   test("BR-2-V-01: 4-day casual leave is accepted", async ({ page }) => {
//     await page.fill('[name="start_date"]', '2026-04-15');
//     await page.fill('[name="end_date"]', '2026-04-18');
//     await page.selectOption('[name="leave_type"]', 'casual');
//     await page.fill('[name="purpose"]', 'Family event');
//     await page.click('button:has-text("Apply")');
//
//     await expect(page.locator("text=submitted")).toBeVisible({ timeout: 5000 });
//     await page.screenshot({ path: "e2e/reports/evidence/BR-2-V-01.png" });
//   });
//
//   test("BR-2-I-01: 1-day casual leave is rejected", async ({ page }) => {
//     await page.fill('[name="start_date"]', '2026-04-15');
//     await page.fill('[name="end_date"]', '2026-04-15');
//     await page.selectOption('[name="leave_type"]', 'casual');
//     await page.fill('[name="purpose"]', 'Quick trip');
//     await page.click('button:has-text("Apply")');
//
//     // Should show error about minimum duration
//     await expect(page.locator("text=minimum")).toBeVisible({ timeout: 5000 });
//     await page.screenshot({ path: "e2e/reports/evidence/BR-2-I-01.png" });
//   });
// });
