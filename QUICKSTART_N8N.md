# 🚀 Quick Start - Run in n8n (5 Minutes)

This is the **fastest way** to get the Fees Explainer Agent running in n8n.

---

## ⚡ Super Quick Setup

### **Step 1: Install & Start n8n (1 minute)**

Choose one:

```bash
# Option A: Using npx (no installation needed)
npx n8n

# Option B: Using npm
npm install -g n8n && n8n start

# Option C: Using Docker
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

Wait for:
```
n8n ready on port 5678
Editor is now accessible via:
http://localhost:5678/
```

---

### **Step 2: Import Workflow (30 seconds)**

1. Open browser: **http://localhost:5678**
2. Click **"Workflows"** → **"Add workflow"** → **"Import from File"**
3. Select: **`n8n_workflow_standalone.json`** (in this directory)
4. Click **"Import"**

✅ Workflow imported with all fee knowledge built-in!

---

### **Step 3: Activate Workflow (10 seconds)**

1. Click the **"Active"** toggle (top-right, make it green)
2. Workflow is now live!

---

### **Step 4: Get Webhook URLs (30 seconds)**

Click on each webhook node and copy the **Production URL**:

1. **"Webhook: Start Query"** → Copy URL (e.g., `http://localhost:5678/webhook/fees-start`)
2. **"Webhook: Receive Answers"** → Copy URL
3. **"Webhook: MCP Approvals"** → Copy URL

---

### **Step 5: Test It! (3 minutes)**

#### **Test 1: Start Conversation**

```bash
# Replace with your actual webhook URL
curl -X POST http://localhost:5678/webhook/fees-start \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ELSS exit load?"
  }'
```

**You should see:**
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

**✅ Working! Copy the `session_id` for next step.**

---

#### **Test 2: Submit Answers**

