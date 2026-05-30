"""SQLite — 서사 동행자(Narrative Companion) 로컬 저장소."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from env_config import (
    APP_DIR,
    get_database_path,
    get_supabase_key,
    get_supabase_url,
    korea_now_str,
    resolve_storage_path,
)

COMPANION_NAME = "서사 동행자"
MAX_RESTORE_TURNS = 30
INQUIRY_TYPES = frozenset({"general", "research_collab", "interview"})

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    nickname                TEXT PRIMARY KEY,
    password_hash           TEXT NOT NULL,
    lang                    TEXT NOT NULL DEFAULT 'ko',
    gender                  TEXT NOT NULL DEFAULT '',
    age_group               TEXT NOT NULL DEFAULT '',
    life_stage              TEXT NOT NULL DEFAULT '',
    first_visit_at          TEXT NOT NULL,
    last_visit_at           TEXT NOT NULL,
    visit_count             INTEGER NOT NULL DEFAULT 1,
    total_turn_count        INTEGER NOT NULL DEFAULT 0,
    last_user_snippet       TEXT NOT NULL DEFAULT '',
    last_assistant_snippet  TEXT NOT NULL DEFAULT '',
    admin_reply             TEXT NOT NULL DEFAULT '',
    agency                  REAL NOT NULL DEFAULT 50,
    reflection_depth        REAL NOT NULL DEFAULT 50,
    emotional_richness      REAL NOT NULL DEFAULT 50,
    relational_connection   REAL NOT NULL DEFAULT 50,
    life_context            TEXT NOT NULL DEFAULT '',
    narrative_stage         TEXT NOT NULL DEFAULT '탐색',
    created_at              TEXT NOT NULL,
    updated_at              TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_nickname           TEXT NOT NULL REFERENCES users(nickname),
    role                    TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content                 TEXT NOT NULL DEFAULT '',
    content_ko              TEXT NOT NULL DEFAULT '',
    display                 TEXT NOT NULL DEFAULT '',
    visit_number            INTEGER NOT NULL DEFAULT 1,
    is_midpoint             INTEGER NOT NULL DEFAULT 0,
    is_system               INTEGER NOT NULL DEFAULT 0,
    turn_type               TEXT NOT NULL DEFAULT 'conversation',
    companion_name          TEXT NOT NULL DEFAULT '서사 동행자',
    created_at              TEXT NOT NULL,
    turn_index              INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS narrative_logs (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id         INTEGER REFERENCES conversations(id),
    user_nickname           TEXT NOT NULL,
    agency                  REAL NOT NULL DEFAULT 0,
    reflection_depth        REAL NOT NULL DEFAULT 0,
    emotional_richness      REAL NOT NULL DEFAULT 0,
    relational_connection   REAL NOT NULL DEFAULT 0,
    life_context            TEXT NOT NULL DEFAULT '',
    narrative_stage         TEXT NOT NULL DEFAULT '',
    narrative_themes        TEXT NOT NULL DEFAULT '',
    metaphors               TEXT NOT NULL DEFAULT '',
    turning_points          TEXT NOT NULL DEFAULT '',
    summoned_narrative      TEXT NOT NULL DEFAULT '',
    current_concern         TEXT NOT NULL DEFAULT '',
    module_type             TEXT NOT NULL DEFAULT 'lifespan',
    learning_audience       TEXT NOT NULL DEFAULT '',
    learning_signals_json TEXT NOT NULL DEFAULT '',
    created_at              TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inquiries (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_nickname           TEXT NOT NULL,
    created_at              TEXT NOT NULL,
    lang                    TEXT NOT NULL DEFAULT 'ko',
    inquiry_type            TEXT NOT NULL DEFAULT 'general',
    message                 TEXT NOT NULL,
    message_ko              TEXT NOT NULL DEFAULT '',
    researcher_affiliation  TEXT NOT NULL DEFAULT '',
    researcher_contact      TEXT NOT NULL DEFAULT '',
    admin_reply             TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_nickname, id);
CREATE INDEX IF NOT EXISTS idx_narrative_logs_user ON narrative_logs(user_nickname, created_at);
CREATE INDEX IF NOT EXISTS idx_inquiries_user ON inquiries(user_nickname, created_at DESC);
"""


