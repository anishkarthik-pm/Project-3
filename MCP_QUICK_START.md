# MCP Server - Quick Start Guide

Get the Financial Fees Explainer MCP server running with Claude Desktop in 5 minutes.

---

## Prerequisites

- Python 3.8+
- Claude Desktop installed
- Google account

---

## 5-Minute Setup

### Step 1: Install Dependencies (1 min)

```bash
cd /home/user/Project-3
pip install -r requirements.txt
```

### Step 2: Google Cloud Setup (2 min)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Fees Explainer MCP"
3. Enable these APIs:
   - [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com)
   - [Google Docs API](https://console.cloud.google.com/apis/library/docs.googleapis.com)
   - [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)

4. Create OAuth credentials:
   - Go to [Credentials](https://console.cloud.google.com/apis/credentials)
   - Create OAuth client ID → Desktop app
   - Download as `credentials.json`
   - Save to project directory

5. Create a [Google Sheet](https://sheets.google.com)
   - Name it: "Fees Explainer Data"
   - Copy the Spreadsheet ID from URL

### Step 3: Configure Environment (1 min)

Create `.env` file:

```bash
FEES_EXPLAINER_SPREADSHEET_ID=your_spreadsheet_id_here
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
```

Run OAuth flow:

```bash
python setup_google_credentials.py --auth
```

This opens your browser to authorize the app and creates `token.json`.

### Step 4: Configure Claude Desktop (1 min)

**Find your Claude config:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Add this (update paths):**

```json
{
  "mcpServers": {
    "groww-fees-explainer": {
      "command": "python",
      "args": ["/FULL/PATH/TO/google_mcp_server.py"],
      "env": {
        "FEES_EXPLAINER_SPREADSHEET_ID": "your_spreadsheet_id",
        "GOOGLE_CREDENTIALS_PATH": "/FULL/PATH/TO/credentials.json",
        "GOOGLE_TOKEN_PATH": "/FULL/PATH/TO/token.json"
      }
    }
  }
}
```

**Important:** Use absolute paths, not relative!

### Step 5: Restart Claude Desktop

1. Quit Claude Desktop
2. Reopen Claude Desktop
3. MCP server connects automatically

---

## Verify It Works

In Claude Desktop, ask:

```
What MCP tools do you have access to?
```

You should see:
- ✅ append_to_google_sheets
- ✅ create_google_doc
- ✅ create_gmail_draft
- ✅ log_audit_entry

---

## Test the Agent

Ask Claude:

```
I want to understand ELSS exit load. I'm investing via SIP for long term.
```

Claude will:
1. Ask clarifying questions
2. Provide factual explanation with official sources
3. Ask permission to:
   - Save to Google Sheets
   - Create a Google Doc
   - Draft an email
   - Log audit trail
4. Execute approved actions

---

## Troubleshooting

### "MCP server not found"

**Check:**
- Python path is correct: `which python`
- File path is absolute, not relative
- Claude Desktop config JSON is valid

**Fix:**
```json
{
  "mcpServers": {
    "groww-fees-explainer": {
      "command": "/usr/bin/python3",  // Use absolute Python path
      "args": ["/home/user/Project-3/google_mcp_server.py"]
      // ...
    }
  }
}
```

### "Module not found"

**Fix:**
```bash
pip install -r requirements.txt
```

If using virtual env, use that Python:
```json
"command": "/path/to/venv/bin/python"
```

### "Credentials not found"

**Fix:**
```bash
# Check files exist
ls -la credentials.json token.json

# If missing credentials.json, download from Google Cloud
# If missing token.json, run auth:
python setup_google_credentials.py --auth
```

### "Spreadsheet not found"

**Fix:**
```bash
# Verify spreadsheet ID in .env
cat .env

# Make sure it's set in Claude config too
# Check the Google account matches the OAuth token
```

### "Permission denied"

**Fix:**
```bash
chmod +x google_mcp_server.py
chmod +x setup_google_credentials.py
```

---

## Example Conversation

**You:**
> What are SIP mandate fees on Groww?

**Claude:**
> I can help explain SIP mandate fees. Let me ask a few clarifying questions:
>
> 1. Are you setting up a new SIP or cancelling an existing one?
> 2. What is your bank (some banks charge for auto-debit mandates)?
> 3. Is the SIP amount above or below ₹5,000 per month?

**You:**
> Setting up new SIP, HDFC Bank, amount is ₹10,000

**Claude:**
> **Scenario:** SIP Mandate Fees & Cancellation
> **Last Checked:** 2025-12-15
>
> **Fee Details:**
>
> 1. Groww does NOT charge any fees for SIP registration...
>    📎 Source: https://groww.in/pricing/
>
> [... more bullets ...]
>
> I'd like to perform these actions:
> 1. 📊 Save to Google Sheet
> 2. 📝 Create Google Doc
> 3. ✉️ Draft email to support
> 4. 📋 Log audit entry
>
> May I proceed?

**You:**
> Yes

**Claude:**
> ✅ Actions completed:
> - Added to Google Sheets
> - Created Google Doc: [URL]
> - Gmail draft created (not sent)
> - Audit logged

---

## What You Get

After using the agent, you'll have:

1. **Google Sheet** with all fee queries organized
2. **Google Docs** with formatted explanations
3. **Gmail drafts** ready to send to support (if you want confirmation)
4. **Audit log** for compliance tracking

All with official source citations!

---

## Next Steps

- ✅ Read [`agent_prompt.md`](agent_prompt.md) to understand agent behavior
- ✅ See [`SETUP_MCP_CLAUDE.md`](SETUP_MCP_CLAUDE.md) for detailed docs
- ✅ Check [`fees_explainer_agent.py`](fees_explainer_agent.py) to customize scenarios
- ✅ Review your Google Sheet to see tracked explanations

---

**Need help?** See full documentation in `SETUP_MCP_CLAUDE.md`

**Happy fee explaining! 💰**
