#!/usr/bin/env python3
"""Google Sheets / 서비스 계정 키가 유효한지 로컬에서 검사."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from env_config import get_google_sheet_id, get_service_account_info  # noqa: E402
from google.oauth2 import service_account  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def main() -> int:
    sa_path = ROOT / "service_account.json"
    print(f"service_account.json: {'있음' if sa_path.is_file() else '없음'}")
    print(f"GOOGLE_SHEET_ID: {get_google_sheet_id() or '(없음)'}")

    info = get_service_account_info()
    if not info:
        print("\n실패: 서비스 계정 정보를 읽지 못했습니다.")
        print("  로컬: service_account.json 배치")
        print("  Cloud: Secrets [gcp_service_account] 또는 GOOGLE_SERVICE_ACCOUNT_JSON")
        return 1

    email = info.get("client_email", "")
    pk = info.get("private_key", "")
    print(f"client_email: {email}")
    print(f"private_key 시작: {pk[:30]!r} ...")
    if not pk.strip().startswith("-----BEGIN"):
        print("\n실패: private_key 형식이 PEM이 아닙니다. Secrets를 다시 생성하세요.")
        return 1

    try:
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=SCOPES
        )
        service = build("sheets", "v4", credentials=creds)
        meta = (
            service.spreadsheets()
            .get(spreadsheetId=get_google_sheet_id(), fields="properties.title")
            .execute()
        )
        title = meta.get("properties", {}).get("title", "?")
        print(f"\n성공: 시트 접근 OK — 「{title}」")
        print("이 상태면 secrets.toml 을 Cloud에 붙여넣고 Reboot 하면 됩니다.")
        return 0
    except Exception as exc:  # noqa: BLE001
        err = str(exc)
        print(f"\n실패: {err}")
        if "Invalid JWT Signature" in err or "invalid_grant" in err:
            print(
                "\n→ GCP에서 JSON 키를 **새로 발급**해야 합니다.\n"
                "  IAM → 서비스 계정 → logger@h-bridge-data... → 키 추가 → JSON\n"
                "  새 파일로 service_account.json 교체 후:\n"
                "  py -3 scripts/build_streamlit_secrets.py\n"
                "  py -3 scripts/verify_sheets.py"
            )
        elif "403" in err or "permission" in err.lower():
            print(f"\n→ 시트 공유에 {email} 을 **편집자**로 추가하세요.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
