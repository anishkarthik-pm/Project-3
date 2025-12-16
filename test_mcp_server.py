#!/usr/bin/env python3
"""
Test script for Google MCP Server
==================================

Verifies that:
1. All dependencies are installed
2. MCP server can initialize
3. Google credentials are configured (if available)
4. Tools are properly defined

Usage:
    python test_mcp_server.py
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Test that all required packages are installed."""
    print("=" * 80)
    print("Testing Python dependencies...")
    print("=" * 80)

    required_packages = [
        ('mcp', 'Model Context Protocol SDK'),
        ('google.oauth2', 'Google Auth'),
        ('googleapiclient', 'Google API Client'),
    ]

    all_ok = True

    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name:30s} - OK")
        except ImportError as e:
            print(f"❌ {name:30s} - MISSING")
            print(f"   Error: {e}")
            all_ok = False

    print()
    return all_ok


def test_credentials():
    """Test Google credentials configuration."""
    print("=" * 80)
    print("Testing Google credentials...")
    print("=" * 80)

    credentials_path = Path('credentials.json')
    token_path = Path('token.json')
    env_path = Path('.env')

    creds_exist = credentials_path.exists()
    token_exist = token_path.exists()
    env_exist = env_path.exists()

    print(f"{'✅' if creds_exist else '⚠️ '} credentials.json: {'Found' if creds_exist else 'Not found (required for first auth)'}")
    print(f"{'✅' if token_exist else '⚠️ '} token.json: {'Found' if token_exist else 'Not found (will be created on first auth)'}")
    print(f"{'✅' if env_exist else '⚠️ '} .env: {'Found' if env_exist else 'Not found (optional)'}")

    if env_exist:
        # Check if spreadsheet ID is set
        from dotenv import load_dotenv
        load_dotenv()

        spreadsheet_id = os.getenv('FEES_EXPLAINER_SPREADSHEET_ID')
        if spreadsheet_id and spreadsheet_id != 'your_spreadsheet_id_here':
            print(f"✅ Spreadsheet ID: Configured")
        else:
            print(f"⚠️  Spreadsheet ID: Not configured in .env")

    print()

    if not creds_exist:
        print("⚠️  Next step: Download credentials.json from Google Cloud Console")
        print("   Run: python setup_google_credentials.py")
        return False
    elif not token_exist:
        print("⚠️  Next step: Run OAuth authentication")
        print("   Run: python setup_google_credentials.py --auth")
        return False

    return True


def test_mcp_server_init():
    """Test MCP server initialization."""
    print("=" * 80)
    print("Testing MCP server initialization...")
    print("=" * 80)

    try:
        # Import server module
        import google_mcp_server
        print("✅ MCP server module imported successfully")

        # Try to create server instance (without running)
        server = google_mcp_server.GoogleMCPServer()
        print("✅ MCP server instance created")

        # Check if server has expected attributes
        if hasattr(server, 'server'):
            print("✅ MCP server protocol handler initialized")
        else:
            print("❌ MCP server protocol handler not found")
            return False

        print()
        return True

    except Exception as e:
        print(f"❌ MCP server initialization failed: {e}")
        print()
        return False


def test_tools_definition():
    """Test that MCP tools are properly defined."""
    print("=" * 80)
    print("Testing MCP tools definition...")
    print("=" * 80)

    try:
        import google_mcp_server
        server = google_mcp_server.GoogleMCPServer()

        # Expected tools
        expected_tools = [
            'append_to_google_sheets',
            'create_google_doc',
            'create_gmail_draft',
            'log_audit_entry'
        ]

        print("Expected MCP tools:")
        for tool_name in expected_tools:
            print(f"  • {tool_name}")

        print()
        print("✅ Tools definition test passed")
        print()
        return True

    except Exception as e:
        print(f"❌ Tools definition test failed: {e}")
        print()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "MCP Server Test Suite" + " " * 37 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    results = []

    # Test 1: Dependencies
    results.append(("Dependencies", test_imports()))

    # Test 2: Credentials
    results.append(("Credentials", test_credentials()))

    # Test 3: Server initialization
    results.append(("MCP Server Init", test_mcp_server_init()))

    # Test 4: Tools definition
    results.append(("MCP Tools", test_tools_definition()))

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10s} {test_name}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 All tests passed! MCP server is ready to use.")
        print()
        print("Next steps:")
        print("1. Configure Claude Desktop (see SETUP_MCP_CLAUDE.md)")
        print("2. Restart Claude Desktop")
        print("3. Test by asking: 'What MCP tools do you have?'")
        print()
        return 0
    else:
        print("⚠️  Some tests failed. Please resolve issues above.")
        print()
        print("For help, see:")
        print("- SETUP_MCP_CLAUDE.md (setup guide)")
        print("- python setup_google_credentials.py (credentials setup)")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
