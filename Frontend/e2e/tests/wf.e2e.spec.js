/**
 * wf.e2e.spec.js — Workflow E2E Tests (TEMPLATE)
 * =================================================
 * Tests complete user journeys across the REAL system.
 * Multi-step flows: login as role A → perform action → 
 * login as role B → verify/respond → verify final state.
 *
 * NAMING CONVENTION:
 *   test("WF-1-E2E-01: <complete flow>")
 *   test("WF-1-NEG-01: <failure flow>")
 *
 * KEY FEATURE: Workflow tests can involve MULTIPLE USERS.
 * For example:
 *   Step 1: Login as student, submit a request
 *   Step 2: Login as manager, approve/reject
 *   Step 3: Login as student, verify result
 */

import { test, expect } from "@playwright/test";
import { loginAs, navigateToModule } from "../helpers/auth.setup.js";

// ═══════════════════════════════════════════════════════
// WF-EXAMPLE: Login → Dashboard → Check Profile Flow
// (DELETE and replace with your module's workflows)
// ═══════════════════════════════════════════════════════

test.describe("WF-1: Login and Navigate Workflow", () => {

  test("WF-1-E2E-01: Student logs in and views dashboard", async ({ page }) => {
    // Step 1: Login
    await loginAs(page, "student");
    await page.screenshot({
      path: "e2e/reports/evidence/WF-1-E2E-01_step1_loggedin.png",
    });

    // Step 2: Verify dashboard loaded with data
    await expect(page).toHaveURL(/dashboard/);
    await page.waitForLoadState("networkidle");
    await page.screenshot({
      path: "e2e/reports/evidence/WF-1-E2E-01_step2_dashboard.png",
    });

    // Step 3: Navigate to profile (proves frontend routing works with backend auth)
    await page.goto("/profile");
    await page.waitForLoadState("networkidle");
    await page.screenshot({
      path: "e2e/reports/evidence/WF-1-E2E-01_step3_profile.png",
    });
  });

  test("WF-1-NEG-01: Invalid credentials prevent entire flow", async ({ page }) => {
    // Step 1: Try to login with bad credentials
    await page.goto("/accounts/login");
    await page.keyboard.press("Enter");
    await page.waitForTimeout(500);

    const usernameInput = page.locator('input[type="text"]').first();
    await usernameInput.waitFor({ state: "visible", timeout: 10000 });
    await usernameInput.fill("baduser");
    await page.locator('input[type="password"]').first().fill("badpass");
    await page.locator('button[type="submit"]').or(
      page.getByRole("button", { name: /sign in|log in/i })
    ).click();

    // Step 2: Verify blocked — cannot reach dashboard
    await page.waitForTimeout(3000);
    await expect(page).not.toHaveURL(/dashboard/);

    // Step 3: Verify cannot reach module pages either
    await page.goto("/profile");
    await page.waitForTimeout(2000);
    await expect(page).not.toHaveURL(/profile/);

    await page.screenshot({
      path: "e2e/reports/evidence/WF-1-NEG-01_blocked.png",
    });
  });
});

// ═══════════════════════════════════════════════════════
// YOUR MODULE'S WORKFLOWS (multi-role flows)
// ═══════════════════════════════════════════════════════
//
// test.describe("WF-2: Leave Request → Manager Approval", () => {
//
//   test("WF-2-E2E-01: Student applies, manager approves", async ({ page, context }) => {
//
//     // ── STEP 1: Student applies for leave ──
//     await loginAs(page, "student");
//     await navigateToModule(page, "/mess");
//     await page.click("text=Apply Leave");
//     await page.fill('[name="start_date"]', '2026-05-01');
//     await page.fill('[name="end_date"]', '2026-05-04');
//     await page.fill('[name="purpose"]', 'E2E test leave');
//     await page.click('button:has-text("Apply")');
//     await expect(page.locator("text=submitted")).toBeVisible();
//     await page.screenshot({ path: "e2e/reports/evidence/WF-2-E2E-01_step1.png" });
//
//     // ── STEP 2: Manager logs in and approves ──
//     // Need a new page/context for different user
//     const managerPage = await context.newPage();
//     await loginAs(managerPage, "staff");
//     await navigateToModule(managerPage, "/mess");
//     await managerPage.click("text=Pending Requests");
//     // Find the leave request
//     await managerPage.click('button:has-text("Approve")');
//     await expect(managerPage.locator("text=Approved")).toBeVisible();
//     await managerPage.screenshot({ path: "e2e/reports/evidence/WF-2-E2E-01_step2.png" });
//     await managerPage.close();
//
//     // ── STEP 3: Student verifies approval ──
//     await page.reload();
//     await expect(page.locator("text=Approved")).toBeVisible();
//     await page.screenshot({ path: "e2e/reports/evidence/WF-2-E2E-01_step3.png" });
//   });
//
//   test("WF-2-NEG-01: Student applies, manager rejects", async ({ page, context }) => {
//     // Similar to above but manager clicks "Reject"
//     // Student should see "Rejected" status
//   });
// });
