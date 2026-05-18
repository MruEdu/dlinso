"""
앱 설정 — 로컬 .env + 배포(Streamlit) st.secrets 통합.

보안 (API 키):
  - 코드에 GEMINI_API_KEY 를 문자열로 넣지 마세요.
  - 로컬: `.env` (Git 제외) — `.env.example` 만 커밋
  - Streamlit Cloud: 앱 → Settings → Secrets → TOML 예:
        GEMINI_API_KEY = "새로_발급한_키"
    저장 후 Reboot app 필수.
  - 유출된 키는 Google AI Studio 에서 폐기·재발급하세요.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
ENV_PATH = APP_DIR / ".env"
SERVICE_ACCOUNT_FILE = APP_DIR / "service_account.json"

load_dotenv(ENV_PATH, override=True)

# st.secrets 내 서비스 계정 JSON (TOML 섹션 또는 JSON 문자열 키)
_SERVICE_ACCOUNT_SECRET_KEYS = (
    "gcp_service_account",
    "google_service_account",
    "service_account",
)
_SERVICE_ACCOUNT_JSON_KEYS = (
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "SERVICE_ACCOUNT_JSON",
    "GCP_SERVICE_ACCOUNT_JSON",
)

# 환경 변수: secrets 우선 → os.environ (.env)
_CONFIG_KEYS = (
    "GEMINI_API_KEY",
    "GOOGLE_SHEET_ID",
    "INQUIRY_EMAIL",
)

# 연구 협업·문의 기본 수신 (env에 추가 주소가 있으면 함께 사용)
DEFAULT_INQUIRY_EMAIL = "hyc6999@gmail.com"


def _streamlit_secrets() -> Any | None:
    try:
        import streamlit as st

        return st.secrets
    except Exception:  # noqa: BLE001
        return None


def _secret_raw(key: str) -> Any | None:
    secrets = _streamlit_secrets()
    if secrets is None:
        return None
    try:
        if key in secrets:
            return secrets[key]
    except Exception:  # noqa: BLE001
        pass
    return None


def get_config(key: str, default: str = "") -> str:
    """배포 secrets → .env 순으로 설정값 조회."""
    raw = _secret_raw(key)
    if raw is not None and str(raw).strip():
        return str(raw).strip()
    return os.getenv(key, default).strip()


def get_gemini_api_key() -> str:
    """
    Gemini API 키 — st.secrets(Cloud) 우선, 없으면 os.getenv / .env.
    하드코딩 금지. 키 미설정 시 빈 문자열.
    """
    key = get_config("GEMINI_API_KEY")
    if not key or key in (
        "your_gemini_api_key_here",
        "your_gemini_api_key",
    ):
        return ""
    return key


def get_google_sheet_id() -> str:
    return get_config("GOOGLE_SHEET_ID")


def get_inquiry_emails() -> list[str]:
    """문의 수신 메일 목록 — 기본 주소 + INQUIRY_EMAIL(쉼표 구분)."""
    seen: set[str] = set()
    ordered: list[str] = []
    for addr in (
        DEFAULT_INQUIRY_EMAIL,
        *(a.strip() for a in get_config("INQUIRY_EMAIL").split(",") if a.strip()),
    ):
        key = addr.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(addr)
    return ordered


def get_inquiry_email() -> str:
    """연구소 문의 mailto 수신자 (복수 시 쉼표 연결)."""
    return ",".join(get_inquiry_emails())


_PEM_BEGIN = "-----BEGIN PRIVATE KEY-----"
_PEM_END = "-----END PRIVATE KEY-----"


def _normalize_private_key(pk: str) -> str:
    """
    Streamlit Secrets TOML 붙여넣기 시 PEM 깨짐 보정.
    (InvalidData InvalidByte — BOM·한글 주석·줄바꿈 누락 등)
    """
    if not isinstance(pk, str):
        return pk
    text = pk.strip().lstrip("\ufeff").strip("\u200b")
    text = text.replace("\\n", "\n").replace("\\r", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # 따옴표로 한 번 더 감싼 경우
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1].replace("\\n", "\n")

    begin = text.find(_PEM_BEGIN)
    if begin < 0:
        return text
    if begin > 0:
        text = text[begin:]
    end = text.find(_PEM_END)
    if end >= 0:
        text = text[: end + len(_PEM_END)]

    _, rest = text.split(_PEM_BEGIN, 1)
    mid, _after = rest.split(_PEM_END, 1)
    body = "".join(line.strip() for line in mid.splitlines())
    body = body.replace(" ", "")
    lines = [_PEM_BEGIN]
    for i in range(0, len(body), 64):
        lines.append(body[i : i + 64])
    lines.append(_PEM_END)
    return "\n".join(lines) + "\n"


def _normalize_service_account_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Streamlit Secrets·JSON 붙여넣기 시 private_key 줄바꿈 보정."""
    out = dict(data)
    pk = out.get("private_key")
    if isinstance(pk, str):
        out["private_key"] = _normalize_private_key(pk)
    return out


def _coerce_service_account_dict(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if isinstance(raw, dict):
        return _normalize_service_account_dict(dict(raw))
    # Streamlit SecretsAttrDict 등
    if hasattr(raw, "keys"):
        try:
            return _normalize_service_account_dict({k: raw[k] for k in raw.keys()})
        except Exception:  # noqa: BLE001
            pass
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return _normalize_service_account_dict(parsed)
        except json.JSONDecodeError:
            return None
    return None


def get_service_account_info() -> dict[str, Any] | None:
    """
    Google 서비스 계정 JSON.
    우선순위: st.secrets(Cloud) → 로컬 service_account.json(개발용, Git 미포함).
    """
    secrets = _streamlit_secrets()
    if secrets is not None:
        for name in _SERVICE_ACCOUNT_SECRET_KEYS:
            info = _coerce_service_account_dict(_secret_raw(name))
            if info and info.get("client_email"):
                return info
        for key in _SERVICE_ACCOUNT_JSON_KEYS:
            info = _coerce_service_account_dict(_secret_raw(key))
            if info and info.get("client_email"):
                return info

    if SERVICE_ACCOUNT_FILE.is_file():
        try:
            data = json.loads(SERVICE_ACCOUNT_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("client_email"):
                return _normalize_service_account_dict(data)
        except (OSError, json.JSONDecodeError):
            pass
    return None


def credentials_source_label() -> str:
    """연결 진단용 — secrets / file / none."""
    secrets = _streamlit_secrets()
    if secrets is not None:
        for name in _SERVICE_ACCOUNT_SECRET_KEYS:
            if _secret_raw(name) is not None:
                return f"st.secrets[{name}]"
        for key in _SERVICE_ACCOUNT_JSON_KEYS:
            if _secret_raw(key) is not None:
                return f"st.secrets[{key}]"
    if SERVICE_ACCOUNT_FILE.is_file():
        try:
            data = json.loads(SERVICE_ACCOUNT_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("client_email"):
                return "service_account.json (local only)"
        except (OSError, json.JSONDecodeError):
            pass
    return "none"


def apply_secrets_to_environ() -> None:
    """비-Streamlit 모듈이 os.getenv만 쓸 때 secrets 값을 환경에 반영."""
    for key in _CONFIG_KEYS:
        val = get_config(key)
        if val:
            os.environ.setdefault(key, val)


KOREA_TZ = ZoneInfo("Asia/Seoul")


def korea_now_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Sheets 등에 기록할 한국 표준시(KST, UTC+9) 시각."""
    return datetime.now(KOREA_TZ).strftime(fmt)