```bash
# Use session_id from above
SESSION_ID="1734234567890"

curl -X POST http://localhost:5678/webhook/fees-answers \
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

**You should see:**
```json
{
  "status": "explanation_ready",
  "explanation": {
    "scenario": "Exit Load & ELSS Lock-in Period",
    "last_checked": "2025-12-15",
    "fee_details": [
      {
        "text": "ELSS funds have a mandatory 3-year lock-in period as per Section 80C...",
        "source": "https://groww.in/p/tax-saving-funds/"
      },
      // ... 5 more bullets
    ],
    "disclaimer": "This information is based on official sources..."
  },
  "mcp_actions_pending_approval": [
    {"action_id": 0, "action_type": "notes", "summary": "Add notes entry..."},
    {"action_id": 1, "action_type": "email", "summary": "Draft email..."},
    {"action_id": 2, "action_type": "audit", "summary": "Log audit entry..."}
  ]
}
```

**✅ Got the fee explanation with sources!**

---

#### **Test 3: Approve MCP Actions**

```bash
curl -X POST http://localhost:5678/webhook/fees-approvals \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"approved_actions\": [
      {\"action_id\": 0, \"action_type\": \"notes\", \"approved\": true},
      {\"action_id\": 1, \"action_type\": \"email\", \"approved\": true},
      {\"action_id\": 2, \"action_type\": \"audit\", \"approved\": true}
    ]
  }"
```

**You should see:**
```json
{
  "status": "mcp_actions_executed",
  "results": {
    "executed": [
      {"action_type": "notes", "status": "success", "message": "Notes entry added..."},
      {"action_type": "email", "status": "success", "message": "Email draft created...", "auto_sent": false},
      {"action_type": "audit", "status": "success", "message": "Audit entry logged..."}
    ]
  }
}
```

**✅ All MCP actions executed!**

---

## 🎉 Success! You're Running!

The agent is now fully operational in n8n with:
- ✅ 3 fee scenarios (ELSS, SIP, Expense Ratio)
- ✅ Clarifying questions
- ✅ Factual explanations with official sources
- ✅ Approval-gated MCP actions
- ✅ No Python required (all logic in n8n)

---

## 🔍 View Execution in n8n UI

1. Go to **http://localhost:5678**
2. Click on your workflow
3. Click **"Executions"** tab (bottom)
4. Click on any execution to see:
   - Input data
   - Output from each node
   - Execution path
   - Success/error status

---

## 🧪 Test Other Scenarios

### **SIP Mandate Fees:**
```bash
curl -X POST http://localhost:5678/webhook/fees-start \
  -H "Content-Type: application/json" \
  -d '{"query": "What are SIP cancellation charges?"}'
```

### **Expense Ratio:**
```bash
curl -X POST http://localhost:5678/webhook/fees-start \
  -H "Content-Type: application/json" \
  -d '{"query": "Direct vs Regular plan expense ratio?"}'
```

---

## 📊 Workflow Visual

```
┌─────────────────────┐
│  User sends query   │
│  "ELSS exit load?"  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│ Webhook: Start Query        │
│ http://localhost:5678/      │
│ webhook/fees-start          │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Detect Scenario                  │
│ Keywords → ELSS/SIP/Expense      │
│ Load clarifying questions        │
└──────────┬───────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Response: Send Clarifiers       │
│ Returns 3 questions + session   │
└─────────────────────────────────┘

           ... User answers ...

┌─────────────────────────────────┐
│ Webhook: Receive Answers        │
│ http://localhost:5678/          │
│ webhook/fees-answers            │
└──────────┬──────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Process Answers                  │
│ Filter bullets (≤6)              │
│ Add citations                    │
│ Prepare MCP actions              │
└──────────┬───────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Response: Send Explanation      │
│ Fee details + MCP for approval  │
└─────────────────────────────────┘

           ... User approves ...

┌─────────────────────────────────┐
│ Webhook: MCP Approvals          │
│ http://localhost:5678/          │
│ webhook/fees-approvals          │
└──────────┬──────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Split Approved Actions           │
│ One output per approved action   │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Switch: Action Type              │
│ Route to handler                 │
└───┬──────────┬─────────┬─────────┘
    │          │         │
    ▼          ▼         ▼
┌────────┐ ┌───────┐ ┌───────┐
│ Notes  │ │ Email │ │ Audit │
│ Handler│ │ Draft │ │  Log  │
└───┬────┘ └───┬───┘ └───┬───┘
    │          │         │
    └──────────┴─────────┘
               │
               ▼
┌─────────────────────────────────┐
│ Response: Execution Complete    │
│ Returns results                 │
└─────────────────────────────────┘
```

---

## 🎯 What's Next?

### **Customize Fee Data:**
1. In n8n, click **"Detect Scenario & Load Clarifiers"** node
2. Edit the `feeScenarios` object
3. Add/modify bullets, sources, clarifiers
4. Save workflow

### **Add More Scenarios:**
```javascript
// In the feeScenarios object, add:
dp_charges: {
  name: 'Demat Account DP Charges',
  clarifiers: [
    'Do you have a demat account?',
    'What type of transaction?'
  ],
  bullets: [
    {
      text: 'Groww charges ₹0 for opening demat account',
      source: 'https://groww.in/pricing/',
      tags: []
    }
    // ... more bullets
  ],
  last_checked: '2025-12-15'
}
```

### **Integrate with Other Apps:**

Add nodes before/after webhooks:
- **Telegram** - Chat bot integration
- **Slack** - Slash commands
- **WhatsApp** - Via Twilio
- **Email** - Incoming email triggers
- **Google Sheets** - Log queries
- **Airtable** - Store conversations

---

## 🐛 Troubleshooting

### **Problem: Webhook returns 404**
✅ Ensure workflow is **Active** (green toggle)
✅ Use **Production URL**, not Test URL
✅ Check webhook path in browser address

### **Problem: "Execution failed"**
✅ Click on the failed node
✅ View error in the output panel
✅ Check **Executions** tab for details

### **Problem: Can't access localhost:5678**
✅ Check n8n is running (`ps aux | grep n8n`)
✅ Try `http://127.0.0.1:5678` instead
✅ Check firewall isn't blocking port 5678

---

## 📚 Resources

- **Full Setup Guide:** `N8N_SETUP_COMPLETE.md`
- **Architecture Details:** `ARCHITECTURE.md`
- **Testing Guide:** `LOCAL_TESTING_GUIDE.md`
- **n8n Docs:** https://docs.n8n.io/

---

## ✅ Verification Checklist

After setup, verify:

- [ ] n8n is running and accessible
- [ ] Workflow imported successfully
- [ ] Workflow is Active (green toggle)
- [ ] All 3 webhooks have URLs
- [ ] Test 1 (start query) works
- [ ] Test 2 (submit answers) works
- [ ] Test 3 (approve MCP) works
- [ ] Can see executions in n8n UI
- [ ] All fee scenarios work (ELSS, SIP, Expense Ratio)

---

**🎉 You're all set! The Fees Explainer Agent is running in n8n!**

For production deployment, see `N8N_SETUP_COMPLETE.md` for security, monitoring, and scaling tips.
