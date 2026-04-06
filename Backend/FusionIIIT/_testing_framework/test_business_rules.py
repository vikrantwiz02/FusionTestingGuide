"""
test_business_rules.py — Specification-Driven Business Rule Test Executor
==========================================================================

HOW IT WORKS:
  1. Reads specs/business_rules.yaml
  2. Each BR gets at minimum: 1 Valid test + 1 Invalid test
  3. Results are collected and written to CSV reports

NAMING CONVENTION:
  class TestBR01_<ShortDescription>(BRTestBase):
      def test_valid_<description>(self):     # Valid input accepted
      def test_invalid_<description>(self):   # Invalid input rejected
"""

from .conftest import BaseModuleTestCase, load_spec


class BRTestBase(BaseModuleTestCase):
    """
    Base class for Business Rule tests.

    EVERY test method MUST set these attributes:
        self._test_id        = "BR-TEST-001"
        self._br_id          = "BR-1"
        self._test_category  = "Valid" or "Invalid"
        self._input_action   = "what was done"
        self._expected_result = "what should happen"
        self._actual_result   = ""
        self._status          = ""
        self._evidence        = ""
    """

    def _record_result(self, actual_result, status, evidence=""):
        """Call this at the end of each test to record results."""
        self._actual_result = actual_result
        self._status = status
        self._evidence = evidence


def generate_br_tests():
    """
    Reads specs/business_rules.yaml and generates test case documentation.
    Returns list of test case dicts for CSV report generation (Sheet 3).
    """
    try:
        spec = load_spec("business_rules.yaml")
    except FileNotFoundError:
        return []

    if not spec or "business_rules" not in spec:
        return []

    test_cases = []
    for br in spec["business_rules"]:
        br_id = br["id"]

        # Valid tests
        for i, vt in enumerate(br.get("valid_tests", []), 1):
            test_cases.append({
                "test_id": f"{br_id}-V-{i:02d}",
                "br_id": br_id,
                "category": "Valid",
                "input_action": vt.get("input_action", ""),
                "expected_result": vt.get("expected_result", ""),
            })

        # Invalid tests
        for i, it in enumerate(br.get("invalid_tests", []), 1):
            test_cases.append({
                "test_id": f"{br_id}-I-{i:02d}",
                "br_id": br_id,
                "category": "Invalid",
                "input_action": it.get("input_action", ""),
                "expected_result": it.get("expected_result", ""),
            })

    return test_cases


# ====================================================================
# CONCRETE TEST METHODS — Teams write their tests below
# ====================================================================
#
# NAMING CONVENTION:
#   class TestBR01_<Rule>(BRTestBase):
#       def test_valid_<case>(self):
#       def test_invalid_<case>(self):
#
# EXAMPLE (teams replace with their own):
# ====================================================================

class TestBR_EXAMPLE(BRTestBase):
    """
    EXAMPLE — Replace with your actual Business Rule tests.

    BR-EXAMPLE: Only authenticated users can access module pages
    Constraint: All endpoints require login

    DELETE this class and write your own.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_valid_authenticated_user_can_access(self):
        """Valid: Logged-in user can access protected endpoint"""
        self._test_id = "BR-EXAMPLE-V-01"
        self._br_id = "BR-EXAMPLE"
        self._test_category = "Valid"
        self._input_action = "GET /mess/ as authenticated user"
        self._expected_result = "200 OK, page content returned"

        # ── ACTUAL TEST LOGIC ──
        self.login_as_student()
        # Replace URL with your module's actual endpoint
        # response = self.api_get('/your/module/endpoint/')
        self._record_result(
            actual_result="Authenticated access granted",
            status="Pass",
            evidence="Response status 200"
        )

    def test_invalid_unauthenticated_user_blocked(self):
        """Invalid: Anonymous user cannot access protected endpoint"""
        self._test_id = "BR-EXAMPLE-I-01"
        self._br_id = "BR-EXAMPLE"
        self._test_category = "Invalid"
        self._input_action = "GET /mess/ without authentication"
        self._expected_result = "Redirected to login or 401/403"

        # ── ACTUAL TEST LOGIC ──
        self.logout()
        # response = self.api_get('/your/module/endpoint/', expected_status=None)
        # self.assertIn(response.status_code, [401, 403, 302])
        self._record_result(
            actual_result="Unauthenticated access blocked",
            status="Pass",
            evidence="Response status 401/403/302"
        )
