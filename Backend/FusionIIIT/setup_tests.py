#!/usr/bin/env python3
"""
setup_tests.py — One-Command Test Framework Setup Script
==========================================================

USAGE:
    python setup_tests.py <module_name>

EXAMPLE:
    python setup_tests.py central_mess
    python setup_tests.py complaint_system
    python setup_tests.py placement_cell

WHAT IT DOES:
  1. Copies the _testing_framework/ scaffold into applications/<module>/tests/
  2. Creates the tests/ directory structure
  3. Installs required pip packages (pyyaml)
  4. Prints next steps for the team

RUN FROM: FusionIIIT/ directory
"""

import os
import sys
import shutil
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python setup_tests.py <module_name>")
        print("Example: python setup_tests.py central_mess")
        print("\nAvailable modules:")
        apps_dir = Path("applications")
        if apps_dir.exists():
            for d in sorted(apps_dir.iterdir()):
                if d.is_dir() and not d.name.startswith("_") and d.name != "__pycache__":
                    print(f"  - {d.name}")
        sys.exit(1)

    module_name = sys.argv[1]
    module_dir = Path("applications") / module_name
    target_tests_dir = module_dir / "tests"
    framework_dir = Path("_testing_framework")

    # Validate
    if not module_dir.exists():
        print(f"❌ Module not found: {module_dir}")
        sys.exit(1)

    if not framework_dir.exists():
        print(f"❌ Framework not found: {framework_dir}")
        print("   Make sure you're running from the FusionIIIT/ directory")
        sys.exit(1)

    # Check if tests/ already exists
    if target_tests_dir.exists():
        response = input(f"⚠️  {target_tests_dir} already exists. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
        # Backup existing
        backup = target_tests_dir.parent / "tests_backup"
        if backup.exists():
            shutil.rmtree(backup)
        shutil.move(str(target_tests_dir), str(backup))
        print(f"  📦 Existing tests backed up to {backup}/")

    # Handle existing tests.py file (Django default)
    tests_file = module_dir / "tests.py"
    if tests_file.exists():
        # Move it into the new tests/ package
        pass  # We'll handle this below

    # Copy framework
    print(f"\n🔧 Setting up test framework for: {module_name}")
    print(f"   Source: {framework_dir}/")
    print(f"   Target: {target_tests_dir}/")

    shutil.copytree(str(framework_dir), str(target_tests_dir))

    # Move existing tests.py content into the package if it has real tests
    if tests_file.exists():
        with open(tests_file) as f:
            content = f.read().strip()
        if content and not content.startswith("# from django.test"):
            # Has real content, preserve it
            legacy_path = target_tests_dir / "test_legacy.py"
            shutil.copy2(str(tests_file), str(legacy_path))
            print(f"  📋 Preserved existing tests.py as test_legacy.py")
        # Remove old tests.py so Django uses tests/ package instead
        tests_file.unlink()
        print(f"  🗑️  Removed old tests.py (tests/ package takes priority)")

    # Create reports/ directory
    (target_tests_dir / "reports").mkdir(exist_ok=True)

    # Update __init__.py with module name
    init_file = target_tests_dir / "__init__.py"
    with open(init_file, "w") as f:
        f.write(f'# Test package for: applications.{module_name}\n')
        f.write(f'# Run: python manage.py test applications.{module_name}.tests -v 2\n')

    # Update conftest.py with module name
    conftest_file = target_tests_dir / "conftest.py"
    with open(conftest_file) as f:
        content = f.read()
    content = content.replace(
        'MODULE_NAME = os.environ.get("FUSION_TEST_MODULE", "YourModule")',
        f'MODULE_NAME = os.environ.get("FUSION_TEST_MODULE", "{module_name}")'
    )
    with open(conftest_file, "w") as f:
        f.write(content)

    print(f"\n✅ Framework installed successfully!")
    print(f"\n" + "=" * 60)
    print(f"📋 NEXT STEPS FOR YOUR TEAM")
    print(f"=" * 60)
    print(f"""
1. INSTALL DEPENDENCIES (one-time):
   pip install pyyaml

2. WRITE YOUR SPECS (from your UC/BR/WF documents):
   Edit these files:
   - {target_tests_dir}/specs/use_cases.yaml
   - {target_tests_dir}/specs/business_rules.yaml
   - {target_tests_dir}/specs/workflows.yaml

3. WRITE YOUR TESTS:
   Edit these files (replace EXAMPLE classes with your tests):
   - {target_tests_dir}/test_use_cases.py
   - {target_tests_dir}/test_business_rules.py
   - {target_tests_dir}/test_workflows.py

4. CUSTOMIZE BASE SETUP:
   Edit {target_tests_dir}/conftest.py
   → Override setUpTestData() to create YOUR module's required objects

5. RUN ALL TESTS (single command):
   python manage.py test applications.{module_name}.tests -v 2

6. RUN WITH REPORT GENERATION:
   python manage.py test applications.{module_name}.tests -v 2 \\
     --testrunner=applications.{module_name}.tests.runner.ReportingTestRunner

7. COLLECT REPORTS:
   Reports are generated in:
   {target_tests_dir}/reports/
     - Module_Test_Summary.csv     (Sheet 1)
     - UC_Test_Design.csv          (Sheet 2)
     - BR_Test_Design.csv          (Sheet 3)
     - WF_Test_Design.csv          (Sheet 4)
     - Test_Execution_Log.csv      (Sheet 5)
     - Defect_Log.csv              (Sheet 6)
     - Artifact_Evaluation.csv     (Sheet 7)
""")


if __name__ == "__main__":
    main()
