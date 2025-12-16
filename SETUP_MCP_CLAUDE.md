# MCP Server Setup for Claude Desktop

Complete guide to connect the Financial Fees Explainer MCP server to Claude Desktop.

---

## 📋 Overview

This MCP server provides Claude with tools to:
- **Save fee explanations** to Google Sheets
- **Create documentation** in Google Docs
- **Draft emails** in Gmail (never auto-sends)
- **Log audit trails** for compliance

**All actions are approval-gated** - Claude will ask for permission before executing.

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd /home/user/Project-3
pip install -r requirements.txt
```

### Step 2: Set Up Google Credentials

Follow the detailed instructions:

```bash
python setup_google_credentials.py
```

This will show you how to:
1. Create a Google Cloud Project
2. Enable required APIs (Sheets, Docs, Gmail)
3. Download OAuth credentials
4. Create a Google Sheet for data storage

After downloading `credentials.json`, run:

```bash
python setup_google_credentials.py --auth
```

This opens your browser for OAuth and creates `token.json`.

### Step 3: Configure Environment

Create a `.env` file:

```bash
FEES_EXPLAINER_SPREADSHEET_ID=your_spreadsheet_id_from_step_2
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
```

### Step 4: Configure Claude Desktop

**Location of Claude Desktop config:**

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Add this to your config:**

```json
{
  "mcpServers": {
    "groww-fees-explainer": {
      "command": "python",
      "args": [
        "/home/user/Project-3/google_mcp_server.py"
      ],
      "env": {
        "FEES_EXPLAINER_SPREADSHEET_ID": "YOUR_SPREADSHEET_ID",
        "GOOGLE_CREDENTIALS_PATH": "/home/user/Project-3/credentials.json",
        "GOOGLE_TOKEN_PATH": "/home/user/Project-3/token.json"
      }
    }
  }
}
```

**Important:** Replace paths and `YOUR_SPREADSHEET_ID` with your actual values.

### Step 5: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. The MCP server should connect automatically

---

## ✅ Verify Connection

In Claude Desktop, ask:

```
What MCP tools do you have access to?
```

You should see:
- `append_to_google_sheets`
- `create_google_doc`
- `create_gmail_draft`
- `log_audit_entry`

---

## 💡 Example Usage

### Example 1: Ask About ELSS Exit Load

**You:**
> I want to understand ELSS exit load and lock-in period. I'm planning to invest via SIP.

**Claude will:**
1. Ask 2-3 clarifying questions (fund type, investment period, etc.)
2. Generate a structured explanation with official sources
3. **Ask for your approval** before:
   - Saving to Google Sheets
   - Creating a Google Doc
   - Drafting an email to support
   - Logging an audit entry

**You approve**, and Claude executes the approved actions.

### Example 2: SIP Mandate Fees

**You:**
> What fees do I pay for setting up and cancelling SIP?

**Claude will:**
1. Ask clarifiers (bank, SIP amount, action type)
2. Provide factual explanation with sources
3. Request approval for MCP actions
4. Execute approved actions

---

## 🔧 Troubleshooting

### Server Not Connecting

**Check logs:**
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`

**Common issues:**
1. **Python not found**: Ensure Python 3.8+ is in PATH
2. **Module not found**: Run `pip install -r requirements.txt`
3. **Invalid credentials**: Re-run `python setup_google_credentials.py --auth`
4. **Wrong paths**: Use absolute paths in claude_desktop_config.json

### Google API Errors

**"Spreadsheet not found":**
- Verify `FEES_EXPLAINER_SPREADSHEET_ID` is correct
- Check the Google account used matches the OAuth token
- Ensure the spreadsheet exists and is accessible

**"Insufficient permissions":**
- Re-run OAuth flow: `python setup_google_credentials.py --auth`
- Ensure all required APIs are enabled in Google Cloud Console

### OAuth Issues

**"Access blocked":**
- Add your email as a test user in OAuth consent screen
- Verify app is not in production mode (should be testing)

**"Token expired":**
- Delete `token.json`
- Re-run: `python setup_google_credentials.py --auth`

---

## 🎯 MCP Tools Reference

### 1. append_to_google_sheets

**Purpose:** Save fee explanation to Google Sheets
**Approval:** Required
**Parameters:**
- `entry_title`: Title of the entry
- `scenario`: Fee scenario name
- `clarifiers`: Q&A from clarification phase
- `fee_details`: Array of `{text, source}` bullets
- `last_checked`: Verification date

**Result:** Adds a row to the "Fee Explanations" sheet

### 2. create_google_doc

**Purpose:** Create formatted documentation in Google Docs
**Approval:** Required
**Parameters:**
- `doc_title`: Document title
- `scenario`: Fee scenario
- `fee_details`: Bullet points with citations
- `last_checked`: Verification date

**Result:** Creates a Google Doc with formatted content, returns URL

### 3. create_gmail_draft

