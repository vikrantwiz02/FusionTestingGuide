"""
test_workflows.py — Specification-Driven Workflow Test Executor
================================================================

HOW IT WORKS:
  1. Reads specs/workflows.yaml
  2. Each WF gets at minimum: 1 End-to-End test + 1 Negative/Exit test
  3. Workflow tests chain multiple API calls to simulate real user flows
  4. Results are collected and written to CSV reports

KEY DIFFERENCE FROM UC/BR TESTS:
  Workflow tests are MULTI-STEP. Each step depends on the previous one.
  A workflow test chains: action1 → verify1 → action2 → verify2 → ... → final state

NAMING CONVENTION:
  class TestWF01_<WorkflowName>(WFTestBase):
      def test_e2e_<description>(self):      # End-to-End happy path
      def test_negative_<description>(self):  # Negative/failure path
      def test_exit_<description>(self):      # Alternate exit test
"""

from .conftest import BaseModuleTestCase, load_spec


class WFTestBase(BaseModuleTestCase):
    """
    Base class for Workflow tests.

    EVERY test method MUST set these attributes:
        self._test_id            = "WF-TEST-001"
        self._wf_id              = "WF-1"
        self._test_category      = "End-to-End" | "Negative" | "Exit"
        self._scenario           = "description of flow"
        self._expected_final_state = "what the system state should be at end"
        self._actual_result       = ""
        self._status              = ""
        self._evidence            = ""

    Workflow tests should use self._steps to record intermediate steps:
        self._steps = []
        self._steps.append({"step": 1, "action": "...", "result": "...", "ok": True})
    """

    def setUp(self):
        super().setUp()
        self._steps = []

    def _add_step(self, step_num, action, expected, actual, passed):
        """Record an intermediate workflow step."""
        self._steps.append({
            "step": step_num,
            "action": action,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        })

    def _record_result(self, actual_result, status, evidence=""):
        """Call this at the end of each test to record final results."""
        self._actual_result = actual_result
        self._status = status
        self._evidence = evidence
        # Build evidence from steps if not provided
        if not evidence and self._steps:
            step_lines = []
            for s in self._steps:
                icon = "✅" if s["passed"] else "❌"
                step_lines.append(f"  Step {s['step']}: {icon} {s['action']} → {s['actual']}")
            self._evidence = "\n".join(step_lines)

    def _all_steps_passed(self):
        """Check if all recorded steps passed."""
        return all(s["passed"] for s in self._steps)


def generate_wf_tests():
    """
    Reads specs/workflows.yaml and generates test case documentation.
    Returns list of test case dicts for CSV report generation (Sheet 4).
    """
    try:
        spec = load_spec("workflows.yaml")
    except FileNotFoundError:
        return []

    if not spec or "workflows" not in spec:
        return []

    test_cases = []
    for wf in spec["workflows"]:
        wf_id = wf["id"]

        # End-to-End tests
        for i, e2e in enumerate(wf.get("e2e_tests", []), 1):
            test_cases.append({
                "test_id": f"{wf_id}-E2E-{i:02d}",
                "wf_id": wf_id,
                "category": "End-to-End",
                "scenario": e2e.get("scenario", ""),
                "expected_final_state": e2e.get("expected_final_state", ""),
            })

        # Negative tests
        for i, neg in enumerate(wf.get("negative_tests", []), 1):
            test_cases.append({
                "test_id": f"{wf_id}-NEG-{i:02d}",
                "wf_id": wf_id,
                "category": "Negative",
                "scenario": neg.get("scenario", ""),
                "expected_final_state": neg.get("expected_final_state", ""),
            })

        # Exit tests
        for i, ext in enumerate(wf.get("exit_tests", []), 1):
            test_cases.append({
                "test_id": f"{wf_id}-EXIT-{i:02d}",
                "wf_id": wf_id,
                "category": "Exit",
                "scenario": ext.get("scenario", ""),
                "expected_final_state": ext.get("expected_final_state", ""),
            })

    return test_cases


# ====================================================================
# CONCRETE WORKFLOW TESTS — Teams write their tests below
# ====================================================================
#
# EXAMPLE (teams replace with their own):
# ====================================================================

class TestWF_EXAMPLE(WFTestBase):
    """
    EXAMPLE — Replace with your actual Workflow tests.

    WF-EXAMPLE: Student Registration → Payment → Use Mess → Deregistration

    DELETE this class and write your own.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_e2e_complete_lifecycle(self):
        """End-to-End: Full student mess lifecycle"""
        self._test_id = "WF-EXAMPLE-E2E-01"
        self._wf_id = "WF-EXAMPLE"
        self._test_category = "End-to-End"
        self._scenario = "Student registers, uses mess for a month, then deregisters"
        self._expected_final_state = "Student is deregistered, all bills settled"

        # ── STEP 1: Student submits registration ──
        self.login_as_student()
        # response = self.api_post('/your/api/register', {...})
        self._add_step(1, "Submit registration request",
                       "Request created with status=pending",
                       "Request created successfully", True)

        # ── STEP 2: Manager approves registration ──
        self.login_as_staff()
        # response = self.api_put('/your/api/register', {...})
        self._add_step(2, "Manager approves registration",
                       "Status changed to Registered",
                       "Status updated correctly", True)

        # ── STEP 3: Student deregisters ──
        self.login_as_student()
        # response = self.api_post('/your/api/deregister', {...})
        self._add_step(3, "Submit deregistration request",
                       "Deregistration request created",
                       "Request created", True)

        # ── FINAL VERIFICATION ──
        if self._all_steps_passed():
            self._record_result(
                actual_result="Full lifecycle completed",
                status="Pass"
            )
        else:
            self._record_result(
                actual_result="Lifecycle incomplete",
                status="Fail"
            )

    def test_negative_registration_without_payment(self):
        """Negative: Registration fails without valid payment"""
        self._test_id = "WF-EXAMPLE-NEG-01"
        self._wf_id = "WF-EXAMPLE"
        self._test_category = "Negative"
        self._scenario = "Student tries to register without uploading payment proof"
        self._expected_final_state = "Registration rejected, student remains unregistered"

        # ── ACTUAL TEST LOGIC ──
        self.login_as_student()
        # response = self.api_post('/your/api/register', {no payment data})
        self._add_step(1, "Submit registration without payment",
                       "Request rejected with error",
                       "Error returned as expected", True)

        self._record_result(
            actual_result="Registration correctly rejected",
            status="Pass"
        )
