# 🎯 START HERE - Run Fees Explainer in n8n

**Welcome! This guide gets you running in 5 minutes.**

---

## 🚀 Quick Start (Choose Your Path)

### **Path 1: n8n Only (Recommended - Easiest)** ⭐

**No Python needed. Everything runs in n8n.**

1. **Install n8n:**
   ```bash
   npx n8n
   ```

2. **Open browser:** http://localhost:5678

3. **Import workflow:**
   - Click "Workflows" → "Import from File"
   - Select: `n8n_workflow_standalone.json`
   - Click "Import"

4. **Activate:**
   - Toggle "Active" (top-right, make it green)

5. **Test:**
   ```bash
   # Get webhook URL from n8n UI, then:
   curl -X POST http://localhost:5678/webhook/fees-start \
     -H "Content-Type: application/json" \
     -d '{"query": "What is ELSS exit load?"}'
   ```

**✅ That's it! See full guide:** `QUICKSTART_N8N.md`

---

### **Path 2: n8n + Python API (Advanced)**

**Better for updating fee data frequently.**

1. **Start Python API:**
   ```bash
   python api_server.py
   ```

2. **Import workflow:**
   - Use `n8n_workflow_fees_explainer.json`
   - Configure Function nodes to call `http://localhost:5000`

3. **Test complete flow**

**See full guide:** `N8N_SETUP_COMPLETE.md`

---

## 📁 File Guide

| File | What It Does |
|------|-------------|
| **`QUICKSTART_N8N.md`** | ⭐ **START HERE** - 5-minute setup for n8n |
| `n8n_workflow_standalone.json` | Import this into n8n (no Python needed) |
| `N8N_SETUP_COMPLETE.md` | Detailed n8n setup with both modes |
| `LOCAL_TESTING_GUIDE.md` | Test Python agent locally |
| `api_server.py` | Flask API for Python agent |
| `fees_explainer_agent.py` | Python agent implementation |
| `README.md` | Complete project documentation |
| `ARCHITECTURE.md` | System architecture details |

---

## 🎯 What This Does

**Input:** User query like "What is ELSS exit load?"

**Process:**
1. Detects fee scenario (ELSS, SIP, or Expense Ratio)
2. Asks 2-3 clarifying questions
3. Generates ≤6 factual bullets with official sources
4. Prepares MCP actions (Notes, Email, Audit)
5. Executes approved actions only

**Output:** Fee explanation with citations + optional MCP actions

---

## 🧪 Test Commands

### Test Python Agent:
```bash
python test_agent.py          # Run all tests
python fees_explainer_agent.py  # Run example
```

### Test API Server:
```bash
python api_server.py           # Start server
./test_api.sh                  # Run API tests
```

### Test n8n Workflow:
```bash
# See QUICKSTART_N8N.md for curl commands
```

---

## ✅ Quick Verification

After setup, check:

- [ ] All 10 Python tests pass (`python test_agent.py`)
- [ ] n8n workflow imported successfully
- [ ] Webhook returns clarifying questions
- [ ] Fee explanations have official sources
- [ ] MCP actions require approval
- [ ] Email drafts are NOT auto-sent

---

## 🎨 What Each Scenario Covers

### **1. Exit Load & ELSS Lock-in Period**
- ELSS 3-year lock-in rules
- Exit load percentages and timelines
- SIP-specific lock-in (per installment)
- Where exit load goes (back to scheme)

**Sources:** Groww, SEBI, AMFI

### **2. SIP Mandate Fees & Cancellation**
- Groww SIP fees (free!)
- Bank mandate charges
- Cancellation process (instant, free)
- Failed installment penalties
- E-mandate limits (UPI vs NACH)

**Sources:** Groww Pricing, NPCI, RBI

### **3. Expense Ratio (Direct vs Regular)**
- Direct vs Regular differences (0.5-1% lower)
- SEBI caps for equity/debt funds
- Long-term compounding impact
- How it's deducted (daily from NAV)

**Sources:** SEBI, AMFI, Groww

---

## 🔧 Customization

### Add New Fee Scenario:

Edit `n8n_workflow_standalone.json` or Python agent:

```javascript
// In n8n Function node:
custom_scenario: {
  name: 'Your New Scenario',
  clarifiers: ['Question 1?', 'Question 2?'],
  bullets: [
    {
      text: 'Fact about fees...',
      source: 'https://official-source.com',
      tags: []
    }
  ],
  last_checked: '2025-12-15'
}
```

### Update Existing Fees:

1. Edit the fee knowledge base
2. Update `last_checked` date
3. Save and test

---

## 📊 Monitoring

### View n8n Executions:
1. Open n8n UI
2. Click "Executions" tab
3. See all webhook calls and results

### Check Output Files:
```bash
# Notes file
cat /home/user/fees_explanations.md

# Email drafts
ls /home/user/email_drafts/

# Audit log
cat /home/user/audit_log.jsonl
```

---

## 🚨 Troubleshooting

### "ModuleNotFoundError"
```bash
cd /home/user/Project-3
python test_agent.py
```

### "Webhook not found"
- Ensure workflow is Active (green toggle)
- Use Production URL from webhook node

### "Permission denied on files"
```bash
mkdir -p /home/user/email_drafts
touch /home/user/fees_explanations.md
chmod 644 /home/user/fees_explanations.md
```

### "Port already in use"
```bash
# Kill process on port
lsof -i :5678
kill -9 <PID>
```

---

## 🎓 Learning Path

**New to this?** Follow in order:

1. ✅ Read this file (you're here!)
2. ✅ `QUICKSTART_N8N.md` - Set up n8n
3. ✅ `README.md` - Understand the project
4. ✅ `ARCHITECTURE.md` - Deep dive into design
5. ✅ `N8N_SETUP_COMPLETE.md` - Production setup

**Want to customize?**
- Modify fee scenarios in workflow
- Add new MCP actions
- Integrate with Slack/Telegram

**Going to production?**
- Enable authentication
- Set up monitoring
- Configure rate limiting
- Enable SSL/HTTPS

---

## 📞 Support

- **n8n Issues:** [n8n Community](https://community.n8n.io/)
- **Project Issues:** Check the README.md
- **Fee Data Updates:** Edit knowledge base in workflow

---

## 🎉 Success Metrics

You'll know it's working when:

✅ Webhook returns clarifying questions
✅ Explanations have ≤6 bullets
✅ Every bullet has an official source URL
✅ MCP actions require approval
✅ Email drafts are created (NOT sent)
✅ All sources are SEBI/AMFI/Groww/AMC

---

## 🚀 Next Steps

1. **Complete Quick Start** (5 min)
2. **Test all 3 scenarios** (10 min)
3. **Customize for your needs** (30 min)
4. **Integrate with your app** (varies)
5. **Deploy to production** (see guides)

---

**Ready? Start with:** `QUICKSTART_N8N.md` 🎯

**Questions?** Check `README.md` for full documentation.

**All files committed to:** `claude/financial-fees-agent-PO5q6`
