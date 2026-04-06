#!/usr/bin/env node
/**
 * setup_e2e.js — Module-Specific E2E Test Setup
 * ================================================
 *
 * USAGE (from Fusion-client/ directory):
 *   node e2e/setup_e2e.js <ModuleName>
 *
 * EXAMPLE:
 *   node e2e/setup_e2e.js Mess
 *   node e2e/setup_e2e.js Examination
 *   node e2e/setup_e2e.js Program_curriculum
 *
 * WHAT IT CREATES:
 *   e2e/tests/<ModuleName>/
 *   ├── uc.e2e.spec.js     ← UC tests for this module
 *   ├── br.e2e.spec.js     ← BR tests for this module
 *   ├── wf.e2e.spec.js     ← WF tests for this module
 *   └── reports/
 *       └── evidence/      ← Screenshots saved here
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CLIENT_DIR = path.resolve(__dirname, "..");
const MODULES_DIR = path.join(CLIENT_DIR, "src", "Modules");

const moduleName = process.argv[2];

if (!moduleName) {
  console.log("Usage: node e2e/setup_e2e.js <ModuleName>");
  console.log("\nAvailable modules:");
  if (fs.existsSync(MODULES_DIR)) {
    fs.readdirSync(MODULES_DIR, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .forEach((d) => console.log(`  - ${d.name}`));
  }
  process.exit(1);
}

// Verify module exists in frontend
const moduleDir = path.join(MODULES_DIR, moduleName);
if (!fs.existsSync(moduleDir)) {
  console.error(`❌ Module not found in src/Modules/: ${moduleName}`);
  process.exit(1);
}

// Derive the module URL path (lowercase, used for navigation)
const moduleUrlPath = `/${moduleName.toLowerCase().replace(/_/g, "-")}`;

const testsDir = path.join(__dirname, "tests", moduleName);
const evidenceDir = path.join(testsDir, "reports", "evidence");

// Create directories
[testsDir, evidenceDir].forEach((dir) => {
  fs.mkdirSync(dir, { recursive: true });
});

console.log(`\n🔧 Setting up E2E tests for: ${moduleName}`);
console.log(`   Module URL:  ${moduleUrlPath}`);
console.log(`   Tests dir:   e2e/tests/${moduleName}/`);

// ═══════════════════════════════════════════════════════
// uc.e2e.spec.js
// ═══════════════════════════════════════════════════════
fs.writeFileSync(
  path.join(testsDir, "uc.e2e.spec.js"),
  `/**
 * Use Case E2E Tests — ${moduleName} Module
 * ============================================
 * REAL browser → REAL frontend → REAL backend → REAL database
 * No mocks. Full stack.
 *
 * NAMING (required for CSV reports):
 *   test("UC-1-HP-01: <description>")
 *   test("UC-1-AP-01: <description>")
 *   test("UC-1-EX-01: <description>")
 *
 * RUN ONLY THIS MODULE:
 *   npx playwright test e2e/tests/${moduleName}/
 */

import { test, expect } from "@playwright/test";
import { loginAs, navigateToModule } from "../../helpers/auth.setup.js";

// ── Module URL ──
const MODULE_URL = "${moduleUrlPath}";

// ═══════════════════════════════════════════════════════
// UC-1: YOUR FIRST USE CASE (replace with your module's UC)
// ═══════════════════════════════════════════════════════

test.describe("UC-1: Access ${moduleName} Module", () => {

  test("UC-1-HP-01: Student navigates to ${moduleName} page", async ({ page }) => {
    // Login as student
    await loginAs(page, "student");

    // Navigate to module
    await navigateToModule(page, MODULE_URL);

    // Verify module page loaded (change this to match your module's content)
    await page.waitForLoadState("networkidle");

    // Screenshot as evidence
    await page.screenshot({
      path: "e2e/tests/${moduleName}/reports/evidence/UC-1-HP-01.png",
      fullPage: true,
    });
  });

  test("UC-1-AP-01: Staff user accesses ${moduleName}", async ({ page }) => {
    await loginAs(page, "staff");
    await navigateToModule(page, MODULE_URL);
    await page.waitForLoadState("networkidle");

    await page.screenshot({
      path: "e2e/tests/${moduleName}/reports/evidence/UC-1-AP-01.png",
    });
  });

  test("UC-1-EX-01: Unauthenticated user cannot access ${moduleName}", async ({ page }) => {
    // Try to access module directly without login
    await page.goto(MODULE_URL);
    await page.waitForTimeout(2000);

    // Should redirect to login
    await expect(page).toHaveURL(/login|accounts/);

    await page.screenshot({
      path: "e2e/tests/${moduleName}/reports/evidence/UC-1-EX-01.png",
    });
  });
});

