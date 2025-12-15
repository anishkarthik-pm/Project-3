#!/usr/bin/env python3
"""
Create a simple, working n8n workflow for Fees Explainer
"""
import json

workflow = {
    "name": "Fees Explainer - Complete Flow",
    "nodes": [
        {
            "parameters": {
                "public": True,
                "initialMessages": "Hi! I can help explain mutual fund fees. Ask me about:\n- ELSS exit load\n- SIP mandate charges\n- Expense ratios",
                "options": {}
            },
            "id": "1",
            "name": "Chat Trigger",
            "type": "@n8n/n8n-nodes-langchain.chatTrigger",
            "typeVersion": 1,
            "position": [240, 340],
            "webhookId": "fees-chat"
        },
        {
            "parameters": {
                "options": {}
            },
            "id": "2",
            "name": "Agent",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "typeVersion": 1,
            "position": [680, 340]
        },
        {
            "parameters": {
                "model": "gpt-3.5-turbo",
                "options": {
                    "systemMessage": """You are a mutual fund fees expert for Groww.

Your job:
1. Ask 2-3 clarifying questions (no personal info)
2. Provide up to 6 factual bullet points with official sources
3. Suggest MCP actions: notes, email draft, audit log

Fee Knowledge:
- ELSS: 3-year lock-in per Section 80C, exit load varies
- SIP: Groww charges ₹0, banks may charge ₹0-50 for mandate
- Expense Ratio: Direct plans 0.5-1% cheaper than Regular

Official Sources:
- https://groww.in/pricing/
- https://groww.in/blog/
- https://www.sebi.gov.in/
- https://www.amfiindia.com/

Always cite sources. No recommendations, facts only."""
                }
            },
            "id": "3",
            "name": "OpenAI Chat Model",
            "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
            "typeVersion": 1,
            "position": [680, 180]
        },
        {
            "parameters": {
                "name": "save_to_notes",
                "description": "Save fee explanation to notes file with date, scenario, and sources",
                "schema": {
                    "type": "object",
                    "properties": {
                        "scenario": {"type": "string", "description": "Fee scenario name"},
                        "explanation": {"type": "string", "description": "Fee explanation with sources"},
                        "date": {"type": "string", "description": "Current date"}
                    },
                    "required": ["scenario", "explanation"]
                }
            },
            "id": "4",
            "name": "Tool: Save Notes",
            "type": "@n8n/n8n-nodes-langchain.toolCode",
            "typeVersion": 1,
            "position": [880, 140]
        },
        {
            "parameters": {
                "name": "create_email_draft",
                "description": "Create email draft to support@groww.in with fee details (NOT auto-send)",
                "schema": {
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body with fee details"}
                    },
                    "required": ["subject", "body"]
                }
            },
            "id": "5",
            "name": "Tool: Email Draft",
            "type": "@n8n/n8n-nodes-langchain.toolCode",
            "typeVersion": 1,
            "position": [880, 280]
        },
        {
            "parameters": {
                "name": "log_audit",
                "description": "Log audit entry for compliance tracking",
                "schema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action performed"},
                        "details": {"type": "string", "description": "Additional details"}
                    },
                    "required": ["action"]
                }
            },
            "id": "6",
            "name": "Tool: Audit Log",
            "type": "@n8n/n8n-nodes-langchain.toolCode",
            "typeVersion": 1,
            "position": [880, 420]
        }
    ],
    "connections": {
        "Chat Trigger": {
            "main": [[{"node": "Agent", "type": "main", "index": 0}]]
        },
        "OpenAI Chat Model": {
            "ai_languageModel": [[{"node": "Agent", "type": "ai_languageModel", "index": 0}]]
        },
        "Tool: Save Notes": {
            "ai_tool": [[{"node": "Agent", "type": "ai_tool", "index": 0}]]
        },
        "Tool: Email Draft": {
            "ai_tool": [[{"node": "Agent", "type": "ai_tool", "index": 0}]]
        },
        "Tool: Audit Log": {
            "ai_tool": [[{"node": "Agent", "type": "ai_tool", "index": 0}]]
        }
    },
    "pinData": {},
    "settings": {
        "executionOrder": "v1"
    },
    "staticData": {},
    "tags": [],
    "triggerCount": 0,
    "updatedAt": "2025-12-15T08:00:00.000Z",
    "versionId": "1.0.0"
}

# Save
with open('/home/user/Project-3/fees_explainer_chat_flow.json', 'w') as f:
    json.dump(workflow, f, indent=2)

print("✓ Created: fees_explainer_chat_flow.json")
print("✓ Nodes: Chat Trigger → Agent → 3 MCP Tools")
print("✓ Ready to import!")
