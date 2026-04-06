
## 14. Full-Stack E2E Testing (Playwright)

> [!IMPORTANT]
> The backend framework (Sections 1–13) covers **API + DB testing in isolation**. This section covers **full-stack integration testing** — a real browser → real frontend → real backend → real database. **No mocks. Everything connected.**

### 14.1 What E2E Tests Prove

| Question | How it's answered |
|----------|------------------|
| Does the frontend + backend work together? | Playwright opens a real Chrome, logs into the real app, performs real actions |
| Are API response formats correct? | If frontend can't display data from the real backend, the test fails |
| Do multi-role workflows work? | Test logs in as Student → submits request → logs in as Manager → approves it |
| Does auth actually protect pages? | Test tries to access pages without login, verifies redirect |

### 14.2 E2E Testing Stack

| Tool | Purpose |
|------|---------|
| **Playwright** | Opens a real browser, clicks real buttons, fills real forms |
| **Real Django server** | Backend runs on `http://127.0.0.1:8000` |
| **Real Vite server** | Frontend runs on `http://localhost:5173` |
| **Real PostgreSQL** | Actual database with real data |

### 14.3 Setup (Per Module)

```bash
# From Fusion-client/ directory

# 1. Install Playwright (one-time)
npm install -D @playwright/test
npx playwright install chromium

# 2. Update test credentials with REAL users from your database
#    Edit: e2e/helpers/auth.setup.js
#    Set real username/password for student, staff, faculty roles

# 3. Generate E2E tests for YOUR MODULE (one-time)
node e2e/setup_e2e.js Mess           # ← Replace with your module name
node e2e/setup_e2e.js Examination    # Another example
node e2e/setup_e2e.js Program_curriculum
```

This creates `e2e/tests/<YourModule>/` with UC/BR/WF test templates specific to your module.

### 14.4 Run YOUR Module's Tests (Single Command)

```bash
# From Fusion-client/ directory
./e2e/run_e2e.sh Mess               # ← Only Mess tests
./e2e/run_e2e.sh Examination        # ← Only Examination tests
./e2e/run_e2e.sh                    # ← ALL modules (optional)
```

This script automatically:
1. Starts the Django backend server
2. Starts the Vite frontend server
3. Waits for both to be ready
4. Runs Playwright E2E tests **only for the specified module**
5. Captures screenshots as evidence
6. Generates CSV reports (same 7-sheet format)
7. Stops both servers

### 14.5 E2E File Structure (Module-Specific)

```
Fusion-client/
├── playwright.config.js                ← Playwright configuration
└── e2e/
    ├── setup_e2e.js                    ← Run: node e2e/setup_e2e.js <Module>
    ├── run_e2e.sh                      ← Run: ./e2e/run_e2e.sh <Module>
    ├── helpers/
    │   ├── auth.setup.js               ← Login helper (EDIT credentials)
    │   └── csv-reporter.js             ← CSV report generator
    ├── tests/
    │   ├── Mess/                       ← Mess team's tests
    │   │   ├── uc.e2e.spec.js
    │   │   ├── br.e2e.spec.js
    │   │   ├── wf.e2e.spec.js
    │   │   └── reports/evidence/       ← Screenshots
    │   ├── Examination/                ← Examination team's tests
    │   │   ├── uc.e2e.spec.js
    │   │   ├── br.e2e.spec.js
    │   │   ├── wf.e2e.spec.js
    │   │   └── reports/evidence/
    │   └── <YourModule>/               ← Your team's tests
    │       └── ...
    └── reports/                        ← Shared CSV output
        ├── html/                       ← Visual HTML report
        └── *.csv                       ← 7-sheet workbook
```

**Each module's tests are isolated.** Mess team only edits `e2e/tests/Mess/`. Examination team only edits `e2e/tests/Examination/`. No conflicts.

### 14.6 Test Naming Convention (Required for Reports)

Test titles **must** start with the spec ID for automatic CSV generation:

```js
// Use Case tests
test("UC-1-HP-01: Student submits feedback successfully")
test("UC-1-AP-01: Different feedback types work")
test("UC-1-EX-01: Empty description shows error")

// Business Rule tests
test("BR-1-V-01: 4-day casual leave accepted")
test("BR-1-I-01: 1-day casual leave rejected")

// Workflow tests
test("WF-1-E2E-01: Student applies, manager approves")
test("WF-1-NEG-01: Student applies, manager rejects")
```

The CSV reporter parses these IDs to auto-generate Sheet 5, 6, and 7.

### 14.7 E2E Test Patterns

#### Pattern 1: UC — Test a Feature in the Real UI

```js
import { test, expect } from "@playwright/test";
import { loginAs, navigateToModule } from "../helpers/auth.setup.js";

test.describe("UC-2: Submit Feedback", () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, "student");       // Real login
    await navigateToModule(page, "/mess"); // Real navigation
  });

  test("UC-2-HP-01: Student submits feedback", async ({ page }) => {
    await page.click("text=Feedback");
    await page.fill('[name="description"]', "Good food");
    await page.click('button:has-text("Submit")');

    await expect(page.locator("text=submitted")).toBeVisible();

    // Screenshot saved as evidence for Test_Execution_Log
    await page.screenshot({
      path: "e2e/reports/evidence/UC-2-HP-01.png",
    });
  });
});
```

#### Pattern 2: BR — Test Constraint Enforcement

```js
test.describe("BR-2: Casual Leave 3-5 Day Constraint", () => {

  test("BR-2-V-01: 4-day leave accepted", async ({ page }) => {
    await loginAs(page, "student");
    await navigateToModule(page, "/mess");
    await page.fill('[name="start_date"]', '2026-05-01');
    await page.fill('[name="end_date"]', '2026-05-04');
    await page.click('button:has-text("Apply")');
    await expect(page.locator("text=submitted")).toBeVisible();
  });

  test("BR-2-I-01: 1-day leave rejected", async ({ page }) => {
    await loginAs(page, "student");
    await navigateToModule(page, "/mess");
    await page.fill('[name="start_date"]', '2026-05-01');
    await page.fill('[name="end_date"]', '2026-05-01');
    await page.click('button:has-text("Apply")');
    await expect(page.locator("text=minimum")).toBeVisible();
  });
});
```

#### Pattern 3: WF — Multi-Role Workflow (Most Powerful)

```js
test.describe("WF-2: Leave Request → Manager Approval", () => {

  test("WF-2-E2E-01: Student applies, manager approves", async ({ page, context }) => {

    // ── Step 1: Student applies for leave ──
    await loginAs(page, "student");
    await navigateToModule(page, "/mess");
    await page.click("text=Apply Leave");
    await page.fill('[name="start_date"]', '2026-05-01');
    await page.fill('[name="end_date"]', '2026-05-04');
    await page.click('button:has-text("Apply")');
    await expect(page.locator("text=submitted")).toBeVisible();
    await page.screenshot({ path: "e2e/reports/evidence/WF-2-step1.png" });

    // ── Step 2: Manager approves (new browser tab, different user) ──
    const managerPage = await context.newPage();
    await loginAs(managerPage, "staff");
    await navigateToModule(managerPage, "/mess");
    await managerPage.click("text=Pending");
    await managerPage.click('button:has-text("Approve")');
    await managerPage.screenshot({ path: "e2e/reports/evidence/WF-2-step2.png" });
    await managerPage.close();

    // ── Step 3: Student verifies approval ──
    await page.reload();
    await expect(page.locator("text=Approved")).toBeVisible();
    await page.screenshot({ path: "e2e/reports/evidence/WF-2-step3.png" });
  });
});
```

### 14.8 How Backend + E2E Tests Fit Together