// ═══════════════════════════════════════════════════════
// ADD MORE USE CASES BELOW (from your UC spec document)
// ═══════════════════════════════════════════════════════
//
// test.describe("UC-2: <Your UC Title>", () => {
//
//   test.beforeEach(async ({ page }) => {
//     await loginAs(page, "student");
//     await navigateToModule(page, MODULE_URL);
//   });
//
//   test("UC-2-HP-01: <Happy path>", async ({ page }) => {
//     // Interact with your module's UI
//     // await page.click("text=Some Tab");
//     // await page.fill('[name="field"]', "value");
//     // await page.click('button:has-text("Submit")');
//     // await expect(page.locator("text=Success")).toBeVisible();
//     // await page.screenshot({ path: "e2e/tests/${moduleName}/reports/evidence/UC-2-HP-01.png" });
//   });
//
//   test("UC-2-AP-01: <Alternate path>", async ({ page }) => { });
//   test("UC-2-EX-01: <Exception path>", async ({ page }) => { });
// });
`
);

// ═══════════════════════════════════════════════════════
// br.e2e.spec.js
// ═══════════════════════════════════════════════════════
fs.writeFileSync(
  path.join(testsDir, "br.e2e.spec.js"),
  `/**
 * Business Rule E2E Tests — ${moduleName} Module
 * =================================================
 * Tests that constraints, validations, and permissions
 * are enforced in the real running system.
 *
 * NAMING:
 *   test("BR-1-V-01: <valid case>")
 *   test("BR-1-I-01: <invalid case>")
 *
 * RUN ONLY THIS MODULE:
 *   npx playwright test e2e/tests/${moduleName}/
 */

import { test, expect } from "@playwright/test";
import { loginAs, navigateToModule } from "../../helpers/auth.setup.js";

const MODULE_URL = "${moduleUrlPath}";

// ═══════════════════════════════════════════════════════
// BR-1: YOUR FIRST BUSINESS RULE
// ═══════════════════════════════════════════════════════

test.describe("BR-1: Authentication required for ${moduleName}", () => {

  test("BR-1-V-01: Authenticated user can access module", async ({ page }) => {
    await loginAs(page, "student");
    await navigateToModule(page, MODULE_URL);

    // Should be on the module page (not redirected)
    await page.waitForLoadState("networkidle");

    await page.screenshot({
      path: "e2e/tests/${moduleName}/reports/evidence/BR-1-V-01.png",
    });
  });

  test("BR-1-I-01: Unauthenticated user is redirected", async ({ page }) => {
    await page.goto(MODULE_URL);
    await page.waitForTimeout(2000);
    await expect(page).toHaveURL(/login|accounts/);

    await page.screenshot({
      path: "e2e/tests/${moduleName}/reports/evidence/BR-1-I-01.png",
    });
  });
});

// ═══════════════════════════════════════════════════════
// ADD MORE BUSINESS RULES BELOW
// ═══════════════════════════════════════════════════════
//
// test.describe("BR-2: <Your Rule>", () => {
//
//   test.beforeEach(async ({ page }) => {
//     await loginAs(page, "student");
//     await navigateToModule(page, MODULE_URL);
//   });
//
//   test("BR-2-V-01: Valid input accepted", async ({ page }) => {
//     // Fill form with valid data
//     // Verify accepted
//   });
//
//   test("BR-2-I-01: Invalid input rejected", async ({ page }) => {
//     // Fill form with invalid data
//     // Verify error shown
//   });
// });
`
);

// ═══════════════════════════════════════════════════════
// wf.e2e.spec.js
// ═══════════════════════════════════════════════════════
fs.writeFileSync(
  path.join(testsDir, "wf.e2e.spec.js"),
  `/**
 * Workflow E2E Tests — ${moduleName} Module
 * ============================================
 * Tests complete multi-step, multi-role user flows.
 *
 * KEY FEATURE: Can test flows involving MULTIPLE USERS:
 *   Step 1: Login as student → submit request
 *   Step 2: Login as manager → approve/reject
 *   Step 3: Login as student → verify result
 *
 * NAMING:
 *   test("WF-1-E2E-01: <complete flow>")
 *   test("WF-1-NEG-01: <failure flow>")
 *
 * RUN ONLY THIS MODULE:
 *   npx playwright test e2e/tests/${moduleName}/
 */

import { test, expect } from "@playwright/test";
import { loginAs, navigateToModule } from "../../helpers/auth.setup.js";

const MODULE_URL = "${moduleUrlPath}";

// ═══════════════════════════════════════════════════════
// WF-1: YOUR FIRST WORKFLOW
// ═══════════════════════════════════════════════════════