def hash_password(password: str) -> str:
    digest = hashlib.sha256(password.strip().encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _is_system_marker_message(text: str) -> bool:
    t = (text or "").strip()
    return t.startswith("[") and t.endswith("]")


def _is_midpoint_user_message(text: str) -> bool:
    t = (text or "").strip()
    return "[중간정리" in t or "[중간 정리" in t


class DatabaseManager:
    def __init__(self, db_path: Path | str | None = None) -> None:
        if db_path is not None:
            raw = str(db_path).strip()
            self.db_path = (
                resolve_storage_path(raw, get_database_path())
                if raw
                else get_database_path()
            )
        else:
            self.db_path = get_database_path()
        self._error: str | None = None
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.ensure_schema()
        except Exception as exc:  # noqa: BLE001
            self._error = str(exc)

    @property
    def is_connected(self) -> bool:
        return self._error is None

    @property
    def error_message(self) -> str | None:
        return self._error

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        """기존 DB에 컬럼 추가."""
        cols = {
            row[1]
            for row in conn.execute("PRAGMA table_info(narrative_logs)").fetchall()
        }
        if "module_type" not in cols:
            conn.execute(
                "ALTER TABLE narrative_logs "
                "ADD COLUMN module_type TEXT NOT NULL DEFAULT 'lifespan'"
            )
        if "learning_audience" not in cols:
            conn.execute(
                "ALTER TABLE narrative_logs "
                "ADD COLUMN learning_audience TEXT NOT NULL DEFAULT ''"
            )
        if "learning_signals_json" not in cols:
            conn.execute(
                "ALTER TABLE narrative_logs "
                "ADD COLUMN learning_signals_json TEXT NOT NULL DEFAULT ''"
            )

    def ensure_schema(self) -> tuple[bool, str | None]:
        if self._error:
            return False, self._error
        try:
            with self._connect() as conn:
                conn.executescript(SCHEMA_SQL)
                self._migrate_schema(conn)
            return True, None
        except Exception as exc:  # noqa: BLE001
            self._error = str(exc)
            return False, str(exc)

    ensure_header_row = ensure_schema

    def nickname_exists(self, nickname: str) -> bool:
        nick = nickname.strip()
        if not nick or not self.is_connected:
            return False
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM users WHERE nickname = ?", (nick,)
            ).fetchone()
            return row is not None

    def get_participant_turn_count(self, nickname: str) -> int:
        nick = nickname.strip()
        if not nick or not self.is_connected:
            return 0
        with self._connect() as conn:
            row = conn.execute(
                "SELECT total_turn_count FROM users WHERE nickname = ?", (nick,)
            ).fetchone()
            return int(row["total_turn_count"]) if row else 0

    def get_admin_reply_meta(self, nickname: str) -> dict[str, str]:
        nick = nickname.strip()
        if not nick or not self.is_connected:
            return {"reply": "", "inquiry_type": "general"}
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT admin_reply, inquiry_type FROM inquiries
                WHERE user_nickname = ? AND admin_reply != ''
                ORDER BY id DESC LIMIT 1
                """,
                (nick,),
            ).fetchone()
            if row and row["admin_reply"]:
                return {
                    "reply": str(row["admin_reply"]),
                    "inquiry_type": str(row["inquiry_type"] or "general"),
                }
            user = conn.execute(
                "SELECT admin_reply FROM users WHERE nickname = ?", (nick,)
            ).fetchone()
            if user and user["admin_reply"]:
                return {"reply": str(user["admin_reply"]), "inquiry_type": "general"}
        return {"reply": "", "inquiry_type": "general"}

    def _user_row_to_profile(self, row: sqlite3.Row, password_hash: str) -> dict[str, str]:
        return {
            "participant_id": str(row["nickname"]),
            "password_hash": password_hash,
            "lang": str(row["lang"] or "ko"),
            "gender": str(row["gender"] or ""),
            "age_group": str(row["age_group"] or ""),
            "life_stage": str(row["life_stage"] or ""),
        }

    def _build_restored_messages(
        self, rows: list[sqlite3.Row]
    ) -> tuple[list[dict[str, Any]], bool, int]:
        entries: list[dict[str, Any]] = []
        has_midpoint = False
        logged_user_turns = 0
        i = 0
        while i < len(rows):
            row = rows[i]
            role = str(row["role"])
            content = str(row["content"] or "")
            display = str(row["display"] or content)

            if role == "assistant" and int(row["is_midpoint"]):
                has_midpoint = True
                entries.append(
                    {
                        "role": "assistant",
                        "content": content,
                        "display": display,
                        "midpoint": True,
                    }
                )
                i += 1
                continue

            if role == "user":
                if int(row["is_system"]) or (
                    content.startswith("[") and not _is_midpoint_user_message(content)
                ):
                    i += 1
                    continue
                if _is_midpoint_user_message(content):
                    i += 1
                    if i < len(rows) and str(rows[i]["role"]) == "assistant":
                        has_midpoint = True
                        ac = str(rows[i]["content"] or "")
                        ad = str(rows[i]["display"] or ac)
                        entries.append(
                            {
                                "role": "assistant",
                                "content": ac,
                                "display": ad,
                                "midpoint": True,
                            }
                        )
                        i += 1
                    continue

                logged_user_turns += 1
                entries.append(
                    {"role": "user", "content": content, "display": display}
                )
                i += 1
                if i < len(rows) and str(rows[i]["role"]) == "assistant":
                    ac = str(rows[i]["content"] or "")
                    ad = str(rows[i]["display"] or ac)
                    if not int(rows[i]["is_system"]):
                        entries.append(
                            {"role": "assistant", "content": ac, "display": ad}
                        )
                    i += 1
                continue

            i += 1

        max_msgs = MAX_RESTORE_TURNS * 2 + (2 if has_midpoint else 0)
        if len(entries) > max_msgs:
            entries = entries[-max_msgs:]
        return entries, has_midpoint, logged_user_turns

    def find_returning_user(
        self, nickname: str, password: str
    ) -> dict[str, Any] | None:
        nick = nickname.strip()
        pw_hash = hash_password(password)
        if not nick or not self.is_connected:
            return None
        with self._connect() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE nickname = ? AND password_hash = ?",
                (nick, pw_hash),
            ).fetchone()
            if not user:
                return None
            msg_rows = conn.execute(
                """
                SELECT * FROM conversations
                WHERE user_nickname = ?
                ORDER BY id ASC
                """,
                (nick,),
            ).fetchall()

        restored_messages, has_midpoint, logged_user_turns = (
            self._build_restored_messages(list(msg_rows))
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

        total_turn_count = max(self.get_participant_turn_count(nick), logged_user_turns)
        meta = self.get_admin_reply_meta(nick)
        last_module_type = "lifespan"
        last_learning_audience = ""
        if msg_rows:
            last_row = msg_rows[-1]
            try:
                last_module_type = (
                    str(last_row["module_type"] or "lifespan").strip() or "lifespan"
                )
            except (KeyError, IndexError, TypeError):
                last_module_type = "lifespan"
            try:
                last_learning_audience = str(
                    last_row["learning_audience"] or ""
                ).strip()
            except (KeyError, IndexError, TypeError):
                last_learning_audience = ""
        return {
            "profile": self._user_row_to_profile(user, pw_hash),
            "recent_turns": recent_turns[-MAX_RESTORE_TURNS:],
            "restored_messages": restored_messages,
            "total_turn_count": total_turn_count,
            "has_midpoint": has_midpoint,
            "last_topic": recent_turns[-1]["user"][:100] if recent_turns else "",
            "admin_reply": meta.get("reply", ""),
            "admin_reply_type": meta.get("inquiry_type", "general"),
            "last_module_type": last_module_type,
            "last_learning_audience": last_learning_audience,
        }

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
        nick = participant_id.strip()
        if not nick:
            return False, "nickname is empty"
        if not self.is_connected:
            return False, self._error
        try:
            now = korea_now_str()
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT * FROM users WHERE nickname = ?", (nick,)
                ).fetchone()
                if not row:
                    return False, "user not found"
                visits = int(row["visit_count"]) + 1
                conn.execute(
                    """
                    UPDATE users SET
                        last_visit_at = ?, visit_count = ?,
                        password_hash = COALESCE(NULLIF(?, ''), password_hash),
                        lang = COALESCE(NULLIF(?, ''), lang),
                        gender = COALESCE(NULLIF(?, ''), gender),
                        age_group = COALESCE(NULLIF(?, ''), age_group),
                        life_stage = COALESCE(NULLIF(?, ''), life_stage),
                        updated_at = ?
                    WHERE nickname = ?
                    """,
                    (
                        now,
                        visits,
                        password_hash,
                        lang,
                        gender,
                        age_group,
                        life_stage,
                        now,
                        nick,
                    ),
                )
            return True, None
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    def _upsert_user_on_register(
        self,
        conn: sqlite3.Connection,
        *,
        nickname: str,
        password_hash: str,
        lang: str,
        gender: str,
        age_group: str,
        life_stage: str,
    ) -> None:
        now = korea_now_str()
        conn.execute(
            """
            INSERT INTO users (
                nickname, password_hash, lang, gender, age_group, life_stage,
                first_visit_at, last_visit_at, visit_count, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(nickname) DO UPDATE SET
                password_hash = excluded.password_hash,
                lang = excluded.lang,
                gender = excluded.gender,
                age_group = excluded.age_group,
                life_stage = excluded.life_stage,
                last_visit_at = excluded.last_visit_at,
                updated_at = excluded.updated_at
            """,
            (
                nickname,
                password_hash,
                lang,
                gender,
                age_group,
                life_stage,
                now,
                now,
                now,
                now,
            ),
        )

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
            assistant_message="dlinso Narrative Companion session started.",
            participant_id=participant_id,
            password_hash=password_hash,
            lang=lang,
            gender=gender,
            age_group=age_group,
            education=education,
            life_stage=education,
            turn_type="registration",
        )

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
        giant_name: str = "",
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
        turn_type: str = "conversation",
        module_type: str = "lifespan",
        learning_audience: str = "",
        learning_signals_json: str = "",
    ) -> tuple[bool, str | None]:
        if not self.is_connected:
            return False, self._error

        profile = profile or {}
        nick = (participant_id or user_id or "").strip()
        edu = (education or life_stage or "").strip()
        companion = giant_name or partner_label or giant or COMPANION_NAME
        u_ko = user_message_ko or (user_message if lang == "ko" else "")
        a_ko = assistant_message_ko or (assistant_message if lang == "ko" else "")
        count_as_turn = not _is_system_marker_message(user_message)
        is_midpoint = _is_midpoint_user_message(user_message)
        is_system = _is_system_marker_message(user_message)
        now = korea_now_str()

        if not nick:
            return False, "participant_id is empty"

        try:
            with self._connect() as conn:
                existing = conn.execute(
                    "SELECT nickname, visit_count FROM users WHERE nickname = ?", (nick,)
                ).fetchone()
                if not existing:
                    self._upsert_user_on_register(
                        conn,
                        nickname=nick,
                        password_hash=password_hash,
                        lang=lang,
                        gender=gender,
                        age_group=age_group,
                        life_stage=edu,
                    )
                    visit_no = 1
                else:
                    visit_no = int(existing["visit_count"])

                turn_row = conn.execute(
                    """
                    SELECT COALESCE(MAX(turn_index), 0) FROM conversations
                    WHERE user_nickname = ? AND visit_number = ?
                    """,
                    (nick, visit_no),
                ).fetchone()
                turn_index = int(turn_row[0]) + 1

                conn.execute(
                    """
                    INSERT INTO conversations (
                        user_nickname, role, content, content_ko, display,
                        visit_number, is_midpoint, is_system, turn_type,
                        companion_name, created_at, turn_index
                    ) VALUES (?, 'user', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nick,
                        user_message,
                        u_ko,
                        user_message,
                        visit_no,
                        1 if is_midpoint else 0,
                        1 if is_system else 0,
                        turn_type,
                        companion,
                        now,
                        turn_index,
                    ),
                )
                assist_cur = conn.execute(
                    """
                    INSERT INTO conversations (
                        user_nickname, role, content, content_ko, display,
                        visit_number, is_midpoint, is_system, turn_type,
                        companion_name, created_at, turn_index
                    ) VALUES (?, 'assistant', ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)
                    """,
                    (
                        nick,
                        assistant_message,
                        a_ko,
                        assistant_message,
                        visit_no,
                        1 if is_midpoint else 0,
                        turn_type,
                        companion,
                        now,
                        turn_index + 1,
                    ),
                )
                assist_id = int(assist_cur.lastrowid)

                conn.execute(
                    """
                    INSERT INTO narrative_logs (
                        conversation_id, user_nickname,
                        agency, reflection_depth, emotional_richness, relational_connection,
                        life_context, narrative_stage, narrative_themes, metaphors,
                        turning_points, summoned_narrative, current_concern,
                        module_type, learning_audience, learning_signals_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        assist_id,
                        nick,
                        float(profile.get("agency", 0)),
                        float(profile.get("reflection_depth", 0)),
                        float(profile.get("emotional_richness", 0)),
                        float(profile.get("relational_connection", 0)),
                        life_context,
                        narrative_stage,
                        narrative_themes,
                        metaphors,
                        turning_points,
                        summoned_narrative,
                        current_concern,
                        (module_type or "lifespan").strip() or "lifespan",
                        (learning_audience or "").strip(),
                        (learning_signals_json or "")[:8000],
                        now,
                    ),
                )

                user_snip = (user_message or "").strip().replace("\n", " ")[:280]
                assist_snip = (assistant_message or "").strip().replace("\n", " ")[:280]
                turns = self.get_participant_turn_count(nick)
                if count_as_turn:
                    turns += 1

                conn.execute(
                    """
                    UPDATE users SET
                        password_hash = COALESCE(NULLIF(?, ''), password_hash),
                        lang = COALESCE(NULLIF(?, ''), lang),
                        gender = COALESCE(NULLIF(?, ''), gender),
                        age_group = COALESCE(NULLIF(?, ''), age_group),
                        life_stage = COALESCE(NULLIF(?, ''), life_stage),
                        last_visit_at = ?,
                        total_turn_count = ?,
                        last_user_snippet = COALESCE(NULLIF(?, ''), last_user_snippet),
                        last_assistant_snippet = COALESCE(NULLIF(?, ''), last_assistant_snippet),
                        admin_reply = COALESCE(NULLIF(?, ''), admin_reply),
                        agency = ?,
                        reflection_depth = ?,
                        emotional_richness = ?,
                        relational_connection = ?,
                        life_context = COALESCE(NULLIF(?, ''), life_context),
                        narrative_stage = COALESCE(NULLIF(?, ''), narrative_stage),
                        updated_at = ?
                    WHERE nickname = ?
                    """,
                    (
                        password_hash,
                        lang,
                        gender,
                        age_group,
                        edu,
                        now,
                        turns,
                        user_snip,
                        assist_snip,
                        admin_reply,
                        float(profile.get("agency", 50)),
                        float(profile.get("reflection_depth", 50)),
                        float(profile.get("emotional_richness", 50)),
                        float(profile.get("relational_connection", 50)),
                        life_context,
                        narrative_stage,
                        now,
                        nick,
                    ),
                )
            return True, None
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

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
        itype = inquiry_type if inquiry_type in INQUIRY_TYPES else "general"
        u_ko = message_ko or (message if lang == "ko" else "")
        nick = participant_id.strip()
        if not nick:
            return False, "participant_id is empty"
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO inquiries (
                        user_nickname, created_at, lang, inquiry_type, message,
                        message_ko, researcher_affiliation, researcher_contact, admin_reply
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, '')
                    """,
                    (
                        nick,
                        korea_now_str(),
                        lang,
                        itype,
                        message,
                        u_ko,
                        researcher_affiliation,
                        researcher_contact,
                    ),
                )
            return True, None
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    def database_label(self) -> str:
        try:
            rel = self.db_path.relative_to(APP_DIR)
            return str(rel)
        except ValueError:
            return str(self.db_path)


