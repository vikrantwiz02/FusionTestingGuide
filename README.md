# Fusion Module Backend Testing Guide — Instructions for All Pairs for both G1 and G2

> **Approach:** Specification-driven, black-box testing  
> **Backend:** `python manage.py test applications.<module>.tests -v 2`  

---

## Table of Contents

1. [Overview — What This Is](#1-overview)
2. [Quick Start — 5 Minutes to First Test](#2-quick-start)
3. [Backend Framework Architecture](#3-backend-framework-architecture)
4. [Step 1 — Setup](#4-step-1-setup)
5. [Step 2 — Write YAML Specs](#5-step-2-write-yaml-specs)
6. [Step 3 — Write Test Code](#6-step-3-write-test-code)
7. [Step 4 — Run Tests](#7-step-4-run-tests)
8. [Step 5 — Collect Reports](#8-step-5-collect-reports)
9. [Test Adequacy Rules](#9-test-adequacy-rules)
10. [Evaluation Logic](#10-evaluation-logic)
11. [Complete Worked Example](#11-complete-worked-example)
12. [Common Patterns & Recipes](#12-common-patterns)
13. [FAQ](#13-faq)

---

## 1. Overview

### What You're Doing

You are performing **systematic, specification-based testing** of your Fusion module. You are testing against three specification sources:

| Source | What It Tests | Min Tests Per Item |
|--------|--------------|-------------------|
| **Use Cases (UC)** | Functional features work as intended | 3 (1 happy + 1 alternate + 1 exception) |
| **Business Rules (BR)** | Constraints, validations, permissions enforced | 2 (1 valid + 1 invalid) |
| **Workflows (WF)** | End-to-end flows and state transitions | 2 (1 e2e + 1 negative) |

### What You're NOT Doing

- ❌ Not reading source code to write tests
- ❌ Not doing random/exploratory testing
- ❌ Not testing implementation details
- ✅ You're testing **behavior** against **specifications**

### What Gets Generated Automatically

Running one command generates all 7 required deliverable sheets as CSV files:

| Sheet | File | Contents |
|-------|------|----------|
| Sheet 1 | `Module_Test_Summary.csv` | Counts, adequacy %, pass rates |
| Sheet 2 | `UC_Test_Design.csv` | All UC test case designs |
| Sheet 3 | `BR_Test_Design.csv` | All BR test case designs |
| Sheet 4 | `WF_Test_Design.csv` | All WF test case designs |
| Sheet 5 | `Test_Execution_Log.csv` | Execution results with evidence |
| Sheet 6 | `Defect_Log.csv` | All failed/partial test records |
| Sheet 7 | `Artifact_Evaluation.csv` | Per-artifact status evaluation |

---

## 2. Quick Start

```bash
# From FusionIIIT/ directory

# 1. Install dependencies
pip install pyyaml

# 2. Setup framework for your module (one-time)
python setup_tests.py <your_module_name>
# Example: python setup_tests.py central_mess

# 3. Edit your spec files (in applications/<module>/tests/specs/)
#    - use_cases.yaml
#    - business_rules.yaml
#    - workflows.yaml

# 4. Write your test code (in applications/<module>/tests/)
#    - test_use_cases.py
#    - test_business_rules.py
#    - test_workflows.py

# 5. Run everything + generate reports (SINGLE COMMAND)
python manage.py test applications.<module>.tests -v 2 \
  --testrunner=applications.<module>.tests.runner.ReportingTestRunner

# 6. Collect CSV reports from applications/<module>/tests/reports/
```

---

## 3. Backend Framework Architecture

```
applications/<your_module>/
└── tests/                          ← Created by setup_tests.py
    ├── __init__.py                 ← Package marker
    ├── conftest.py                 ← Base setup (users, API client, helpers)
    ├── specs/                      ← YOUR specification YAML files
    │   ├── use_cases.yaml          ← UC definitions + test designs
    │   ├── business_rules.yaml     ← BR definitions + test designs
    │   └── workflows.yaml          ← WF definitions + test designs
    ├── test_use_cases.py           ← YOUR UC test implementations
    ├── test_business_rules.py      ← YOUR BR test implementations
    ├── test_workflows.py           ← YOUR WF test implementations
    ├── runner.py                   ← Report generator (DON'T EDIT)
    └── reports/                    ← Auto-generated output
        ├── Module_Test_Summary.csv
        ├── UC_Test_Design.csv
        ├── BR_Test_Design.csv
        ├── WF_Test_Design.csv
        ├── Test_Execution_Log.csv
        ├── Defect_Log.csv
        └── Artifact_Evaluation.csv
```

**Files you EDIT:** `conftest.py`, `specs/*.yaml`, `test_*.py`  
**Files you DON'T EDIT:** `runner.py`, `__init__.py`

---

## 4. Step 1 — Setup

### 4.1 Install Dependencies

```bash
pip install pyyaml
```

### 4.2 Run Setup Script

```bash
cd FusionIIIT/
python setup_tests.py <your_module_name>
```

This copies the framework scaffold into your module's `tests/` directory.

### 4.3 Customize Base Setup (`conftest.py`)

Open `applications/<module>/tests/conftest.py` and modify `setUpTestData()` to create the base objects YOUR module needs.

> [!IMPORTANT]
> **Every module's models are different.** You MUST customize `setUpTestData()` to create the model instances your API endpoints require (e.g., Student, Designation, ExtraInfo, etc.)

```python
# Example customization for a module that needs Student objects:

from applications.globals.models import ExtraInfo, HoldsDesignation, Designation
from applications.academic_information.models import Student

class BaseModuleTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.student_user = User.objects.create_user(
            username='2021BCS001', password='test123'
        )
        cls.staff_user = User.objects.create_user(
            username='staffuser', password='test123'
        )

        # Create ExtraInfo (required by Fusion)
        cls.student_extra = ExtraInfo.objects.create(
            user=cls.student_user,
            id='2021BCS001',
            user_type='student'
        )
        cls.staff_extra = ExtraInfo.objects.create(
            user=cls.staff_user,
            id='staffuser',
            user_type='staff'
        )

        # Create Student
        cls.student = Student.objects.create(
            id=cls.student_extra,
            programme='B.Tech',
            batch=2021
        )

        # Create Designations (if your module has role-based access)
        # cls.designation = Designation.objects.create(name='mess_manager')
        # HoldsDesignation.objects.create(
        #     user=cls.staff_user,
        #     working=cls.staff_user,
        #     designation=cls.designation
        # )
```

---

## 5. Step 2 — Write YAML Specs

### 5.1 Use Cases (`specs/use_cases.yaml`)

For each UC from your specification document, add:

```yaml
use_cases:
  - id: "UC-1"
    title: "Apply for Rebate"
    description: "Student applies for mess leave/rebate"
    actors: "Student"
    preconditions: "Student is registered in mess"

    happy_paths:
      - scenario: "Student applies for 4-day casual leave with valid dates"
        preconditions: "Student is logged in and registered"
        input_action: "POST /mess/leave with start_date=future, end_date=future+3, leave_type=casual"
        expected_result: "Rebate created with status=pending"

    alternate_paths:
      - scenario: "Student applies for vacation leave instead of casual"
        preconditions: "Student is logged in"
        input_action: "POST /mess/leave with leave_type=vacation, 10 days"
        expected_result: "Vacation leave request created"

    exception_paths:
      - scenario: "Student applies with past start date"
        preconditions: "Student is logged in"
        input_action: "POST /mess/leave with start_date=yesterday"
        expected_result: "Request rejected with date error"
```

### 5.2 Business Rules (`specs/business_rules.yaml`)

```yaml
business_rules:
  - id: "BR-1"
    title: "Casual leave 3-5 day constraint"
    description: "Casual leave must be between 3 and 5 days"

    valid_tests:
      - input_action: "Apply casual leave for 3 days"
        expected_result: "Request accepted"

    invalid_tests:
      - input_action: "Apply casual leave for 1 day"
        expected_result: "Request rejected with constraint error"
```

### 5.3 Workflows (`specs/workflows.yaml`)

```yaml
workflows:
  - id: "WF-1"
    title: "Leave Request Workflow"
    description: "Student applies → Manager reviews → Accept/Reject"

    e2e_tests:
      - scenario: "Student applies, manager accepts, rebate count updated"
        expected_final_state: "Leave status=accepted, monthly bill rebate_count incremented"

    negative_tests:
      - scenario: "Student applies, manager rejects"
        expected_final_state: "Leave status=rejected, no bill changes"
```

---

## 6. Step 3 — Write Test Code

### 6.1 Use Case Tests (`test_use_cases.py`)

Delete the `TestUC_EXAMPLE` class and add your own. **Naming is critical:**

```python
from .conftest import BaseModuleTestCase
from .test_use_cases import UCTestBase

class TestUC01_ApplyRebate(UCTestBase):
    """UC-1: Student applies for mess rebate"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create module-specific objects needed for this UC

    def test_hp01_valid_casual_leave(self):
        """Happy Path: 4-day casual leave with valid future dates"""
        # ── METADATA (required for reports) ──
        self._test_id = "UC-1-HP-01"
        self._uc_id = "UC-1"
        self._test_category = "Happy Path"
        self._scenario = "Student applies for 4-day casual leave"
        self._preconditions = "Student registered in mess"
        self._input_action = "POST /mess/leave with valid dates"
        self._expected_result = "Rebate created, status=1"

        # ── ACTUAL TEST LOGIC ──
        self.login_as_student()
        response = self.api_post('/mess/leave', {
            'leave_type': 'casual',
            'start_date': self.future_date(5),
            'end_date': self.future_date(8),
            'purpose': 'Family event',
        }, expected_status=None)

        # Check response
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 1:
                self._record_result("Rebate created", "Pass",
                                    f"Response: {data}")
            else:
                self._record_result(f"Unexpected status: {data}",
                                    "Fail", f"Response: {data}")
                self.fail(f"Expected status=1, got {data}")
        else:
            self._record_result(f"HTTP {response.status_code}",
                                "Fail", f"Status: {response.status_code}")
            self.fail(f"Expected 200, got {response.status_code}")

    def test_ap01_vacation_leave(self):
        """Alternate Path: Vacation leave instead of casual"""
        self._test_id = "UC-1-AP-01"
        self._uc_id = "UC-1"
        self._test_category = "Alternate Path"
        self._scenario = "Student applies for vacation leave"
        # ... (same pattern)

    def test_ex01_past_dates_rejected(self):
        """Exception: Start date in the past"""
        self._test_id = "UC-1-EX-01"
        self._uc_id = "UC-1"
        self._test_category = "Exception"
        self._scenario = "Student applies with past start date"
        self._preconditions = "Student logged in"
        self._input_action = "POST /mess/leave with start_date=yesterday"
        self._expected_result = "Request rejected"

        self.login_as_student()
        response = self.api_post('/mess/leave', {
            'leave_type': 'casual',
            'start_date': self.past_date(1),
            'end_date': self.future_date(2),
            'purpose': 'Test',
        }, expected_status=None)

        data = response.json()
        if data.get('status') == 3:
            self._record_result("Correctly rejected", "Pass",
                                f"Response: {data}")
        else:
            self._record_result(f"Not rejected: {data}", "Fail",
                                f"Response: {data}")
            self.fail("Past dates should be rejected")
```

### 6.2 Business Rule Tests (`test_business_rules.py`)

```python
from .test_business_rules import BRTestBase

class TestBR01_CasualLeaveDuration(BRTestBase):
    """BR-1: Casual leave must be 3-5 days"""

    def test_valid_3day_leave(self):
        self._test_id = "BR-1-V-01"
        self._br_id = "BR-1"
        self._test_category = "Valid"
        self._input_action = "Apply casual leave for exactly 3 days"
        self._expected_result = "Request accepted"

        self.login_as_student()
        response = self.api_post('/mess/leave', {
            'leave_type': 'casual',
            'start_date': self.future_date(5),
            'end_date': self.future_date(7),  # 3 days
            'purpose': 'Test',
        }, expected_status=None)
        data = response.json()

        if data.get('status') == 1:
            self._record_result("3-day leave accepted", "Pass", str(data))
        else:
            self._record_result(f"Rejected: {data}", "Fail", str(data))
            self.fail("3-day casual leave should be accepted")

    def test_invalid_2day_leave(self):
        self._test_id = "BR-1-I-01"
        self._br_id = "BR-1"
        self._test_category = "Invalid"
        self._input_action = "Apply casual leave for 2 days"
        self._expected_result = "Rejected with constraint error"

        self.login_as_student()
        response = self.api_post('/mess/leave', {
            'leave_type': 'casual',
            'start_date': self.future_date(5),
            'end_date': self.future_date(6),  # 2 days
            'purpose': 'Test',
        }, expected_status=None)
        data = response.json()

        if data.get('status') == 4:
            self._record_result("Correctly rejected", "Pass", str(data))
        else:
            self._record_result(f"Not rejected: {data}", "Fail", str(data))
            self.fail("2-day casual leave should be rejected")
```

### 6.3 Workflow Tests (`test_workflows.py`)

```python
from .test_workflows import WFTestBase

class TestWF01_LeaveRequestFlow(WFTestBase):
    """WF-1: Leave Request → Manager Review → Accept/Reject"""

    def test_e2e_leave_accepted(self):
        self._test_id = "WF-1-E2E-01"
        self._wf_id = "WF-1"
        self._test_category = "End-to-End"
        self._scenario = "Student → Apply → Manager Approves → Rebate counted"
        self._expected_final_state = "Leave accepted, rebate_count updated"

        # Step 1: Student applies
        self.login_as_student()
        resp = self.api_post('/mess/leave', {...}, expected_status=None)
        step1_ok = resp.json().get('status') == 1
        self._add_step(1, "Student applies for leave",
                       "Leave created pending", str(resp.json()), step1_ok)

        # Step 2: Manager approves
        self.login_as_staff()
        leave_id = ...  # Get the leave ID
        resp = self.api_post('/mess/rebateresponse', {
            'id_rebate': leave_id, 'status': '2', 'remark': 'Approved'
        }, expected_status=None)
        step2_ok = True  # Check response
        self._add_step(2, "Manager approves leave",
                       "Status changed to accepted", str(resp.json()), step2_ok)

        # Step 3: Verify DB state
        # from your_module.models import Rebate
        # rebate = Rebate.objects.get(id=leave_id)
        # step3_ok = rebate.status == '2'
        step3_ok = True
        self._add_step(3, "Verify DB state",
                       "Rebate status=2", "Verified", step3_ok)

        if self._all_steps_passed():
            self._record_result("Complete flow worked", "Pass")
        else:
            self._record_result("Flow incomplete", "Fail")
            self.fail("Workflow did not complete successfully")
```

---

## 7. Step 4 — Run Tests

### Single Command — Run + Generate Reports

```bash
# From FusionIIIT/ directory

python manage.py test applications.<module>.tests -v 2 \
  --testrunner=applications.<module>.tests.runner.ReportingTestRunner
```

### Run Without Reports (faster, for debugging)

```bash
python manage.py test applications.<module>.tests -v 2
```

### Run Only Specific Test Types

```bash
# Only UC tests
python manage.py test applications.<module>.tests.test_use_cases -v 2

# Only BR tests
python manage.py test applications.<module>.tests.test_business_rules -v 2

# Only WF tests
python manage.py test applications.<module>.tests.test_workflows -v 2
```

### Run a Single Test Class

```bash
python manage.py test applications.<module>.tests.test_use_cases.TestUC01_ApplyRebate -v 2
```

### Set Tester Name in Reports

```bash
TESTER_NAME="Vikrant" python manage.py test applications.<module>.tests -v 2 \
  --testrunner=applications.<module>.tests.runner.ReportingTestRunner
```

---

## 8. Step 5 — Collect Reports

After running, find all 7 CSV files in:

```
applications/<module>/tests/reports/
```

**Import into Google Sheets / Excel:**
1. Open Google Sheets
2. File → Import → Upload each CSV
3. Each CSV becomes one sheet in your workbook
4. Rename sheets to match required names (Sheet 1 through Sheet 7)

---

## 9. Test Adequacy Rules

### Formula

```
Adequacy % = (Designed Tests / Required Tests) × 100
```

### Requirements

| Spec Source | Min Tests Per Item | Formula |
|------------|-------------------|---------|
| Use Cases | 3 (1 HP + 1 AP + 1 EX) | Required = 3 × NumUCs |
| Business Rules | 2 (1 Valid + 1 Invalid) | Required = 2 × NumBRs |
| Workflows | 2 (1 E2E + 1 Negative) | Required = 2 × NumWFs |

### Target: 100% Adequacy

> [!CAUTION]
> If your module has 5 UCs, 8 BRs, and 3 WFs, you need **minimum** 15 + 16 + 6 = **37 tests**.

---

## 10. Evaluation Logic

### Use Case Final Status

| Condition | Status |
|-----------|--------|
| ALL UC tests pass | **Implemented Correctly** |
| At least one pass, some partial/fail | **Partially Implemented** |
| Major expected behavior wrong | **Incorrectly Implemented** |
| No usable support found | **Not Implemented** |

### Business Rule Final Status

| Condition | Status |
|-----------|--------|
| ALL BR tests pass | **Enforced Correctly** |
| Some enforcement exists | **Partially Enforced** |
| Rule behaves wrongly | **Incorrectly Enforced** |
| No evidence of enforcement | **Not Enforced** |

### Workflow Final Status

| Condition | Status |
|-----------|--------|
| ALL WF tests pass | **Complete** |
| Main path exists but negative/alt fails | **Partial** |
| Transitions substantially wrong | **Incorrect** |
| No meaningful workflow support | **Missing** |

> [!NOTE]
> The `runner.py` applies this logic **automatically** and writes the correct status to `Artifact_Evaluation.csv`.

---

## 11. Complete Worked Example

### Suppose Your Module Has:

- 2 Use Cases (UC-1, UC-2)
- 3 Business Rules (BR-1, BR-2, BR-3)
- 1 Workflow (WF-1)

### Required Tests:

```
UC Tests Required  = 3 × 2 = 6   (2 HP + 2 AP + 2 EX)
BR Tests Required  = 2 × 3 = 6   (3 Valid + 3 Invalid)
WF Tests Required  = 2 × 1 = 2   (1 E2E + 1 Negative)
Total Required     = 14
```

### Your Test Files Should Have:

```python
# test_use_cases.py
class TestUC01_Feature1(UCTestBase):
    def test_hp01_...(self): ...   # UC-1 Happy Path
    def test_ap01_...(self): ...   # UC-1 Alternate Path
    def test_ex01_...(self): ...   # UC-1 Exception

class TestUC02_Feature2(UCTestBase):
    def test_hp01_...(self): ...   # UC-2 Happy Path
    def test_ap01_...(self): ...   # UC-2 Alternate Path
    def test_ex01_...(self): ...   # UC-2 Exception

# test_business_rules.py
class TestBR01_Rule1(BRTestBase):
    def test_valid_...(self): ...  # BR-1 Valid
    def test_invalid_...(self): ...# BR-1 Invalid

class TestBR02_Rule2(BRTestBase):
    def test_valid_...(self): ...
    def test_invalid_...(self): ...

class TestBR03_Rule3(BRTestBase):
    def test_valid_...(self): ...
    def test_invalid_...(self): ...

# test_workflows.py
class TestWF01_Flow1(WFTestBase):
    def test_e2e_...(self): ...    # WF-1 End-to-End
    def test_negative_...(self): ...# WF-1 Negative
```

### Generated `Module_Test_Summary.csv`:

```csv
Metric,Value
Total Use Cases,2
Total Business Rules,3
Total Workflows,1
Required UC Tests,6
Designed UC Tests,6
Required BR Tests,6
Designed BR Tests,6
Required WF Tests,2
Designed WF Tests,2
UC Adequacy %,100.0%
BR Adequacy %,100.0%
WF Adequacy %,100.0%
Total Tests Executed,14
Total Pass,12
Total Partial,0
Total Fail,2
Strict Pass Rate %,85.7%
```

---

## 12. Common Patterns

### Pattern 1: Testing an API Endpoint

```python
def test_hp01_get_all_items(self):
    self.login_as_student()
    response = self.api_get('/your/api/endpoint')
    self.assertIn('payload', response.data)
    self._record_result("Items retrieved", "Pass", str(response.data))
```

### Pattern 2: Testing Create + Verify DB

```python
def test_hp01_create_item(self):
    self.login_as_student()
    response = self.api_post('/your/api/endpoint', {
        'field1': 'value1',
        'field2': 'value2',
    })
    # Verify in database
    from your_module.models import YourModel
    self.assert_object_exists(YourModel, field1='value1')
    self._record_result("Object created in DB", "Pass")
```

### Pattern 3: Testing Permission (BR)

```python
def test_invalid_unauthorized_access(self):
    self.logout()  # No authentication
    response = self.api_get('/your/api/endpoint', expected_status=None)
    self.assertIn(response.status_code, [401, 403, 302])
    self._record_result("Access blocked", "Pass")
```

### Pattern 4: Testing State Transition (WF)

```python
def test_e2e_approval_flow(self):
    # Step 1: Create request as student
    self.login_as_student()
    self.api_post('/api/create', {'data': 'value'})
    self._add_step(1, "Create request", "Pending", "Created", True)

    # Step 2: Approve as staff
    self.login_as_staff()
    self.api_put('/api/approve', {'id': 1, 'status': 'approved'})
    self._add_step(2, "Approve request", "Approved", "Approved", True)

    # Step 3: Verify final state
    from module.models import Request
    obj = Request.objects.get(id=1)
    step3_ok = obj.status == 'approved'
    self._add_step(3, "Verify DB", "status=approved", obj.status, step3_ok)

    self._record_result("Flow complete", "Pass" if self._all_steps_passed() else "Fail")
```

### Pattern 5: Testing with form-data (File Uploads)

```python
def test_hp01_upload_document(self):
    from django.core.files.uploadedfile import SimpleUploadedFile
    self.login_as_student()
    fake_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
    response = self.client.post('/your/api/upload', {
        'document': fake_file,
        'title': 'Test Document',
    }, format='multipart')
    self._record_result("Upload successful", "Pass")
```

---

## 13. FAQ

### Q: My module uses Django template views, not REST APIs. How do I test?

Use Django's test client instead of APIClient:

```python
response = self.client.post('/module/endpoint/', {
    'field1': 'value1'
}, follow=True)  # follow=True follows redirects
self.assertEqual(response.status_code, 200)
```

### Q: Do I need a running database to run tests?

**No.** Django creates a temporary test database automatically. It's destroyed after tests complete. You do NOT need your production PostgreSQL data.

### Q: My module depends on objects from other modules (Student, ExtraInfo). How do I create them?

Create them in `setUpTestData()` in your `conftest.py`. These are test-only objects — they don't affect real data.

### Q: What if my test passes the behavior but the data format is slightly different?

Use **"Partial"** status:

```python
self._record_result("Data returned but format differs", "Partial",
                    f"Expected list, got dict: {response.data}")
```

### Q: Can I add more tests than the minimum?

**Yes!** The minimum (3×UC + 2×BR + 2×WF) ensures **100% adequacy**. More tests improve coverage and earn better evaluations.

### Q: How do I handle tests that need specific dates?

Use the helper methods:

```python
self.future_date(5)   # 5 days from today
self.past_date(3)     # 3 days ago
self.today()          # Today's date string
```

### Q: What if a test discovers a real bug?

The runner **automatically** logs it in `Defect_Log.csv`. The test will appear as "Fail" in the execution log and the defect will include the error traceback.

### Q: I am getting `django.db.utils.ProgrammingError: relation "xyz" does not exist` when I run setup tests!

This happens when the overall FusionIIIT repository has broken test migrations unrelated to your module. 

**Quick Fix:**
1. Try running your test suite by adding `--keepdb` to the end of the testing command.
2. If this is a global error restricting all tests broadly, backend maintainers must fix their base `models.py` logic vs migrations configuration.


---
