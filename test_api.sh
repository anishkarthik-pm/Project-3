#!/bin/bash

# Quick API Testing Script
# Usage: ./test_api.sh

set -e  # Exit on error

echo "========================================="
echo "Fees Explainer Agent - API Testing"
echo "========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if API server is running
echo -e "\n${BLUE}[1/5] Checking API Server...${NC}"
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API Server is running${NC}"
else
    echo -e "${YELLOW}⚠ API Server not running. Start it with: python api_server.py${NC}"
    echo -e "${YELLOW}⚠ Opening new terminal recommended${NC}"
    exit 1
fi

# Test 1: Health Check
echo -e "\n${BLUE}[2/5] Testing Health Endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:5000/health)
echo "Response: $HEALTH_RESPONSE"
echo -e "${GREEN}✓ Health check passed${NC}"

# Test 2: Start Conversation
echo -e "\n${BLUE}[3/5] Starting Conversation (ELSS Exit Load)...${NC}"
START_RESPONSE=$(curl -s -X POST http://localhost:5000/api/fees-explainer/start \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ELSS exit load?"}')

echo "$START_RESPONSE" | python -m json.tool

# Extract session_id
SESSION_ID=$(echo "$START_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['session_id'])" 2>/dev/null)

if [ -z "$SESSION_ID" ]; then
    echo -e "${YELLOW}⚠ Could not extract session_id${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ Conversation started${NC}"
echo -e "${GREEN}Session ID: $SESSION_ID${NC}"

# Test 3: Submit Answers
echo -e "\n${BLUE}[4/5] Submitting Answers...${NC}"
ANSWERS_RESPONSE=$(curl -s -X POST http://localhost:5000/api/fees-explainer/answers \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"answers\": {
      \"Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?\": \"ELSS\",
      \"Do you plan to redeem within 1 year of investment?\": \"No, after 3 years\",
      \"Is this a lumpsum investment or SIP?\": \"SIP\"
    }
  }")

echo "$ANSWERS_RESPONSE" | python -m json.tool | head -30
echo "..."
echo -e "\n${GREEN}✓ Answers processed${NC}"

# Test 4: Approve & Execute MCP Actions
echo -e "\n${BLUE}[5/5] Approving MCP Actions...${NC}"
APPROVALS_RESPONSE=$(curl -s -X POST http://localhost:5000/api/fees-explainer/approvals \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"approved_actions\": [
      {\"action_id\": 0, \"approved\": true},
      {\"action_id\": 1, \"approved\": true},
      {\"action_id\": 2, \"approved\": true}
    ]
  }")

echo "$APPROVALS_RESPONSE" | python -m json.tool

echo -e "\n${GREEN}✓ MCP Actions executed${NC}"

# Verify files created
echo -e "\n${BLUE}Verifying Output Files...${NC}"

if [ -f "/home/user/fees_explanations.md" ]; then
    echo -e "${GREEN}✓ Notes file created${NC}"
    echo "Preview:"
    tail -10 /home/user/fees_explanations.md
else
    echo -e "${YELLOW}⚠ Notes file not found${NC}"
fi

if [ -d "/home/user/email_drafts" ]; then
    DRAFT_COUNT=$(ls -1 /home/user/email_drafts/*.eml 2>/dev/null | wc -l)
    echo -e "${GREEN}✓ Email drafts directory exists (${DRAFT_COUNT} drafts)${NC}"
else
    echo -e "${YELLOW}⚠ Email drafts directory not found${NC}"
fi

if [ -f "/home/user/audit_log.jsonl" ]; then
    echo -e "${GREEN}✓ Audit log created${NC}"
    echo "Last entry:"
    tail -1 /home/user/audit_log.jsonl | python -m json.tool
else
    echo -e "${YELLOW}⚠ Audit log not found${NC}"
fi

echo -e "\n========================================="
echo -e "${GREEN}API Testing Complete!${NC}"
echo "========================================="
echo -e "\nSession ID: ${GREEN}$SESSION_ID${NC}"
echo -e "View full session: ${BLUE}curl http://localhost:5000/api/fees-explainer/session/$SESSION_ID${NC}"
