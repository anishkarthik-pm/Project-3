# n8n Workflow Setup Guide

> Step-by-step guide to set up the Fees Explainer Agent workflow in n8n

---

## Prerequisites

- n8n installed (self-hosted or cloud)
- Access to n8n UI
- Python agent running (or accessible via HTTP)

---

## Option 1: Import JSON Workflow (Recommended)

### Step 1: Open n8n

Navigate to your n8n instance:
```
http://localhost:5678  # Self-hosted
# or
https://your-instance.n8n.cloud  # Cloud
```

### Step 2: Import Workflow

1. Click **Workflows** in the left sidebar
2. Click **Add workflow** → **Import from File**
3. Select `n8n_workflow_fees_explainer.json`
4. Click **Import**

### Step 3: Configure Webhook URLs

The workflow will automatically generate webhook URLs. Note them down:

```
Webhook 1: http://localhost:5678/webhook/fees-explainer-start
Webhook 2: http://localhost:5678/webhook/fees-explainer-answers
Webhook 3: http://localhost:5678/webhook/fees-explainer-approvals
```

### Step 4: Activate Workflow

1. Click the **Active** toggle in the top-right
2. Workflow is now live!

---

## Option 2: Manual Setup

If you prefer to build the workflow from scratch:

### Node 1: Webhook Trigger - User Query

1. Add **Webhook** node
2. Configure:
   - **Path**: `fees-explainer-start`
   - **Method**: POST
   - **Response Mode**: Respond to Webhook

### Node 2: Initialize Agent (Function)

1. Add **Function** node
2. Connect from Webhook Trigger
3. Paste code:

```javascript
// Extract user query
const userQuery = $input.item.json.query;

// Initialize agent (simplified - in production, call Python agent API)
const response = {
  scenario: detectScenario(userQuery), // Implement scenario detection
  clarifying_questions: getClarifiers(scenario),
  session_id: Date.now().toString()
};

function detectScenario(query) {
  const q = query.toLowerCase();
  if (q.includes('exit load') || q.includes('elss') || q.includes('lock')) {
    return 'Exit Load & ELSS Lock-in Period';
  } else if (q.includes('sip') || q.includes('mandate') || q.includes('cancel')) {
    return 'SIP Mandate Fees & Cancellation';
  } else {
    return 'Expense Ratio (Direct vs Regular Plans)';
  }
}

function getClarifiers(scenario) {
  const clarifiers = {
    'Exit Load & ELSS Lock-in Period': [
      'Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?',
      'Do you plan to redeem within 1 year of investment?',
      'Is this a lumpsum investment or SIP?'
    ],
    'SIP Mandate Fees & Cancellation': [
      'Are you setting up a new SIP or cancelling an existing one?',
      'What is your bank (some banks charge for auto-debit mandates)?',
      'Is the SIP amount above or below ₹5,000 per month?'
    ],
    'Expense Ratio (Direct vs Regular Plans)': [
      'Are you investing in Direct Plan or Regular Plan?',
      'Which fund category: Equity, Debt, or Hybrid?',
      'Do you want to understand how expense ratio impacts returns?'
    ]
  };
  return clarifiers[scenario] || [];
}

return {
  json: {
    session_id: response.session_id,
    scenario: response.scenario,
    clarifiers: response.clarifying_questions,
    user_query: userQuery
  }
};
```

### Node 3: Send Clarifying Questions (Respond to Webhook)

1. Add **Respond to Webhook** node
2. Connect from Initialize Agent
3. Configure:
   - **Response Mode**: JSON
   - **Response Body**:

```json
{
  "status": "clarifiers_required",
  "scenario": "{{ $json.scenario }}",
  "questions": "{{ $json.clarifiers }}",
  "session_id": "{{ $json.session_id }}",
  "instructions": "Please answer the following questions to get accurate fee information"
}
```

### Node 4: Webhook - Receive Answers

1. Add new **Webhook** node
2. Configure:
   - **Path**: `fees-explainer-answers`
   - **Method**: POST
   - **Response Mode**: Respond to Webhook

### Node 5: Process Answers & Generate Explanation (Function)

1. Add **Function** node
2. Connect from Webhook - Receive Answers
3. Paste code:

```javascript
const answers = $input.item.json.answers;
const sessionId = $input.item.json.session_id;

// In production, call Python agent's process_clarifiers() method
// For now, return mock explanation

const explanation = {
  scenario: 'Exit Load & ELSS Lock-in Period',
  last_checked: '2025-12-15',
  fee_details: [
    {
      text: 'ELSS funds have a mandatory 3-year lock-in period as per Section 80C.',
      source: 'https://groww.in/p/tax-saving-funds/'
    },
    // ... more bullets
  ],
  disclaimer: 'This information is based on official sources. Always verify exact fees from the fund\'s SID.'
};

const mcpActions = [
  {
    action_id: 0,
    action_type: 'notes',
    summary: 'Add notes entry: Fee Explanation: ' + explanation.scenario,
    payload: {
      entry_title: 'Fee Explanation: ' + explanation.scenario,
      date: new Date().toISOString(),
      scenario: explanation.scenario,
      fee_details: explanation.fee_details,
      last_checked: explanation.last_checked
    }
  },
  {
    action_id: 1,
    action_type: 'email',
    summary: 'Draft email to support@groww.in',
    payload: {
      to: 'support@groww.in',
      subject: 'Fee Clarification Request: ' + explanation.scenario,
      draft_only: true
    }
  },
  {
    action_id: 2,
    action_type: 'audit',
    summary: 'Log audit entry',
    payload: {
      who: 'FeesExplainerAgent',
      when: new Date().toISOString(),
      action: 'Generated fee explanation for: ' + explanation.scenario
    }
  }
];

return {
  json: {
    session_id: sessionId,
    explanation: explanation,
    mcp_actions: mcpActions,
    answers: answers
  }
};
```

