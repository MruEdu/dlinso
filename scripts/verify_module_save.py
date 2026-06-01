#!/usr/bin/env python3
"""모듈별 저장·Supabase 경로 스모크 테스트 (로컬 .env 필요)."""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from database_manager import (  # noqa: E402
    DatabaseManager,
    is_supabase_configured,
    log_isolation_turn_dual,
)
from isolation_database_manager import IsolationDatabaseManager  # noqa: E402


def main() -> int:
    nick = f"verify_{uuid.uuid4().hex[:6]}"
    print(f"nickname={nick}  supabase={is_supabase_configured()}\n")

    db = DatabaseManager()
    ok1, e1 = db.log_conversation(
        "여정 테스트",
        "응답",
        participant_id=nick,
        password_hash="x",
        module_type="lifespan",
        lang="ko",
        gender="M",
        age_group="20",
        education="test",
        supabase_guest_id="should_be_ignored",
        isolation_signals_json="{}",
    )
    print(f"[{'OK' if ok1 else 'FAIL'}] 여정 lifespan  err={e1}")

    ok2, e2 = db.log_conversation(
        "학습 테스트",
        "응답",
        participant_id=nick,
        password_hash="x",
        module_type="learning",
        learning_audience="student",
        learning_signals_json=json.dumps({"thin_axis": "bloom"}),
        supabase_guest_id="ignored",
    )
    print(f"[{'OK' if ok2 else 'FAIL'}] 학습 learning  err={e2}")

    iso = IsolationDatabaseManager()
    ok3, e3 = log_isolation_turn_dual(
        iso,
        nickname=nick,
        user_message="숲 테스트",
        assistant_message="응답",
        participant_id=nick,
        password_hash="x",
        module_type="isolation",
        isolation_signals_json='{"source":"verify"}',
        supabase_guest_id="guest_verify",
        lang="ko",
        gender="M",
        age_group="20",
        education="test",
    )
    print(f"[{'OK' if ok3 else 'FAIL'}] 숲 isolation  err={e3}")

    if not (ok1 and ok2 and ok3):
        return 1
    print("\n전 모듈 로컬+Supabase 경로 OK. Table Editor에서 nickname 확인.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
