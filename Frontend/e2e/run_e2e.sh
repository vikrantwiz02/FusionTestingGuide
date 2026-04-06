#!/bin/bash
# ============================================================
# run_e2e.sh — Module-Specific E2E Test Runner
# ============================================================
#
# USAGE (from Fusion-client/ directory):
#   ./e2e/run_e2e.sh <ModuleName>
#
# EXAMPLES:
#   ./e2e/run_e2e.sh Mess
#   ./e2e/run_e2e.sh Examination
#   ./e2e/run_e2e.sh                   ← Runs ALL module E2E tests
#
# WHAT IT DOES:
#   1. Starts Django backend (background)
#   2. Starts Vite frontend (background)
#   3. Waits for both to be ready
#   4. Runs Playwright E2E tests for the specified module
#   5. Generates CSV reports
#   6. Stops both servers
#
# PREREQUISITES:
#   - Backend: Python venv activated, DB configured
#   - Frontend: npm install done
#   - Playwright: npm install -D @playwright/test && npx playwright install
# ============================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLIENT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$(dirname "$CLIENT_DIR")/Fusion/FusionIIIT"

MODULE_NAME="${1:-}"

if [ -n "$MODULE_NAME" ]; then
  TEST_PATH="e2e/tests/$MODULE_NAME/"
  if [ ! -d "$CLIENT_DIR/$TEST_PATH" ]; then
    echo -e "${RED}❌ No E2E tests found for module: $MODULE_NAME${NC}"
    echo "   Expected: $CLIENT_DIR/$TEST_PATH"
    echo ""
    echo "   Run setup first:"
    echo "   node e2e/setup_e2e.js $MODULE_NAME"
    exit 1
  fi
  echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
  echo -e "${GREEN}  E2E Testing — ${MODULE_NAME} Module               ${NC}"
  echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
else
  TEST_PATH="e2e/tests/"
  echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
  echo -e "${GREEN}  E2E Testing — ALL Modules                        ${NC}"
  echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
fi

# Create report directories
mkdir -p "$CLIENT_DIR/e2e/reports"
if [ -n "$MODULE_NAME" ]; then
  mkdir -p "$CLIENT_DIR/e2e/tests/$MODULE_NAME/reports/evidence"
fi

# ── Step 1: Start Backend ──
echo -e "\n${YELLOW}[1/5] Starting Django backend...${NC}"
cd "$BACKEND_DIR"
python manage.py runserver 8000 > /tmp/fusion_backend.log 2>&1 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# ── Step 2: Start Frontend ──
echo -e "${YELLOW}[2/5] Starting Vite frontend...${NC}"
cd "$CLIENT_DIR"
npm run dev > /tmp/fusion_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"

# ── Cleanup function ──
cleanup() {
  echo -e "\n${YELLOW}Stopping servers...${NC}"
  kill $BACKEND_PID 2>/dev/null && echo "  ⬛ Backend stopped" || true
  kill $FRONTEND_PID 2>/dev/null && echo "  ⬛ Frontend stopped" || true
}
trap cleanup EXIT

# ── Step 3: Wait for both servers ──
echo -e "${YELLOW}[3/5] Waiting for servers to start...${NC}"

for i in $(seq 1 30); do
  if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo -e "  ✅ Backend ready (http://127.0.0.1:8000)"
    break
  fi
  if [ $i -eq 30 ]; then
    echo -e "  ${RED}❌ Backend failed to start. Check /tmp/fusion_backend.log${NC}"
    exit 1
  fi
  sleep 1
done

for i in $(seq 1 30); do
  if curl -s http://localhost:5173/ > /dev/null 2>&1; then
    echo -e "  ✅ Frontend ready (http://localhost:5173)"
    break
  fi
  if [ $i -eq 30 ]; then
    echo -e "  ${RED}❌ Frontend failed to start. Check /tmp/fusion_frontend.log${NC}"
    exit 1
  fi
  sleep 1
done

# ── Step 4: Run Playwright Tests ──
echo -e "\n${YELLOW}[4/5] Running E2E tests: ${TEST_PATH}${NC}"
cd "$CLIENT_DIR"

TEST_EXIT_CODE=0
npx playwright test "$TEST_PATH" --reporter=list,json,html || TEST_EXIT_CODE=$?

# ── Step 5: Generate CSV Reports ──
echo -e "\n${YELLOW}[5/5] Generating CSV reports...${NC}"
if [ -n "$MODULE_NAME" ]; then
  MODULE_NAME_ENV="$MODULE_NAME" node e2e/helpers/csv-reporter.js || true
else
  node e2e/helpers/csv-reporter.js || true
fi

# ── Summary ──
echo -e "\n${GREEN}═══════════════════════════════════════════════════${NC}"
if [ -n "$MODULE_NAME" ]; then
  echo -e "${GREEN}  ✅ E2E Testing Complete — ${MODULE_NAME}          ${NC}"
else
  echo -e "${GREEN}  ✅ E2E Testing Complete — All Modules              ${NC}"
fi
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "  Reports:"
echo "    CSV:         e2e/reports/"
echo "    HTML:        e2e/reports/html/index.html"
if [ -n "$MODULE_NAME" ]; then
  echo "    Evidence:    e2e/tests/$MODULE_NAME/reports/evidence/"
fi
echo ""
echo "  Commands:"
echo "    View report: npx playwright show-report e2e/reports/html"
echo "    Debug test:  npx playwright test $TEST_PATH --headed --debug"
echo ""

if [ "$TEST_EXIT_CODE" -ne 0 ]; then
  echo -e "  ${RED}⚠️  Some tests failed. Check reports for details.${NC}"
fi

exit $TEST_EXIT_CODE
