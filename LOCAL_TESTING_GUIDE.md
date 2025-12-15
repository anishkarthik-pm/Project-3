# Local Testing Guide

> Complete guide to test the Fees Explainer Agent locally (with and without n8n)

---

## Quick Start - 3 Ways to Test

### ✅ **Option 1: Python Agent Only (Fastest - 2 minutes)**
Test the agent logic without n8n

### ✅ **Option 2: Python Agent + Flask API (5 minutes)**
Test the agent via HTTP API (simulates n8n integration)

### ✅ **Option 3: Full n8n Workflow (15 minutes)**
Test complete workflow with n8n locally

---

## Option 1: Python Agent Only (Recommended for Quick Testing)

### Step 1: Run the Built-in Tests

```bash
# Navigate to project directory
cd /home/user/Project-3

# Run comprehensive test suite
python test_agent.py
```

**Expected Output:**
```
============================================================
Running Fees Explainer Agent Tests
============================================================

✓ Scenario detection tests passed
✓ Clarifying questions tests passed
✓ Fee explanation generation tests passed
✓ MCP actions preparation tests passed
✓ Approval gating tests passed
✓ MCP execution with approval tests passed
✓ Partial approval tests passed
✓ No PII in outputs tests passed
✓ Official sources only tests passed
✓ Last checked date tests passed

============================================================
Test Results: 10 passed, 0 failed
============================================================
```

---

### Step 2: Run Example Interaction

```bash
# Run the example scenario
python fees_explainer_agent.py
```

**Expected Output:**
```
================================================================================
Example 1: User asks about ELSS exit load
================================================================================

Scenario: Exit Load & ELSS Lock-in Period

Clarifying Questions:
1. Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?
2. Do you plan to redeem within 1 year of investment?
3. Is this a lumpsum investment or SIP?

Fee Explanation (Exit Load & ELSS Lock-in Period):
Last Checked: 2025-12-15

Fee Details:
1. ELSS funds have a mandatory 3-year lock-in period...
   📎 Source: https://groww.in/p/tax-saving-funds/

[... more bullets ...]

MCP Actions Pending Approval: 3
  - Add notes entry: Fee Explanation: Exit Load & ELSS Lock-in Period
  - Draft email to support@groww.in
  - Log audit entry

Execution Results:
  Executed: 3
  Skipped: 0
  Errors: 0
```

---

### Step 3: Test MCP Handlers

```bash
# Test MCP handlers directly
python mcp_handlers.py
```

**Expected Output:**
```
Approval Required: Do you want to append this fee explanation to your notes?
Payload: {...}

Audit Log Result: {
  "status": "success",
  "tool": "log_audit_entry",
  "message": "Audit entry logged: Test audit log"
}
```

---

### Step 4: Interactive Testing (Custom Scenarios)

Create a test script:

```bash
cat > test_custom_scenario.py << 'EOF'
from fees_explainer_agent import FeesExplainerAgent

# Initialize agent
agent = FeesExplainerAgent()

# Test SIP Mandate Fees scenario
print("=" * 60)
print("Testing SIP Mandate Fees Scenario")
print("=" * 60)

response = agent.start_conversation("What are SIP cancellation charges?")

print(f"\nScenario Detected: {response['scenario']}")
print("\nClarifying Questions:")
for i, q in enumerate(response['clarifying_questions'], 1):
    print(f"{i}. {q}")

# Provide answers
answers = {
    response['clarifying_questions'][0]: "Cancelling existing SIP",
    response['clarifying_questions'][1]: "HDFC Bank",
    response['clarifying_questions'][2]: "Above ₹5,000"
}

print("\n" + "=" * 60)
print("User Answers:")
for q, a in answers.items():
    print(f"Q: {q}")
    print(f"A: {a}\n")

# Process answers
result = agent.process_clarifiers(answers)

print("=" * 60)
print("Fee Explanation:")
print("=" * 60)
for i, detail in enumerate(result['explanation']['fee_details'], 1):
    print(f"\n{i}. {detail['text']}")
    print(f"   Source: {detail['source']}")

print("\n" + "=" * 60)
print(f"MCP Actions Pending: {result['mcp_actions_pending']}")
print("=" * 60)
EOF

python test_custom_scenario.py
```

---

