"""숲 · 연결의 서사 — 독립 SQLite (프로젝트 data/isolation.db)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from database_manager import DatabaseManager
from env_config import get_isolation_database_path


class IsolationDatabaseManager(DatabaseManager):
    """dlinso.db 와 분리된 숲 모듈 전용 저장소."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        super().__init__(db_path or get_isolation_database_path())

    def log_conversation(
        self,
        user_message: str,
        assistant_message: str,
        *,
        module_type: str = "isolation",
        **kwargs: Any,
    ) -> tuple[bool, str | None]:
        mod = (module_type or "isolation").strip() or "isolation"
        if mod == "lifespan":
            mod = "isolation"
        return super().log_conversation(
            user_message, assistant_message, module_type=mod, **kwargs
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
        ok, err = super().log_registration(
            participant_id=participant_id,
            password_hash=password_hash,
            lang=lang,
            gender=gender,
            age_group=age_group,
            education=education,
        )
        if ok:
            from database_manager import _sync_isolation_user_profile_to_supabase

            _sync_isolation_user_profile_to_supabase(
                self,
                participant_id,
                {
                    "password_hash": password_hash,
                    "lang": lang,
                    "gender": gender,
                    "age_group": age_group,
                    "life_stage": education,
                },
            )
        return ok, err

    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        super()._migrate_schema(conn)
        cols = {
            row[1]
            for row in conn.execute("PRAGMA table_info(narrative_logs)").fetchall()
        }
        if "isolation_signals_json" not in cols:
            conn.execute(
                "ALTER TABLE narrative_logs "
                "ADD COLUMN isolation_signals_json TEXT NOT NULL DEFAULT ''"
            )
