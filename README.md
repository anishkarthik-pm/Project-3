# Groww Mutual Funds - Fees Explainer Agent

AI agent that explains mutual fund fees using official sources only.

---

## 🚀 Quick Start

### n8n Chat Flow (Recommended)

**1. Install n8n**
```bash
npx n8n
```

**2. Import Workflow**
- Open: http://localhost:5678
- Import: `fees_explainer_chat_flow.json`
- Add OpenAI API key
- Activate

**3. Chat**
- Click "Chat" button
- Ask: "What is ELSS exit load?"
- Agent explains with sources

See: `SIMPLE_IMPORT.md` for details

---

### Python API (Alternative)

**Start Server**
```bash
python api_server.py
```

**Test**
```bash
curl -X POST http://localhost:5000/api/fees-explainer/start \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ELSS exit load?"}'
```

**Run Tests**
```bash
python test_agent.py
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `fees_explainer_chat_flow.json` | **Import this into n8n** |
| `SIMPLE_IMPORT.md` | Setup guide |
| `fees_explainer_agent.py` | Python agent |
| `api_server.py` | Flask API |
| `mcp_handlers.py` | MCP tools |
| `test_agent.py` | Tests |

---

## 💰 Fee Scenarios

1. **Exit Load & ELSS** - Lock-in periods, exit loads
2. **SIP Mandate Fees** - Setup/cancellation charges
3. **Expense Ratio** - Direct vs Regular plans

---

## 🔒 Key Features

✅ Facts only from SEBI/AMFI/Groww
✅ No PII collection
✅ Approval-gated MCP actions
✅ Email drafts never auto-send
✅ Sources cited for every bullet

---

## 🛠️ MCP Actions

1. **Notes** - Save to markdown
2. **Email** - Draft (no auto-send)
3. **Audit** - Compliance log

All require approval.

---

## 🎯 n8n Workflow

Import `fees_explainer_chat_flow.json`:
- Chat Trigger
- AI Agent
- 3 MCP Tools

---

**Branch:** `claude/financial-fees-agent-PO5q6`
