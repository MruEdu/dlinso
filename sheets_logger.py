"""Google Sheets — 글로벌 로그 · 문의 · 재방문 인증."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

from env_config import (
    apply_secrets_to_environ,
    credentials_source_label,
    get_google_sheet_id,
    get_service_account_info,
    korea_now_str,
)

apply_secrets_to_environ()

EXPECTED_SHEET_ID = "1aamo-Sf330d6tlrmR-GkA494V66Ow2NcGU9x7E7vbrI"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "service_account.json"

MAIN_SHEET_DEFAULT = "시트1"
INQUIRIES_SHEET = "Inquiries"
PARTICIPANTS_SHEET = "참여자"

PARTICIPANTS_HEADER = [
    "식별코드",
    "비밀번호해시",
    "언어",
    "성별",
    "연령대",
    "학력",
    "첫방문",
    "최근방문",
    "방문횟수",
    "총대화턴수",
    "최근사용자질문",
    "최근정원사답변",
    "admin_reply",
    "자아 주도성",
    "성찰 깊이",
    "정서적 풍요",
    "관계성",
    "맥락",
    "삶의 이야기 진행도",
]

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

# 재로그인 시 복원할 대화 쌍(사용자+정원사) 상한 — 예전 5쌍은 5/10·중간정리 소실 원인
MAX_RESTORE_TURNS = 30


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

    def _row_user_text(self, row: list[str]) -> str:
        return self._cell(row, "사용자 질문_원문") or self._cell(row, "사용자 질문")

    def _row_assistant_text(self, row: list[str]) -> str:
        return self._cell(row, "Gemini 답변_원문") or self._cell(row, "Gemini 답변")

    def _is_midpoint_row(self, row: list[str]) -> bool:
        user_q = self._row_user_text(row)
        return bool(user_q) and "중간정리" in user_q and user_q.strip().startswith("[")

    def _is_conversation_row(self, row: list[str]) -> bool:
        user_q = self._row_user_text(row)
        if not user_q or user_q.startswith("["):
            return False
        return bool(self._row_assistant_text(row))

    @staticmethod
    def _is_system_marker_message(text: str) -> bool:
        return (text or "").strip().startswith("[")

    def _read_sheet_data_rows(self, sheet_title: str, last_col: str) -> list[list[str]]:
        if not self.is_connected or sheet_title not in self._sheet_titles:
            return []
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=self.sheet_id,
                    range=self._range(sheet_title, f"A2:{last_col}"),
                )
                .execute()
            )
            return result.get("values", [])
        except Exception:  # noqa: BLE001
            return []

    def _participants_last_col(self) -> str:
        return column_letter(len(PARTICIPANTS_HEADER))

    def _find_participant_sheet_row(self, nickname: str) -> int | None:
        """참여자 시트에서 식별코드 행 번호(1-based). 없으면 None."""
        nick = nickname.strip()
        if not nick:
            return None
        for offset, row in enumerate(
            self._read_sheet_data_rows(
                PARTICIPANTS_SHEET, self._participants_last_col()
            )
        ):
            if row and row[0].strip() == nick:
                return offset + 2
        return None

    def _participant_cell(self, row: list[str], header: str) -> str:
        try:
            idx = PARTICIPANTS_HEADER.index(header)
        except ValueError:
            return ""
        if idx >= len(row):
            return ""
        return row[idx].strip()

    def _write_participants_row(
        self, row_number: int | None, values: list[str]
    ) -> None:
        last_col = self._participants_last_col()
        if row_number is not None:
            (
                self._service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.sheet_id,
                    range=self._range(
                        PARTICIPANTS_SHEET, f"A{row_number}:{last_col}"
                    ),
                    valueInputOption="USER_ENTERED",
                    body={"values": [values]},
                )
                .execute()
            )
            return
        (
            self._service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.sheet_id,
                range=self._range(PARTICIPANTS_SHEET, f"A:{last_col}"),
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [values]},
            )
            .execute()
        )

    def record_visit(
        self,
        *,
        participant_id: str,
        password_hash: str = "",
        lang: str = "ko",
        gender: str = "",
        age_group: str = "",
        life_stage: str = "",
    ) -> tuple[bool, str | None]:
        """로그인·가입 시 방문 1회 기록 — 참여자 시트에 닉네임당 한 줄."""
        if not self.is_connected:
            return False, self._error
        self._ensure_sheet_exists(PARTICIPANTS_SHEET, PARTICIPANTS_HEADER)
        nick = participant_id.strip()
        if not nick:
            return False, "식별코드가 비어 있습니다."
        try:
            now = korea_now_str()
            row_no = self._find_participant_sheet_row(nick)
            existing: list[str] = []
            if row_no is not None:
                rows = self._read_sheet_data_rows(
                    PARTICIPANTS_SHEET, self._participants_last_col()
                )
                idx = row_no - 2
                if 0 <= idx < len(rows):
                    existing = rows[idx]

            visits = 1
            if existing:
                try:
                    visits = int(self._participant_cell(existing, "방문횟수") or "0") + 1
                except ValueError:
                    visits = 1
            turns = 0
            if existing:
                try:
                    turns = int(self._participant_cell(existing, "총대화턴수") or "0")
                except ValueError:
                    turns = 0

            first_seen = self._participant_cell(existing, "첫방문") if existing else ""
            if not first_seen:
                first_seen = now

            pw = password_hash or self._participant_cell(existing, "비밀번호해시")
            values = [
                nick,
                pw,
                lang or self._participant_cell(existing, "언어") or "ko",
                gender or self._participant_cell(existing, "성별"),
                age_group or self._participant_cell(existing, "연령대"),
                life_stage or self._participant_cell(existing, "학력"),
                first_seen,
                now,
                str(visits),
                str(turns),
                self._participant_cell(existing, "최근사용자질문"),
                self._participant_cell(existing, "최근정원사답변"),
                self._participant_cell(existing, "admin_reply"),
                self._participant_cell(existing, "자아 주도성"),
                self._participant_cell(existing, "성찰 깊이"),
                self._participant_cell(existing, "정서적 풍요"),
                self._participant_cell(existing, "관계성"),
                self._participant_cell(existing, "맥락"),
                self._participant_cell(existing, "삶의 이야기 진행도"),
            ]
            self._write_participants_row(row_no, values)
            return True, None
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    def _upsert_participant_from_turn(
        self,
        *,
        participant_id: str,
        password_hash: str,
        lang: str,
        gender: str,
        age_group: str,
        education: str,
        user_message: str,
        assistant_message: str,
        admin_reply: str,
        profile: dict[str, float],
        life_context: str,
        narrative_stage: str,
        count_as_turn: bool,
    ) -> None:
        if not self.is_connected:
            return
        self._ensure_sheet_exists(PARTICIPANTS_SHEET, PARTICIPANTS_HEADER)
        nick = participant_id.strip()
        if not nick:
            return

        now = korea_now_str()
        row_no = self._find_participant_sheet_row(nick)
        existing: list[str] = []
        if row_no is not None:
            rows = self._read_sheet_data_rows(
                PARTICIPANTS_SHEET, self._participants_last_col()
            )
            idx = row_no - 2
            if 0 <= idx < len(rows):
                existing = rows[idx]

        visits = 1
        if existing:
            try:
                visits = int(self._participant_cell(existing, "방문횟수") or "1")
            except ValueError:
                visits = 1

        turns = 0
        if existing:
            try:
                turns = int(self._participant_cell(existing, "총대화턴수") or "0")
            except ValueError:
                turns = 0
        if count_as_turn:
            turns += 1

        first_seen = self._participant_cell(existing, "첫방문") if existing else now
        user_snip = (user_message or "").strip().replace("\n", " ")[:280]
        assist_snip = (assistant_message or "").strip().replace("\n", " ")[:280]

        values = [
            nick,
            password_hash or self._participant_cell(existing, "비밀번호해시"),
            lang or self._participant_cell(existing, "언어") or "ko",
            gender or self._participant_cell(existing, "성별"),
            age_group or self._participant_cell(existing, "연령대"),
            education or self._participant_cell(existing, "학력"),
            first_seen,
            now,
            str(visits),
            str(turns),
            user_snip or self._participant_cell(existing, "최근사용자질문"),
            assist_snip or self._participant_cell(existing, "최근정원사답변"),
            admin_reply or self._participant_cell(existing, "admin_reply"),
            str(round(float(profile.get("agency", 0)), 1)),
            str(round(float(profile.get("reflection_depth", 0)), 1)),
            str(round(float(profile.get("emotional_richness", 0)), 1)),
            str(round(float(profile.get("relational_connection", 0)), 1)),
            life_context or self._participant_cell(existing, "맥락"),
            narrative_stage or self._participant_cell(existing, "삶의 이야기 진행도"),
        ]
        self._write_participants_row(row_no, values)

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
            self._ensure_sheet_exists(PARTICIPANTS_SHEET, PARTICIPANTS_HEADER)
            return True, None
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    def get_participant_turn_count(self, nickname: str) -> int:
        """참여자 시트의 누적 사용자 턴 수."""
        nick = nickname.strip()
        if not nick or not self.is_connected:
            return 0
        row_no = self._find_participant_sheet_row(nick)
        if row_no is None:
            return 0
        rows = self._read_sheet_data_rows(
            PARTICIPANTS_SHEET, self._participants_last_col()
        )
        idx = row_no - 2
        if idx < 0 or idx >= len(rows):
            return 0
        try:
            return int(self._participant_cell(rows[idx], "총대화턴수") or "0")
        except ValueError:
            return 0

    def _build_restored_messages(
        self, matching_rows: list[list[str]]
    ) -> tuple[list[dict[str, Any]], bool, int]:
        """시트 행 → 채팅 messages (중간정리 포함), has_midpoint, 로그상 사용자 턴 수."""
        entries: list[dict[str, Any]] = []
        has_midpoint = False
        logged_user_turns = 0
        for row in matching_rows:
            user_q = self._row_user_text(row)
            assist = self._row_assistant_text(row)
            if not assist:
                continue
            if self._is_midpoint_row(row):
                has_midpoint = True
                entries.append(
                    {
                        "role": "assistant",
                        "content": assist,
                        "display": assist,
                        "midpoint": True,
                    }
                )
                continue
            if not user_q or user_q.startswith("["):
                continue
            logged_user_turns += 1
            entries.append(
                {"role": "user", "content": user_q, "display": user_q}
            )
            entries.append(
                {"role": "assistant", "content": assist, "display": assist}
            )

        max_msgs = MAX_RESTORE_TURNS * 2 + (2 if has_midpoint else 0)
        if len(entries) > max_msgs:
            entries = entries[-max_msgs:]

        return entries, has_midpoint, logged_user_turns

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

        restored_messages, has_midpoint, logged_user_turns = (
            self._build_restored_messages(matching)
        )
        recent_turns: list[dict[str, str]] = []
        i = 0
        while i < len(restored_messages):
            msg = restored_messages[i]
            if msg.get("role") == "user":
                user_t = str(msg.get("content") or "")
                assist_t = ""
                if (
                    i + 1 < len(restored_messages)
                    and restored_messages[i + 1].get("role") == "assistant"
                    and not restored_messages[i + 1].get("midpoint")
                ):
                    assist_t = str(restored_messages[i + 1].get("content") or "")
                recent_turns.append({"user": user_t, "assistant": assist_t})
                i += 2 if assist_t else 1
            else:
                i += 1

        sheet_turns = self.get_participant_turn_count(nick)
        total_turn_count = max(sheet_turns, logged_user_turns)

        meta = self.get_admin_reply_meta(nick)
        return {
            "profile": profile,
            "recent_turns": recent_turns[-MAX_RESTORE_TURNS:],
            "restored_messages": restored_messages,
            "total_turn_count": total_turn_count,
            "has_midpoint": has_midpoint,
            "last_topic": recent_turns[-1]["user"][:100] if recent_turns else "",
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
            ts = korea_now_str()
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
            ts = korea_now_str()
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
            self._upsert_participant_from_turn(
                participant_id=code,
                password_hash=password_hash or "",
                lang=lang,
                gender=gender,
                age_group=age_group,
                education=edu,
                user_message=user_message,
                assistant_message=assistant_message,
                admin_reply=admin_reply,
                profile=profile,
                life_context=life_context,
                narrative_stage=narrative_stage,
                count_as_turn=not self._is_system_marker_message(user_message),
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
