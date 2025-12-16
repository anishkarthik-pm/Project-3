#!/usr/bin/env python3
"""
Local Testing Script for MCP Server
====================================

Tests the MCP server locally without Claude Desktop.
Simulates MCP tool calls and verifies Google API integration.

Usage:
    # Test all
    python test_local_mcp.py

    # Test specific tool
    python test_local_mcp.py --tool append_to_google_sheets
    python test_local_mcp.py --tool create_google_doc
    python test_local_mcp.py --tool create_gmail_draft
    python test_local_mcp.py --tool log_audit_entry
"""

import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_append_to_google_sheets():
    """Test appending to Google Sheets."""
    print("\n" + "=" * 80)
    print("TEST: append_to_google_sheets")
    print("=" * 80)

    from google_mcp_server import GoogleMCPServer

    server = GoogleMCPServer()

    # Test data
    test_args = {
        "entry_title": "Test Entry - Exit Load & ELSS",
        "scenario": "Exit Load & ELSS Lock-in Period",
        "clarifiers": {
            "Fund type": "ELSS",
            "Investment period": "Long term",
            "Investment type": "SIP"
        },
        "fee_details": [
            {
                "text": "ELSS funds have a mandatory 3-year lock-in period.",
                "source": "https://groww.in/p/tax-saving-funds/"
            },
            {
                "text": "For SIP investments, each installment has separate lock-in.",
                "source": "https://groww.in/p/tax-saving-funds/"
            }
        ],
        "last_checked": "2025-12-16"
    }

    try:
        print("\n📊 Testing Google Sheets append...")
        print(f"Entry: {test_args['entry_title']}")
        print(f"Scenario: {test_args['scenario']}")
        print(f"Fee details: {len(test_args['fee_details'])} bullets")

        result = await server._append_to_sheets(test_args)

        print("\n✅ Success!")
        print(json.dumps(result, indent=2))

        if result.get('status') == 'success':
            print("\n🎉 Google Sheets integration working!")
            print(f"Spreadsheet ID: {result.get('spreadsheet_id')}")
            print(f"Updated range: {result.get('updated_range')}")
            return True
        else:
            print("\n❌ Failed")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check FEES_EXPLAINER_SPREADSHEET_ID in .env")
        print("2. Verify credentials.json exists")
        print("3. Run: python setup_google_credentials.py --auth")
        print("4. Ensure Google Sheets API is enabled")
        return False


async def test_create_google_doc():
    """Test creating Google Doc."""
    print("\n" + "=" * 80)
    print("TEST: create_google_doc")
    print("=" * 80)

    from google_mcp_server import GoogleMCPServer

    server = GoogleMCPServer()

    test_args = {
        "doc_title": f"Test Fee Explanation - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "scenario": "SIP Mandate Fees & Cancellation",
        "clarifiers": {
            "Action": "Setting up new SIP",
            "Bank": "HDFC Bank"
        },
        "fee_details": [
            {
                "text": "Groww does NOT charge any fees for SIP registration.",
                "source": "https://groww.in/pricing/"
            },
            {
                "text": "Your bank may charge ₹0-50 for e-mandate setup.",
                "source": "https://groww.in/blog/sip-in-mutual-funds"
            }
        ],
        "last_checked": "2025-12-16"
    }

    try:
        print("\n📝 Testing Google Doc creation...")
        print(f"Title: {test_args['doc_title']}")
        print(f"Scenario: {test_args['scenario']}")

        result = await server._create_doc(test_args)

        print("\n✅ Success!")
        print(json.dumps(result, indent=2))

        if result.get('status') == 'success':
            print("\n🎉 Google Docs integration working!")
            print(f"Doc URL: {result.get('doc_url')}")
            print("\n👉 Open the URL above to verify the document")
            return True
        else:
            print("\n❌ Failed")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Verify credentials.json exists")
        print("2. Run: python setup_google_credentials.py --auth")
        print("3. Ensure Google Docs API is enabled")
        return False


