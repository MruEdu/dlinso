#!/usr/bin/env python3
"""service_account.json + .env → .streamlit/secrets.toml (Streamlit Cloud용)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
SA_PATH = ROOT / "service_account.json"
OUT_PATH = ROOT / ".streamlit" / "secrets.toml"


def _read_env_key(name: str) -> str:
    if not ENV_PATH.is_file():
        return ""
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        if key.strip() == name:
            return val.strip().strip('"').strip("'")
    return ""


def _toml_escape_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def main() -> int:
    if not SA_PATH.is_file():
        print(f"없음: {SA_PATH}", file=sys.stderr)
        print("GCP에서 서비스 계정 JSON 키를 새로 받아 이 경로에 저장하세요.", file=sys.stderr)
        return 1

    gemini = _read_env_key("GEMINI_API_KEY")
    sheet_id = _read_env_key("GOOGLE_SHEET_ID") or "1aamo-Sf330d6tlrmR-GkA494V66Ow2NcGU9x7E7vbrI"
    sa = json.loads(SA_PATH.read_text(encoding="utf-8"))

    lines = [
        "# Streamlit Cloud → Settings → Secrets (전체 복사)",
        "# 생성: py -3 scripts/build_streamlit_secrets.py",
        "# 키 교체 후 반드시 이 스크립트를 다시 실행하세요.",
        "",
        f"GEMINI_API_KEY = {_toml_escape_string(gemini)}",
        f"GOOGLE_SHEET_ID = {_toml_escape_string(sheet_id)}",
        "",
        "# 방법 A — TOML 섹션 (Streamlit 권장)",
        "[gcp_service_account]",
    ]
    for key, value in sa.items():
        if key == "private_key":
            pk = value.replace("\r\n", "\n").replace("\r", "\n")
            lines.append('private_key = """')
            lines.extend(pk.split("\n"))
            lines.append('"""')
        else:
            lines.append(f"{key} = {_toml_escape_string(str(value))}")

    lines.extend(
        [
            "",
            "# 방법 B — JSON 한 줄 (방법 A와 동시에 쓰지 마세요. 하나만 남기세요.)",
            f"GOOGLE_SERVICE_ACCOUNT_JSON = {_toml_escape_string(json.dumps(sa, ensure_ascii=False))}",
            "",
        ]
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"저장됨: {OUT_PATH}")
    print()
    print("Cloud Secrets에는 [gcp_service_account] 블록만 남기고")
    print("GOOGLE_SERVICE_ACCOUNT_JSON 줄은 삭제하는 것을 권장합니다.")
    print()
    print("다음: py -3 scripts/verify_sheets.py 로 로컬에서 연결 확인")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
