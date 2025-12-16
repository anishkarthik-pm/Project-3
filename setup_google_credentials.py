#!/usr/bin/env python3
"""
Google API Credentials Setup for MCP Server
===========================================

This script helps you set up Google API credentials for the MCP server.

Steps:
1. Creates a Google Cloud Project (or uses existing)
2. Enables required APIs (Sheets, Docs, Gmail)
3. Creates OAuth 2.0 credentials
4. Downloads credentials.json
5. Runs initial OAuth flow to generate token.json

Usage:
    python setup_google_credentials.py
"""

import os
import json
import webbrowser
from pathlib import Path

# Instructions for manual setup
SETUP_INSTRUCTIONS = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Google API Credentials Setup                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Follow these steps to set up Google API credentials:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. CREATE GOOGLE CLOUD PROJECT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   a) Go to: https://console.cloud.google.com/
   b) Click "Select a project" → "New Project"
   c) Name: "Fees Explainer MCP Server" (or any name)
   d) Click "Create"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. ENABLE REQUIRED APIs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Enable these APIs for your project:

   ✓ Google Sheets API
     https://console.cloud.google.com/apis/library/sheets.googleapis.com

   ✓ Google Docs API
     https://console.cloud.google.com/apis/library/docs.googleapis.com

   ✓ Gmail API
     https://console.cloud.google.com/apis/library/gmail.googleapis.com

   Click "Enable" for each API.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. CREATE OAuth 2.0 CREDENTIALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   a) Go to: https://console.cloud.google.com/apis/credentials
   b) Click "Create Credentials" → "OAuth client ID"
   c) If prompted, configure OAuth consent screen:
      - User Type: External (or Internal if using Google Workspace)
      - App name: "Fees Explainer MCP"
      - User support email: your email
      - Developer contact: your email
      - Click "Save and Continue"
      - Scopes: Skip (we'll add via code)
      - Test users: Add your email
      - Click "Save and Continue"

   d) Create OAuth client ID:
      - Application type: "Desktop app"
      - Name: "MCP Server Client"
      - Click "Create"

   e) Download the JSON file:
      - Click the download icon (⬇) next to your new credential
      - Save as: credentials.json
      - Move it to this directory: {project_dir}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. CREATE GOOGLE SHEET FOR DATA STORAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   a) Go to: https://sheets.google.com
   b) Create a new spreadsheet
   c) Name it: "Fees Explainer Data"
   d) Copy the Spreadsheet ID from the URL:
      https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit

   e) Save the ID - you'll need it for the .env file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. CREATE .env FILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Create a .env file in {project_dir} with:

   FEES_EXPLAINER_SPREADSHEET_ID=your_spreadsheet_id_here
   GOOGLE_CREDENTIALS_PATH=credentials.json
   GOOGLE_TOKEN_PATH=token.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. RUN INITIAL AUTHENTICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Once credentials.json is in place, run:

   python setup_google_credentials.py --auth

   This will:
   - Open your browser for Google OAuth
   - Ask you to grant permissions
   - Save token.json for future use

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After completing these steps, your MCP server will be ready to use!

"""


def check_credentials_exist():
    """Check if credentials.json exists."""
    return Path('credentials.json').exists()


def check_token_exists():
    """Check if token.json exists."""
    return Path('token.json').exists()


def run_oauth_flow():
    """Run OAuth flow to generate token.json."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify'
    ]

    if not check_credentials_exist():
        print("❌ Error: credentials.json not found!")
        print("\nPlease download OAuth 2.0 credentials from Google Cloud Console.")
        print("See instructions above.\n")
        return False

    print("🔐 Starting OAuth flow...")
    print("Your browser will open for authentication.\n")

    try:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        # Save credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

        print("✅ Authentication successful!")
        print("✅ token.json has been created.\n")
        return True

    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}\n")
        return False


def create_env_template():
    """Create .env template if it doesn't exist."""
    env_path = Path('.env')

    if env_path.exists():
        print("ℹ️  .env file already exists.")
        return

    template = """# Google API Configuration
FEES_EXPLAINER_SPREADSHEET_ID=your_spreadsheet_id_here
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
"""

    with open('.env', 'w') as f:
        f.write(template)

    print("✅ Created .env template. Please update with your Spreadsheet ID.\n")


def main():
    """Main setup function."""
    import sys

    print(SETUP_INSTRUCTIONS.format(project_dir=os.getcwd()))

    if '--auth' in sys.argv:
        # Run OAuth flow
        success = run_oauth_flow()
        if success:
            print("━" * 80)
            print("✅ Setup complete! You can now use the MCP server.")
            print("━" * 80)
        return

    # Check current status
    print("\n" + "=" * 80)
    print("CURRENT STATUS")
    print("=" * 80)

    creds_exist = check_credentials_exist()
    token_exist = check_token_exists()
    env_exist = Path('.env').exists()

    print(f"{'✅' if creds_exist else '❌'} credentials.json: {'Found' if creds_exist else 'Not found'}")
    print(f"{'✅' if token_exist else '❌'} token.json: {'Found' if token_exist else 'Not found'}")
    print(f"{'✅' if env_exist else '❌'} .env: {'Found' if env_exist else 'Not found'}")
    print()

    if not creds_exist:
        print("Next step: Download credentials.json from Google Cloud Console")
        print("           (See instructions above)")
    elif not token_exist:
        print("Next step: Run authentication")
        print("           python setup_google_credentials.py --auth")
        create_env_template()
    else:
        print("✅ All set! Your MCP server is ready to use.")

    print("=" * 80)


if __name__ == '__main__':
    main()
