# Complete n8n Setup Guide - Fees Explainer Agent

> Step-by-step guide to run the Fees Explainer Agent as a complete n8n workflow

---

## 🎯 Overview

This guide shows you how to run the entire Fees Explainer Agent inside n8n with two approaches:

1. **Standalone n8n** - All logic inside n8n (no Python required)
2. **n8n + Python API** - n8n calls Python agent via HTTP

We'll start with the standalone approach for simplicity.

---

## 📦 Prerequisites

- **n8n** installed (npm, Docker, or n8n Cloud)
- **Node.js** 16+ (if installing via npm)
- **OR** Docker (for containerized setup)

---

## 🚀 Quick Start (5 Steps)

### Step 1: Install n8n

Choose one method:

#### **Option A: Using npm (Recommended)**
```bash
# Install n8n globally
npm install -g n8n

# Start n8n
n8n start
```

#### **Option B: Using npx (No Installation)**
```bash
# Run directly without installing
npx n8n
```

#### **Option C: Using Docker**
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

#### **Option D: n8n Cloud**
Sign up at https://n8n.io/cloud

**Expected Output:**
```
n8n ready on port 5678
Editor is now accessible via:
http://localhost:5678/
```

---

### Step 2: Access n8n Editor

Open browser and go to:
```
http://localhost:5678
```

First time users will see a setup wizard:
1. Set up admin email and password
2. Click "Continue" through the welcome screens

---

### Step 3: Import the Workflow

1. Click **"Workflows"** in the left sidebar
2. Click **"Add Workflow"** dropdown → **"Import from File"**
3. Select: `/home/user/Project-3/n8n_workflow_fees_explainer.json`
4. Click **"Import"**

The workflow will appear with all nodes connected.

---

### Step 4: Configure Webhook Nodes

The workflow has 3 webhook triggers. n8n will auto-generate URLs.

#### **Find Webhook URLs:**

1. Click on the **"Webhook Trigger - User Query"** node
2. Look for **"Production URL"** or **"Test URL"**
3. Copy the URL (e.g., `http://localhost:5678/webhook/abc123`)

Note down all 3 webhook URLs:
```
Start:     http://localhost:5678/webhook/[ID-1]
Answers:   http://localhost:5678/webhook/[ID-2]
Approvals: http://localhost:5678/webhook/[ID-3]
```

---

### Step 5: Activate the Workflow

1. Click the **"Active"** toggle in the top-right corner
2. The toggle should turn green
3. Workflow is now live!

---

## 🧪 Test the Workflow

### Test 1: Start Conversation

```bash
# Replace [WEBHOOK-ID] with your actual webhook ID
curl -X POST http://localhost:5678/webhook/[WEBHOOK-ID] \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ELSS exit load?"
  }'
```

**Expected Response:**
```json
{
  "status": "clarifiers_required",
  "scenario": "Exit Load & ELSS Lock-in Period",
  "questions": [
    "Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?",
    "Do you plan to redeem within 1 year of investment?",
    "Is this a lumpsum investment or SIP?"
  ],
  "session_id": "1734234567890"
}
```

### Test 2: Submit Answers

```bash
# Use the session_id from previous response
curl -X POST http://localhost:5678/webhook/[WEBHOOK-ID-2] \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "1734234567890",
    "answers": {
      "Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?": "ELSS",
      "Do you plan to redeem within 1 year of investment?": "No, after 3 years",
      "Is this a lumpsum investment or SIP?": "SIP"
    }
  }'
```

**Expected Response:**
```json
{
  "status": "explanation_ready",
  "explanation": {
    "scenario": "Exit Load & ELSS Lock-in Period",
    "last_checked": "2025-12-15",
    "fee_details": [
      {
        "text": "ELSS funds have a mandatory 3-year lock-in period...",
        "source": "https://groww.in/p/tax-saving-funds/"
      }
      // ... more bullets
    ]
  },
  "mcp_actions_pending_approval": [...]
}
```

### Test 3: Approve MCP Actions

```bash
curl -X POST http://localhost:5678/webhook/[WEBHOOK-ID-3] \
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

---

## 🔧 Workflow Configuration - Two Modes

### **Mode 1: Standalone n8n (Simpler)**

All logic runs inside n8n Function nodes. No external dependencies.

**Pros:**
- No Python server needed
- Faster setup
- All logic in one place

**Cons:**
- Fee data is static in the workflow
- Harder to update fee information

### **Mode 2: n8n + Python API (Recommended for Production)**

n8n calls the Python agent via HTTP.

**Pros:**
- Centralized fee knowledge base
- Easy to update fees
- Reusable across platforms

**Cons:**
- Requires Python API server running
- More moving parts

---

## 📝 Mode 1: Standalone Setup (Current Workflow)

The imported workflow already has all logic in Function nodes.

### **Key Nodes Explained:**

#### **1. Webhook Trigger - User Query**
- **Type:** Webhook
- **Path:** Auto-generated
- **Method:** POST
- **Action:** Receives user query

#### **2. Initialize Agent (Function Node)**
```javascript
// This node detects scenario and loads clarifiers
const userQuery = $input.item.json.query;

