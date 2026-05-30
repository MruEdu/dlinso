"""숲 · 연결의 서사 — 독립 SQLite (프로젝트 data/isolation.db)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from database_manager import DatabaseManager
from env_config import get_isolation_database_path


class IsolationDatabaseManager(DatabaseManager):
    """dlinso.db 와 분리된 숲 모듈 전용 저장소."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        super().__init__(db_path or get_isolation_database_path())

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
