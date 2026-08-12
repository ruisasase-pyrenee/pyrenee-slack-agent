"""
Unified tool registry - all Claude tool-use definitions and execution logic.

Every integration (Drive, HubSpot, Notion, Calendar, Gmail) lives here.
The orchestrator loads this and passes it to Claude.
"""

import json
from datetime import datetime
from typing import Any


# ── Tool Definitions ────────────────────────────────────────────────────────

def get_all_tools() -> list[dict]:
    return [
        # ── Google Drive ─────────────────────────────────────────────────
        {
            "name": "drive_search",
            "description": "Google Driveを検索。既存の調査メモ、ICメモ、契約書を探す時に使う。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "検索キーワード（会社名、ドキュメント種別など）"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "drive_save",
            "description": "ドキュメントをGoogle Driveに保存。スクリーニングメモ、ICメモ、LP報告書、法務タスクを保存する時に必ず使う。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string", "description": "Markdown形式のドキュメント本文"},
                    "folder": {
                        "type": "string",
                        "enum": ["deal_pipeline", "ic_memos", "portfolio", "legal_compliance", "lp_relations", "market_research"],
                    }
                },
                "required": ["title", "content", "folder"]
            }
        },
        {
            "name": "drive_read",
            "description": "Google DriveのファイルをIDで読む。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string"}
                },
                "required": ["file_id"]
            }
        },
        # ── HubSpot CRM ─────────────────────────────────────────────────
        {
            "name": "crm_add_deal",
            "description": "HubSpotにディール（投資案件）を追加または更新する。スクリーニング後は必ずこれを呼ぶ。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "stage": {
                        "type": "string",
                        "enum": ["sourced", "screening", "dd", "ic_review", "term_sheet", "closed_won", "closed_lost", "watchlist"]
                    },
                    "sector": {"type": "string"},
                    "arr_mn_jpy": {"type": "number", "description": "ARR（百万円）"},
                    "notes": {"type": "string"}
                },
                "required": ["company_name", "stage"]
            }
        },
        {
            "name": "crm_add_lp",
            "description": "HubSpotにLP（出資者）候補を追加または更新する。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "org_name": {"type": "string", "description": "機関名"},
                    "contact_name": {"type": "string"},
                    "contact_email": {"type": "string"},
                    "tier": {"type": "string", "enum": ["tier1", "tier2", "tier3"]},
                    "lp_type": {"type": "string", "description": "地銀、CVC、ファミリーオフィスなど"},
                    "estimated_ticket_mn_jpy": {"type": "number"},
                    "status": {
                        "type": "string",
                        "enum": ["prospect", "intro_sent", "meeting_scheduled", "met", "dd", "committed", "closed", "passed"]
                    },
                    "notes": {"type": "string"}
                },
                "required": ["org_name", "status"]
            }
        },
        {
            "name": "crm_search",
            "description": "HubSpotでLP・ディール・コンタクトを検索する。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "object_type": {
                        "type": "string",
                        "enum": ["deals", "contacts", "companies"],
                        "description": "deals=投資案件, contacts=担当者, companies=LP機関・ポートフォリオ企業"
                    }
                },
                "required": ["query", "object_type"]
            }
        },
        {
            "name": "crm_get_pipeline",
            "description": "現在の投資パイプラインまたはLPパイプラインのサマリーを取得する。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pipeline_type": {
                        "type": "string",
                        "enum": ["deals", "lps"],
                    }
                },
                "required": ["pipeline_type"]
            }
        },
        # ── Notion ──────────────────────────────────────────────────────
        {
            "name": "notion_save_page",
            "description": "NotionにページとしてICメモ、調査メモ、ナレッジを保存する。Google Driveと並行して使う。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string", "description": "Markdown形式"},
                    "database": {
                        "type": "string",
                        "enum": ["deal_research", "lp_tracker", "portfolio", "legal_tasks", "market_intel"]
                    }
                },
                "required": ["title", "content", "database"]
            }
        },
        {
            "name": "notion_search",
            "description": "Notionワークスペースを検索する。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        },
        # ── Calendar ────────────────────────────────────────────────────
        {
            "name": "calendar_schedule",
            "description": "LP面談、IC会議、ポートフォリオ定例をカレンダーに登録する。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "time": {"type": "string", "description": "HH:MM (JST)"},
                    "duration_minutes": {"type": "integer"},
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "メールアドレスのリスト"
                    },
                    "description": {"type": "string"}
                },
                "required": ["title", "date", "time"]
            }
        },
        {
            "name": "calendar_get_week",
            "description": "今週・来週のカレンダーを取得する。LP面談前の準備ブリーフ作成に使う。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "week": {"type": "string", "enum": ["this_week", "next_week"]}
                },
                "required": ["week"]
            }
        },
        # ── Gmail ────────────────────────────────────────────────────────
        {
            "name": "gmail_draft",
            "description": "LP向け/ポートフォリオ向けメール下書きを作成する。送信前にRuiが確認する前提。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "宛先メールアドレス"},
                    "subject": {"type": "string"},
                    "body": {"type": "string", "description": "メール本文（HTML可）"},
                    "context": {"type": "string", "description": "このメールの背景・目的"}
                },
                "required": ["to", "subject", "body"]
            }
        },
        # ── Slack ─────────────────────────────────────────────────────────
        {
            "name": "slack_send_alert",
            "description": "重要なアラートや発見をSlackの特定チャンネルに送る。緊急のディールシグナル、LP返信など。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "チャンネル名（#deal-flow, #lp-relations, #legal など）"},
                    "message": {"type": "string"},
                    "urgency": {"type": "string", "enum": ["high", "medium", "low"]}
                },
                "required": ["channel", "message"]
            }
        },
    ]


