# n8n Import Fix - Use This Workflow

## ✅ Problem Solved!

The original `n8n_workflow_standalone.json` had JSON parsing errors.

**Use this instead:** **`n8n_fees_explainer_working.json`**

---

## 🚀 Quick Import (30 Seconds)

### 1. Start n8n
```bash
npx n8n
# Opens at http://localhost:5678
```

### 2. Import the Working File

1. Go to **http://localhost:5678**
2. Click **Workflows** → **Add workflow** → **Import from File**
3. Select: **`n8n_fees_explainer_working.json`** ✅
4. Click **Import**

**✓ Will import successfully!**

### 3. Activate
Click the **"Active"** toggle (top-right, make it green)

### 4. Get Webhook URL
- Click the **"Webhook: Start Query"** node
- Copy the **Production URL** (e.g., `http://localhost:5678/webhook/fees-start`)

### 5. Test
```bash
curl -X POST http://localhost:5678/webhook/fees-start \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ELSS exit load?"
  }'
```

**Expected:**
```json
{
  "session_id": "1734567890123",
  "scenario": "Exit Load & ELSS Lock-in Period",
  "questions": ["...", "...", "..."],
  "fees": ["...", "...", "..."],
  "last_checked": "2025-12-15",
  "status": "clarifiers_required"
}
```

**✅ Working!**

---

## 📊 What's in This Workflow

### Current Nodes (2):

1. **Webhook: Start Query** - Receives user queries
2. **Detect Scenario** - Identifies fee scenario and returns:
   - Scenario name
   - Clarifying questions
   - Fee details with official sources
   - Last checked date

### Scenarios Covered (3):

- **Exit Load & ELSS** - Lock-in periods, exit loads
- **SIP Mandate Fees** - Setup/cancellation charges
- **Expense Ratio** - Direct vs Regular plans

---

## 🔧 Extend the Workflow

### Add More Nodes

Edit `generate_workflow.py` and add nodes to the `nodes` array:

```python
# Add a new node
{
    "parameters": {
        "mode": "runOnceForAllItems",
        "jsCode": "// Your code here"
    },
    "id": "my_new_node",
    "name": "My New Node",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [680, 300]
}
```

Then regenerate:
```bash
python generate_workflow.py
```

### Add More Scenarios

In the `Detect Scenario` code node, edit the `scenarios` object:

```javascript
const scenarios = {
  // Existing scenarios...

  // NEW SCENARIO
  dp_charges: {
    name: 'Demat Account DP Charges',
    questions: [
      'Do you have a demat account?',
      'Buy or Sell transaction?'
    ],
    fees: [
      'Groww charges ₹0 for demat account opening (https://groww.in/pricing/)',
      'DP charges: ₹20 per stock sold (https://groww.in/pricing/)'
    ]
  }
};
```

---

## 🐛 Troubleshooting

### "Could not import file" Error

**Problem:** Using the wrong file

**Solution:**
✅ Use: `n8n_fees_explainer_working.json`
❌ Don't use: `n8n_workflow_standalone.json` (has errors)

### Webhook Returns 404

**Problem:** Workflow not active

**Solution:**
- Ensure workflow is **Active** (green toggle)
- Use **Production URL**, not Test URL

### Node Execution Fails

**Problem:** JavaScript error in Code node

**Solution:**
1. Click the failed node
2. View error in output panel
3. Edit the `jsCode` parameter
4. Test with **"Execute Node"** button

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `n8n_fees_explainer_working.json` | **✅ Main workflow to import** |
| `fees_explainer_n8n_simple.json` | Minimal 2-node example |
| `generate_workflow.py` | Python script to create workflows |
| `n8n_workflow_standalone.json` | ❌ Deprecated (has JSON errors) |

---

## 🎯 Next Steps

1. ✅ **Import the working workflow**
2. ✅ **Test with curl or Postman**
3. ✅ **Add more scenarios or nodes**
4. ✅ **Customize for your needs**
5. ✅ **Deploy to production n8n**

---

## 💡 Pro Tips

### View Executions

1. Click **"Executions"** tab in n8n
2. See all webhook calls
3. Debug input/output for each node

### Manual Testing

1. Click on any node
2. Click **"Execute Node"** in toolbar
3. Provide test JSON input
4. See output immediately

### Add Integrations

Drag these nodes before/after webhooks:
- **Telegram** - Bot integration
- **Slack** - Slash commands
- **Email** - Trigger from inbox
- **Google Sheets** - Log conversations
- **HTTP Request** - Call external APIs

---

**✅ All fixed! You can now import and use the workflow in n8n.**

For the complete guide, see `QUICKSTART_N8N.md`
