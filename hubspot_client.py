"""
HubSpot CRM自動連携。

- メールの送信者をHubSpotで照合
- 重要なメールを自動でノートとして記録
- コンタクトの最終接触日を更新

Required env:
  HUBSPOT_API_KEY  HubSpot Private App Token
"""

import os
import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY", "")
BASE_URL = "https://api.hubapi.com"


def is_configured() -> bool:
    return bool(HUBSPOT_API_KEY)


def _headers():
    return {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }


def find_contact_by_email(email: str) -> dict | None:
    """メールアドレスでHubSpotコンタクトを検索する。"""
    if not is_configured():
        return None
    try:
        resp = requests.post(
            f"{BASE_URL}/crm/v3/objects/contacts/search",
            headers=_headers(),
            json={
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email.lower().strip(),
                    }]
                }],
                "properties": ["firstname", "lastname", "email", "company", "hs_lead_status"],
                "limit": 1,
            },
            timeout=10,
        )
        data = resp.json()
        results = data.get("results", [])
        return results[0] if results else None
    except Exception as e:
        logger.warning(f"HubSpot contact search failed: {e}")
        return None


def create_note(contact_id: str, note_body: str) -> bool:
    """コンタクトにノートを作成する。"""
    if not is_configured():
        return False
    try:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        resp = requests.post(
            f"{BASE_URL}/crm/v3/objects/notes",
            headers=_headers(),
            json={
                "properties": {
                    "hs_note_body": note_body,
                    "hs_timestamp": str(now_ms),
                },
                "associations": [{
                    "to": {"id": contact_id},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}],
                }],
            },
            timeout=10,
        )
        return resp.status_code in (200, 201)
    except Exception as e:
        logger.warning(f"HubSpot note creation failed: {e}")
        return False


def update_last_contact(contact_id: str) -> bool:
    """最終接触日を更新する。"""
    if not is_configured():
        return False
    try:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        resp = requests.patch(
            f"{BASE_URL}/crm/v3/objects/contacts/{contact_id}",
            headers=_headers(),
            json={"properties": {"notes_last_contacted": str(now_ms)}},
            timeout=10,
        )
        return resp.status_code == 200
    except Exception as e:
        logger.warning(f"HubSpot update failed: {e}")
        return False


def sync_email_to_hubspot(email: dict, note_text: str = "") -> str | None:
    """
    メールをHubSpotに自動同期する。
    コンタクトが見つかればノートを作成して最終接触日を更新。
    戻り値: コンタクト名（見つかった場合）
    """
    if not is_configured():
        return None

    sender = email.get("from", "")
    # メールアドレスを抽出 (例: "Tim Moore <tim@timmoore.work>")
    import re
    match = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]+", sender)
    if not match:
        return None

    email_addr = match.group(0)
    contact = find_contact_by_email(email_addr)
    if not contact:
        return None

    contact_id = contact["id"]
    props = contact.get("properties", {})
    name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip() or email_addr

    # ノート作成
    body = note_text or f"メール受信: {email.get('subject', '')} ({email.get('date', '')})"
    create_note(contact_id, body)
    update_last_contact(contact_id)

    logger.info(f"HubSpot synced: {name} ({email_addr})")
    return name
