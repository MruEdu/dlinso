#!/usr/bin/env python3
"""
Supabase 통신선 강제 점검 — 가짜 1행 INSERT 후 Table Editor에서 확인.

  cd E:\\dlinso_v2
  pip install -r requirements.txt
  python scripts/force_db_test.py

성공 시 isolation_narratives 등에 test_force_db_* 닉네임 행이 생깁니다.
실패 시 RLS/키 오류 메시지가 그대로 출력됩니다.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from database_manager import (  # noqa: E402
    DLINSO_TURNS_TABLE,
    DLINSO_USERS_TABLE,
    ISOLATION_NARRATIVES_TABLE,
    NARRATIVE_ASSETS_TABLE,
    USER_SESSIONS_TABLE,
    get_supabase_client,
    get_supabase_url,
    is_supabase_configured,
    sync_conversation_turn_to_supabase,
    sync_isolation_narrative_to_supabase,
    sync_user_to_supabase,
)
from env_config import get_supabase_key  # noqa: E402


def _mask_key(key: str) -> str:
    k = (key or "").strip()
    if len(k) <= 12:
        return "(empty or too short)"
    return f"{k[:12]}..."


def main() -> int:
    print("=== dlinso Supabase force_db_test ===\n")
    url = get_supabase_url()
    key = get_supabase_key()
    print(f"URL: {url or '(empty)'}")
    print(f"KEY: {_mask_key(key)}")
    print(f"configured: {is_supabase_configured()}\n")

    if not is_supabase_configured():
        print("FAIL: SUPABASE_URL / SUPABASE_KEY 가 .env 또는 환경에 없습니다.")
        return 1

    client = get_supabase_client()
    if client is None:
        print("FAIL: Supabase 클라이언트 초기화 실패")
        return 1

    nick = f"test_force_db_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    print(f"테스트 닉네임: {nick}\n")

    results: list[tuple[str, bool, str | None]] = []

    ok, err = sync_isolation_narrative_to_supabase(
        nickname=nick,
        user_input="[force_db_test] 사용자 가짜 발화",
        ai_response="[force_db_test] AI 가짜 응답",
        signals_json=json.dumps(
            {
                "source": "force_db_test",
                "anchor_quote": "통신선 점검",
                "recovery_strength": "weak",
            },
            ensure_ascii=False,
        ),
    )
    results.append((ISOLATION_NARRATIVES_TABLE, ok, err))

    ok, err = sync_user_to_supabase(
        nickname=nick,
        password_hash="",
        lang="ko",
        total_turn_count=1,
        last_user_snippet="force_db_test",
    )
    results.append((DLINSO_USERS_TABLE, ok, err))

    ok, err = sync_conversation_turn_to_supabase(
        nickname=nick,
        module_type="lifespan",
        turn_type="conversation",
        user_input="[force_db_test] 여정 테스트",
        ai_response="[force_db_test] 응답",
    )
    results.append((DLINSO_TURNS_TABLE, ok, err))

    # user_sessions · narrative_assets — 직접 INSERT
    try:
        client.table(USER_SESSIONS_TABLE).upsert(
            {
                "nickname": nick,
                "module_type": "lifespan",
                "session_context": {"force_db_test": True, "at": now},
                "metadata_json": {},
                "turn_count": 1,
                "asset_progress": 10.0,
            },
            on_conflict="nickname",
        ).execute()
        results.append((USER_SESSIONS_TABLE, True, None))
    except Exception as exc:  # noqa: BLE001
        results.append((USER_SESSIONS_TABLE, False, str(exc)))

    try:
        client.table(NARRATIVE_ASSETS_TABLE).insert(
            {
                "nickname": nick,
                "module_type": "lifespan",
                "raw_narrative": "force_db_test narrative",
                "core_competencies": ["통신점검"],
                "emotion_keywords": ["확인"],
                "scene_fragments": [],
                "deidentified": True,
                "source_snippet": "force_db_test",
            }
        ).execute()
        results.append((NARRATIVE_ASSETS_TABLE, True, None))
    except Exception as exc:  # noqa: BLE001
        results.append((NARRATIVE_ASSETS_TABLE, False, str(exc)))

    print("--- 결과 ---")
    failed = 0
    for table, ok_row, err_row in results:
        status = "OK" if ok_row else "FAIL"
        print(f"  [{status}] {table}" + (f" — {err_row}" if err_row else ""))
        if not ok_row:
            failed += 1

    print()
    if failed:
        print(
            f"{failed}개 테이블 실패. RLS/SQL 스크립트·publishable 키를 확인하세요."
        )
        return 2

    print("전 테이블 INSERT 성공.")
    print(f"Supabase Table Editor → isolation_narratives → nickname = {nick}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
