#!/usr/bin/env python3
"""
Generate valid n8n workflow JSON for Fees Explainer Agent
"""

import json

workflow = {
    "name": "Groww Fees Explainer - Complete",
    "nodes": [
        # Webhook 1: Start Query
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "fees-start",
                "responseMode": "lastNode",
                "options": {}
            },
            "id": "webhook_start",
            "name": "Webhook: Start Query",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1.1,
            "position": [240, 300]
        },

        # Code Node: Detect Scenario
        {
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """// Fees Explainer - Scenario Detection
const query = ($input.item.json.query || '').toLowerCase();

// Fee scenarios database
const scenarios = {
  elss: {
    name: 'Exit Load & ELSS Lock-in Period',
    questions: [
      'Are you asking about ELSS (tax-saving) or non-ELSS equity funds?',
      'Do you plan to redeem within 1 year of investment?',
      'Is this a lumpsum investment or SIP?'
    ],
    fees: [
      'ELSS has mandatory 3-year lock-in per Section 80C (https://groww.in/p/tax-saving-funds/)',
      'Exit load typically 1% if redeemed within 1 year (https://groww.in/blog/what-is-exit-load-in-mutual-funds)',
      'For SIP in ELSS, each installment has separate 3-year lock-in (https://groww.in/p/tax-saving-funds/)'
    ]
  },
  sip: {
    name: 'SIP Mandate Fees & Cancellation',
    questions: [
      'Are you setting up or cancelling a SIP?',
      'What is your bank?',
      'SIP amount above or below ₹5,000/month?'
    ],
    fees: [
      'Groww charges ₹0 for SIP setup/cancellation (https://groww.in/pricing/)',
      'Banks may charge ₹0-50 for e-mandate setup (https://groww.in/blog/sip-in-mutual-funds)',
      'Failed SIP may incur bank charges ₹100-300 (https://groww.in/blog/sip-in-mutual-funds)'
    ]
  },
  expense: {
    name: 'Expense Ratio (Direct vs Regular)',
    questions: [
      'Direct Plan or Regular Plan?',
      'Equity, Debt, or Hybrid fund?',
      'Want to understand long-term impact?'
    ],
    fees: [
      'Direct Plans are 0.5-1% cheaper than Regular Plans (https://groww.in/blog/direct-mutual-fund)',
      'Equity: Direct 1-1.5%, Regular 1.5-2.5% per SEBI cap (https://www.sebi.gov.in)',
      'Over 10 years, 1% lower ER can increase returns by 12-15% (https://groww.in/blog/direct-mutual-fund)'
    ]
  }
};

// Detect scenario
let key = 'expense';
if (query.includes('elss') || query.includes('exit load') || query.includes('lock')) {
  key = 'elss';
} else if (query.includes('sip') || query.includes('mandate') || query.includes('cancel')) {
  key = 'sip';
}

const scenario = scenarios[key];
const sessionId = Date.now().toString();

return {
  json: {
    session_id: sessionId,
    scenario: scenario.name,
    questions: scenario.questions,
    fees: scenario.fees,
    last_checked: '2025-12-15',
    status: 'clarifiers_required'
  }
};"""
            },
            "id": "detect_scenario",
            "name": "Detect Scenario",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [460, 300]
        }
    ],

    "connections": {
        "Webhook: Start Query": {
            "main": [[{"node": "Detect Scenario", "type": "main", "index": 0}]]
        }
    },

    "pinData": {},
    "settings": {"executionOrder": "v1"},
    "staticData": {},
    "tags": [],
    "triggerCount": 0,
    "updatedAt": "2025-12-15T06:30:00.000Z",
    "versionId": "1.0.0"
}

# Write to file
output_file = '/home/user/Project-3/n8n_fees_explainer_working.json'
with open(output_file, 'w') as f:
    json.dump(workflow, f, indent=2)

print(f"✓ Created valid n8n workflow: {output_file}")
print(f"✓ {len(workflow['nodes'])} nodes")
print("✓ Ready to import into n8n!")
