"""서사 기록실 — JSON/PDF 내보내기 · 비식별화 필터 (프로토타입)."""

from __future__ import annotations

import json
import re
from datetime import datetime
from io import BytesIO
from typing import Any
from zoneinfo import ZoneInfo

KOREA_TZ = ZoneInfo("Asia/Seoul")

# 초안: 이름·연락처·이메일·주민번호 유사 패턴
_PII_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b[\w.-]+@[\w.-]+\.\w+\b", re.I), "[email]"),
    (re.compile(r"\b01[0-9]-?\d{3,4}-?\d{4}\b"), "[phone]"),
    (re.compile(r"\b\d{6}-\d{7}\b"), "[id-number]"),
    (re.compile(r"\b(19|20)\d{2}년?\s*\d{1,2}월\s*\d{1,2}일\b"), "[date]"),
)


def deidentify_text(text: str, *, nickname: str = "") -> str:
    """개인 식별 가능 문자열을 플레이스홀더로 치환."""
    out = (text or "").strip()
    if nickname:
        out = re.sub(re.escape(nickname), "[participant]", out, flags=re.I)
    for pattern, repl in _PII_PATTERNS:
        out = pattern.sub(repl, out)
    return out


def build_export_payload(
    *,
    nickname: str,
    messages: list[dict[str, Any]],
    profile: dict[str, float] | None = None,
    narrative_stage: str = "",
    life_context: str = "",
    narrative_themes: str = "",
    metaphors: str = "",
    module_type: str = "lifespan",
) -> dict[str, Any]:
    """비식별화된 서사 아카이브 JSON."""
    profile = profile or {}
    turns: list[dict[str, str]] = []
    for msg in messages:
        role = str(msg.get("role") or "")
        content = deidentify_text(
            str(msg.get("content") or msg.get("display") or ""),
            nickname=nickname,
        )
        if not content or content.startswith("["):
            continue
        turns.append({"role": role, "content": content})

    return {
        "schema": "dlinso.narrative_archive.v1",
        "exported_at": datetime.now(KOREA_TZ).isoformat(),
        "module_type": module_type,
        "narrative_stage": narrative_stage,
        "life_context": deidentify_text(life_context, nickname=nickname),
        "narrative_themes": deidentify_text(narrative_themes, nickname=nickname),
        "metaphors": deidentify_text(metaphors, nickname=nickname),
        "profile_scores": {
            k: round(float(profile.get(k, 0)), 1)
            for k in ("agency", "reflection_depth", "emotional_richness", "relational_connection")
        },
        "turns": turns,
        "deidentified": True,
    }


def export_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def export_pdf_bytes(payload: dict[str, Any]) -> bytes:
    """
    경량 PDF — fpdf2 없이 UTF-8 텍스트 기반 아카이브 (.pdf 확장자, 열람용).
    향후 fpdf2/reportlab 로 레이아웃 고도화 가능.
    """
    lines = [
        "Dlinso Narrative Archive",
        f"Exported: {payload.get('exported_at', '')}",
        f"Module: {payload.get('module_type', '')}",
        f"Stage: {payload.get('narrative_stage', '')}",
        "",
        "--- Life Context ---",
        payload.get("life_context") or "—",
        "",
        "--- Themes ---",
        payload.get("narrative_themes") or "—",
        "",
        "--- Record ---",
    ]
    for i, turn in enumerate(payload.get("turns") or [], 1):
        role = "User" if turn.get("role") == "user" else "Archive Guide"
        lines.append(f"[{i}] {role}: {turn.get('content', '')}")
    body = "\n".join(lines).encode("utf-8")
    return body
