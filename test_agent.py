"""
Test Suite for Fees Explainer Agent
====================================

Tests the core functionality of the agent and MCP handlers.
"""

import json
from datetime import datetime
from fees_explainer_agent import FeesExplainerAgent
from mcp_handlers import MCPServer, ApprovalRequired


def test_scenario_detection():
    """Test that agent correctly identifies fee scenarios."""
    agent = FeesExplainerAgent()

    # Test ELSS scenario
    response = agent.start_conversation("What is ELSS lock-in period?")
    assert 'Exit Load' in response['scenario']
    assert len(response['clarifying_questions']) <= 3

    # Test SIP scenario
    agent2 = FeesExplainerAgent()
    response2 = agent2.start_conversation("SIP cancellation charges")
    assert 'SIP Mandate' in response2['scenario']

    # Test expense ratio scenario
    agent3 = FeesExplainerAgent()
    response3 = agent3.start_conversation("Direct vs Regular plan fees")
    assert 'Expense Ratio' in response3['scenario']

    print("✓ Scenario detection tests passed")


def test_clarifying_questions():
    """Test that agent asks appropriate clarifying questions."""
    agent = FeesExplainerAgent()
    response = agent.start_conversation("Tell me about exit load")

    assert 'clarifying_questions' in response
    assert len(response['clarifying_questions']) >= 2
    assert len(response['clarifying_questions']) <= 3

    # Verify no PII is collected
    questions_text = ' '.join(response['clarifying_questions']).lower()
    assert 'name' not in questions_text
    assert 'email' not in questions_text
    assert 'phone' not in questions_text
    assert 'account' not in questions_text

    print("✓ Clarifying questions tests passed")


def test_fee_explanation_generation():
    """Test fee explanation generation with citations."""
    agent = FeesExplainerAgent()

    # Start conversation
    agent.start_conversation("ELSS exit load for SIP")

    # Provide answers
    answers = {
        'Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?': 'ELSS',
        'Do you plan to redeem within 1 year of investment?': 'No, after 3 years',
        'Is this a lumpsum investment or SIP?': 'SIP'
    }

    response = agent.process_clarifiers(answers)

    # Verify explanation structure
    assert 'explanation' in response
    explanation = response['explanation']

    assert 'scenario' in explanation
    assert 'last_checked' in explanation
    assert 'fee_details' in explanation
    assert 'disclaimer' in explanation

    # Verify bullets
    fee_details = explanation['fee_details']
    assert len(fee_details) <= 6
    assert len(fee_details) >= 1

    # Verify each bullet has text and source
    for detail in fee_details:
        assert 'text' in detail
        assert 'source' in detail
        assert detail['source'].startswith('http')

    # Verify official sources only
    allowed_domains = [
        'groww.in',
        'sebi.gov.in',
        'amfiindia.com',
        'npci.org.in',
        'rbi.org.in'
    ]

    for detail in fee_details:
        source_domain = detail['source'].split('/')[2]
        assert any(domain in source_domain for domain in allowed_domains), \
            f"Unofficial source: {detail['source']}"

    print("✓ Fee explanation generation tests passed")


def test_mcp_actions_preparation():
    """Test that MCP actions are correctly prepared."""
    agent = FeesExplainerAgent()
    agent.start_conversation("SIP mandate fees")

    answers = {
        'Are you setting up a new SIP or cancelling an existing one?': 'Cancelling',
        'What is your bank (some banks charge for auto-debit mandates)?': 'HDFC',
        'Is the SIP amount above or below ₹5,000 per month?': 'Above ₹5,000'
    }

    response = agent.process_clarifiers(answers)

    # Verify MCP actions
    assert 'mcp_actions_pending' in response
    assert response['mcp_actions_pending'] == 3

    mcp_actions = agent.get_mcp_actions_for_approval()
    assert len(mcp_actions) == 3

    # Verify action types
    action_types = [action['action_type'] for action in mcp_actions]
    assert 'notes' in action_types
    assert 'email' in action_types
    assert 'audit' in action_types

    # Verify all require approval
    for action in mcp_actions:
        assert action['requires_approval'] is True
        assert action['approved'] is False

    print("✓ MCP actions preparation tests passed")


def test_approval_gating():
    """Test that MCP actions require approval."""
    server = MCPServer()

    # Try to execute without approval
    try:
        result = server.execute_tool(
            'append_to_notes',
            {
                'entry_title': 'Test Entry',
                'date': datetime.now().isoformat(),
                'scenario': 'Test Scenario',
                'fee_details': [
                    {'text': 'Test detail', 'source': 'https://groww.in/test'}
                ],
                'last_checked': '2025-12-15'
            },
            approved=False
        )
        assert False, "Should have raised ApprovalRequired"
    except ApprovalRequired as e:
        assert 'Approval required' in str(e)
        assert e.tool_name == 'append_to_notes'

    print("✓ Approval gating tests passed")