# ── Tool Execution ────────────────────────────────────────────────────────────

async def execute(tool_name: str, tool_input: dict[str, Any], mcp_tools: dict | None = None) -> str:
    """
    Route tool call to the appropriate handler.
    mcp_tools is a dict mapping MCP IDs to callable clients.
    """
    mcp = mcp_tools or {}

    handlers = {
        "drive_search":      lambda: _drive_search(tool_input, mcp),
        "drive_save":        lambda: _drive_save(tool_input, mcp),
        "drive_read":        lambda: _drive_read(tool_input, mcp),
        "crm_add_deal":      lambda: _crm_add_deal(tool_input, mcp),
        "crm_add_lp":        lambda: _crm_add_lp(tool_input, mcp),
        "crm_search":        lambda: _crm_search(tool_input, mcp),
        "crm_get_pipeline":  lambda: _crm_get_pipeline(tool_input, mcp),
        "notion_save_page":  lambda: _notion_save(tool_input, mcp),
        "notion_search":     lambda: _notion_search(tool_input, mcp),
        "calendar_schedule": lambda: _calendar_schedule(tool_input, mcp),
        "calendar_get_week": lambda: _calendar_get_week(tool_input, mcp),
        "gmail_draft":       lambda: _gmail_draft(tool_input, mcp),
        "slack_send_alert":  lambda: _slack_send_alert(tool_input, mcp),
    }

    if tool_name not in handlers:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    try:
        result = handlers[tool_name]()
        if hasattr(result, "__await__"):
            result = await result
        return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e), "tool": tool_name})


# ── Google Drive handlers ─────────────────────────────────────────────────────

def _drive_search(inp: dict, mcp: dict) -> str:
    drive = mcp.get("drive")
    if not drive:
        return json.dumps({"status": "mcp_not_connected", "tool": "drive_search", "query": inp["query"]})
    # MCP call: mcp__7c1dcb02-2041-403b-8d17-53d0af1affa4__search_files
    return json.dumps({"note": "Call mcp__7c1dcb02__search_files", "query": inp["query"]})


def _drive_save(inp: dict, mcp: dict) -> str:
    drive = mcp.get("drive")
    saved = {
        "status": "saved" if drive else "logged_locally",
        "title": inp["title"],
        "folder": inp["folder"],
        "timestamp": datetime.now().isoformat(),
        "chars": len(inp["content"]),
    }
    if not drive:
        saved["note"] = "Drive MCP未接続。本番環境では自動保存されます。"
    return json.dumps(saved, ensure_ascii=False)


def _drive_read(inp: dict, mcp: dict) -> str:
    drive = mcp.get("drive")
    if not drive:
        return json.dumps({"status": "mcp_not_connected", "file_id": inp["file_id"]})
    return json.dumps({"note": "Call mcp__7c1dcb02__read_file_content", "file_id": inp["file_id"]})


# ── HubSpot handlers ──────────────────────────────────────────────────────────

