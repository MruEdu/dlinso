"""Google Sheets — 글로벌 로그 · 문의 · 재방문 인증."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

from env_config import (
    apply_secrets_to_environ,
    credentials_source_label,
    get_google_sheet_id,
    get_service_account_info,
)

apply_secrets_to_environ()

EXPECTED_SHEET_ID = "1aamo-Sf330d6tlrmR-GkA494V66Ow2NcGU9x7E7vbrI"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "service_account.json"

MAIN_SHEET_DEFAULT = "시트1"
INQUIRIES_SHEET = "Inquiries"

HEADER_ROW = [
    "식별코드",
    "비밀번호해시",
    "언어",
    "성별",
    "연령대",
    "학력",
    "타임스탬프",
    "상담 거장",
    "현재 고민",
    "소환된 과거 서사",
    "사용자 질문_원문",
    "Gemini 답변_원문",
    "사용자 질문_한국어",
    "Gemini 답변_한국어",
    "admin_reply",
    "자아 주도성",
    "성찰 깊이",
    "정서적 풍요",
    "관계성",
    "맥락",
    "삶의 이야기 진행도",
    "Narrative_Themes",
    "Metaphors",
    "Turning_Points",
]

INQUIRIES_HEADER = [
    "식별코드",
    "타임스탬프",
    "언어",
    "Inquiry_Type",
    "문의내용_원문",
    "문의내용_한국어",
    "Researcher_Affiliation",
    "Researcher_Contact",
    "admin_reply",
]

INQUIRY_TYPES = frozenset(
    {"general", "research_collab", "interview"}
)


def column_letter(index: int) -> str:
    """1-based column index → A, B, …, Z, AA, …"""
    if index < 1:
        return "A"
    letters = ""
    n = index
    while n > 0:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def main_sheet_last_column() -> str:
    return column_letter(len(HEADER_ROW))


def hash_password(password: str) -> str:
    digest = hashlib.sha256(password.strip().encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


class SheetsLogger:
    def __init__(self, service_account_path: str | Path | None = None) -> None:
        self.sheet_id = get_google_sheet_id()
        self._service_account_info: dict | None = None
        self.service_account_path: Path | None = None
        if service_account_path is not None:
            self.service_account_path = Path(service_account_path).resolve()
        else:
            default = Path(SERVICE_ACCOUNT_FILE)
            if default.is_file():
                self.service_account_path = default.resolve()
        self.service_account_email: str | None = None
        self.credentials_source: str = ""
        self.worksheet_title: str = MAIN_SHEET_DEFAULT
        self._sheet_titles: list[str] = []
        self._service = None
        self._error: str | None = None
        self._col: dict[str, int] = {h: i for i, h in enumerate(HEADER_ROW)}
        self._initialize()

    def _range(self, sheet_title: str, cells: str) -> str:
        title = sheet_title.replace("'", "''")
        return f"'{title}'!{cells}"

    def _main_range(self, cells: str) -> str:
        return self._range(self.worksheet_title, cells)

    def _resolve_service_account(self) -> dict | None:
        """st.secrets → 명시 경로 파일 → 기본 service_account.json."""
        info = get_service_account_info()
        if info:
            self.credentials_source = credentials_source_label()
            return info
        if self.service_account_path and self.service_account_path.is_file():
            try:
                data = json.loads(
                    self.service_account_path.read_text(encoding="utf-8")
                )
                if isinstance(data, dict):
                    self.credentials_source = str(self.service_account_path.name)
                    return data
            except (OSError, json.JSONDecodeError):
                return None
        return None

    def _initialize(self) -> None:
        if not self.sheet_id:
            self._error = (
                "GOOGLE_SHEET_ID가 설정되지 않았습니다. "
                "(Streamlit Secrets 또는 .env)"
            )
            return
        sa_data = self._resolve_service_account()
        if not sa_data:
            self._error = (
                "서비스 계정을 찾을 수 없습니다. "
                "Streamlit Cloud에서는 st.secrets['gcp_service_account'] "
                "또는 GOOGLE_SERVICE_ACCOUNT_JSON을 설정하거나, "
                "로컬에서는 service_account.json을 배치하세요."
            )
            return
        try:
            self._service_account_info = sa_data
            self.service_account_email = sa_data.get("client_email")
            credentials = service_account.Credentials.from_service_account_info(
                sa_data, scopes=SCOPES
            )
            self._service = build("sheets", "v4", credentials=credentials)
            self._load_sheet_meta()
        except Exception as exc:  # noqa: BLE001
            self._service = None
            self._error = f"Google Sheets 인증 실패: {exc}"

    def _load_sheet_meta(self) -> None:
        if self._service is None:
            return
        try:
            meta = (
                self._service.spreadsheets()
                .get(
                    spreadsheetId=self.sheet_id,
                    fields="spreadsheetId,sheets.properties.title",
                )
                .execute()
            )
            self._sheet_titles = [
                s["properties"]["title"] for s in meta.get("sheets", [])
            ]
            if self._sheet_titles:
                self.worksheet_title = self._sheet_titles[0]
        except Exception as exc:  # noqa: BLE001
            self._service = None
            self._error = f"시트 접근 불가: {exc}"

    def _ensure_sheet_exists(self, title: str, header: list[str]) -> None:
        if title in self._sheet_titles or self._service is None:
            return
        try:
            (
                self._service.spreadsheets()
                .batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body={
                        "requests": [
                            {"addSheet": {"properties": {"title": title}}}
                        ]
                    },
                )
                .execute()
            )
            self._sheet_titles.append(title)
            (
                self._service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.sheet_id,
                    range=self._range(title, "A1"),
                    valueInputOption="USER_ENTERED",
                    body={"values": [header]},
                )
                .execute()
            )
        except Exception:  # noqa: BLE001
            pass

    def _read_main_rows(self) -> list[list[str]]:
        if not self.is_connected:
            return []
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=self.sheet_id,
                    range=self._main_range(f"A2:{main_sheet_last_column()}"),
                )
                .execute()
            )
            return result.get("values", [])
        except Exception:  # noqa: BLE001
            return []

    def _cell(self, row: list[str], name: str) -> str:
        idx = self._col.get(name)
        if idx is None or idx >= len(row):
            return ""
        return row[idx].strip()

    def _is_conversation_row(self, row: list[str]) -> bool:
        user_q = self._cell(row, "사용자 질문_원문") or self._cell(row, "사용자 질문")
        if not user_q or user_q.startswith("["):
            return False
        assist = self._cell(row, "Gemini 답변_원문") or self._cell(row, "Gemini 답변")
        return bool(assist)

    @property
    def is_connected(self) -> bool:
        return self._service is not None and self._error is None

    @property
    def error_message(self) -> str | None:
        return self._error

    def ensure_header_row(self) -> tuple[bool, str | None]:
        if not self.is_connected:
            return False, self._error
        try:
            last_col = main_sheet_last_column()
            header_range = self._main_range(f"A1:{last_col}1")
            result = (
                self._service.spreadsheets()
                .values()
                .get(spreadsheetId=self.sheet_id, range=header_range)
                .execute()
            )
            values = result.get("values", [])
            if not values or values[0] != HEADER_ROW:
                (
                    self._service.spreadsheets()
                    .values()
                    .update(
                        spreadsheetId=self.sheet_id,
                        range=header_range,
                        valueInputOption="USER_ENTERED",
                        body={"values": [HEADER_ROW]},
                    )
                    .execute()
                )
            self._col = {h: i for i, h in enumerate(HEADER_ROW)}
            self._ensure_sheet_exists(INQUIRIES_SHEET, INQUIRIES_HEADER)
            return True, None
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    def nickname_exists(self, nickname: str) -> bool:
        nick = nickname.strip()
        for row in self._read_main_rows():
            if self._cell(row, "식별코드") == nick:
                return True
        return False

    def find_returning_user(
        self, nickname: str, password: str
    ) -> dict[str, Any] | None:
        nick = nickname.strip()
        pw_hash = hash_password(password)
        matching: list[list[str]] = []

        for row in self._read_main_rows():
            if self._cell(row, "식별코드") != nick:
                continue
            stored = self._cell(row, "비밀번호해시")
            if stored and stored != pw_hash:
                continue
            if not stored:
                continue
            matching.append(row)

        if not matching:
            return None

        latest = matching[-1]
        profile = {
            "participant_id": nick,
            "password_hash": pw_hash,
            "lang": self._cell(latest, "언어") or "ko",
            "gender": self._cell(latest, "성별"),
            "age_group": self._cell(latest, "연령대"),
            "life_stage": self._cell(latest, "학력"),
        }

        turns: list[dict[str, str]] = []
        for row in matching:
            if not self._is_conversation_row(row):
                continue
            turns.append(
                {
                    "user": self._cell(row, "사용자 질문_원문")
                    or self._cell(row, "사용자 질문"),
                    "assistant": self._cell(row, "Gemini 답변_원문")
                    or self._cell(row, "Gemini 답변"),
                }
            )

        meta = self.get_admin_reply_meta(nick)
        return {
            "profile": profile,
            "recent_turns": turns[-5:],
            "last_topic": turns[-1]["user"][:100] if turns else "",
            "admin_reply": meta.get("reply", ""),
            "admin_reply_type": meta.get("inquiry_type", "general"),
        }

    def get_admin_reply(self, nickname: str) -> str:
        """Inquiries 시트 또는 메인 시트 admin_reply 최신값."""
        return self.get_admin_reply_meta(nickname).get("reply", "")

    def get_admin_reply_meta(self, nickname: str) -> dict[str, str]:
        """답변 본문 + 문의 유형(연구 협업 강조 UI용)."""
        nick = nickname.strip()
        meta = self._get_inquiry_admin_reply_meta(nick)
        if meta.get("reply"):
            return meta
        for row in reversed(self._read_main_rows()):
            if self._cell(row, "식별코드") != nick:
                continue
            ar = self._cell(row, "admin_reply")
            if ar:
                return {"reply": ar, "inquiry_type": "general"}
        return {"reply": "", "inquiry_type": "general"}

    def _inquiry_col_index(self, header: str) -> int:
        try:
            return INQUIRIES_HEADER.index(header)
        except ValueError:
            return -1

    def _get_inquiry_admin_reply_meta(self, nickname: str) -> dict[str, str]:
        if not self.is_connected or INQUIRIES_SHEET not in self._sheet_titles:
            return {"reply": "", "inquiry_type": "general"}
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=self.sheet_id,
                    range=self._range(INQUIRIES_SHEET, "A2:I"),
                )
                .execute()
            )
            rows = result.get("values", [])
            i_type = self._inquiry_col_index("Inquiry_Type")
            i_reply = self._inquiry_col_index("admin_reply")
            for row in reversed(rows):
                if not row or row[0].strip() != nickname:
                    continue
                reply = ""
                if i_reply >= 0 and len(row) > i_reply:
                    reply = row[i_reply].strip()
                if not reply and len(row) >= 5:
                    reply = row[4].strip() if len(row) == 5 else ""
                if reply:
                    itype = "general"
                    if i_type >= 0 and len(row) > i_type and row[i_type].strip():
                        itype = row[i_type].strip()
                    return {"reply": reply, "inquiry_type": itype}
        except Exception:  # noqa: BLE001
            pass
        return {"reply": "", "inquiry_type": "general"}

    def log_inquiry(
        self,
        participant_id: str,
        message: str,
        *,
        lang: str = "ko",
        inquiry_type: str = "general",
        message_ko: str = "",
        researcher_affiliation: str = "",
        researcher_contact: str = "",
    ) -> tuple[bool, str | None]:
        if not self.is_connected:
            return False, self._error
        self._ensure_sheet_exists(INQUIRIES_SHEET, INQUIRIES_HEADER)
        itype = inquiry_type if inquiry_type in INQUIRY_TYPES else "general"
        u_ko = message_ko or (message if lang == "ko" else "")
        try:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [""] * len(INQUIRIES_HEADER)
            row[0] = participant_id
            row[1] = ts
            row[2] = lang
            row[3] = itype
            row[4] = message
            row[5] = u_ko
            row[6] = researcher_affiliation
            row[7] = researcher_contact
            row[8] = ""
            (
                self._service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.sheet_id,
                    range=self._range(
                        INQUIRIES_SHEET, f"A:{column_letter(len(INQUIRIES_HEADER))}"
                    ),
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [row]},
                )
                .execute()
            )
            return True, None
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    def log_conversation(
        self,
        user_message: str,
        assistant_message: str,
        *,
        participant_id: str = "",
        user_id: str = "",
        password_hash: str = "",
        lang: str = "ko",
        gender: str = "",
        age_group: str = "",
        education: str = "",
        life_stage: str = "",
        user_message_ko: str = "",
        assistant_message_ko: str = "",
        giant_name: str = "마음의 정원사",
        partner_label: str = "",
        giant: str = "",
        current_concern: str = "",
        summoned_narrative: str = "",
        admin_reply: str = "",
        profile: dict[str, float] | None = None,
        life_context: str = "",
        narrative_stage: str = "",
        narrative_themes: str = "",
        metaphors: str = "",
        turning_points: str = "",
    ) -> tuple[bool, str | None]:
        if not self.is_connected:
            return False, self._error

        profile = profile or {}
        code = (participant_id or user_id or "").strip()
        edu = (education or life_stage or "").strip()
        counselor = giant_name or partner_label or giant or "마음의 정원사"
        u_ko = user_message_ko or (user_message if lang == "ko" else "")
        a_ko = assistant_message_ko or (assistant_message if lang == "ko" else "")

        try:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [""] * len(HEADER_ROW)
            row[self._col["식별코드"]] = code
            row[self._col["비밀번호해시"]] = password_hash or ""
            row[self._col["언어"]] = lang
            row[self._col["성별"]] = gender
            row[self._col["연령대"]] = age_group
            row[self._col["학력"]] = edu
            row[self._col["타임스탬프"]] = ts
            row[self._col["상담 거장"]] = counselor
            row[self._col["현재 고민"]] = current_concern
            row[self._col["소환된 과거 서사"]] = summoned_narrative
            row[self._col["사용자 질문_원문"]] = user_message
            row[self._col["Gemini 답변_원문"]] = assistant_message
            row[self._col["사용자 질문_한국어"]] = u_ko
            row[self._col["Gemini 답변_한국어"]] = a_ko
            row[self._col["admin_reply"]] = admin_reply
            row[self._col["자아 주도성"]] = str(
                round(float(profile.get("agency", 0)), 1)
            )
            row[self._col["성찰 깊이"]] = str(
                round(float(profile.get("reflection_depth", 0)), 1)
            )
            row[self._col["정서적 풍요"]] = str(
                round(float(profile.get("emotional_richness", 0)), 1)
            )
            row[self._col["관계성"]] = str(
                round(float(profile.get("relational_connection", 0)), 1)
            )
            row[self._col["맥락"]] = life_context
            row[self._col["삶의 이야기 진행도"]] = narrative_stage
            if "Narrative_Themes" in self._col:
                row[self._col["Narrative_Themes"]] = narrative_themes
            if "Metaphors" in self._col:
                row[self._col["Metaphors"]] = metaphors
            if "Turning_Points" in self._col:
                row[self._col["Turning_Points"]] = turning_points

            last_col = main_sheet_last_column()
            (
                self._service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.sheet_id,
                    range=self._main_range(f"A:{last_col}"),
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [row]},
                )
                .execute()
            )
            return True, None
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    def log_registration(
        self,
        *,
        participant_id: str,
        password_hash: str,
        lang: str = "ko",
        gender: str = "",
        age_group: str = "",
        education: str = "",
    ) -> tuple[bool, str | None]:
        return self.log_conversation(
            user_message="[신규 방문 등록]",
            assistant_message="dlinso narrative research session started.",
            participant_id=participant_id,
            password_hash=password_hash,
            lang=lang,
            gender=gender,
            age_group=age_group,
            education=education,
            user_message_ko="[신규 방문 등록]",
            assistant_message_ko="dlinso 서사 연구 세션 시작",
            giant_name="마음의 정원사",
        )