## Option 2: Python Agent + Flask API

This simulates how n8n would interact with the agent via HTTP.

### Step 1: Create Flask API Server

```bash
cat > api_server.py << 'EOF'
"""
Flask API Server for Fees Explainer Agent
Simulates n8n webhook integration
"""

from flask import Flask, request, jsonify
from fees_explainer_agent import FeesExplainerAgent
from datetime import datetime

app = Flask(__name__)

# In-memory session storage (use Redis in production)
sessions = {}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route('/api/fees-explainer/start', methods=['POST'])
def start_conversation():
    """
    Start fee explanation conversation.
    Endpoint: POST /api/fees-explainer/start
    Body: {"query": "What is ELSS exit load?"}
    """
    try:
        data = request.get_json()
        query = data.get('query')

        if not query:
            return jsonify({"error": "Missing 'query' field"}), 400

        # Initialize agent
        agent = FeesExplainerAgent()
        response = agent.start_conversation(query)

        # Store session
        session_id = response.get('session_id', str(datetime.now().timestamp()))
        sessions[session_id] = agent

        response['session_id'] = session_id

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/fees-explainer/answers', methods=['POST'])
def process_answers():
    """
    Process clarifying answers.
    Endpoint: POST /api/fees-explainer/answers
    Body: {"session_id": "...", "answers": {...}}
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        answers = data.get('answers')

        if not session_id or not answers:
            return jsonify({"error": "Missing 'session_id' or 'answers'"}), 400

        # Get agent from session
        agent = sessions.get(session_id)
        if not agent:
            return jsonify({"error": "Invalid session_id"}), 404

        # Process answers
        response = agent.process_clarifiers(answers)
        response['session_id'] = session_id

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/fees-explainer/approvals', methods=['POST'])
def process_approvals():
    """
    Process MCP action approvals.
    Endpoint: POST /api/fees-explainer/approvals
    Body: {"session_id": "...", "approved_actions": [...]}
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        approved_actions = data.get('approved_actions', [])

        if not session_id:
            return jsonify({"error": "Missing 'session_id'"}), 400

        # Get agent from session
        agent = sessions.get(session_id)
        if not agent:
            return jsonify({"error": "Invalid session_id"}), 404

        # Approve actions
        for approval in approved_actions:
            action_id = approval.get('action_id')
            is_approved = approval.get('approved', False)

            if is_approved:
                agent.approve_mcp_action(action_id)

        # Execute approved actions
        results = agent.execute_approved_mcp_actions()
        results['session_id'] = session_id

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/fees-explainer/session/<session_id>', methods=['GET'])
def get_session_summary(session_id):
    """Get session summary."""
    agent = sessions.get(session_id)
    if not agent:
        return jsonify({"error": "Invalid session_id"}), 404

    summary = agent.get_conversation_summary()
    summary['session_id'] = session_id

    return jsonify(summary), 200


if __name__ == '__main__':
    print("=" * 60)
    print("Fees Explainer Agent API Server")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /health")
    print("  POST /api/fees-explainer/start")
    print("  POST /api/fees-explainer/answers")
    print("  POST /api/fees-explainer/approvals")
    print("  GET  /api/fees-explainer/session/<session_id>")
    print("\nStarting server on http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
EOF
```

### Step 2: Install Flask

```bash
pip install flask
```

### Step 3: Start the API Server

```bash
python api_server.py
```

**Expected Output:**
```
============================================================
Fees Explainer Agent API Server
============================================================

Endpoints:
  GET  /health
  POST /api/fees-explainer/start
  POST /api/fees-explainer/answers
  POST /api/fees-explainer/approvals
  GET  /api/fees-explainer/session/<session_id>

Starting server on http://localhost:5000
============================================================
```

---

### Step 4: Test API with curl

**Terminal 1: Keep server running**

**Terminal 2: Run tests**

#### Test 1: Health Check

```bash
curl http://localhost:5000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-15T10:30:00.123456"
}
```

#### Test 2: Start Conversation

```bash
curl -X POST http://localhost:5000/api/fees-explainer/start \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ELSS exit load?"
  }'
```