function detectScenario(query) {
  const q = query.toLowerCase();
  if (q.includes('exit load') || q.includes('elss') || q.includes('lock')) {
    return 'Exit Load & ELSS Lock-in Period';
  } else if (q.includes('sip') || q.includes('mandate')) {
    return 'SIP Mandate Fees & Cancellation';
  } else {
    return 'Expense Ratio (Direct vs Regular Plans)';
  }
}

const scenario = detectScenario(userQuery);
// ... loads clarifiers based on scenario
```

#### **3. Process Answers (Function Node)**
```javascript
// Filters relevant bullets based on answers
// Generates explanation with citations
// Prepares MCP actions
```

#### **4. Switch Node - Route MCP Actions**
Routes each approved action to the correct handler:
- `action_type == 'notes'` → Notes Handler
- `action_type == 'email'` → Email Handler
- `action_type == 'audit'` → Audit Handler

---

## 🔌 Mode 2: Connect to Python API

If you want to use the Python agent:

### Step 1: Start Python API Server

```bash
# Terminal 1 - Start Python server
cd /home/user/Project-3
python api_server.py
```

### Step 2: Update Function Nodes in n8n

#### Update "Initialize Agent" Node:

1. Click on the **"Initialize Agent"** node
2. Replace the code with:

```javascript
// Call Python API instead of local logic
const response = await this.helpers.httpRequest({
  method: 'POST',
  url: 'http://localhost:5000/api/fees-explainer/start',
  body: {
    query: $input.item.json.query
  },
  json: true
});

return {
  json: response
};
```

#### Update "Process Answers" Node:

```javascript
const response = await this.helpers.httpRequest({
  method: 'POST',
  url: 'http://localhost:5000/api/fees-explainer/answers',
  body: {
    session_id: $input.item.json.session_id,
    answers: $input.item.json.answers
  },
  json: true
});

return {
  json: response
};
```

#### Update MCP Execution Nodes:

For each MCP handler (Notes, Email, Audit), update to call Python API:

```javascript
const response = await this.helpers.httpRequest({
  method: 'POST',
  url: 'http://localhost:5000/api/fees-explainer/approvals',
  body: {
    session_id: $input.item.json.session_id,
    approved_actions: $input.item.json.approved_actions
  },
  json: true
});

return {
  json: response
};
```

---

## 📊 Testing Inside n8n UI

### Manual Execution:

1. Click on a workflow node
2. Click **"Execute Node"** button in the top bar
3. Provide test data in the input panel
4. Click **"Execute"**
5. View output in the right panel

### Example Test Data:

For **"Webhook Trigger"** node:
```json
{
  "query": "What is ELSS exit load?"
}
```

For **"Process Answers"** node:
```json
{
  "session_id": "1734234567890",
  "answers": {
    "Are you asking about ELSS or non-ELSS?": "ELSS",
    "Do you plan to redeem within 1 year?": "No",
    "Is this lumpsum or SIP?": "SIP"
  }
}
```

---

## 🔍 Debugging Tips

### View Execution Data:

1. Click on any node
2. Click **"Executions"** tab (bottom panel)
3. Select a past execution
4. View input/output data for each node

### Enable Debugging:

1. Go to **Settings** → **Executions**
2. Enable **"Save manual executions"**
3. Enable **"Save executions on error"**

### Check Logs:

```bash
# If running via npm
tail -f ~/.n8n/logs/n8n.log

# If running via Docker
docker logs -f n8n
```

---

## 🎨 Customizing the Workflow

### Add New Fee Scenario:

1. Click on **"Initialize Agent"** Function node
2. Add to the `scenarios` object:

```javascript
const scenarios = {
  'exit_load_elss': { /* ... */ },
  'sip_mandate_fees': { /* ... */ },
  'expense_ratio': { /* ... */ },

  // NEW SCENARIO
  'dp_charges': {
    name: 'Demat Account DP Charges',
    clarifiers: [
      'Do you have a demat account with Groww?',
      'What type of transaction: Buy or Sell?',
      'Is it equity or mutual fund?'
    ],
    bullets: [
      {
        text: 'Groww charges ₹0 for opening demat account...',
        source: 'https://groww.in/pricing/'
      }
      // ... more bullets
    ]
  }
};
```

### Modify MCP Actions:

Add/remove MCP actions in the **"Process Answers"** node:

```javascript
const mcpActions = [
  // Existing actions
  { action_type: 'notes', ... },
  { action_type: 'email', ... },
  { action_type: 'audit', ... },

  // NEW ACTION
  {
    action_id: 3,
    action_type: 'slack_notification',
    summary: 'Send Slack notification to support team',
    payload: {
      channel: '#support',
      message: `New fee query: ${scenario}`
    }
  }
];
```

Then add a new route in the **Switch** node and create a Slack handler.

---

## 🚨 Common Issues & Solutions

### Issue 1: Webhook Returns 404

**Problem:** Webhook URL not found

**Solution:**
- Ensure workflow is **Active** (green toggle)
- Use **Production URL**, not Test URL
- Check webhook path matches

### Issue 2: Function Node Errors

**Problem:** `ReferenceError: variable is not defined`

**Solution:**
- Check all variables are declared
- Use `const`, `let`, or `var`
- Verify JSON structure with `JSON.stringify()`

### Issue 3: HTTP Request Fails

**Problem:** Cannot connect to Python API

**Solution:**
```bash
# Check Python server is running
curl http://localhost:5000/health

