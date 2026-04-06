"""
runner.py — Custom Test Runner + Automated Report Generator
=============================================================

THIS IS THE CORE OF THE FRAMEWORK.

When tests are run with:
    python manage.py test applications.<module>.tests -v 2

This runner:
  1. Runs all tests normally (Django's test infrastructure)
  2. Collects results from every test method
  3. Reads YAML spec files for test design documentation
  4. Generates ALL 7 CSV report sheets automatically

Output files (in tests/reports/):
  - Module_Test_Summary.csv     (Sheet 1)
  - UC_Test_Design.csv          (Sheet 2)
  - BR_Test_Design.csv          (Sheet 3)
  - WF_Test_Design.csv          (Sheet 4)
  - Test_Execution_Log.csv      (Sheet 5)
  - Defect_Log.csv              (Sheet 6)
  - Artifact_Evaluation.csv     (Sheet 7)
"""

import csv
import os
import sys
import traceback
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from django.test.runner import DiscoverRunner
from django.test import TestResult


class ReportCollectingResult(TestResult):
    """
    Extended TestResult that captures metadata from test methods
    for report generation.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_records = []  # All test execution records
        self.defects = []       # Failed/partial test records

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record_test(test, "Pass")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record_test(test, "Fail", err)

    def addError(self, test, err):
        super().addError(test, err)
        self._record_test(test, "Fail", err)

    def _record_test(self, test, status, err=None):
        """Extract metadata from test method and record it."""
        record = {
            "test_id": getattr(test, "_test_id", test.id().split(".")[-1]),
            "source_type": self._detect_source_type(test),
            "source_id": getattr(test, "_uc_id", "") or
                         getattr(test, "_br_id", "") or
                         getattr(test, "_wf_id", ""),
            "test_category": getattr(test, "_test_category", ""),
            "scenario": getattr(test, "_scenario", test.shortDescription() or ""),
            "preconditions": getattr(test, "_preconditions", ""),
            "input_action": getattr(test, "_input_action", ""),
            "expected_result": getattr(test, "_expected_result", ""),
            "actual_result": getattr(test, "_actual_result",
                                     self._format_error(err) if err else "Test passed"),
            "status": getattr(test, "_status", status),
            "evidence": getattr(test, "_evidence", ""),
            "tester": os.environ.get("TESTER_NAME", "Automated"),
            "test_class": test.__class__.__name__,
            "test_method": test._testMethodName,
        }

        # Override status from test attribute if it was set
        if hasattr(test, "_status") and test._status:
            record["status"] = test._status
        else:
            record["status"] = status

        self.test_records.append(record)

        # Record defects
        if record["status"] in ("Fail", "Partial"):
            error_desc = self._format_error(err) if err else record["actual_result"]
            self.defects.append({
                "defect_id": f"DEF-{len(self.defects) + 1:03d}",
                "related_test_id": record["test_id"],
                "related_artifact": record["source_id"],
                "severity": "High" if record["status"] == "Fail" else "Medium",
                "description": error_desc[:500],
                "suggested_fix": "Investigate and fix the failing condition",
            })

    def _detect_source_type(self, test):
        """Detect if this is a UC, BR, or WF test from the class hierarchy."""
        class_name = test.__class__.__name__
        module_name = test.__class__.__module__
        if "use_case" in module_name or "UC" in class_name:
            return "UC"
        elif "business_rule" in module_name or "BR" in class_name:
            return "BR"
        elif "workflow" in module_name or "WF" in class_name:
            return "WF"
        return "Other"

    def _format_error(self, err):
        """Format an error tuple into a readable string."""
        if err:
            return "".join(traceback.format_exception(*err))[:500]
        return ""


class ReportingTestRunner(DiscoverRunner):
    """
    Custom Django test runner that:
    1. Runs all tests normally
    2. After completion, generates all 7 CSV report sheets
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_result = None

    def get_resultclass(self):
        return ReportCollectingResult

    def run_suite(self, suite, **kwargs):
        """Override to use our custom result class."""
        result = ReportCollectingResult(
            self.debug_sql, self.failfast, self.buffer
        )
        # If verbosity > 0, also print to console
        if self.verbosity > 0:
            result = unittest_TextTestResult_wrapper(result, self.verbosity)

        suite(result)
        self.report_result = result
        return result

    def suite_result(self, suite, result, *args, **kwargs):
        """After tests complete, generate all reports."""
        # Handle wrapped result
        actual_result = result
        if hasattr(result, '_inner'):
            actual_result = result._inner

        self._generate_reports(actual_result)
        return super().suite_result(suite, result, *args, **kwargs)

    def _generate_reports(self, result):
        """Generate all 7 CSV report sheets."""
        if not hasattr(result, 'test_records'):
            print("\n⚠️  No test records collected. Skipping report generation.")
            return

        # Detect the tests/ directory from any test record
        reports_dir = self._find_reports_dir()
        reports_dir.mkdir(parents=True, exist_ok=True)

        print("\n" + "=" * 60)
        print("📊 GENERATING TEST REPORTS")
        print("=" * 60)

        records = result.test_records
        defect_records = result.defects

        # Load YAML specs for design sheets
        uc_design = self._load_yaml_safe("use_cases.yaml", "use_cases")
        br_design = self._load_yaml_safe("business_rules.yaml", "business_rules")
        wf_design = self._load_yaml_safe("workflows.yaml", "workflows")

        # Generate each sheet
        self._gen_sheet2_uc_design(reports_dir, uc_design)
        self._gen_sheet3_br_design(reports_dir, br_design)
        self._gen_sheet4_wf_design(reports_dir, wf_design)
        self._gen_sheet5_execution_log(reports_dir, records)
        self._gen_sheet6_defect_log(reports_dir, defect_records)
        self._gen_sheet7_artifact_eval(reports_dir, records, uc_design, br_design, wf_design)
        self._gen_sheet1_summary(reports_dir, records, uc_design, br_design, wf_design)

        print("\n" + "=" * 60)
        print(f"✅ All 7 reports generated in: {reports_dir}")
        print("=" * 60 + "\n")

    def _find_reports_dir(self):
        """Find or create the reports directory."""
        # Try to find it relative to test files
        for path in sys.path:
            candidate = Path(path) / "reports"
            if candidate.parent.name == "tests":
                return candidate
        # Fallback: create in current directory
        return Path.cwd() / "test_reports"

    def _load_yaml_safe(self, filename, key):
        """Try to load a YAML spec file, return empty list if not found."""
        try:
            import yaml
            # Search for specs/ directory
            for path in sys.path:
                specs_path = Path(path) / "specs" / filename
                if specs_path.exists():
                    with open(specs_path) as f:
                        data = yaml.safe_load(f)
                        return data.get(key, []) if data else []
            # Also try from CWD
            for specs_path in Path.cwd().rglob(f"specs/{filename}"):
                with open(specs_path) as f:
                    data = yaml.safe_load(f)
                    return data.get(key, []) if data else []
        except Exception:
            pass
        return []

    def _write_csv(self, reports_dir, filename, headers, rows):
        """Write CSV file."""
        filepath = reports_dir / filename
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)
        print(f"  📄 {filename} ({len(rows)} rows)")

    # ── Sheet 1: Module Test Summary ──────────────────────

    def _gen_sheet1_summary(self, reports_dir, records, uc_specs, br_specs, wf_specs):
        num_ucs = len(uc_specs)
        num_brs = len(br_specs)
        num_wfs = len(wf_specs)

        required_uc = 3 * num_ucs
        required_br = 2 * num_brs
        required_wf = 2 * num_wfs

        uc_records = [r for r in records if r["source_type"] == "UC"]
        br_records = [r for r in records if r["source_type"] == "BR"]
        wf_records = [r for r in records if r["source_type"] == "WF"]

        designed_uc = len(uc_records)
        designed_br = len(br_records)
        designed_wf = len(wf_records)

        total_executed = len(records)
        total_pass = sum(1 for r in records if r["status"] == "Pass")
        total_partial = sum(1 for r in records if r["status"] == "Partial")
        total_fail = sum(1 for r in records if r["status"] == "Fail")

        uc_adequacy = f"{(designed_uc / required_uc * 100):.1f}%" if required_uc > 0 else "N/A"
        br_adequacy = f"{(designed_br / required_br * 100):.1f}%" if required_br > 0 else "N/A"
        wf_adequacy = f"{(designed_wf / required_wf * 100):.1f}%" if required_wf > 0 else "N/A"
        pass_rate = f"{(total_pass / total_executed * 100):.1f}%" if total_executed > 0 else "N/A"

        rows = [
            ["Total Use Cases", num_ucs],
            ["Total Business Rules", num_brs],
            ["Total Workflows", num_wfs],
            ["Required UC Tests", required_uc],
            ["Designed UC Tests", designed_uc],
            ["Required BR Tests", required_br],
            ["Designed BR Tests", designed_br],
            ["Required WF Tests", required_wf],
            ["Designed WF Tests", designed_wf],
            ["UC Adequacy %", uc_adequacy],
            ["BR Adequacy %", br_adequacy],
            ["WF Adequacy %", wf_adequacy],
            ["Total Tests Executed", total_executed],
            ["Total Pass", total_pass],
            ["Total Partial", total_partial],
            ["Total Fail", total_fail],
            ["Strict Pass Rate %", pass_rate],
        ]
        self._write_csv(reports_dir, "Module_Test_Summary.csv", ["Metric", "Value"], rows)

    # ── Sheet 2: UC Test Design ───────────────────────────

    def _gen_sheet2_uc_design(self, reports_dir, uc_specs):
        headers = ["Test ID", "UC ID", "Test Category", "Scenario",
                    "Preconditions", "Input / Action", "Expected Result"]
        rows = []
        for uc in uc_specs:
            uc_id = uc["id"]
            for i, hp in enumerate(uc.get("happy_paths", []), 1):
                rows.append([f"{uc_id}-HP-{i:02d}", uc_id, "Happy Path",
                            hp.get("scenario", ""), hp.get("preconditions", ""),
                            hp.get("input_action", ""), hp.get("expected_result", "")])
            for i, ap in enumerate(uc.get("alternate_paths", []), 1):
                rows.append([f"{uc_id}-AP-{i:02d}", uc_id, "Alternate Path",
                            ap.get("scenario", ""), ap.get("preconditions", ""),
                            ap.get("input_action", ""), ap.get("expected_result", "")])
            for i, ep in enumerate(uc.get("exception_paths", []), 1):
                rows.append([f"{uc_id}-EX-{i:02d}", uc_id, "Exception",
                            ep.get("scenario", ""), ep.get("preconditions", ""),
                            ep.get("input_action", ""), ep.get("expected_result", "")])
        self._write_csv(reports_dir, "UC_Test_Design.csv", headers, rows)

    # ── Sheet 3: BR Test Design ───────────────────────────

    def _gen_sheet3_br_design(self, reports_dir, br_specs):
        headers = ["Test ID", "BR ID", "Test Category", "Input / Action", "Expected Result"]
        rows = []
        for br in br_specs:
            br_id = br["id"]
            for i, vt in enumerate(br.get("valid_tests", []), 1):
                rows.append([f"{br_id}-V-{i:02d}", br_id, "Valid",
                            vt.get("input_action", ""), vt.get("expected_result", "")])
            for i, it in enumerate(br.get("invalid_tests", []), 1):
                rows.append([f"{br_id}-I-{i:02d}", br_id, "Invalid",
                            it.get("input_action", ""), it.get("expected_result", "")])
        self._write_csv(reports_dir, "BR_Test_Design.csv", headers, rows)

    # ── Sheet 4: WF Test Design ───────────────────────────

    def _gen_sheet4_wf_design(self, reports_dir, wf_specs):
        headers = ["Test ID", "WF ID", "Test Category", "Scenario", "Expected Final State"]
        rows = []
        for wf in wf_specs:
            wf_id = wf["id"]
            for i, e2e in enumerate(wf.get("e2e_tests", []), 1):
                rows.append([f"{wf_id}-E2E-{i:02d}", wf_id, "End-to-End",
                            e2e.get("scenario", ""), e2e.get("expected_final_state", "")])
            for i, neg in enumerate(wf.get("negative_tests", []), 1):
                rows.append([f"{wf_id}-NEG-{i:02d}", wf_id, "Negative",
                            neg.get("scenario", ""), neg.get("expected_final_state", "")])
            for i, ext in enumerate(wf.get("exit_tests", []), 1):
                rows.append([f"{wf_id}-EXIT-{i:02d}", wf_id, "Exit",
                            ext.get("scenario", ""), ext.get("expected_final_state", "")])
        self._write_csv(reports_dir, "WF_Test_Design.csv", headers, rows)

    # ── Sheet 5: Test Execution Log ───────────────────────

    def _gen_sheet5_execution_log(self, reports_dir, records):
        headers = ["Test ID", "Source Type", "Source ID", "Expected Result",
                    "Actual Result", "Status", "Evidence", "Tester"]
        rows = []
        for r in records:
            rows.append([
                r["test_id"], r["source_type"], r["source_id"],
                r["expected_result"], r["actual_result"],
                r["status"], r["evidence"], r["tester"]
            ])
        self._write_csv(reports_dir, "Test_Execution_Log.csv", headers, rows)

    # ── Sheet 6: Defect Log ───────────────────────────────

    def _gen_sheet6_defect_log(self, reports_dir, defects):
        headers = ["Defect ID", "Related Test ID", "Related Artifact",
                    "Severity", "Description", "Suggested Fix"]
        rows = []
        for d in defects:
            rows.append([
                d["defect_id"], d["related_test_id"], d["related_artifact"],
                d["severity"], d["description"], d["suggested_fix"]
            ])
        self._write_csv(reports_dir, "Defect_Log.csv", headers, rows)

    # ── Sheet 7: Artifact Evaluation ──────────────────────

    def _gen_sheet7_artifact_eval(self, reports_dir, records, uc_specs, br_specs, wf_specs):
        headers = ["Artifact ID", "Artifact Type", "Tests", "Pass",
                    "Partial", "Fail", "Final Status", "Remarks"]
        rows = []

        # Evaluate UCs
        for uc in uc_specs:
            uc_id = uc["id"]
            uc_tests = [r for r in records if r["source_id"] == uc_id]
            p = sum(1 for t in uc_tests if t["status"] == "Pass")
            pa = sum(1 for t in uc_tests if t["status"] == "Partial")
            f = sum(1 for t in uc_tests if t["status"] == "Fail")
            total = len(uc_tests)

            if total == 0:
                status = "Not Implemented"
            elif f == 0 and pa == 0:
                status = "Implemented Correctly"
            elif p > 0:
                status = "Partially Implemented"
            else:
                status = "Incorrectly Implemented"

            remarks = f"{p}/{total} passed" if total > 0 else "No tests executed"
            rows.append([uc_id, "UC", total, p, pa, f, status, remarks])

        # Evaluate BRs
        for br in br_specs:
            br_id = br["id"]
            br_tests = [r for r in records if r["source_id"] == br_id]
            p = sum(1 for t in br_tests if t["status"] == "Pass")
            pa = sum(1 for t in br_tests if t["status"] == "Partial")
            f = sum(1 for t in br_tests if t["status"] == "Fail")
            total = len(br_tests)

            if total == 0:
                status = "Not Enforced"
            elif f == 0 and pa == 0:
                status = "Enforced Correctly"
            elif p > 0:
                status = "Partially Enforced"
            else:
                status = "Incorrectly Enforced"

            remarks = f"{p}/{total} passed" if total > 0 else "No tests executed"
            rows.append([br_id, "BR", total, p, pa, f, status, remarks])

        # Evaluate WFs
        for wf in wf_specs:
            wf_id = wf["id"]
            wf_tests = [r for r in records if r["source_id"] == wf_id]
            p = sum(1 for t in wf_tests if t["status"] == "Pass")
            pa = sum(1 for t in wf_tests if t["status"] == "Partial")
            f = sum(1 for t in wf_tests if t["status"] == "Fail")
            total = len(wf_tests)

            if total == 0:
                status = "Missing"
            elif f == 0 and pa == 0:
                status = "Complete"
            elif p > 0:
                status = "Partial"
            else:
                status = "Incorrect"

            remarks = f"{p}/{total} passed" if total > 0 else "No tests executed"
            rows.append([wf_id, "WF", total, p, pa, f, status, remarks])

        self._write_csv(reports_dir, "Artifact_Evaluation.csv", headers, rows)


# Helper to maintain console output while collecting results
import unittest

def unittest_TextTestResult_wrapper(collecting_result, verbosity):
    """Wraps our collecting result to also print to console."""

    class WrappedResult(unittest.TextTestResult):
        def __init__(self):
            super().__init__(sys.stderr, True, verbosity)
            self._inner = collecting_result

        def addSuccess(self, test):
            super().addSuccess(test)
            self._inner.addSuccess(test)

        def addFailure(self, test, err):
            super().addFailure(test, err)
            self._inner.addFailure(test, err)

        def addError(self, test, err):
            super().addError(test, err)
            self._inner.addError(test, err)

        def addSkip(self, test, reason):
            super().addSkip(test, reason)

        @property
        def test_records(self):
            return self._inner.test_records

        @property
        def defects(self):
            return self._inner.defects

    return WrappedResult()