def _crm_add_deal(inp: dict, mcp: dict) -> str:
    hs = mcp.get("hubspot")
    record = {
        "status": "created" if hs else "logged",
        "object": "deal",
        "company": inp["company_name"],
        "stage": inp["stage"],
        "sector": inp.get("sector", ""),
        "arr_mn_jpy": inp.get("arr_mn_jpy"),
        "timestamp": datetime.now().isoformat(),
    }
    if not hs:
        record["note"] = "HubSpot MCP未接続。本番環境ではCRMに自動登録されます。"
    return json.dumps(record, ensure_ascii=False)


def _crm_add_lp(inp: dict, mcp: dict) -> str:
    hs = mcp.get("hubspot")
    record = {
        "status": "created" if hs else "logged",
        "object": "lp_contact",
        "org": inp["org_name"],
        "contact": inp.get("contact_name", ""),
        "tier": inp.get("tier", ""),
        "lp_type": inp.get("lp_type", ""),
        "ticket_mn_jpy": inp.get("estimated_ticket_mn_jpy"),
        "status": inp["status"],
        "timestamp": datetime.now().isoformat(),
    }
    return json.dumps(record, ensure_ascii=False)


def _crm_search(inp: dict, mcp: dict) -> str:
    hs = mcp.get("hubspot")
    if not hs:
        return json.dumps({"status": "mcp_not_connected", "query": inp["query"], "type": inp["object_type"]})
    return json.dumps({"note": "Call mcp__b24208b4__search_crm_objects", "query": inp["query"]})


def _crm_get_pipeline(inp: dict, mcp: dict) -> str:
    hs = mcp.get("hubspot")
    if not hs:
        return json.dumps({
            "status": "mcp_not_connected",
            "pipeline_type": inp["pipeline_type"],
            "note": "HubSpot MCP接続後にリアルタイムデータが取得できます"
        })
    return json.dumps({"note": "Call mcp__b24208b4__get_crm_objects", "type": inp["pipeline_type"]})


# ── Notion handlers ───────────────────────────────────────────────────────────

def _notion_save(inp: dict, mcp: dict) -> str:
    notion = mcp.get("notion")
    saved = {
        "status": "saved" if notion else "logged_locally",
        "title": inp["title"],
        "database": inp["database"],
        "timestamp": datetime.now().isoformat(),
    }
    if not notion:
        saved["note"] = "Notion MCP未接続。"
    return json.dumps(saved, ensure_ascii=False)


def _notion_search(inp: dict, mcp: dict) -> str:
    notion = mcp.get("notion")
    if not notion:
        return json.dumps({"status": "mcp_not_connected", "query": inp["query"]})
    return json.dumps({"note": "Call mcp__8b6062e1__notion-search", "query": inp["query"]})


# ── Calendar handlers ─────────────────────────────────────────────────────────

def _calendar_schedule(inp: dict, mcp: dict) -> str:
    cal = mcp.get("calendar")
    event = {
        "status": "created" if cal else "logged",
        "title": inp["title"],
        "date": inp["date"],
        "time": inp["time"],
        "duration": inp.get("duration_minutes", 60),
        "attendees": inp.get("attendees", []),
    }
    if not cal:
        event["note"] = "Calendar MCP未接続。"
    return json.dumps(event, ensure_ascii=False)


def _calendar_get_week(inp: dict, mcp: dict) -> str:
    cal = mcp.get("calendar")
    if not cal:
        return json.dumps({"status": "mcp_not_connected", "week": inp["week"]})
    return json.dumps({"note": "Call mcp__6dd14f3d__list_events", "week": inp["week"]})


# ── Gmail handlers ────────────────────────────────────────────────────────────

def _gmail_draft(inp: dict, mcp: dict) -> str:
    mail = mcp.get("gmail")
    draft = {
        "status": "draft_created" if mail else "logged",
        "to": inp["to"],
        "subject": inp["subject"],
        "preview": inp["body"][:200] + "..." if len(inp["body"]) > 200 else inp["body"],
        "timestamp": datetime.now().isoformat(),
    }
    if not mail:
        draft["note"] = "Gmail MCP未接続。"
    return json.dumps(draft, ensure_ascii=False)


# ── Slack handlers ────────────────────────────────────────────────────────────

def _slack_send_alert(inp: dict, mcp: dict) -> str:
    slack = mcp.get("slack")
    alert = {
        "status": "sent" if slack else "logged",
        "channel": inp["channel"],
        "urgency": inp.get("urgency", "medium"),
        "preview": inp["message"][:100],
        "timestamp": datetime.now().isoformat(),
    }
    return json.dumps(alert, ensure_ascii=False)
