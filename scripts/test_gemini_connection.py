#!/usr/bin/env python3
"""
Gemini API 연결 테스트 — GEMINI_API_KEY 값은 출력하지 않습니다.

로컬: 프로젝트 루트 .env 또는 h-bridge-research-assistant/.env
배포: Streamlit Cloud Settings → Secrets 의 GEMINI_API_KEY

사용:
  python scripts/test_gemini_connection.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HB_ENV = ROOT / "h-bridge-research-assistant" / ".env"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

# 루트 env_config 기준 .env + 로컬 개발용 하위 .env
from env_config import ENV_PATH, get_gemini_api_key

load_dotenv(ENV_PATH, override=True)
if HB_ENV.is_file():
    load_dotenv(HB_ENV, override=True)


def main() -> int:
    key = get_gemini_api_key()
    if not key:
        print("FAIL: GEMINI_API_KEY가 없습니다.")
        print(f"  - 로컬: {ENV_PATH} 또는 {HB_ENV}")
        print("  - Cloud: Streamlit Settings → Secrets → GEMINI_API_KEY")
        return 1

    print(f"OK: GEMINI_API_KEY 로드됨 (길이 {len(key)}자, 값은 표시하지 않음)")

    try:
        import google.generativeai as genai

        genai.configure(api_key=key)
        # 1) 모델 목록 — 키·네트워크 검증
        models = [
            m.name
            for m in genai.list_models()
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
        if not models:
            print("FAIL: 사용 가능한 Gemini 모델을 찾지 못했습니다.")
            return 1
        print(f"OK: API 인증 성공 (generateContent 모델 {len(models)}개)")

        # 2) 짧은 생성 테스트
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say PONG")
        text = ""
        try:
            text = (response.text or "").strip()
        except ValueError:
            for cand in getattr(response, "candidates", None) or []:
                content = getattr(cand, "content", None)
                for part in getattr(content, "parts", None) or []:
                    piece = getattr(part, "text", None)
                    if piece:
                        text = str(piece).strip()
                        break
        if text:
            print(f"OK: generate_content 성공 (미리보기: {text[:40]!r})")
        else:
            print("OK: generate_content 호출 완료 (본문 비어 있음 — 키는 유효)")
        return 0
    except Exception as exc:  # noqa: BLE001
        err = str(exc).lower()
        if "leaked" in err or "reported" in err:
            print(
                "FAIL: Key may be blocked (leaked). "
                "Create a new key in Google AI Studio; update .env and Cloud Secrets."
            )
        else:
            print(f"FAIL: Gemini error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
