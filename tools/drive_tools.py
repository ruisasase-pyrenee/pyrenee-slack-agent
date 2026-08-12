"""
Google Drive integration tools for the PE fund agent.
These are wrapped as Claude tool-use definitions.
"""

import json
from datetime import datetime
from typing import Any


def get_tool_definitions() -> list[dict]:
    """Return tool definitions for Claude tool use."""
    return [
        {
            "name": "search_drive",
            "description": "Search Google Drive for files related to portfolio companies, deals, or documents. Use when you need to find existing research or documents.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (company name, document type, etc.)"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "read_drive_file",
            "description": "Read the contents of a specific Google Drive file by file ID or name.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Google Drive file ID"
                    }
                },
                "required": ["file_id"]
            }
        },
        {
            "name": "save_to_drive",
            "description": "Create or update a document in Google Drive. Use to save screening memos, IC memos, compliance checklists, and LP reports.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Document title"
                    },
                    "content": {
                        "type": "string",
                        "description": "Document content in markdown format"
                    },
                    "folder": {
                        "type": "string",
                        "enum": ["deal_pipeline", "portfolio", "legal_compliance", "lp_relations", "ic_memos"],
                        "description": "Target folder in the fund's Google Drive structure"
                    }
                },
                "required": ["title", "content", "folder"]
            }
        },
        {
            "name": "list_portfolio",
            "description": "List all portfolio companies and their current status from Google Drive.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "update_deal_status",
            "description": "Update the status of a deal in the pipeline (screening, dd, ic_review, term_sheet, closed, passed).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Company name"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["screening", "dd", "ic_review", "term_sheet", "closed", "passed"],
                        "description": "New deal status"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notes on the status change"
                    }
                },
                "required": ["company_name", "status"]
            }
        },
        {
            "name": "update_legal_task",
            "description": "Update the status of a legal/compliance checklist item.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task name (must match exactly from checklist)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "blocked"],
                        "description": "New task status"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notes or blockers"
                    }
                },
                "required": ["task", "status"]
            }
        },
    ]


# Tool execution handlers that call the MCP tools
# These are called by the agent orchestrator when Claude invokes a tool

async def execute_tool(tool_name: str, tool_input: dict[str, Any], mcp_client=None) -> str:
    """Execute a tool and return the result as a string."""

    if tool_name == "search_drive":
        return await _search_drive(tool_input["query"], mcp_client)

    elif tool_name == "read_drive_file":
        return await _read_drive_file(tool_input["file_id"], mcp_client)

    elif tool_name == "save_to_drive":
        return await _save_to_drive(
            tool_input["title"],
            tool_input["content"],
            tool_input["folder"],
            mcp_client
        )

    elif tool_name == "list_portfolio":
        return await _list_portfolio(mcp_client)

    elif tool_name == "update_deal_status":
        return await _update_deal_status(
            tool_input["company_name"],
            tool_input["status"],
            tool_input.get("notes", ""),
            mcp_client
        )

    elif tool_name == "update_legal_task":
        return await _update_legal_task(
            tool_input["task"],
            tool_input["status"],
            tool_input.get("notes", ""),
            mcp_client
        )

    return f"Unknown tool: {tool_name}"


async def _search_drive(query: str, mcp_client) -> str:
    if mcp_client is None:
        return json.dumps({"error": "Google Drive MCP not connected", "query": query})
    try:
        result = await mcp_client.call_tool(
            "mcp__7c1dcb02-2041-403b-8d17-53d0af1affa4__search_files",
            {"query": query}
        )
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _read_drive_file(file_id: str, mcp_client) -> str:
    if mcp_client is None:
        return json.dumps({"error": "Google Drive MCP not connected"})
    try:
        result = await mcp_client.call_tool(
            "mcp__7c1dcb02-2041-403b-8d17-53d0af1affa4__read_file_content",
            {"file_id": file_id}
        )
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _save_to_drive(title: str, content: str, folder: str, mcp_client) -> str:
    if mcp_client is None:
        # Fallback: return what would be saved (for testing without MCP)
        return json.dumps({
            "status": "simulated",
            "title": title,
            "folder": folder,
            "timestamp": datetime.now().isoformat(),
            "note": "Google Drive MCP not connected - document logged locally"
        })
    try:
        result = await mcp_client.call_tool(
            "mcp__7c1dcb02-2041-403b-8d17-53d0af1affa4__create_file",
            {
                "name": title,
                "content": content,
                "mimeType": "text/plain"
            }
        )
        return json.dumps({"status": "saved", "result": result}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _list_portfolio(mcp_client) -> str:
    if mcp_client is None:
        return json.dumps({"portfolio": [], "note": "Google Drive MCP not connected"})
    try:
        result = await mcp_client.call_tool(
            "mcp__7c1dcb02-2041-403b-8d17-53d0af1affa4__search_files",
            {"query": "portfolio"}
        )
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _update_deal_status(company: str, status: str, notes: str, mcp_client) -> str:
    # Save a deal status update log to Drive
    content = f"""# Deal Status Update
Company: {company}
Status: {status}
Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Notes: {notes}
"""
    return await _save_to_drive(
        f"[Deal] {company} - Status: {status}",
        content,
        "deal_pipeline",
        mcp_client
    )


async def _update_legal_task(task: str, status: str, notes: str, mcp_client) -> str:
    content = f"""# Legal Task Update
Task: {task}
Status: {status}
Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Notes: {notes}
"""
    return await _save_to_drive(
        f"[Legal] {task} - {status}",
        content,
        "legal_compliance",
        mcp_client
    )