```
 ┌────────────────────────────────────────────────────────┐
 │               YOUR MODULE'S TESTING                    │
 ├──────────────────────┬─────────────────────────────────┤
 │  BACKEND TESTS       │  E2E TESTS (Playwright)         │
 │  (Django TestCase)   │                                 │
 │                      │                                 │
 │  Tests in isolation: │  Tests EVERYTHING connected:    │
 │  • API logic correct │  • Real browser opens UI        │
 │  • DB state changes  │  • Real login to real backend   │
 │  • Validation rules  │  • Real forms, real API calls   │
 │  • No browser needed │  • Real DB state changes        │
 │                      │  • Multi-role workflows          │
 │                      │  • Auto-screenshots as evidence  │
 │                      │                                 │
 │  Command:            │  Command:                       │
 │  python manage.py    │  ./e2e/run_e2e.sh <Module>      │
 │  test apps.<mod>     │                                 │
 │  .tests -v 2         │  (starts both servers, runs     │
 │                      │   tests for YOUR module only,   │
 │  Reports: 7 CSVs     │   generates reports,            │
 │  (auto-generated)    │   stops servers)                │
 │                      │  Reports: 7 CSVs + screenshots  │
 │                      │  + HTML report + video on fail   │
 └──────────────────────┴─────────────────────────────────┘
```

> [!TIP]
> **Both count towards your deliverables.** Backend tests verify API correctness fast (no browser). E2E tests prove the full system works end-to-end. Combined, they give you maximum coverage and evidence.

### 14.9 Running E2E Tests (Commands)

```bash
# Full automated run — YOUR MODULE ONLY (recommended)
./e2e/run_e2e.sh Mess
./e2e/run_e2e.sh Examination

# Run all modules
./e2e/run_e2e.sh

# Or manually (if servers are already running):
npx playwright test e2e/tests/Mess/                 # Only Mess
npx playwright test e2e/tests/Examination/          # Only Examination
npx playwright test e2e/tests/                      # All modules

# Generate CSV reports after manual run
node e2e/helpers/csv-reporter.js

# View HTML report
npx playwright show-report e2e/reports/html

# Debug a failing test (opens browser visually)
npx playwright test e2e/tests/Mess/ --headed --debug
```

---

## Appendix: File Listing

```
BACKEND (Fusion/FusionIIIT/)
├── setup_tests.py                            ← Run: python setup_tests.py <module>
├── _testing_framework/                       ← Template (don't edit directly)
│   ├── __init__.py
│   ├── conftest.py                           ← Base setup template
│   ├── test_use_cases.py                     ← UC test template
│   ├── test_business_rules.py                ← BR test template
│   ├── test_workflows.py                     ← WF test template
│   ├── runner.py                             ← Report generator (auto 7 CSVs)
│   └── specs/
│       ├── use_cases.yaml                    ← YAML template
│       ├── business_rules.yaml               ← YAML template
│       └── workflows.yaml                    ← YAML template
└── applications/<your_module>/
    └── tests/                                ← Created by setup_tests.py
        ├── (same structure as framework)
        └── reports/                          ← Auto-generated CSVs

E2E / FULL-STACK (Fusion-client/)
├── playwright.config.js                      ← Playwright configuration
└── e2e/
    ├── setup_e2e.js                          ← Run: node e2e/setup_e2e.js <Module>
    ├── run_e2e.sh                            ← Run: ./e2e/run_e2e.sh <Module>
    ├── helpers/
    │   ├── auth.setup.js                     ← Login helper (set real credentials)
    │   └── csv-reporter.js                   ← Generates 7-sheet CSVs
    └── tests/
        ├── Mess/                             ← Mess team's E2E tests
        │   ├── uc.e2e.spec.js
        │   ├── br.e2e.spec.js
        │   ├── wf.e2e.spec.js
        │   └── reports/evidence/             ← Auto-captured screenshots
        ├── Examination/                      ← Examination team's tests
        └── <YourModule>/                     ← Your team's tests
```


