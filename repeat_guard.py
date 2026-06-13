"""Layer B — AI 응답 반복 방지 (생성 후 유사도 검증 · 1회 재생)."""

from __future__ import annotations

import re
from collections.abc import Callable
from difflib import SequenceMatcher

REPEAT_COMPLAINT_KEYWORDS: tuple[str, ...] = (
    "반복",
    "같은 질문",
    "또 그",
    "또 물",
    "질문이 반복",
    "질문을 반복",
    "또 같은",
    "계속 같은",
    "똑같",
)

_DUPLICATE_THRESHOLD = 0.78


def normalize_reply_text(text: str) -> str:
    return re.sub(r"\s+", "", (text or "").lower())


def is_near_duplicate_reply(
    candidate: str,
    prior: str,
    *,
    threshold: float = _DUPLICATE_THRESHOLD,
) -> bool:
    a = normalize_reply_text(candidate)
    b = normalize_reply_text(prior)
    if not a or not b:
        return False
    if len(a) >= 12 and (a in b or b in a):
        return True
    return SequenceMatcher(None, a, b).ratio() >= threshold


def recent_assistant_replies(messages: list[dict], *, limit: int = 3) -> list[str]:
    out: list[str] = []
    for msg in reversed(messages):
        if msg.get("role") != "assistant":
            continue
        text = str(msg.get("display") or msg.get("content") or "").strip()
        if text:
            out.append(text)
        if len(out) >= limit:
            break
    return out


def user_flags_repeat_complaint(text: str) -> bool:
    t = (text or "").strip()
    return any(k in t for k in REPEAT_COMPLAINT_KEYWORDS)


def reply_needs_reguard(
    reply: str,
    messages: list[dict],
    last_user_display: str,
) -> bool:
    cleaned = (reply or "").strip()
    if not cleaned:
        return False
    if user_flags_repeat_complaint(last_user_display):
        return True
    priors = recent_assistant_replies(messages, limit=3)
    return any(is_near_duplicate_reply(cleaned, prior) for prior in priors)


def build_repeat_retry_prompt(original_user: str) -> str:
    base = (original_user or "").strip()
    suffix = (
        "\n\n[시스템] 직전 AI 질문과 동일한 문장·문구·「~인가요?」 구조를 사용하지 마세요. "
        "참여자가 방금 말한 **새 주제의 키워드**에만 맞춰 완전히 다른 각도의 "
        "담백한 단문 1~2개로만 답하세요."
    )
    return base + suffix if base else suffix.strip()


def fallback_nonduplicate_reply(lang: str = "ko") -> str:
    if lang == "ko":
        return (
            "같은 질문을 반복한 것 같아요. 미안해요. "
            "방금 말씀하신 내용 기준으로, 지금 가장 마음에 걸리는 한 가지만 "
            "조금 더 짚어 주실 수 있을까요?"
        )
    return (
        "Sorry if I repeated myself. "
        "From what you just shared, could you say a bit more about "
        "the one thing that weighs on you most right now?"
    )


def guard_reply_against_duplicates(
    reply: str,
    messages: list[dict],
    last_user_display: str,
    *,
    regenerate: Callable[[], str],
    lang: str = "ko",
) -> str:
    """중복·반복 불만 시 1회 재생, 실패 시 비-LLM 폴백."""
    cleaned = (reply or "").strip()
    priors = recent_assistant_replies(messages, limit=3)

    def _is_unacceptable(candidate: str) -> bool:
        text = (candidate or "").strip()
        if not text:
            return True
        if user_flags_repeat_complaint(last_user_display):
            return any(is_near_duplicate_reply(text, prior) for prior in priors)
        return any(is_near_duplicate_reply(text, prior) for prior in priors)

    if not _is_unacceptable(cleaned):
        return cleaned

    retry = (regenerate() or "").strip()
    if retry and not _is_unacceptable(retry):
        return retry

    fallback = fallback_nonduplicate_reply(lang)
    if not any(is_near_duplicate_reply(fallback, prior) for prior in priors):
        return fallback
    return retry or fallback or cleaned
