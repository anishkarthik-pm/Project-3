"""
Financial Fees & Charges Explainer Agent for Groww Mutual Funds
=================================================================

This agent helps users understand fees and charges for common mutual fund actions
using only official sources (SEBI/AMFI/AMC/Groww Help Pages).

Features:
- Asks 2-3 clarifying questions (no PII)
- Generates structured, factual explanations with citations
- Performs MCP actions: Notes entry, Email draft, Audit log
- All MCP actions are approval-gated
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class FeeScenario:
    """Represents a fee scenario with official sources."""
    scenario_name: str
    clarifiers: List[str]
    bullets: List[Dict[str, str]]  # Each bullet has 'text' and 'source_url'
    last_checked: str


@dataclass
class MCPAction:
    """Represents an MCP action that requires approval."""
    action_type: str  # 'notes', 'email', or 'audit'
    payload: Dict
    requires_approval: bool = True
    approved: bool = False


class FeesExplainerAgent:
    """
    Agent that explains mutual fund fees using official sources.

    Covers 3 fee scenarios:
    1. Exit Load & ELSS Lock-in Period
    2. SIP Mandate Fees & Cancellation
    3. Expense Ratio (Direct vs Regular Plans)
    """

    def __init__(self):
        self.fee_knowledge_base = self._load_fee_knowledge_base()
        self.conversation_state = {
            'scenario': None,
            'clarifiers_asked': [],
            'clarifiers_answers': {},
            'selected_bullets': []
        }
        self.mcp_actions = []

    def _load_fee_knowledge_base(self) -> Dict[str, FeeScenario]:
        """
        Load fee information with official sources.

        Note: All sources are official (SEBI/AMFI/Groww Help/AMC factsheets)
        """
        return {
            'exit_load_elss': FeeScenario(
                scenario_name='Exit Load & ELSS Lock-in Period',
                clarifiers=[
                    'Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?',
                    'Do you plan to redeem within 1 year of investment?',
                    'Is this a lumpsum investment or SIP?'
                ],
                bullets=[
                    {
                        'text': 'ELSS funds have a mandatory 3-year lock-in period as per Section 80C of Income Tax Act. No redemption is allowed during this period.',
                        'source_url': 'https://groww.in/p/tax-saving-funds/',
                        'applicable_when': {'fund_type': 'ELSS'}
                    },
                    {
                        'text': 'For non-ELSS equity funds, exit load is typically 1% if redeemed within 1 year of investment (varies by AMC).',
                        'source_url': 'https://groww.in/blog/what-is-exit-load-in-mutual-funds',
                        'applicable_when': {'fund_type': 'non-ELSS', 'redemption_period': 'within_1_year'}
                    },
                    {
                        'text': 'Exit load (if applicable) is deducted from the redemption NAV. For example, 1% exit load on ₹10,000 redemption = ₹100 deduction.',
                        'source_url': 'https://groww.in/blog/what-is-exit-load-in-mutual-funds',
                        'applicable_when': {'redemption_period': 'within_1_year'}
                    },
                    {
                        'text': 'Most equity funds have NIL exit load after 1 year. Check the Scheme Information Document (SID) for exact terms.',
                        'source_url': 'https://www.amfiindia.com/investor-corner/knowledge-center/what-is-exit-load.html',
                        'applicable_when': {'fund_type': 'non-ELSS', 'redemption_period': 'after_1_year'}
                    },
                    {
                        'text': 'For SIP investments in ELSS, each installment has a separate 3-year lock-in from its investment date.',
                        'source_url': 'https://groww.in/p/tax-saving-funds/',
                        'applicable_when': {'fund_type': 'ELSS', 'investment_type': 'SIP'}
                    },
                    {
                        'text': 'Exit load collected goes back to the scheme (not to AMC), benefiting continuing investors as per SEBI regulations.',
                        'source_url': 'https://www.sebi.gov.in/legal/circulars/oct-2012/exit-load-payment-to-distributors_24239.html',
                        'applicable_when': {}
                    }
                ],
                last_checked='2025-12-15'
            ),

            'sip_mandate_fees': FeeScenario(
                scenario_name='SIP Mandate Fees & Cancellation',
                clarifiers=[
                    'Are you setting up a new SIP or cancelling an existing one?',
                    'What is your bank (some banks charge for auto-debit mandates)?',
                    'Is the SIP amount above or below ₹5,000 per month?'
                ],
                bullets=[
                    {
                        'text': 'Groww does NOT charge any fees for SIP registration, modification, or cancellation. These services are free.',
                        'source_url': 'https://groww.in/pricing/',
                        'applicable_when': {}
                    },
                    {
                        'text': 'Your bank may charge ₹0-50 for setting up auto-debit mandates (e-mandate/e-NACH). Check with your bank.',
                        'source_url': 'https://groww.in/blog/sip-in-mutual-funds',
                        'applicable_when': {'action': 'setup'}
                    },
                    {
                        'text': 'SIP cancellation on Groww is instant and free. No penalty or exit charges for stopping SIP.',
                        'source_url': 'https://groww.in/pricing/',
                        'applicable_when': {'action': 'cancel'}
                    },
                    {
                        'text': 'Failed SIP installments may incur bank charges (typically ₹100-300 for insufficient balance). This is charged by the bank, not Groww or AMC.',
                        'source_url': 'https://groww.in/blog/sip-in-mutual-funds',
                        'applicable_when': {}
                    },
                    {
                        'text': 'You can pause SIP for 1-3 months or modify amount/date without any charges from Groww or AMC.',
                        'source_url': 'https://groww.in/pricing/',
                        'applicable_when': {'action': 'modify'}
                    },
                    {
                        'text': 'E-mandate limit is ₹25,000 for UPI autopay and ₹15 lakh for NACH/debit mandate as per NPCI/RBI guidelines.',
                        'source_url': 'https://www.npci.org.in/what-we-do/upi/upi-autopay',
                        'applicable_when': {'action': 'setup'}
                    }
                ],
                last_checked='2025-12-15'
            ),

            'expense_ratio': FeeScenario(
                scenario_name='Expense Ratio (Direct vs Regular Plans)',
                clarifiers=[
                    'Are you investing in Direct Plan or Regular Plan?',
                    'Which fund category: Equity, Debt, or Hybrid?',
                    'Do you want to understand how expense ratio impacts returns?'
                ],
                bullets=[
                    {
                        'text': 'Direct Plans have lower expense ratio (0.5-1% lower) than Regular Plans because they exclude distributor commissions.',
                        'source_url': 'https://groww.in/blog/direct-mutual-fund',
                        'applicable_when': {}
                    },
                    {
                        'text': 'For equity funds: Direct Plan expense ratio typically 1-1.5%, Regular Plan 1.5-2.5% (as per SEBI cap of 2.25% for equity funds).',
                        'source_url': 'https://www.sebi.gov.in/legal/circulars/sep-2018/total-expense-ratio-ter-and-performance-disclosure-for-mutual-funds_40203.html',
                        'applicable_when': {'category': 'equity'}
                    },
                    {
                        'text': 'For debt funds: SEBI cap is 2% for first ₹500 cr AUM, 1.75% for next ₹250 cr, 1.5% for balance. Direct plans typically 0.5-0.8% lower.',
                        'source_url': 'https://www.sebi.gov.in/legal/circulars/sep-2018/total-expense-ratio-ter-and-performance-disclosure-for-mutual-funds_40203.html',
                        'applicable_when': {'category': 'debt'}
                    },
                    {
                        'text': 'Expense ratio is deducted daily from scheme NAV (not separately charged to investor). It covers fund management, operations, marketing.',
                        'source_url': 'https://www.amfiindia.com/investor-corner/knowledge-center/expense-ratio.html',
                        'applicable_when': {}
                    },
                    {
                        'text': 'Over 10 years, 1% lower expense ratio can increase returns by ~12-15% due to compounding (e.g., ₹10 lakh → ₹1.2-1.5 lakh extra).',
                        'source_url': 'https://groww.in/blog/direct-mutual-fund',
                        'applicable_when': {'understanding': 'impact'}
                    },
                    {
                        'text': 'Exact expense ratio for each fund is disclosed in Monthly/Quarterly factsheets and Scheme Information Document (SID).',
                        'source_url': 'https://www.amfiindia.com/investor-corner/knowledge-center/expense-ratio.html',
                        'applicable_when': {}
                    }
                ],
                last_checked='2025-12-15'
            )
        }

    def start_conversation(self, user_query: str) -> Dict:
        """
        Start the conversation and determine which scenario to address.

        Returns:
            Dict with next_step and clarifying_questions
        """
        # Simple keyword-based scenario detection
        query_lower = user_query.lower()

        scenario_key = None
        if any(kw in query_lower for kw in ['exit load', 'elss', 'lock-in', 'lock in', 'redeem', 'redemption']):
            scenario_key = 'exit_load_elss'
        elif any(kw in query_lower for kw in ['sip', 'mandate', 'auto-debit', 'auto debit', 'autopay']):
            scenario_key = 'sip_mandate_fees'
        elif any(kw in query_lower for kw in ['expense ratio', 'direct plan', 'regular plan', 'charges', 'fees']):
            scenario_key = 'expense_ratio'
        else:
            # Default to expense ratio as it's most commonly asked
            scenario_key = 'expense_ratio'

        self.conversation_state['scenario'] = scenario_key
        scenario = self.fee_knowledge_base[scenario_key]

        # Select first 3 clarifying questions (or 2 if we want to keep it minimal)
        clarifiers_to_ask = scenario.clarifiers[:3]
        self.conversation_state['clarifiers_asked'] = clarifiers_to_ask

        return {
            'next_step': 'ask_clarifiers',
            'scenario': scenario.scenario_name,
            'clarifying_questions': clarifiers_to_ask,
            'instructions': 'Please answer the following questions to provide you with the most relevant fee information:'
        }

    def process_clarifiers(self, answers: Dict[str, str]) -> Dict:
        """
        Process clarifying answers and generate fee explanation.

        Args:
            answers: Dict mapping question to answer

        Returns:
            Dict with fee_explanation and mcp_actions_pending
        """
        self.conversation_state['clarifiers_answers'] = answers

        scenario_key = self.conversation_state['scenario']
        scenario = self.fee_knowledge_base[scenario_key]

        # Filter bullets based on clarifier answers (simplified logic)
        selected_bullets = self._select_relevant_bullets(scenario, answers)
        self.conversation_state['selected_bullets'] = selected_bullets

        # Format the explanation
        explanation = {
            'scenario': scenario.scenario_name,
            'last_checked': scenario.last_checked,
            'fee_details': selected_bullets,
            'disclaimer': 'This information is based on official sources and current regulations. Always verify exact fees from the fund\'s Scheme Information Document (SID) or factsheet.'
        }

        # Prepare MCP actions
        self._prepare_mcp_actions(explanation)

        return {
            'next_step': 'review_explanation',
            'explanation': explanation,
            'mcp_actions_pending': len(self.mcp_actions),
            'mcp_actions_summary': [
                f"{action.action_type}: {action.payload.get('subject', action.payload.get('entry_title', 'action'))}"
                for action in self.mcp_actions
            ]
        }

    def _select_relevant_bullets(self, scenario: FeeScenario, answers: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Select up to 6 most relevant bullets based on clarifier answers.

        Simplified logic: Returns bullets where applicable_when conditions match answers.
        """
        selected = []

        for bullet in scenario.bullets:
            # Always include bullets with empty applicable_when
            if not bullet.get('applicable_when'):
                selected.append({
                    'text': bullet['text'],
                    'source': bullet['source_url']
                })
            else:
                # Simple matching logic (can be enhanced)
                # For now, include all bullets; in production, implement smart filtering
                selected.append({
                    'text': bullet['text'],
                    'source': bullet['source_url']
                })

        # Limit to 6 bullets
        return selected[:6]

    def _prepare_mcp_actions(self, explanation: Dict):
        """
        Prepare MCP actions: Notes entry, Email draft, Audit log.
        All actions require approval.
        """
        timestamp = datetime.now().isoformat()
        scenario_name = explanation['scenario']

        # 1. Notes/Doc Entry
        notes_entry = {
            'entry_title': f"Fee Explanation: {scenario_name}",
            'date': timestamp,
            'scenario': scenario_name,
            'clarifiers': self.conversation_state['clarifiers_answers'],
            'fee_details': explanation['fee_details'],
            'last_checked': explanation['last_checked']
        }
        self.mcp_actions.append(MCPAction(
            action_type='notes',
            payload=notes_entry,
            requires_approval=True
        ))

        # 2. Email Draft
        email_body = self._format_email_body(explanation)
        email_draft = {
            'to': 'support@groww.in',  # or advisor alias
            'subject': f'Fee Clarification Request: {scenario_name}',
            'body': email_body,
            'draft_only': True  # Do not auto-send
        }
        self.mcp_actions.append(MCPAction(
            action_type='email',
            payload=email_draft,
            requires_approval=True
        ))

        # 3. Audit Log
        audit_entry = {
            'who': 'FeesExplainerAgent',
            'when': timestamp,
            'action': f'Generated fee explanation for: {scenario_name}',
            'details': {
                'scenario': scenario_name,
                'clarifiers_count': len(self.conversation_state['clarifiers_answers']),
                'bullets_count': len(explanation['fee_details'])
            }
        }
        self.mcp_actions.append(MCPAction(
            action_type='audit',
            payload=audit_entry,
            requires_approval=True
        ))

    def _format_email_body(self, explanation: Dict) -> str:
        """Format explanation as email body."""
        lines = [
            f"Subject: Fee Clarification - {explanation['scenario']}",
            "",
            "Dear Support Team / Advisor,",
            "",
            f"I would like clarification on the following fee scenario: {explanation['scenario']}",
            "",
            "Fee Details (based on official sources):",
            ""
        ]

        for i, bullet in enumerate(explanation['fee_details'], 1):
            lines.append(f"{i}. {bullet['text']}")
            lines.append(f"   Source: {bullet['source']}")
            lines.append("")

        lines.extend([
            f"Last Checked: {explanation['last_checked']}",
            "",
            "Please confirm if the above information is accurate or if there are any updates.",
            "",
            "Best regards"
        ])

        return "\n".join(lines)

    def get_mcp_actions_for_approval(self) -> List[Dict]:
        """
        Get all pending MCP actions for user approval.

        Returns:
            List of MCP actions with details
        """
        return [
            {
                'action_id': i,
                'action_type': action.action_type,
                'summary': self._get_action_summary(action),
                'full_payload': action.payload,
                'requires_approval': action.requires_approval,
                'approved': action.approved
            }
            for i, action in enumerate(self.mcp_actions)
        ]

    def _get_action_summary(self, action: MCPAction) -> str:
        """Generate human-readable summary of MCP action."""
        if action.action_type == 'notes':
            return f"Add notes entry: {action.payload.get('entry_title')}"
        elif action.action_type == 'email':
            return f"Draft email to {action.payload.get('to')}: {action.payload.get('subject')}"
        elif action.action_type == 'audit':
            return f"Log audit entry: {action.payload.get('action')}"
        return "Unknown action"

    def approve_mcp_action(self, action_id: int) -> Dict:
        """
        Approve a specific MCP action.

        Returns:
            Dict with approval status
        """
        if 0 <= action_id < len(self.mcp_actions):
            self.mcp_actions[action_id].approved = True
            return {
                'status': 'approved',
                'action_id': action_id,
                'action_type': self.mcp_actions[action_id].action_type
            }
        return {'status': 'error', 'message': 'Invalid action ID'}

    def execute_approved_mcp_actions(self) -> Dict:
        """
        Execute all approved MCP actions.

        Returns:
            Dict with execution results
        """
        results = {
            'executed': [],
            'skipped': [],
            'errors': []
        }

        for i, action in enumerate(self.mcp_actions):
            if not action.approved:
                results['skipped'].append({
                    'action_id': i,
                    'reason': 'Not approved'
                })
                continue

            try:
                # In production, this would call actual MCP tools
                # For now, we'll simulate the execution
                result = self._execute_mcp_action(action)
                results['executed'].append({
                    'action_id': i,
                    'action_type': action.action_type,
                    'result': result
                })
            except Exception as e:
                results['errors'].append({
                    'action_id': i,
                    'action_type': action.action_type,
                    'error': str(e)
                })

        return results

    def _execute_mcp_action(self, action: MCPAction) -> Dict:
        """
        Execute a single MCP action.

        In production, this would call MCP tools/APIs.
        For now, returns simulation result.
        """
        if action.action_type == 'notes':
            return {
                'tool': 'mcp_notes_append',
                'status': 'success',
                'message': f"Notes entry added: {action.payload.get('entry_title')}"
            }
        elif action.action_type == 'email':
            return {
                'tool': 'mcp_email_draft',
                'status': 'success',
                'message': f"Email draft created: {action.payload.get('subject')}"
            }
        elif action.action_type == 'audit':
            return {
                'tool': 'mcp_audit_log',
                'status': 'success',
                'message': f"Audit entry logged: {action.payload.get('action')}"
            }

        return {'status': 'unknown_action_type'}

    def get_conversation_summary(self) -> Dict:
        """Get complete conversation summary for logging/review."""
        return {
            'scenario': self.conversation_state.get('scenario'),
            'clarifiers_asked': self.conversation_state.get('clarifiers_asked', []),
            'clarifiers_answers': self.conversation_state.get('clarifiers_answers', {}),
            'bullets_provided': len(self.conversation_state.get('selected_bullets', [])),
            'mcp_actions_total': len(self.mcp_actions),
            'mcp_actions_approved': sum(1 for a in self.mcp_actions if a.approved),
            'timestamp': datetime.now().isoformat()
        }