# ---------------------------------------------------------------------------
# Supabase — 숲 모듈 클라우드 이중 저장 (로컬 SQLite 실패 시에만 중단)
# ---------------------------------------------------------------------------

ISOLATION_NARRATIVES_TABLE = "isolation_narratives"
_supabase_client: Any | None = None
_supabase_init_attempted = False


def _parse_signals_json(raw: str) -> dict[str, Any]:
    text = (raw or "").strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {"value": data}
    except json.JSONDecodeError:
        return {"raw": text[:8000]}


def get_supabase_client() -> Any | None:
    """Supabase 클라이언트 — URL·Key: st.secrets [supabase] 또는 .env."""
    global _supabase_client, _supabase_init_attempted
    if _supabase_client is not None:
        return _supabase_client
    if _supabase_init_attempted:
        return None
    _supabase_init_attempted = True

    url = get_supabase_url()
    key = get_supabase_key()
    if not url or not key:
        return None
    try:
        from supabase import create_client

        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception:  # noqa: BLE001
        _supabase_client = None
        return None


def is_supabase_configured() -> bool:
    return bool(get_supabase_url() and get_supabase_key())


def sync_isolation_narrative_to_supabase(
    *,
    nickname: str,
    user_input: str,
    ai_response: str,
    signals_json: str = "",
) -> tuple[bool, str | None]:
    """
    isolation_narratives 테이블에 1행 INSERT.
    실패해도 예외를 밖으로 던지지 않음 — 호출부에서 로그만 남김.
    """
    client = get_supabase_client()
    if client is None:
        return False, "Supabase URL/Key 미설정 또는 클라이언트 초기화 실패"

    row = {
        "nickname": (nickname or "").strip(),
        "user_input": user_input or "",
        "ai_response": ai_response or "",
        "signals_json": _parse_signals_json(signals_json),
    }
    try:
        client.table(ISOLATION_NARRATIVES_TABLE).insert(row).execute()
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def notify_supabase_sync(ok: bool, err: str | None = None) -> None:
    if ok:
        msg = "✅ Supabase 클라우드 DB 저장 완료"
        try:
            print(msg, flush=True)
        except UnicodeEncodeError:
            print("[OK] Supabase 클라우드 DB 저장 완료", flush=True)
    else:
        detail = f": {err}" if err else ""
        msg = f"❌ Supabase Sync Failed{detail}"
        try:
            print(msg, flush=True)
        except UnicodeEncodeError:
            print(f"[FAIL] Supabase Sync Failed{detail}", flush=True)


