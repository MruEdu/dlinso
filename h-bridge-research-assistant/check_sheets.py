"""Google Sheets 연동 진단 스크립트 (일회성 점검용)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR / ".env")

from sheets_logger import SheetsLogger  # noqa: E402

EXPECTED_SHEET_ID = "1aamo-Sf330d6tlrmR-GkA494V66Ow2NcGU9x7E7vbrI"
SA_PATH = APP_DIR / "service_account.json"


def main() -> int:
    print(f"작업 폴더: {APP_DIR}")
    print(f"service_account.json 존재: {SA_PATH.is_file()}")

    if SA_PATH.is_file():
        try:
            data = json.loads(SA_PATH.read_text(encoding="utf-8"))
            email = data.get("client_email", "(없음)")
            print(f"서비스 계정 이메일: {email}")
        except Exception as exc:
            print(f"JSON 읽기 실패: {exc}")

    logger = SheetsLogger(SA_PATH)
    print(f"GOOGLE_SHEET_ID: {logger.sheet_id or '(미설정)'}")
    print(f"기대 시트 ID 일치: {logger.sheet_id == EXPECTED_SHEET_ID}")
    print(f"연결됨(is_connected): {logger.is_connected}")
    if logger.error_message:
        print(f"오류: {logger.error_message}")

    if logger.is_connected:
        ok, err = logger.ensure_header_row()
        print(f"헤더/시트 접근 테스트: {'성공' if ok else '실패'}")
        if err:
            print(f"  상세: {err}")
        if ok:
            ok2, err2 = logger.log_conversation(
                user_message="[연동 테스트]",
                assistant_message="dlinso sheet logging test OK",
                participant_id="TEST",
                password_hash="sha256:test",
                lang="en",
                gender="기타",
                age_group="30대",
                education="성인(일반)",
                user_message_ko="[연동 테스트]",
                assistant_message_ko="dlinso 시트 로깅 점검 완료",
                giant_name="마음의 정원사",
                current_concern="",
                summoned_narrative="테스트 자원",
                profile={
                    "emotional_richness": 55,
                    "reflection_depth": 60,
                    "agency": 50,
                    "relational_connection": 45,
                },
                narrative_stage="탐색",
                life_context="기타",
                narrative_themes="회복력; 가족",
                metaphors="등대",
                turning_points="진학",
            )
            print(f"테스트 행 기록: {'성공' if ok2 else '실패'}")
            if err2:
                print(f"  상세: {err2}")

    return 0 if logger.is_connected else 1


if __name__ == "__main__":
    sys.exit(main())
