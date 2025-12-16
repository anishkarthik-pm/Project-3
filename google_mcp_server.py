#!/usr/bin/env python3
"""
MCP Server for Financial Fees Explainer Agent
==============================================

Provides MCP tools that integrate with Google Sheets, Docs, and Gmail.
Can be connected directly to Claude Desktop.

Tools:
1. append_to_google_sheets - Save fee explanations to Google Sheets
2. create_google_doc - Create documentation in Google Docs
3. create_gmail_draft - Create email draft in Gmail (never auto-sends)
4. log_audit_entry - Log to Google Sheets audit log

All tools are approval-gated for compliance.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Optional

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import AnyUrl

# Google API imports
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes for Google APIs
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Configuration - can be overridden via environment variables
SPREADSHEET_ID = os.getenv('FEES_EXPLAINER_SPREADSHEET_ID', '')
NOTES_SHEET_NAME = 'Fee Explanations'
AUDIT_SHEET_NAME = 'Audit Log'


class GoogleMCPServer:
    """MCP Server with Google Sheets, Docs, and Gmail integration."""

    def __init__(self):
        self.server = Server("groww-fees-explainer-mcp")
        self.creds: Optional[Credentials] = None
        self._setup_handlers()

    def _get_credentials(self) -> Credentials:
        """Get or refresh Google API credentials."""
        if self.creds and self.creds.valid:
            return self.creds

        token_file = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
        creds_file = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(token_file, SCOPES)

        # Refresh or get new credentials
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(creds_file):
                    raise FileNotFoundError(
                        f"Google credentials file not found: {creds_file}\n"
                        "Please download OAuth 2.0 credentials from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())

        return self.creds

    def _setup_handlers(self):
        """Set up MCP protocol handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available MCP tools."""
            return [
                Tool(
                    name="append_to_google_sheets",
                    description=(
                        "Appends a fee explanation entry to Google Sheets. "
                        "Stores scenario, date, clarifiers, fee details with citations, "
                        "and last checked date. Requires approval."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entry_title": {
                                "type": "string",
                                "description": "Title of the fee explanation entry"
                            },
                            "scenario": {
                                "type": "string",
                                "description": "Fee scenario name (e.g., 'Exit Load & ELSS')"
                            },
                            "clarifiers": {
                                "type": "object",
                                "description": "Questions and answers from clarification phase"
                            },
                            "fee_details": {
                                "type": "array",
                                "description": "Array of fee details with text and source URLs",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string"},
                                        "source": {"type": "string", "format": "uri"}
                                    },
                                    "required": ["text", "source"]
                                }
                            },
                            "last_checked": {
                                "type": "string",
                                "description": "Date when fee info was last verified"
                            }
                        },
                        "required": ["entry_title", "scenario", "fee_details", "last_checked"]
                    }
                ),
                Tool(
                    name="create_google_doc",
                    description=(
                        "Creates a Google Doc with fee explanation details. "
                        "Formats the document with proper headings, bullets, and citations. "
                        "Returns the document URL. Requires approval."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "doc_title": {
                                "type": "string",
                                "description": "Title of the Google Doc"
                            },
                            "scenario": {
                                "type": "string",
                                "description": "Fee scenario name"
                            },
                            "clarifiers": {
                                "type": "object",
                                "description": "Questions and answers"
                            },
                            "fee_details": {
                                "type": "array",
                                "description": "Fee details with citations",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string"},
                                        "source": {"type": "string"}
                                    }
                                }
                            },
                            "last_checked": {
                                "type": "string",
                                "description": "Verification date"
                            }
                        },
                        "required": ["doc_title", "scenario", "fee_details", "last_checked"]
                    }
                ),
                Tool(
                    name="create_gmail_draft",
                    description=(
                        "Creates a draft email in Gmail with fee clarification details. "
                        "NEVER auto-sends - only creates draft for review. "
                        "Requires approval before creation."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "Recipient email (e.g., support@groww.in)"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject line"
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body with fee details and sources"
                            }
                        },
                        "required": ["to", "subject", "body"]
                    }
                ),
                Tool(
                    name="log_audit_entry",
                    description=(
                        "Logs an audit trail entry to Google Sheets. "
                        "Records who, when, what action, and details for compliance. "
                        "Requires approval."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "who": {
                                "type": "string",
                                "description": "Entity that performed the action"
                            },
                            "action": {
                                "type": "string",
                                "description": "Description of the action performed"
                            },
                            "details": {
                                "type": "object",
                                "description": "Additional metadata about the action"
                            }
                        },
                        "required": ["who", "action"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool execution requests."""

            try:
                if name == "append_to_google_sheets":
                    result = await self._append_to_sheets(arguments)
                elif name == "create_google_doc":
                    result = await self._create_doc(arguments)
                elif name == "create_gmail_draft":
                    result = await self._create_gmail_draft(arguments)
                elif name == "log_audit_entry":
                    result = await self._log_audit(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "error": str(e),
                        "tool": name
                    }, indent=2)
                )]

    async def _append_to_sheets(self, args: dict) -> dict:
        """Append fee explanation to Google Sheets."""
        creds = self._get_credentials()
        service = build('sheets', 'v4', credentials=creds)

        spreadsheet_id = SPREADSHEET_ID
        if not spreadsheet_id:
            raise ValueError(
                "FEES_EXPLAINER_SPREADSHEET_ID environment variable not set. "
                "Please create a Google Sheet and set the ID."
            )

        # Prepare row data
        timestamp = datetime.now().isoformat()

        # Format fee details as text
        fee_text = "\n".join([
            f"• {detail['text']}\n  Source: {detail['source']}"
            for detail in args['fee_details']
        ])

        # Format clarifiers
        clarifiers_text = json.dumps(args.get('clarifiers', {}))

        # Row data: [Timestamp, Title, Scenario, Clarifiers, Fee Details, Last Checked]
        row_data = [
            timestamp,
            args['entry_title'],
            args['scenario'],
            clarifiers_text,
            fee_text,
            args['last_checked']
        ]

        # Append to sheet
        try:
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{NOTES_SHEET_NAME}!A:F",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_data]}
            ).execute()

            return {
                "status": "success",
                "tool": "append_to_google_sheets",
                "message": f"Entry appended: {args['entry_title']}",
                "spreadsheet_id": spreadsheet_id,
                "updated_range": result.get('updates', {}).get('updatedRange'),
                "rows_added": 1
            }

        except HttpError as e:
            if e.resp.status == 404:
                # Sheet doesn't exist, try to create it
                return await self._create_sheet_and_append(service, spreadsheet_id, row_data, args)
            raise

    async def _create_sheet_and_append(self, service, spreadsheet_id: str, row_data: list, args: dict) -> dict:
        """Create the sheet if it doesn't exist and append data."""
        # Create the sheet with headers
        headers = ['Timestamp', 'Entry Title', 'Scenario', 'Clarifiers', 'Fee Details', 'Last Checked']

        try:
            # Add new sheet
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': NOTES_SHEET_NAME
                            }
                        }
                    }]
                }
            ).execute()

            # Add headers and data
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{NOTES_SHEET_NAME}!A1:F1",
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()

            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{NOTES_SHEET_NAME}!A:F",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_data]}
            ).execute()

            return {
                "status": "success",
                "tool": "append_to_google_sheets",
                "message": f"Sheet created and entry appended: {args['entry_title']}",
                "spreadsheet_id": spreadsheet_id,
                "updated_range": result.get('updates', {}).get('updatedRange'),
                "rows_added": 1
            }

        except HttpError as e:
            raise Exception(f"Failed to create sheet: {str(e)}")

    async def _create_doc(self, args: dict) -> dict:
        """Create a Google Doc with fee explanation."""
        creds = self._get_credentials()
        docs_service = build('docs', 'v1', credentials=creds)

        # Create document
        doc = docs_service.documents().create(
            body={'title': args['doc_title']}
        ).execute()

        doc_id = doc['documentId']

        # Build content
        requests = []
        index = 1

        # Title
        requests.append({
            'insertText': {
                'location': {'index': index},
                'text': f"{args['doc_title']}\n\n"
            }
        })
        index += len(args['doc_title']) + 2

        # Scenario
        requests.append({
            'insertText': {
                'location': {'index': index},
                'text': f"Scenario: {args['scenario']}\n"
            }
        })
        index += len(f"Scenario: {args['scenario']}\n")

        # Last Checked
        requests.append({
            'insertText': {
                'location': {'index': index},
                'text': f"Last Checked: {args['last_checked']}\n\n"
            }
        })
        index += len(f"Last Checked: {args['last_checked']}\n\n")

        # Clarifiers (if provided)
        if args.get('clarifiers'):
            requests.append({
                'insertText': {
                    'location': {'index': index},
                    'text': "Context:\n"
                }
            })
            index += len("Context:\n")

            for question, answer in args['clarifiers'].items():
                text = f"  Q: {question}\n  A: {answer}\n"
                requests.append({
                    'insertText': {
                        'location': {'index': index},
                        'text': text
                    }
                })
                index += len(text)

            requests.append({
                'insertText': {
                    'location': {'index': index},
                    'text': "\n"
                }
            })
            index += 1

        # Fee Details
        requests.append({
            'insertText': {
                'location': {'index': index},
                'text': "Fee Details:\n\n"
            }
        })
        index += len("Fee Details:\n\n")

        for i, detail in enumerate(args['fee_details'], 1):
            text = f"{i}. {detail['text']}\n"
            requests.append({
                'insertText': {
                    'location': {'index': index},
                    'text': text
                }
            })
            index += len(text)

            source_text = f"   Source: {detail['source']}\n\n"
            requests.append({
                'insertText': {
                    'location': {'index': index},
                    'text': source_text
                }
            })
            index += len(source_text)

        # Update document with all content
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        return {
            "status": "success",
            "tool": "create_google_doc",
            "message": f"Google Doc created: {args['doc_title']}",
            "doc_id": doc_id,
            "doc_url": doc_url
        }

    async def _create_gmail_draft(self, args: dict) -> dict:
        """Create a draft email in Gmail (never auto-sends)."""
        creds = self._get_credentials()
        service = build('gmail', 'v1', credentials=creds)

        # Create email message
        import base64
        from email.mime.text import MIMEText

        message = MIMEText(args['body'])
        message['to'] = args['to']
        message['subject'] = args['subject']

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        # Create draft
        draft = service.users().drafts().create(
            userId='me',
            body={
                'message': {
                    'raw': raw_message
                }
            }
        ).execute()

        return {
            "status": "success",
            "tool": "create_gmail_draft",
            "message": f"Gmail draft created (NOT sent)",
            "draft_id": draft['id'],
            "to": args['to'],
            "subject": args['subject'],
            "auto_sent": False,
            "note": "Draft saved in Gmail. Review and send manually."
        }

    async def _log_audit(self, args: dict) -> dict:
        """Log audit entry to Google Sheets."""
        creds = self._get_credentials()
        service = build('sheets', 'v4', credentials=creds)

        spreadsheet_id = SPREADSHEET_ID
        if not spreadsheet_id:
            raise ValueError("FEES_EXPLAINER_SPREADSHEET_ID not set")

        timestamp = datetime.now().isoformat()

        # Row data: [Timestamp, Who, Action, Details]
        row_data = [
            timestamp,
            args['who'],
            args['action'],
            json.dumps(args.get('details', {}))
        ]

        try:
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{AUDIT_SHEET_NAME}!A:D",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_data]}
            ).execute()

            return {
                "status": "success",
                "tool": "log_audit_entry",
                "message": f"Audit entry logged: {args['action']}",
                "spreadsheet_id": spreadsheet_id,
                "updated_range": result.get('updates', {}).get('updatedRange'),
                "entry_timestamp": timestamp
            }

        except HttpError as e:
            if e.resp.status == 404:
                # Create audit sheet
                headers = ['Timestamp', 'Who', 'Action', 'Details']

                service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={
                        'requests': [{
                            'addSheet': {
                                'properties': {
                                    'title': AUDIT_SHEET_NAME
                                }
                            }
                        }]
                    }
                ).execute()

                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"{AUDIT_SHEET_NAME}!A1:D1",
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()

                result = service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range=f"{AUDIT_SHEET_NAME}!A:D",
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [row_data]}
                ).execute()

                return {
                    "status": "success",
                    "tool": "log_audit_entry",
                    "message": f"Audit sheet created and entry logged: {args['action']}",
                    "spreadsheet_id": spreadsheet_id,
                    "entry_timestamp": timestamp
                }
            raise

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="groww-fees-explainer-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                )
            )


async def main():
    """Main entry point."""
    server = GoogleMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