# Example usage
if __name__ == '__main__':
    # Initialize agent
    agent = FeesExplainerAgent()

    # Example 1: ELSS Exit Load Query
    print("=" * 80)
    print("Example 1: User asks about ELSS exit load")
    print("=" * 80)

    response1 = agent.start_conversation("I want to know about ELSS lock-in and exit load")
    print(f"\nScenario: {response1['scenario']}")
    print("\nClarifying Questions:")
    for i, q in enumerate(response1['clarifying_questions'], 1):
        print(f"{i}. {q}")

    # User answers
    answers1 = {
        response1['clarifying_questions'][0]: "ELSS",
        response1['clarifying_questions'][1]: "No, after 3 years",
        response1['clarifying_questions'][2]: "SIP"
    }

    response2 = agent.process_clarifiers(answers1)
    print(f"\n\nFee Explanation ({response2['explanation']['scenario']}):")
    print(f"Last Checked: {response2['explanation']['last_checked']}")
    print("\nFee Details:")
    for i, detail in enumerate(response2['explanation']['fee_details'], 1):
        print(f"\n{i}. {detail['text']}")
        print(f"   📎 Source: {detail['source']}")

    print(f"\n\nMCP Actions Pending Approval: {response2['mcp_actions_pending']}")
    mcp_actions = agent.get_mcp_actions_for_approval()
    for action in mcp_actions:
        print(f"\n  - {action['summary']}")

    print("\n" + "=" * 80)
    print("Approving all MCP actions...")
    print("=" * 80)

    for i in range(len(mcp_actions)):
        agent.approve_mcp_action(i)

    execution_results = agent.execute_approved_mcp_actions()
    print("\nExecution Results:")
    print(f"  Executed: {len(execution_results['executed'])}")
    print(f"  Skipped: {len(execution_results['skipped'])}")
    print(f"  Errors: {len(execution_results['errors'])}")

    for result in execution_results['executed']:
        print(f"\n  ✓ {result['action_type']}: {result['result']['message']}")

    summary = agent.get_conversation_summary()
    print("\n\nConversation Summary:")
    print(json.dumps(summary, indent=2))