**Expected:**
```json
{
  "next_step": "ask_clarifiers",
  "scenario": "Exit Load & ELSS Lock-in Period",
  "clarifying_questions": [
    "Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?",
    "Do you plan to redeem within 1 year of investment?",
    "Is this a lumpsum investment or SIP?"
  ],
  "session_id": "1734234567.890"
}
```

**Copy the session_id for next steps!**

#### Test 3: Submit Answers

```bash
# Replace SESSION_ID with actual value from step 2
SESSION_ID="1734234567.890"

curl -X POST http://localhost:5000/api/fees-explainer/answers \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"answers\": {
      \"Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?\": \"ELSS\",
      \"Do you plan to redeem within 1 year of investment?\": \"No, after 3 years\",
      \"Is this a lumpsum investment or SIP?\": \"SIP\"
    }
  }"
```

**Expected:**
```json
{
  "next_step": "review_explanation",
  "explanation": {
    "scenario": "Exit Load & ELSS Lock-in Period",
    "last_checked": "2025-12-15",
    "fee_details": [
      {
        "text": "ELSS funds have a mandatory 3-year lock-in...",
        "source": "https://groww.in/p/tax-saving-funds/"
      }
      // ... more bullets
    ]
  },
  "mcp_actions_pending": 3,
  "mcp_actions_summary": [
    "notes: Add notes entry: Fee Explanation: Exit Load & ELSS",
    "email: Draft email to support@groww.in",
    "audit: Log audit entry"
  ]
}
```

#### Test 4: Approve & Execute MCP Actions

```bash
# Approve all 3 actions
curl -X POST http://localhost:5000/api/fees-explainer/approvals \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"approved_actions\": [
      {\"action_id\": 0, \"approved\": true},
      {\"action_id\": 1, \"approved\": true},
      {\"action_id\": 2, \"approved\": true}
    ]
  }"
```

**Expected:**
```json
{
  "executed": [
    {
      "action_id": 0,
      "action_type": "notes",
      "result": {
        "status": "success",
        "message": "Notes entry added: Fee Explanation: Exit Load & ELSS"
      }
    }
    // ... more results
  ],
  "skipped": [],
  "errors": []
}
```

#### Test 5: Verify Files Created

```bash
# Check notes file
cat /home/user/fees_explanations.md

# Check email drafts
ls -la /home/user/email_drafts/

# Check audit log
cat /home/user/audit_log.jsonl
```

---

### Step 5: Test with Postman/Insomnia (Optional)

Import this collection:

```bash
cat > postman_collection.json << 'EOF'
{
  "info": {
    "name": "Fees Explainer Agent API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:5000/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["health"]
        }
      }
    },
    {
      "name": "2. Start Conversation",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"query\": \"What is ELSS exit load?\"\n}"
        },
        "url": {
          "raw": "http://localhost:5000/api/fees-explainer/start",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "fees-explainer", "start"]
        }
      }
    },
    {
      "name": "3. Submit Answers",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"session_id\": \"{{session_id}}\",\n  \"answers\": {\n    \"Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?\": \"ELSS\",\n    \"Do you plan to redeem within 1 year of investment?\": \"No\",\n    \"Is this a lumpsum investment or SIP?\": \"SIP\"\n  }\n}"
        },
        "url": {
          "raw": "http://localhost:5000/api/fees-explainer/answers",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "fees-explainer", "answers"]
        }
      }
    }
  ]
}
EOF
```

---

## Option 3: Full n8n Workflow Testing

### Step 1: Install n8n

```bash
# Using npm (Node.js required)
npm install -g n8n

# OR using npx (no installation)
npx n8n

# OR using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### Step 2: Start n8n

```bash
# If installed globally
n8n start

# If using npx
npx n8n

# If using Docker (already running from step 1)
```

**Expected Output:**
```
n8n ready on port 5678
Editor is now accessible via:
http://localhost:5678/
```

### Step 3: Import Workflow

1. Open browser: http://localhost:5678
2. Click **Workflows** → **Import from File**
3. Select `/home/user/Project-3/n8n_workflow_fees_explainer.json`
4. Click **Import**

### Step 4: Configure Workflow Nodes

#### Update Function Nodes to Call Local API

1. Click on **Initialize Agent** node
2. Replace the function code with:

```javascript
const response = await $http.request({
  method: 'POST',
  url: 'http://localhost:5000/api/fees-explainer/start',
  body: {
    query: $input.item.json.query
  }
});