**Purpose:** Draft email to support/advisor (never auto-sends)
**Approval:** Required
**Parameters:**
- `to`: Recipient email (e.g., support@groww.in)
- `subject`: Email subject
- `body`: Email body with fee details

**Result:** Creates draft in Gmail, does NOT send

### 4. log_audit_entry

**Purpose:** Log compliance trail to Google Sheets
**Approval:** Required
**Parameters:**
- `who`: Entity performing action (e.g., "FeesExplainerAgent")
- `action`: Action description
- `details`: Additional metadata (optional)

**Result:** Adds entry to "Audit Log" sheet with timestamp

---

## 📁 Project Structure

```
Project-3/
├── google_mcp_server.py           # MCP server with Google APIs
├── setup_google_credentials.py    # Setup script
├── claude_desktop_config.json     # Example Claude config
├── requirements.txt               # Python dependencies
├── fees_explainer_agent.py        # Agent logic (standalone)
├── credentials.json               # OAuth credentials (you create)
├── token.json                     # OAuth token (auto-generated)
└── .env                          # Environment variables
```

---

## 🔒 Security & Compliance

### Data Privacy
- **No PII collection**: Agent asks only product-related questions
- **Local credentials**: OAuth tokens stored locally, never transmitted
- **Approval-gated**: All actions require explicit user consent

### Sources
- **Official only**: SEBI, AMFI, AMC factsheets, Groww help pages
- **Citations required**: Every bullet point has a source URL
- **Date stamped**: "Last checked" date for verification

### Email Safety
- **Draft only**: Emails are NEVER auto-sent
- **Review required**: User must manually send from Gmail
- **No automation**: No scheduled or bulk sending

---

## 🎓 Fee Scenarios Covered

### 1. Exit Load & ELSS Lock-in
- ELSS 3-year lock-in period
- Exit load for equity funds (typically 1% if <1 year)
- SIP vs lumpsum implications
- Source: SEBI/AMFI/Groww

### 2. SIP Mandate Fees
- Platform fees (Groww: ₹0)
- Bank e-mandate charges
- Failed installment penalties
- Source: Groww Pricing, NPCI guidelines

### 3. Expense Ratio
- Direct vs Regular plan differences
- SEBI caps by fund category
- Long-term impact calculation
- Source: SEBI circulars, AMFI

---

## 📞 Support

**MCP Server Issues:**
- Check logs in Claude Desktop logs folder
- Verify Python version: `python --version` (need 3.8+)
- Test server standalone: `python google_mcp_server.py`

**Google API Issues:**
- Verify APIs are enabled in Cloud Console
- Check OAuth consent screen is configured
- Ensure scopes match (Sheets, Docs, Gmail)

**Agent Logic:**
- See `fees_explainer_agent.py` for scenario definitions
- Modify fee knowledge base to add scenarios
- Update source URLs as needed

---

## 🔄 Updates

**Updating fee information:**
1. Edit `fees_explainer_agent.py`
2. Update bullet points and sources
3. Change `last_checked` date
4. Restart Claude Desktop

**Adding new scenarios:**
1. Add to `fee_knowledge_base` in agent
2. Define clarifiers and bullets
3. Add official source URLs
4. Test with Claude

---

## ✨ Example Claude Conversation

```
You: I want to know about ELSS lock-in and exit load

Claude: I can help explain ELSS fees and lock-in periods. Let me ask a few
clarifying questions:

1. Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?
2. Do you plan to redeem within 1 year of investment?
3. Is this a lumpsum investment or SIP?

You: ELSS, No I'll invest for 5+ years, SIP

Claude: Here's the fee explanation for ELSS with SIP:

**Scenario:** Exit Load & ELSS Lock-in Period
**Last Checked:** 2025-12-15

**Fee Details:**

1. ELSS funds have a mandatory 3-year lock-in period as per Section 80C...
   📎 Source: https://groww.in/p/tax-saving-funds/

2. For SIP investments in ELSS, each installment has a separate 3-year lock-in...
   📎 Source: https://groww.in/p/tax-saving-funds/

[...4 more bullets with sources...]

I'd like to perform these actions (requires your approval):
- Save this explanation to your Google Sheet
- Create a Google Doc with formatted details
- Draft an email to support@groww.in for confirmation
- Log this interaction in the audit trail

May I proceed with these actions?

You: Yes, approve all

Claude: ✅ All actions completed:
- Added entry to Google Sheets: "Fee Explanation: Exit Load & ELSS"
- Created Google Doc: [link]
- Gmail draft created (not sent): "Fee Clarification Request: Exit Load & ELSS"
- Audit entry logged: 2025-12-16T10:30:00Z

You can review the draft in Gmail and send it manually if needed.
```

---

## 🎯 Next Steps

1. ✅ Complete Google API setup
2. ✅ Configure Claude Desktop
3. ✅ Test with a simple query
4. ✅ Review generated Google Sheet/Doc
5. ✅ Verify Gmail draft creation
6. 🚀 Use for real fee clarifications!

---

**Happy explaining! 💰📊**