def test_mcp_execution_with_approval():
    """Test MCP action execution after approval."""
    agent = FeesExplainerAgent()
    agent.start_conversation("Direct vs Regular expense ratio")

    answers = {
        'Are you investing in Direct Plan or Regular Plan?': 'Direct',
        'Which fund category: Equity, Debt, or Hybrid?': 'Equity',
        'Do you want to understand how expense ratio impacts returns?': 'Yes'
    }

    agent.process_clarifiers(answers)

    # Approve all actions
    for i in range(3):
        agent.approve_mcp_action(i)

    # Execute approved actions
    results = agent.execute_approved_mcp_actions()

    assert len(results['executed']) == 3
    assert len(results['skipped']) == 0
    assert len(results['errors']) == 0

    # Verify each execution
    for execution in results['executed']:
        assert execution['result']['status'] == 'success'

    print("✓ MCP execution with approval tests passed")


def test_partial_approval():
    """Test that only approved actions are executed."""
    agent = FeesExplainerAgent()
    agent.start_conversation("ELSS lock-in")

    answers = {
        'Are you asking about ELSS (tax-saving) mutual funds or non-ELSS equity funds?': 'ELSS',
        'Do you plan to redeem within 1 year of investment?': 'Yes',
        'Is this a lumpsum investment or SIP?': 'Lumpsum'
    }

    agent.process_clarifiers(answers)

    # Approve only actions 0 and 2 (skip 1)
    agent.approve_mcp_action(0)
    agent.approve_mcp_action(2)

    results = agent.execute_approved_mcp_actions()

    assert len(results['executed']) == 2
    assert len(results['skipped']) == 1

    # Verify correct actions executed
    executed_types = [e['action_type'] for e in results['executed']]
    assert 'notes' in executed_types
    assert 'audit' in executed_types
    assert 'email' not in executed_types

    print("✓ Partial approval tests passed")


def test_no_pii_in_outputs():
    """Verify that no PII is collected or stored."""
    agent = FeesExplainerAgent()
    agent.start_conversation("SIP fees")

    answers = {
        'Are you setting up a new SIP or cancelling an existing one?': 'Setting up',
        'What is your bank (some banks charge for auto-debit mandates)?': 'ICICI',
        'Is the SIP amount above or below ₹5,000 per month?': 'Below'
    }

    response = agent.process_clarifiers(answers)

    # Check explanation
    explanation_text = json.dumps(response['explanation']).lower()
    assert 'email' not in explanation_text or '@' not in explanation_text
    assert 'phone' not in explanation_text
    assert 'account number' not in explanation_text

    # Check MCP actions
    for action in agent.get_mcp_actions_for_approval():
        payload_text = json.dumps(action['full_payload']).lower()
        # Allow email in 'to' field only (support@groww.in)
        if action['action_type'] != 'email':
            assert '@' not in payload_text or 'support@groww.in' in payload_text

    print("✓ No PII in outputs tests passed")


def test_official_sources_only():
    """Verify all sources are official."""
    agent = FeesExplainerAgent()

    for scenario_key, scenario in agent.fee_knowledge_base.items():
        for bullet in scenario.bullets:
            source = bullet['source_url']

            # Check domain
            assert source.startswith('http'), f"Invalid URL: {source}"

            allowed_domains = [
                'groww.in',
                'sebi.gov.in',
                'amfiindia.com',
                'npci.org.in',
                'rbi.org.in'
            ]

            source_domain = source.split('/')[2].replace('www.', '')
            assert any(domain in source_domain for domain in allowed_domains), \
                f"Unofficial source in {scenario_key}: {source}"

    print("✓ Official sources only tests passed")


def test_last_checked_date():
    """Verify last_checked date is present and recent."""
    agent = FeesExplainerAgent()

    for scenario_key, scenario in agent.fee_knowledge_base.items():
        assert scenario.last_checked is not None
        assert len(scenario.last_checked) == 10  # YYYY-MM-DD format
        assert scenario.last_checked.startswith('2025')

    print("✓ Last checked date tests passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running Fees Explainer Agent Tests")
    print("=" * 60 + "\n")

    tests = [
        test_scenario_detection,
        test_clarifying_questions,
        test_fee_explanation_generation,
        test_mcp_actions_preparation,
        test_approval_gating,
        test_mcp_execution_with_approval,
        test_partial_approval,
        test_no_pii_in_outputs,
        test_official_sources_only,
        test_last_checked_date
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
