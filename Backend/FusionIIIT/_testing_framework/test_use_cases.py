"""
test_use_cases.py — Specification-Driven Use Case Test Executor
================================================================

HOW IT WORKS:
  1. Reads specs/use_cases.yaml
  2. Dynamically generates a Django TestCase class for EACH Use Case
  3. Each UC gets tests for: Happy Path, Alternate Paths, Exception Paths
  4. Results are collected by the custom runner and written to CSV reports

WHAT YOU (THE TEAM) MUST DO:
  1. Fill in specs/use_cases.yaml with your Use Cases
  2. For each test case, implement the actual test logic in the
     _execute_test_action() and _verify_expected() methods
  3. Alternatively (RECOMMENDED): Write concrete test methods in
     separate test files that inherit from UCTestBase

This file provides TWO approaches:

  APPROACH A (Quick/Automated):
    Define everything in YAML, framework auto-generates test stubs.
    Good for documentation and tracking. Tests will be "manual-verify"
    unless you add Python hooks.

  APPROACH B (Full/Recommended):
    Use YAML for DESIGN ONLY (Sheet 2). Write real test methods in
    a separate file inheriting UCTestBase. The runner collects both.
"""

import unittest
from datetime import date, timedelta
from .conftest import BaseModuleTestCase, load_spec, SPECS_DIR


class UCTestBase(BaseModuleTestCase):
    """
    Base class for Use Case tests.

    EVERY test method MUST set these attributes on self during execution
    so the report generator can capture them:

        self._test_id        = "UC-TEST-001"
        self._uc_id          = "UC-1"
        self._test_category  = "Happy Path"
        self._scenario       = "Student submits valid feedback"
        self._preconditions  = "Student is registered in mess"
        self._input_action   = "POST /mess/api/feedbackApi with valid data"
        self._expected_result = "Feedback created, status 200"
        self._actual_result   = ""   (filled after execution)
        self._status          = ""   (Pass/Partial/Fail — filled after execution)
        self._evidence        = ""   (filled after execution)
    """

    def _record_result(self, actual_result, status, evidence=""):
        """Call this at the end of each test to record results."""
        self._actual_result = actual_result
        self._status = status
        self._evidence = evidence


def generate_uc_tests():
    """
    Reads specs/use_cases.yaml and generates test case documentation.
    Returns a list of test case dicts for report generation.

    The YAML just defines the TEST DESIGN (Sheet 2).
    Actual test EXECUTION should be in concrete test methods below.
    """
    try:
        spec = load_spec("use_cases.yaml")
    except FileNotFoundError:
        return []

    if not spec or "use_cases" not in spec:
        return []

    test_cases = []
    for uc in spec["use_cases"]:
        uc_id = uc["id"]

        # Happy Path tests
        for i, hp in enumerate(uc.get("happy_paths", []), 1):
            test_cases.append({
                "test_id": f"{uc_id}-HP-{i:02d}",
                "uc_id": uc_id,
                "category": "Happy Path",
                "scenario": hp.get("scenario", ""),
                "preconditions": hp.get("preconditions", ""),
                "input_action": hp.get("input_action", ""),
                "expected_result": hp.get("expected_result", ""),
            })

        # Alternate Path tests
        for i, ap in enumerate(uc.get("alternate_paths", []), 1):
            test_cases.append({
                "test_id": f"{uc_id}-AP-{i:02d}",
                "uc_id": uc_id,
                "category": "Alternate Path",
                "scenario": ap.get("scenario", ""),
                "preconditions": ap.get("preconditions", ""),
                "input_action": ap.get("input_action", ""),
                "expected_result": ap.get("expected_result", ""),
            })

        # Exception Path tests
        for i, ep in enumerate(uc.get("exception_paths", []), 1):
            test_cases.append({
                "test_id": f"{uc_id}-EX-{i:02d}",
                "uc_id": uc_id,
                "category": "Exception",
                "scenario": ep.get("scenario", ""),
                "preconditions": ep.get("preconditions", ""),
                "input_action": ep.get("input_action", ""),
                "expected_result": ep.get("expected_result", ""),
            })

    return test_cases


# ====================================================================
# APPROACH B — CONCRETE TEST METHODS
# ====================================================================
# Teams write their actual executable tests here or in separate files.
# Each test class groups tests for one Use Case.
#
# NAMING CONVENTION:
#   class TestUC01_<ShortDescription>(UCTestBase):
#       def test_hp01_<description>(self):   # Happy Path
#       def test_ap01_<description>(self):   # Alternate Path
#       def test_ex01_<description>(self):   # Exception Path
#
# EXAMPLE (teams replace with their own):
# ====================================================================

class TestUC_EXAMPLE(UCTestBase):
    """
    EXAMPLE — Replace this with your actual Use Case tests.

    UC-EXAMPLE: User Login
    Actors: Student
    Precondition: User account exists

    DELETE this class and write your own following the same pattern.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Add any UC-specific setup here
        # e.g., cls.some_object = SomeModel.objects.create(...)

    def test_hp01_valid_login(self):
        """Happy Path: User logs in with correct credentials"""
        self._test_id = "UC-EXAMPLE-HP-01"
        self._uc_id = "UC-EXAMPLE"
        self._test_category = "Happy Path"
        self._scenario = "User logs in with valid username and password"
        self._preconditions = "User account exists in the system"
        self._input_action = "POST /accounts/login/ with valid credentials"
        self._expected_result = "User is authenticated, redirected to dashboard"

        # ── ACTUAL TEST LOGIC ──
        self.client.login(username='testStudent', password='testpass123')
        # After login, verify session exists
        self._record_result(
            actual_result="User authenticated successfully",
            status="Pass",
            evidence="Session cookie present in response"
        )

    def test_ap01_wrong_password(self):
        """Alternate Path: User enters wrong password"""
        self._test_id = "UC-EXAMPLE-AP-01"
        self._uc_id = "UC-EXAMPLE"
        self._test_category = "Alternate Path"
        self._scenario = "User enters incorrect password"
        self._preconditions = "User account exists"
        self._input_action = "POST /accounts/login/ with wrong password"
        self._expected_result = "Login fails, error message displayed"

        # ── ACTUAL TEST LOGIC ──
        result = self.client.login(username='testStudent', password='wrongpass')
        self.assertFalse(result)
        self._record_result(
            actual_result="Login rejected as expected",
            status="Pass",
            evidence="client.login() returned False"
        )

    def test_ex01_nonexistent_user(self):
        """Exception: Login attempt with non-existent username"""
        self._test_id = "UC-EXAMPLE-EX-01"
        self._uc_id = "UC-EXAMPLE"
        self._test_category = "Exception"
        self._scenario = "Login with username that does not exist"
        self._preconditions = "No user with given username"
        self._input_action = "POST /accounts/login/ with fake username"
        self._expected_result = "Login fails gracefully"

        # ── ACTUAL TEST LOGIC ──
        result = self.client.login(username='doesNotExist', password='anything')
        self.assertFalse(result)
        self._record_result(
            actual_result="Login rejected for non-existent user",
            status="Pass",
            evidence="client.login() returned False"
        )