# If not, start it
python api_server.py
```

### Issue 4: MCP Files Not Created

**Problem:** Files not appearing in filesystem

**Solution:**
```bash
# Create directories first
mkdir -p /home/user/email_drafts
touch /home/user/fees_explanations.md
touch /home/user/audit_log.jsonl

# Check permissions
chmod 644 /home/user/fees_explanations.md
```

---

## 📱 Integration Examples

### Integrate with Telegram Bot:

1. Add **Telegram Trigger** node before "Initialize Agent"
2. Extract message text:
```javascript
const query = $input.item.json.message.text;
return { json: { query } };
```

3. Add **Telegram** node after responses to send messages back

### Integrate with Slack:

1. Add **Slack Trigger** node
2. Use slash command: `/fees-explainer ELSS exit load`
3. Send responses back to Slack channel

### Integrate with WhatsApp (via Twilio):

1. Add **Webhook** node for Twilio incoming messages
2. Process queries
3. Use **HTTP Request** node to send Twilio API response

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] All webhooks tested with real requests
- [ ] Error handling added to Function nodes
- [ ] Timeout configured (Settings → Executions → Timeout)
- [ ] Credentials secured (use n8n Credentials feature)
- [ ] Rate limiting enabled (prevent abuse)
- [ ] Monitoring/alerting set up
- [ ] Backup workflow exported (JSON)
- [ ] Documentation updated with webhook URLs
- [ ] Load tested with concurrent requests
- [ ] SSL/HTTPS enabled for webhooks

---

## 📈 Monitoring & Analytics

### Track Usage:

Add a **Set** node before final response:

```javascript
// Log metrics
return {
  json: {
    ...existingData,
    metrics: {
      timestamp: new Date().toISOString(),
      scenario: $input.item.json.scenario,
      session_id: $input.item.json.session_id,
      mcp_actions_approved: $input.item.json.approved_actions.length
    }
  }
};
```

Then pipe to:
- **Google Sheets** (for simple tracking)
- **Airtable** (structured database)
- **Postgres** (production database)
- **Webhook** (to your analytics service)

---

## 🔐 Security Best Practices

### 1. Add Authentication:

In webhook settings:
- Enable **Basic Auth** or **Header Auth**
- Set credentials in n8n Credentials store

### 2. Validate Input:

Add validation node before processing:

```javascript
const query = $input.item.json.query;

// Validate query
if (!query || query.length < 5 || query.length > 500) {
  throw new Error('Invalid query length');
}

// Sanitize input
const sanitized = query.replace(/<[^>]*>/g, ''); // Remove HTML tags

return { json: { query: sanitized } };
```

### 3. Rate Limiting:

Use **RateLimit** node or add to Function:

```javascript
// Simple in-memory rate limit
const rateLimits = {};
const ip = $input.item.json.headers['x-forwarded-for'];
const now = Date.now();

if (rateLimits[ip] && now - rateLimits[ip] < 60000) {
  throw new Error('Rate limit exceeded. Try again in 1 minute.');
}

rateLimits[ip] = now;
```

---

## 📚 Additional Resources

- **n8n Documentation:** https://docs.n8n.io/
- **n8n Community:** https://community.n8n.io/
- **Workflow Templates:** https://n8n.io/workflows/
- **YouTube Tutorials:** Search "n8n tutorial"

---

## 🎓 Next Steps

1. ✅ **Complete this setup guide**
2. ✅ **Test all 3 fee scenarios**
3. ✅ **Customize fee data for your needs**
4. ✅ **Add your own integrations (Slack, Telegram, etc.)**
5. ✅ **Deploy to production n8n instance**
6. ✅ **Set up monitoring and alerts**

---

**You're now ready to run the Fees Explainer Agent in n8n! 🚀**

For questions, refer to the main `README.md` or check the n8n community forums.
