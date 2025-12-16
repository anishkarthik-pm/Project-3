# Groww Mutual Funds - Fees Explainer Agent

AI agent that explains mutual fund fees using official sources only.

---

## 🚀 Quick Start

### 🎯 Option 1: MCP Server for Claude Desktop (RECOMMENDED)

**Connect directly to Claude Desktop** with Google Sheets, Docs, and Gmail integration.

**Setup (5 minutes):**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up Google credentials
python setup_google_credentials.py

# 3. Follow the guided setup, then run auth
python setup_google_credentials.py --auth

# 4. Configure Claude Desktop
# See: SETUP_MCP_CLAUDE.md for complete instructions
```

**Features:**
- ✅ Save explanations to Google Sheets
- ✅ Create docs in Google Docs
- ✅ Draft emails in Gmail (approval-gated)
- ✅ Compliance audit logging
- ✅ Works directly with Claude Desktop

**Documentation:** See [`SETUP_MCP_CLAUDE.md`](SETUP_MCP_CLAUDE.md)

---

### Option 2: n8n Chat Flow

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

### Option 3: Python API

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
| **MCP Server (Claude Desktop)** | |
| `google_mcp_server.py` | **MCP server with Google APIs** |
| `SETUP_MCP_CLAUDE.md` | **Complete setup guide** |
| `setup_google_credentials.py` | Google auth setup script |
| `claude_desktop_config.json` | Example Claude config |
| `agent_prompt.md` | Agent behavior guide |
| **n8n Workflow** | |
| `fees_explainer_chat_flow.json` | n8n workflow file |
| `SIMPLE_IMPORT.md` | n8n setup guide |
| **Python Components** | |
| `fees_explainer_agent.py` | Core agent logic |
| `api_server.py` | Flask API server |
| `mcp_handlers.py` | Local MCP tools |
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
