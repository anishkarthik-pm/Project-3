# Import This - Simple Chat Flow

## File to Import

**`fees_explainer_chat_flow.json`** ✅

---

## What You Get

```
Chat Trigger (user types question)
    ↓
AI Agent (GPT-3.5)
    ↓
3 MCP Tools:
- Save to Notes
- Create Email Draft
- Log Audit
```

---

## Import Steps

### 1. Start n8n
```bash
npx n8n
```

### 2. Import
- Open: http://localhost:5678
- Click: **Workflows** → **Import from File**
- Select: **`fees_explainer_chat_flow.json`**
- Click: **Import**

### 3. Add OpenAI Credentials
- Click **"OpenAI Chat Model"** node
- Click **"Credentials"**
- Add your OpenAI API key
- Or change to **"Anthropic Claude"** if you prefer

### 4. Activate
- Click **"Active"** toggle

### 5. Test
- Click **"Chat"** button in top-right
- Type: "What is ELSS exit load?"
- Agent will:
  - Ask clarifying questions
  - Provide fee details with sources
  - Offer to save notes/email/audit

---

## How It Works

**User:** "What is ELSS exit load?"

**Agent:**
1. Asks 2-3 questions
2. Provides 6 bullets with sources
3. Offers: "Would you like me to save this to notes?"

**User:** "Yes, save to notes"

**Agent:** Uses `save_to_notes` tool, confirms saved

---

## Customize

### Change AI Model

Click **"OpenAI Chat Model"** node → Replace with:
- **Anthropic Claude**
- **Google Gemini**
- **Local LLM**

### Edit System Prompt

Click **"OpenAI Chat Model"** → **Options** → **System Message**

```
You are a Groww mutual fund fees expert.

Rules:
- Ask 2-3 clarifiers (no PII)
- Give ≤6 bullets with sources
- Facts only, no recommendations
- Offer MCP tools when done

Scenarios:
1. ELSS: 3-year lock-in, exit load
2. SIP: Mandate fees, cancellation
3. Expense Ratio: Direct vs Regular
```

### Add More Tools

Drag **"Tool: Code"** node → Connect to Agent

---

## Test Without OpenAI

Replace **"OpenAI Chat Model"** with **"Manual Chat Input"**:
1. Delete OpenAI node
2. Add **"Manual Chat Input"** node
3. Connect to Agent
4. Type responses manually (for testing)

---

## That's It

Simple. Complete. Works.

Import → Add API Key → Test Chat
