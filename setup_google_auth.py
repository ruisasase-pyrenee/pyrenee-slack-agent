"""
Google認証セットアップ。

Step 1: python setup_google_auth.py       → URLを表示
Step 2: python setup_google_auth.py CODE  → token.json生成
"""
import sys
import json
import requests
from pathlib import Path
from urllib.parse import urlencode

CREDS = json.loads(Path("credentials.json").read_text())["installed"]
CLIENT_ID = CREDS["client_id"]
CLIENT_SECRET = CREDS["client_secret"]
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def generate_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)
    print("\n=== このURLをスマホで開いてください ===\n")
    print(url)
    print("\n認証後に表示されたコードをここに貼って実行:")
    print("  python setup_google_auth.py <コード>")


def save_token(code: str):
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    data = resp.json()
    if "error" in data:
        print(f"エラー: {data}")
        return

    # google-auth形式のtoken.jsonに変換
    token = {
        "token": data.get("access_token"),
        "refresh_token": data.get("refresh_token"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scopes": SCOPES,
        "expiry": None,
    }
    Path("token.json").write_text(json.dumps(token))
    print("\ntoken.json を保存しました。Google認証完了！")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        generate_url()
    else:
        save_token(sys.argv[1])