test.describe("WF-1: Login → Navigate → Use ${moduleName}", () => {

  test("WF-1-E2E-01: Student logs in and accesses ${moduleName}", async ({ page }) => {
    // Step 1: Login
    await loginAs(page, "student");
    await page.screenshot({
      path: "e2e/tests/${moduleName}/reports/evidence/WF-1-E2E-01_step1.png",
    });

    // Step 2: Navigate to module
    await navigateToModule(page, MODULE_URL);
    await page.waitForLoadState("networkidle");
    await page.screenshot({
      path: "e2e/tests/${moduleName}/reports/evidence/WF-1-E2E-01_step2.png",
    });

    // Step 3: Verify module content is visible
    // Change this assertion to match YOUR module's content
    // await expect(page.locator("text=<your module heading>")).toBeVisible();
  });

  test("WF-1-NEG-01: Invalid login blocks entire flow", async ({ page }) => {
    await page.goto("/accounts/login");
    await page.keyboard.press("Enter");
    await page.waitForTimeout(500);

    const usernameInput = page.locator('input[type="text"]').first();
    await usernameInput.waitFor({ state: "visible", timeout: 10000 });
    await usernameInput.fill("fakeuser");
    await page.locator('input[type="password"]').first().fill("wrongpass");
    await page.locator('button[type="submit"]').or(
      page.getByRole("button", { name: /sign in|log in/i })
    ).click();

    await page.waitForTimeout(3000);
    await expect(page).not.toHaveURL(/dashboard/);

    // Cannot reach module either
    await page.goto(MODULE_URL);
    await page.waitForTimeout(2000);
    await expect(page).not.toHaveURL(new RegExp(MODULE_URL.slice(1)));

    await page.screenshot({
      path: "e2e/tests/${moduleName}/reports/evidence/WF-1-NEG-01.png",
    });
  });
});

// ═══════════════════════════════════════════════════════
// ADD MULTI-ROLE WORKFLOWS BELOW
// ═══════════════════════════════════════════════════════
//
// test.describe("WF-2: <Multi-role flow>", () => {
//
//   test("WF-2-E2E-01: Student submits → Manager approves", async ({ page, context }) => {
//     // ── Step 1: Student action ──
//     await loginAs(page, "student");
//     await navigateToModule(page, MODULE_URL);
//     // ... fill form, submit
//     await page.screenshot({ path: "e2e/tests/${moduleName}/reports/evidence/WF-2-step1.png" });
//
//     // ── Step 2: Manager action (NEW browser tab) ──
//     const managerPage = await context.newPage();
//     await loginAs(managerPage, "staff");
//     await navigateToModule(managerPage, MODULE_URL);
//     // ... find request, approve
//     await managerPage.screenshot({ path: "e2e/tests/${moduleName}/reports/evidence/WF-2-step2.png" });
//     await managerPage.close();
//
//     // ── Step 3: Student verifies ──
//     await page.reload();
//     // await expect(page.locator("text=Approved")).toBeVisible();
//     await page.screenshot({ path: "e2e/tests/${moduleName}/reports/evidence/WF-2-step3.png" });
//   });
// });
`
);

console.log(`  📄 Created uc.e2e.spec.js`);
console.log(`  📄 Created br.e2e.spec.js`);
console.log(`  📄 Created wf.e2e.spec.js`);
console.log(`  📁 Created reports/evidence/`);

console.log(`\n✅ E2E tests created for: ${moduleName}`);
console.log(`\n${"=".repeat(60)}`);
console.log("📋 NEXT STEPS");
console.log("=".repeat(60));
console.log(`
1. INSTALL PLAYWRIGHT (one-time, from Fusion-client/):
   npm install -D @playwright/test
   npx playwright install chromium

2. SET REAL CREDENTIALS:
   Edit e2e/helpers/auth.setup.js
   → Set real username/password for student, staff, faculty

3. EDIT YOUR TESTS:
   e2e/tests/${moduleName}/uc.e2e.spec.js   ← Replace example UCs
   e2e/tests/${moduleName}/br.e2e.spec.js   ← Replace example BRs
   e2e/tests/${moduleName}/wf.e2e.spec.js   ← Replace example WFs

4. RUN ONLY YOUR MODULE's E2E TESTS:
   ./e2e/run_e2e.sh ${moduleName}

5. OR MANUALLY (if servers already running):
   npx playwright test e2e/tests/${moduleName}/

6. COLLECT REPORTS:
   e2e/tests/${moduleName}/reports/evidence/  ← Screenshots
   e2e/reports/                               ← CSV reports

7. DEBUG A FAILING TEST:
   npx playwright test e2e/tests/${moduleName}/ --headed --debug
`);
