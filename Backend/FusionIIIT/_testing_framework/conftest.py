"""
conftest.py — Base Test Setup & Shared Fixtures
=================================================
INSTRUCTIONS FOR ALL TEAMS:
1. Copy this entire _testing_framework/ folder into your module:
      applications/<your_module>/tests/
2. Edit the SETUP section below to create users/objects YOUR module needs.
3. The base class handles: user creation, API client, request factory.
   You add: module-specific model instances in setUpTestData().

This file provides:
  - BaseModuleTestCase: base class for all specification-driven tests
  - Helper methods for API calls, DB checks, login simulation
"""

import os
import json
import yaml
import csv
from pathlib import Path
from datetime import date, timedelta, datetime
from collections import OrderedDict

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# ============================================================
# CONFIGURATION — Each team edits this section
# ============================================================

# Name of your module (used in report headers)
MODULE_NAME = os.environ.get("FUSION_TEST_MODULE", "YourModule")

# Path to this tests/ directory (auto-detected)
TESTS_DIR = Path(__file__).parent
SPECS_DIR = TESTS_DIR / "specs"
REPORTS_DIR = TESTS_DIR / "reports"


def load_spec(filename):
    """Load a YAML spec file from specs/ directory."""
    filepath = SPECS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(
            f"Spec file not found: {filepath}\n"
            f"Create {filename} in {SPECS_DIR}/ following the template."
        )
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def ensure_reports_dir():
    """Create reports/ directory if it doesn't exist."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def write_csv(filename, headers, rows):
    """Write a CSV report file."""
    ensure_reports_dir()
    filepath = REPORTS_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
    print(f"\n  ✅ Report generated: {filepath}")


# ============================================================
# BASE TEST CASE — All test classes inherit from this
# ============================================================

@override_settings(
    # Use an in-memory test database for speed
    # Django's test runner handles this automatically with PostgreSQL
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class BaseModuleTestCase(TestCase):
    """
    Base class providing:
      - Test users with different roles (student, staff, faculty)
      - API client with authentication
      - Request factory for unit-testing views directly
      - Helper methods for common operations

    CUSTOMIZATION:
      Each module team should subclass this and override setUpTestData()
      to create module-specific objects (e.g., Student, Designation, etc.)
    """

    @classmethod
    def setUpTestData(cls):
        """
        Override this in your module to create required base objects.
        Called once for the entire TestCase class (fast).

        Example for mess module:
            cls.student_user = User.objects.create_user(
                username='2021BCS001', password='test123'
            )
            # ... create ExtraInfo, Student, Reg_main, etc.
        """
        # Default test users — override/extend in your module
        cls.student_user = User.objects.create_user(
            username='testStudent', password='testpass123',
            first_name='Test', last_name='Student'
        )
        cls.staff_user = User.objects.create_user(
            username='testStaff', password='testpass123',
            first_name='Test', last_name='Staff'
        )
        cls.faculty_user = User.objects.create_user(
            username='testFaculty', password='testpass123',
            first_name='Test', last_name='Faculty'
        )

    def setUp(self):
        """Called before each individual test method."""
        self.client = APIClient()
        self.factory = RequestFactory()

    # ── Auth Helpers ──────────────────────────────────────

    def login_as_student(self):
        """Authenticate API client as the test student user."""
        self.client.force_authenticate(user=self.student_user)

    def login_as_staff(self):
        """Authenticate API client as the test staff user."""
        self.client.force_authenticate(user=self.staff_user)

    def login_as_faculty(self):
        """Authenticate API client as the test faculty user."""
        self.client.force_authenticate(user=self.faculty_user)

    def login_as(self, user):
        """Authenticate API client as a specific user."""
        self.client.force_authenticate(user=user)

    def logout(self):
        """Remove authentication from API client."""
        self.client.force_authenticate(user=None)

    # ── API Helpers ───────────────────────────────────────

    def api_get(self, url, expected_status=200, **kwargs):
        """Make a GET request and optionally assert status code."""
        response = self.client.get(url, **kwargs)
        if expected_status:
            self.assertEqual(
                response.status_code, expected_status,
                f"GET {url} returned {response.status_code}, expected {expected_status}\n"
                f"Response: {getattr(response, 'data', response.content[:500])}"
            )
        return response

    def api_post(self, url, data=None, expected_status=200, **kwargs):
        """Make a POST request and optionally assert status code."""
        response = self.client.post(url, data=data or {}, format='json', **kwargs)
        if expected_status:
            self.assertEqual(
                response.status_code, expected_status,
                f"POST {url} returned {response.status_code}, expected {expected_status}\n"
                f"Response: {getattr(response, 'data', response.content[:500])}"
            )
        return response

    def api_put(self, url, data=None, expected_status=200, **kwargs):
        """Make a PUT request and optionally assert status code."""
        response = self.client.put(url, data=data or {}, format='json', **kwargs)
        if expected_status:
            self.assertEqual(
                response.status_code, expected_status,
                f"PUT {url} returned {response.status_code}, expected {expected_status}\n"
                f"Response: {getattr(response, 'data', response.content[:500])}"
            )
        return response

    def api_delete(self, url, expected_status=200, **kwargs):
        """Make a DELETE request and optionally assert status code."""
        response = self.client.delete(url, **kwargs)
        if expected_status:
            self.assertEqual(
                response.status_code, expected_status,
                f"DELETE {url} returned {response.status_code}, expected {expected_status}\n"
                f"Response: {getattr(response, 'data', response.content[:500])}"
            )
        return response

    # ── DB Verification Helpers ───────────────────────────

    def assert_object_exists(self, model_class, **filters):
        """Assert that a database object matching filters exists."""
        exists = model_class.objects.filter(**filters).exists()
        self.assertTrue(
            exists,
            f"Expected {model_class.__name__} with {filters} to exist, but it doesn't."
        )

    def assert_object_not_exists(self, model_class, **filters):
        """Assert that no database object matching filters exists."""
        exists = model_class.objects.filter(**filters).exists()
        self.assertFalse(
            exists,
            f"Expected {model_class.__name__} with {filters} to NOT exist, but it does."
        )

    def assert_object_field(self, model_class, filters, field, expected_value):
        """Assert that a specific field on a DB object has an expected value."""
        obj = model_class.objects.get(**filters)
        actual = getattr(obj, field)
        self.assertEqual(
            actual, expected_value,
            f"{model_class.__name__}.{field} = {actual}, expected {expected_value}"
        )

    def assert_object_count(self, model_class, expected_count, **filters):
        """Assert the count of objects matching filters."""
        actual = model_class.objects.filter(**filters).count()
        self.assertEqual(
            actual, expected_count,
            f"Expected {expected_count} {model_class.__name__} objects with {filters}, "
            f"found {actual}"
        )

    # ── Date Helpers ──────────────────────────────────────

    @staticmethod
    def future_date(days=1):
        """Return a date N days in the future."""
        return str(date.today() + timedelta(days=days))

    @staticmethod
    def past_date(days=1):
        """Return a date N days in the past."""
        return str(date.today() - timedelta(days=days))

    @staticmethod
    def today():
        """Return today's date as string."""
        return str(date.today())