async def test_create_gmail_draft():
    """Test creating Gmail draft."""
    print("\n" + "=" * 80)
    print("TEST: create_gmail_draft")
    print("=" * 80)

    from google_mcp_server import GoogleMCPServer

    server = GoogleMCPServer()

    test_args = {
        "to": "support@example.com",
        "subject": f"Test Fee Clarification - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "body": """Dear Support Team,

This is a test email from the Fees Explainer MCP server.

Scenario: Expense Ratio

Fee Details:
1. Direct Plans have lower expense ratio (0.5-1% lower) than Regular Plans.
   Source: https://groww.in/blog/direct-mutual-fund

2. For equity funds: Direct Plan expense ratio typically 1-1.5%.
   Source: https://www.sebi.gov.in/legal/circulars/...

Last Checked: 2025-12-16

Best regards
"""
    }

    try:
        print("\n✉️  Testing Gmail draft creation...")
        print(f"To: {test_args['to']}")
        print(f"Subject: {test_args['subject']}")

        result = await server._create_gmail_draft(test_args)

        print("\n✅ Success!")
        print(json.dumps(result, indent=2))

        if result.get('status') == 'success':
            print("\n🎉 Gmail integration working!")
            print(f"Draft ID: {result.get('draft_id')}")
            print(f"Auto-sent: {result.get('auto_sent')} (should be False)")
            print("\n👉 Check your Gmail drafts to verify")
            return True
        else:
            print("\n❌ Failed")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Verify credentials.json exists")
        print("2. Run: python setup_google_credentials.py --auth")
        print("3. Ensure Gmail API is enabled")
        return False


async def test_log_audit_entry():
    """Test audit logging."""
    print("\n" + "=" * 80)
    print("TEST: log_audit_entry")
    print("=" * 80)

    from google_mcp_server import GoogleMCPServer

    server = GoogleMCPServer()

    test_args = {
        "who": "TestScript",
        "action": "Local MCP server testing",
        "details": {
            "test_type": "local_testing",
            "timestamp": datetime.now().isoformat(),
            "tools_tested": ["sheets", "docs", "gmail", "audit"]
        }
    }

    try:
        print("\n📋 Testing audit logging...")
        print(f"Who: {test_args['who']}")
        print(f"Action: {test_args['action']}")

        result = await server._log_audit(test_args)

        print("\n✅ Success!")
        print(json.dumps(result, indent=2))

        if result.get('status') == 'success':
            print("\n🎉 Audit logging working!")
            print(f"Spreadsheet ID: {result.get('spreadsheet_id')}")
            print(f"Entry timestamp: {result.get('entry_timestamp')}")
            return True
        else:
            print("\n❌ Failed")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check FEES_EXPLAINER_SPREADSHEET_ID in .env")
        print("2. Verify credentials.json exists")
        print("3. Run: python setup_google_credentials.py --auth")
        return False


async def test_all():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 22 + "MCP Server Local Testing" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")

    # Check prerequisites
    print("\n📋 Checking prerequisites...")

    creds_exist = Path('credentials.json').exists()
    token_exist = Path('token.json').exists()
    env_exist = Path('.env').exists()

    print(f"{'✅' if creds_exist else '❌'} credentials.json")
    print(f"{'✅' if token_exist else '❌'} token.json")
    print(f"{'✅' if env_exist else '⚠️ '} .env")

    if not creds_exist or not token_exist:
        print("\n❌ Prerequisites missing!")
        print("\nRun this first:")
        print("  python setup_google_credentials.py --auth")
        return

    if env_exist:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        spreadsheet_id = os.getenv('FEES_EXPLAINER_SPREADSHEET_ID')
        if not spreadsheet_id or spreadsheet_id == 'your_spreadsheet_id_here':
            print("\n⚠️  Warning: FEES_EXPLAINER_SPREADSHEET_ID not set in .env")
            print("Some tests may fail. Create a Google Sheet and set the ID.")
            print()

    # Run tests
    results = []

    print("\n" + "=" * 80)
    print("Starting tests...")
    print("=" * 80)

    # Test 1: Google Sheets
    results.append(("Google Sheets", await test_append_to_google_sheets()))

    # Test 2: Google Docs
    results.append(("Google Docs", await test_create_google_doc()))

    # Test 3: Gmail
    results.append(("Gmail Drafts", await test_create_gmail_draft()))

    # Test 4: Audit Log
    results.append(("Audit Log", await test_log_audit_entry()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10s} {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 80)

    if all_passed:
        print("🎉 All tests passed! MCP server is ready for Claude Desktop.\n")
        print("Next steps:")
        print("1. Configure Claude Desktop (see SETUP_MCP_CLAUDE.md)")
        print("2. Restart Claude Desktop")
        print("3. Ask Claude: 'What MCP tools do you have?'")
        print()
    else:
        print("⚠️  Some tests failed. Fix issues above before using with Claude.\n")

    return all_passed


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test MCP server locally"
    )
    parser.add_argument(
        '--tool',
        choices=['append_to_google_sheets', 'create_google_doc', 'create_gmail_draft', 'log_audit_entry'],
        help='Test specific tool only'
    )

    args = parser.parse_args()

    if args.tool:
        # Test specific tool
        if args.tool == 'append_to_google_sheets':
            await test_append_to_google_sheets()
        elif args.tool == 'create_google_doc':
            await test_create_google_doc()
        elif args.tool == 'create_gmail_draft':
            await test_create_gmail_draft()
        elif args.tool == 'log_audit_entry':
            await test_log_audit_entry()
    else:
        # Test all
        await test_all()


if __name__ == '__main__':
    asyncio.run(main())
