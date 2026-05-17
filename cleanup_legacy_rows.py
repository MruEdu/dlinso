"""메인 시트에서 구버전·테스트·열 밀림 행을 제거합니다."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR / ".env")

from sheets_logger import SheetsLogger  # noqa: E402

SA_PATH = APP_DIR / "service_account.json"


def _cell(logger: SheetsLogger, row: list[str], name: str) -> str:
    idx = logger._col.get(name)
    if idx is None or idx >= len(row):
        return ""
    return row[idx].strip()


def row_drop_reason(logger: SheetsLogger, row: list[str]) -> str | None:
    code = _cell(logger, row, "식별코드")
    if not code:
        return "empty id"
    if re.match(r"^\d{4}-\d{2}-\d{2}", code):
        return "legacy misaligned (timestamp in id)"
    if code.upper() == "TEST":
        return "test row"
    if len(_cell(logger, row, "성별")) > 40:
        return "misaligned columns"
    if _cell(logger, row, "사용자 질문_원문") in ("50",) and _cell(
        logger, row, "Gemini 답변_원문"
    ) in ("50",):
        return "misaligned columns"
    if re.match(r"^\d{4}-\d{2}-\d{2}", _cell(logger, row, "연령대")):
        return "misaligned columns"
    return None


def main() -> int:
    logger = SheetsLogger(SA_PATH)
    if not logger.is_connected:
        print(f"연결 실패: {logger.error_message}")
        return 1

    rows = logger._read_main_rows()
    to_drop: list[tuple[int, str]] = []
    for offset, row in enumerate(rows):
        sheet_row = offset + 2  # 1-based, row 1 = header
        reason = row_drop_reason(logger, row)
        if reason:
            to_drop.append((sheet_row, reason))

    if not to_drop:
        print("삭제할 행이 없습니다.")
        return 0

    meta = (
        logger._service.spreadsheets()
        .get(
            spreadsheetId=logger.sheet_id,
            fields="sheets.properties(sheetId,title)",
        )
        .execute()
    )
    sheet_id = None
    for sh in meta.get("sheets", []):
        if sh["properties"]["title"] == logger.worksheet_title:
            sheet_id = sh["properties"]["sheetId"]
            break
    if sheet_id is None:
        print("워크시트 ID를 찾을 수 없습니다.")
        return 1

    print(f"탭: {logger.worksheet_title} — 삭제 예정 {len(to_drop)}행")
    for r, why in to_drop:
        print(f"  행 {r}: {why}")

    # 아래 행부터 삭제해야 인덱스가 밀리지 않음
    requests = []
    for sheet_row, _ in sorted(to_drop, key=lambda x: x[0], reverse=True):
        start = sheet_row - 1  # 0-based
        requests.append(
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": start,
                        "endIndex": start + 1,
                    }
                }
            }
        )

    logger._service.spreadsheets().batchUpdate(
        spreadsheetId=logger.sheet_id,
        body={"requests": requests},
    ).execute()

    remaining = len(logger._read_main_rows())
    print(f"정리 완료. 남은 데이터 행: {remaining}행")
    return 0


if __name__ == "__main__":
    sys.exit(main())