### Node 6: Send Explanation & MCP Actions (Respond to Webhook)

1. Add **Respond to Webhook** node
2. Connect from Process Answers
3. Configure response with explanation and MCP actions

### Node 7: Webhook - MCP Action Approvals

1. Add new **Webhook** node
2. Configure:
   - **Path**: `fees-explainer-approvals`
   - **Method**: POST

### Node 8: Switch - MCP Action Type

1. Add **Switch** node
2. Connect from Webhook - Approvals
3. Add 3 routes:
   - Route 1: `{{ $json.action_type }} == 'notes'`
   - Route 2: `{{ $json.action_type }} == 'email'`
   - Route 3: `{{ $json.action_type }} == 'audit'`

### Nodes 9-11: MCP Action Handlers

#### Node 9: MCP - Append to Notes

1. Add **Write File** or **HTTP Request** node (call MCP server)
2. Connect from Switch (notes route)
3. Configure to append to `/home/user/fees_explanations.md`

#### Node 10: MCP - Create Email Draft

1. Add **Email** or **HTTP Request** node
2. Connect from Switch (email route)
3. Configure to create draft (NOT send)

#### Node 11: MCP - Log Audit Entry

1. Add **Write File** or **HTTP Request** node
2. Connect from Switch (audit route)
3. Configure to append to `/home/user/audit_log.jsonl`

### Node 12: Send Completion Response

1. Add **Respond to Webhook** node
2. Connect from all 3 MCP action handlers
3. Return execution results

---

## Connecting to Python Agent

### Option A: HTTP Request (Recommended)

Replace Function nodes with **HTTP Request** nodes that call your Python agent API:

```
POST http://localhost:5000/agent/start
POST http://localhost:5000/agent/process-answers
POST http://localhost:5000/agent/execute-mcp
```

### Option B: Python Code Node

If using n8n with Python support:

1. Use **Code** node with Python
2. Import `fees_explainer_agent.py`
3. Call agent methods directly

---

## Testing the Workflow

### Test 1: Start Query

```bash
curl -X POST http://localhost:5678/webhook/fees-explainer-start \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ELSS exit load?"}'
```

Expected: Clarifying questions

### Test 2: Submit Answers

```bash
curl -X POST http://localhost:5678/webhook/fees-explainer-answers \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "1734234567890",
    "answers": {
      "question1": "ELSS",
      "question2": "After 3 years",
      "question3": "SIP"
    }
  }'
```

Expected: Explanation + MCP actions

### Test 3: Approve Actions

```bash
curl -X POST http://localhost:5678/webhook/fees-explainer-approvals \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "1734234567890",
    "approved_actions": [
      {"action_id": 0, "approved": true},
      {"action_id": 1, "approved": true},
      {"action_id": 2, "approved": true}
    ]
  }'
```

Expected: Execution results

---

## Troubleshooting

### Webhooks Not Working

1. Check workflow is **Active**
2. Verify webhook URLs in n8n UI
3. Check firewall/port 5678 is accessible

### MCP Actions Failing

1. Verify file paths exist:
   ```bash
   mkdir -p /home/user/email_drafts
   touch /home/user/fees_explanations.md
   touch /home/user/audit_log.jsonl
   ```

2. Check file permissions:
   ```bash
   chmod 644 /home/user/fees_explanations.md
   chmod 644 /home/user/audit_log.jsonl
   ```

### Python Agent Not Responding

1. Verify agent is running:
   ```bash
   python fees_explainer_agent.py
   ```

2. Check HTTP endpoint:
   ```bash
   curl http://localhost:5000/health
   ```

---

## Advanced Configuration

### Authentication

Add **Basic Auth** or **API Key** to webhooks:

1. Edit Webhook node
2. Go to **Credentials**
3. Add authentication method

### Rate Limiting

Add **Rate Limit** node before processing:

1. Add **RateLimit** node
2. Configure: 10 requests per minute per IP

### Logging

Add **HTTP Request** node to external logging service:

1. After each major step
2. Send logs to your logging platform

---

## Production Checklist

- [ ] Workflow activated
- [ ] Webhooks tested with real requests
- [ ] MCP actions verified (files created)
- [ ] Error handling configured
- [ ] Authentication enabled
- [ ] Rate limiting active
- [ ] Monitoring/logging set up
- [ ] Backup workflow exported

---

## Support

For n8n-specific issues:
- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)

For this workflow:
- See [README.md](./README.md)
- Check [examples/](./examples/)
