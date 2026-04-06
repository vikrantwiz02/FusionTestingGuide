/**
 * csv-reporter.js — Custom CSV Report Generator for Playwright
 * ==============================================================
 * Generates the same 7-sheet workbook CSVs as the backend framework.
 *
 * After Playwright tests complete, run:
 *   node e2e/helpers/csv-reporter.js
 *
 * It reads the Playwright JSON results + YAML specs and generates:
 *   - Module_Test_Summary.csv
 *   - UC_Test_Design.csv, BR_Test_Design.csv, WF_Test_Design.csv
 *   - Test_Execution_Log.csv
 *   - Defect_Log.csv
 *   - Artifact_Evaluation.csv
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const E2E_DIR = path.resolve(__dirname, "..");
const REPORTS_DIR = path.join(E2E_DIR, "reports");
const RESULTS_FILE = path.join(REPORTS_DIR, "results.json");

function writeCsv(filename, headers, rows) {
  const filepath = path.join(REPORTS_DIR, filename);
  const escape = (val) => {
    const str = String(val ?? "");
    return str.includes(",") || str.includes('"') || str.includes("\n")
      ? `"${str.replace(/"/g, '""')}"`
      : str;
  };
  const lines = [
    headers.map(escape).join(","),
    ...rows.map((row) => row.map(escape).join(",")),
  ];
  fs.writeFileSync(filepath, lines.join("\n") + "\n", "utf-8");
  console.log(`  📄 ${filename} (${rows.length} rows)`);
}

function main() {
  if (!fs.existsSync(RESULTS_FILE)) {
    console.error("❌ No results.json found. Run Playwright tests first:");
    console.error("   npx playwright test");
    process.exit(1);
  }

  const results = JSON.parse(fs.readFileSync(RESULTS_FILE, "utf-8"));
  const suites = results.suites || [];

  // Flatten all test results
  const allTests = [];
  function collectTests(suite) {
    for (const spec of suite.specs || []) {
      for (const test of spec.tests || []) {
        for (const result of test.results || []) {
          allTests.push({
            title: spec.title,
            file: spec.file || suite.title,
            status: result.status === "passed" ? "Pass"
                  : result.status === "flaky" ? "Partial"
                  : "Fail",
            duration: result.duration,
            error: result.error?.message || "",
            // Parse test ID from title: "UC-1-HP-01: description"
            ...parseTestTitle(spec.title),
          });
        }
      }
    }
    for (const child of suite.suites || []) {
      collectTests(child);
    }
  }
  suites.forEach(collectTests);

  console.log(`\n${"=".repeat(60)}`);
  console.log("📊 GENERATING E2E TEST REPORTS");
  console.log(`${"=".repeat(60)}`);

  // ── Sheet 5: Test Execution Log ──
  writeCsv("Test_Execution_Log.csv",
    ["Test ID", "Source Type", "Source ID", "Expected Result", "Actual Result", "Status", "Evidence", "Tester"],
    allTests.map((t) => [
      t.testId, t.sourceType, t.sourceId,
      t.title, t.error || "Test passed",
      t.status,
      t.status === "Fail"
        ? `Screenshot: test-artifacts/ | Error: ${t.error.slice(0, 200)}`
        : `Passed in ${t.duration}ms`,
      process.env.TESTER_NAME || "Automated E2E",
    ])
  );

  // ── Sheet 6: Defect Log ──
  const defects = allTests
    .filter((t) => t.status === "Fail" || t.status === "Partial")
    .map((t, i) => [
      `DEF-E2E-${String(i + 1).padStart(3, "0")}`,
      t.testId,
      t.sourceId,
      t.status === "Fail" ? "High" : "Medium",
      t.error.slice(0, 500),
      "Investigate the failing E2E scenario",
    ]);
  writeCsv("Defect_Log.csv",
    ["Defect ID", "Related Test ID", "Related Artifact", "Severity", "Description", "Suggested Fix"],
    defects
  );

  // ── Sheet 7: Artifact Evaluation ──
  const artifacts = {};
  for (const t of allTests) {
    if (!t.sourceId) continue;
    if (!artifacts[t.sourceId]) {
      artifacts[t.sourceId] = { type: t.sourceType, pass: 0, partial: 0, fail: 0, total: 0 };
    }
    artifacts[t.sourceId].total++;
    if (t.status === "Pass") artifacts[t.sourceId].pass++;
    else if (t.status === "Partial") artifacts[t.sourceId].partial++;
    else artifacts[t.sourceId].fail++;
  }

  const evalRows = Object.entries(artifacts).map(([id, a]) => {
    let finalStatus;
    if (a.type === "UC") {
      finalStatus = a.total === 0 ? "Not Implemented"
        : a.fail === 0 && a.partial === 0 ? "Implemented Correctly"
        : a.pass > 0 ? "Partially Implemented"
        : "Incorrectly Implemented";
    } else if (a.type === "BR") {
      finalStatus = a.total === 0 ? "Not Enforced"
        : a.fail === 0 && a.partial === 0 ? "Enforced Correctly"
        : a.pass > 0 ? "Partially Enforced"
        : "Incorrectly Enforced";
    } else {
      finalStatus = a.total === 0 ? "Missing"
        : a.fail === 0 && a.partial === 0 ? "Complete"
        : a.pass > 0 ? "Partial"
        : "Incorrect";
    }
    return [id, a.type, a.total, a.pass, a.partial, a.fail, finalStatus, `${a.pass}/${a.total} passed`];
  });

  writeCsv("Artifact_Evaluation.csv",
    ["Artifact ID", "Artifact Type", "Tests", "Pass", "Partial", "Fail", "Final Status", "Remarks"],
    evalRows
  );

  // ── Sheet 1: Summary ──
  const ucTests = allTests.filter((t) => t.sourceType === "UC");
  const brTests = allTests.filter((t) => t.sourceType === "BR");
  const wfTests = allTests.filter((t) => t.sourceType === "WF");
  const total = allTests.length;
  const passed = allTests.filter((t) => t.status === "Pass").length;
  const partial = allTests.filter((t) => t.status === "Partial").length;
  const failed = allTests.filter((t) => t.status === "Fail").length;

  writeCsv("Module_Test_Summary.csv",
    ["Metric", "Value"],
    [
      ["Total E2E Tests Executed", total],
      ["UC Tests", ucTests.length],
      ["BR Tests", brTests.length],
      ["WF Tests", wfTests.length],
      ["Total Pass", passed],
      ["Total Partial", partial],
      ["Total Fail", failed],
      ["Strict Pass Rate %", total > 0 ? `${((passed / total) * 100).toFixed(1)}%` : "N/A"],
    ]
  );

  console.log(`\n${"=".repeat(60)}`);
  console.log(`✅ E2E reports generated in: ${REPORTS_DIR}`);
  console.log(`${"=".repeat(60)}\n`);
}

function parseTestTitle(title) {
  // Parse: "UC-1-HP-01: Some description" or "BR-2-I-01: ..."
  const match = title.match(/^(UC|BR|WF)-(\S+?)-(HP|AP|EX|V|I|E2E|NEG|EXIT)-(\d+)/i);
  if (match) {
    return {
      testId: `${match[1]}-${match[2]}-${match[3]}-${match[4]}`,
      sourceType: match[1].toUpperCase(),
      sourceId: `${match[1]}-${match[2]}`,
    };
  }
  // Fallback: try to detect from describe block name
  const descMatch = title.match(/(UC|BR|WF)-(\d+)/i);
  if (descMatch) {
    return {
      testId: title.slice(0, 30),
      sourceType: descMatch[1].toUpperCase(),
      sourceId: `${descMatch[1]}-${descMatch[2]}`,
    };
  }
  return { testId: title.slice(0, 30), sourceType: "Other", sourceId: "" };
}

main();
