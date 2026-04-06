#!/bin/bash
# ============================================================
# run_e2e.sh — Single Command to Run Full-Stack E2E Tests
# ============================================================
#
# USAGE (from Fusion-client/ directory):
#   chmod +x e2e/run_e2e.sh
#   ./e2e/run_e2e.sh
#
# WHAT IT DOES:
#   1. Starts Django backend server (background)
#   2. Starts Vite frontend server (background)
#   3. Waits for both to be ready
#   4. Runs Playwright E2E tests
#   5. Generates CSV reports
#   6. Stops both servers
#   7. Prints summary
#
# PREREQUISITES:
#   - Backend: Python venv activated, DB configured
#   - Frontend: npm install done
#   - Playwright: npx playwright install
# ============================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLIENT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$(dirname "$CLIENT_DIR")/Fusion/FusionIIIT"

echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Fusion E2E Testing — Full Stack Integration      ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"

# Create evidence directory
mkdir -p "$CLIENT_DIR/e2e/reports/evidence"
mkdir -p "$CLIENT_DIR/e2e/reports/html"

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

# ── Step 3: Wait for both servers ──
echo -e "${YELLOW}[3/5] Waiting for servers to start...${NC}"

# Wait for backend
for i in $(seq 1 30); do
  if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo -e "  ✅ Backend ready (http://127.0.0.1:8000)"
    break
  fi
  if [ $i -eq 30 ]; then
    echo -e "  ${RED}❌ Backend failed to start. Check /tmp/fusion_backend.log${NC}"
    kill $FRONTEND_PID 2>/dev/null || true
    exit 1
  fi
  sleep 1
done

# Wait for frontend
for i in $(seq 1 30); do
  if curl -s http://localhost:5173/ > /dev/null 2>&1; then
    echo -e "  ✅ Frontend ready (http://localhost:5173)"
    break
  fi
  if [ $i -eq 30 ]; then
    echo -e "  ${RED}❌ Frontend failed to start. Check /tmp/fusion_frontend.log${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
  fi
  sleep 1
done

# ── Step 4: Run Playwright Tests ──
echo -e "\n${YELLOW}[4/5] Running E2E tests...${NC}"
cd "$CLIENT_DIR"

# Run Playwright
npx playwright test --reporter=list,json,html || TEST_EXIT_CODE=$?

# ── Step 5: Generate CSV Reports ──
echo -e "\n${YELLOW}[5/5] Generating CSV reports...${NC}"
node e2e/helpers/csv-reporter.js || true

# ── Cleanup: Stop servers ──
echo -e "\n${YELLOW}Stopping servers...${NC}"
kill $BACKEND_PID 2>/dev/null && echo "  ⬛ Backend stopped" || true
kill $FRONTEND_PID 2>/dev/null && echo "  ⬛ Frontend stopped" || true

# ── Summary ──
echo -e "\n${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ E2E Testing Complete                           ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "  Reports:     $CLIENT_DIR/e2e/reports/"
echo "  Screenshots: $CLIENT_DIR/e2e/reports/evidence/"
echo "  HTML Report: $CLIENT_DIR/e2e/reports/html/index.html"
echo "  CSV Files:   Module_Test_Summary.csv"
echo "               Test_Execution_Log.csv"
echo "               Defect_Log.csv"
echo "               Artifact_Evaluation.csv"
echo ""

if [ "${TEST_EXIT_CODE:-0}" -ne 0 ]; then
  echo -e "  ${RED}⚠️  Some tests failed. Check reports for details.${NC}"
  exit $TEST_EXIT_CODE
fi