def log_isolation_turn_dual(
    db: "DatabaseManager",
    *,
    nickname: str = "",
    user_message: str = "",
    assistant_message: str = "",
    signals_json: str = "",
    **log_kwargs: Any,
) -> tuple[bool, str | None]:
    """
    이중 저장: 1) 로컬 SQLite  2) Supabase isolation_narratives.
    로컬 실패 시 즉시 반환. Supabase 실패 시에도 로컬 성공이면 (True, None).
    """
    um = user_message or str(log_kwargs.get("user_message") or "")
    am = assistant_message or str(log_kwargs.get("assistant_message") or "")
    sig = (
        signals_json or str(log_kwargs.get("isolation_signals_json") or "") or ""
    )[:8000]
    log_kwargs = dict(log_kwargs)
    log_kwargs.setdefault("module_type", "isolation")
    log_kwargs["isolation_signals_json"] = sig

    if not db.is_connected:
        return False, db.error_message or "database not connected"

    db.ensure_schema()
    ok, err = db.log_conversation(
        user_message=um,
        assistant_message=am,
        **log_kwargs,
    )
    if not ok:
        return ok, err

    nick = nickname or str(log_kwargs.get("participant_id") or "")
    if is_supabase_configured():
        sb_ok, sb_err = sync_isolation_narrative_to_supabase(
            nickname=nick,
            user_input=um,
            ai_response=am,
            signals_json=sig,
        )
        notify_supabase_sync(sb_ok, sb_err)
    return ok, err
