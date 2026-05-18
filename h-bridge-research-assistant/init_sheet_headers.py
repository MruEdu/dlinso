"""새 구글 시트에 14열 헤더를 작성하고 서비스 계정 이메일을 출력합니다."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR / ".env")

from sheets_logger import HEADER_ROW, INQUIRIES_HEADER, SheetsLogger  # noqa: E402

SA_PATH = APP_DIR / "service_account.json"


def print_service_account_email() -> str | None:
    if not SA_PATH.is_file():
        print("\n" + "!" * 62)
        print("  service_account.json 파일이 없습니다.")
        print(f"  경로: {SA_PATH}")
        print("!" * 62 + "\n")
        return None

    data = json.loads(SA_PATH.read_text(encoding="utf-8"))
    email = data.get("client_email", "")
    print("\n" + "=" * 62)
    print("   박사님 시트 공유용 — 서비스 계정 이메일 (편집자로 추가)")
    print("=" * 62)
    print(f"\n   >>>  {email}  <<<\n")
    print("=" * 62 + "\n")
    return email or None


def main() -> int:
    print(f"GOOGLE_SHEET_ID: {__import__('os').getenv('GOOGLE_SHEET_ID', '')}")
    print_service_account_email()

    logger = SheetsLogger(SA_PATH)
    if not logger.is_connected:
        print(f"연결 실패: {logger.error_message}")
        return 1

    ok, err = logger.ensure_header_row()
    if ok:
        print(f"메인 시트 헤더 {len(HEADER_ROW)}열 작성 완료:")
        print("  ", ", ".join(HEADER_ROW))
        print(f"Inquiries 시트: {', '.join(INQUIRIES_HEADER)}")
    else:
        print(f"헤더 작성 실패: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