return {
  json: response
};
```

3. Repeat for **Process Answers** and **Approvals** nodes

### Step 5: Activate Workflow

1. Click **Active** toggle (top-right)
2. Note the webhook URLs

### Step 6: Test Webhooks

```bash
# Get webhook URL from n8n UI (e.g., http://localhost:5678/webhook/abc123)

# Test start endpoint
curl -X POST http://localhost:5678/webhook/YOUR_WEBHOOK_ID \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ELSS exit load?"}'
```

---

## Automated Testing Script

Create a complete end-to-end test:

```bash
cat > test_e2e.sh << 'EOF'
#!/bin/bash

echo "========================================="
echo "End-to-End Testing Script"
echo "========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Python Agent
echo -e "\n${GREEN}[1/3] Testing Python Agent...${NC}"
python test_agent.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python Agent tests passed${NC}"
else
    echo -e "${RED}✗ Python Agent tests failed${NC}"
    exit 1
fi

# Test 2: Example Interaction
echo -e "\n${GREEN}[2/3] Running Example Interaction...${NC}"
python fees_explainer_agent.py > /tmp/agent_output.log
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Example interaction completed${NC}"
    echo "Output saved to /tmp/agent_output.log"
else
    echo -e "${RED}✗ Example interaction failed${NC}"
    exit 1
fi

# Test 3: API Server (if running)
echo -e "\n${GREEN}[3/3] Testing API Server (if available)...${NC}"
HEALTH=$(curl -s http://localhost:5000/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ API Server is running${NC}"
    echo "Response: $HEALTH"
else
    echo -e "${RED}⚠ API Server not running (optional)${NC}"
fi

echo -e "\n========================================="
echo -e "${GREEN}All tests completed!${NC}"
echo "========================================="
EOF

chmod +x test_e2e.sh
./test_e2e.sh
```

---

## Troubleshooting

### Issue 1: Import Errors

**Problem:** `ModuleNotFoundError: No module named 'fees_explainer_agent'`

**Solution:**
```bash
# Ensure you're in the project directory
cd /home/user/Project-3

# Run from project root
python test_agent.py
```

### Issue 2: File Permission Errors

**Problem:** `Permission denied: /home/user/fees_explanations.md`

**Solution:**
```bash
# Create directories and set permissions
mkdir -p /home/user/email_drafts
touch /home/user/fees_explanations.md
touch /home/user/audit_log.jsonl
chmod 644 /home/user/fees_explanations.md
chmod 644 /home/user/audit_log.jsonl
```

### Issue 3: Flask Not Found

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
pip install flask
```

### Issue 4: Port Already in Use

**Problem:** `Address already in use: Port 5000`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process (replace PID)
kill -9 <PID>

# Or use different port
python api_server.py --port 5001
```

---

## Verification Checklist

After testing, verify:

- [ ] All 10 unit tests pass
- [ ] Example interaction completes successfully
- [ ] MCP files are created (`fees_explanations.md`, `email_drafts/`, `audit_log.jsonl`)
- [ ] API server responds to health check
- [ ] Complete flow works (start → answers → approvals)
- [ ] Approval gating works (rejected actions are skipped)
- [ ] No PII in any outputs
- [ ] All sources are official URLs

---

## Next Steps

Once local testing is complete:

1. **Deploy to Staging**: Test in staging environment
2. **Load Testing**: Use tools like Apache Bench or Locust
3. **User Acceptance Testing**: Get feedback from support team
4. **Production Deployment**: Deploy to production n8n instance

---

## Quick Reference

### Test Commands

```bash
# Unit tests
python test_agent.py

# Example interaction
python fees_explainer_agent.py

# MCP handlers
python mcp_handlers.py

# API server
python api_server.py

# E2E test
./test_e2e.sh
```

### API Endpoints

```
GET  http://localhost:5000/health
POST http://localhost:5000/api/fees-explainer/start
POST http://localhost:5000/api/fees-explainer/answers
POST http://localhost:5000/api/fees-explainer/approvals
```

### Output Files

```
/home/user/fees_explanations.md    # Notes
/home/user/email_drafts/*.eml       # Email drafts
/home/user/audit_log.jsonl          # Audit log
```

---

**Happy Testing! 🚀**
