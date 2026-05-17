"""
Google認証セットアップ（2ステップ）。

Step 1: python setup_google_auth.py url     → URLを表示
Step 2: python setup_google_auth.py CODE    → コードを貼ってtoken.json生成
"""
import sys
import json
import pickle
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.readonly",
]
STATE_FILE = Path("auth_state.pkl")


def generate_url():
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_secrets_file(
        "credentials.json", scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )
    # PKCE無効化
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true",
    )
    # stateを保存
    STATE_FILE.write_bytes(pickle.dumps({
        "client_config": json.loads(Path("credentials.json").read_text()),
        "code_verifier": getattr(flow, "_code_verifier", None),
    }))
    print("\n=== このURLをスマホで開いて、Googleアカウントでログインしてください ===")
    print()
    print(auth_url)
    print()
    print("認証後に表示される「コード」をコピーして、以下を実行:")
    print("  python setup_google_auth.py <コード>")


def save_token(code: str):
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_secrets_file(
        "credentials.json", scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )
    flow.fetch_token(code=code)
    Path("token.json").write_text(flow.credentials.to_json())
    STATE_FILE.unlink(missing_ok=True)
    print("\ntoken.json を保存しました。Google認証完了！")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "url":
        generate_url()
    else:
        save_token(sys.argv[1])
