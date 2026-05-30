"""SQLite .db 내용 간단 조회 — python scripts/peek_db.py"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def peek(path: Path) -> None:
    if not path.is_file():
        print(f"SKIP: not found - {path}")
        return
    print(f"\n=== {path.name} ===")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    tables = [
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
    ]
    print("테이블:", ", ".join(tables) or "(없음)")
    for table in ("users", "conversations", "narrative_logs", "inquiries"):
        if table in tables:
            n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table}: {n}행")
    rows = conn.execute(
        """
        SELECT user_nickname, role, substr(content, 1, 60) AS snippet, created_at
        FROM conversations
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()
    if rows:
        print("\n최근 대화 5건:")
        for r in rows:
            print(f"  [{r['created_at']}] {r['user_nickname']} | {r['role']}: {r['snippet']!r}")
    else:
        print("\n대화 기록 없음")
    conn.close()


def main() -> int:
    targets = [ROOT / "data" / "dlinso.db", ROOT / "data" / "isolation.db"]
    if len(sys.argv) > 1:
        targets = [Path(sys.argv[1])]
    for p in targets:
        peek(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
