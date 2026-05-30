#!/usr/bin/env python3
"""
Upstage Solar API 연결 테스트 — UPSTAGE_API_KEY 값은 출력하지 않습니다.

  cd E:\\dlinso_v2
  pip install -r requirements.txt
  python scripts/test_upstage_connection.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Windows cmd: UTF-8 stdout (bat sets PYTHONIOENCODING; this covers edge cases)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from env_config import ENV_PATH, get_llm_provider, get_upstage_api_key, get_upstage_model_name

load_dotenv(ENV_PATH, override=True)


def main() -> int:
    print(f"LLM_PROVIDER={get_llm_provider()!r}")
    key = get_upstage_api_key()
    if not key:
        print("FAIL: UPSTAGE_API_KEY가 없습니다.")
        print(f"  - 로컬: {ENV_PATH} 에 키를 넣으세요.")
        return 1
    print(f"OK: UPSTAGE_API_KEY 로드됨 (길이 {len(key)}자)")

    model = get_upstage_model_name()
    print(f"모델: {model}")

    try:
        from llm_client import generate_text

        text = generate_text("Reply with exactly one word: PONG", max_tokens=32)
        if text:
            print(f"OK: 응답 미리보기: {text[:80]!r}")
        else:
            print("OK: 호출 완료 (본문 비어 있음)")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
