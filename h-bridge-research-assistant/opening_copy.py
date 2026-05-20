"""가입 시 선택한 연령·성별·생애주기에 맞는 첫 안내 문구."""

from __future__ import annotations

from collections.abc import Callable


def _slug(value: str) -> str:
    return (
        value.strip()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "_")
    )


def _lookup(t: Callable[[str], str], key: str) -> str | None:
    if not key:
        return None
    text = t(key).strip()
    if text and text != key:
        return text
    return None


def resolve_opening_message(
    *,
    t: Callable[[str], str],
    age_group: str = "",
    gender: str = "",
    life_stage: str = "",
) -> str:
    """
    우선순위: 생애주기(학력) → 연령대 → 기본 opening.
    성별은 짧은 격려 문장을 덧붙일 때만 사용(opening_gender_note_*).
    """
    stage = (life_stage or "").strip()
    age = (age_group or "").strip()
    gen = (gender or "").strip()

    for key in (
        f"opening_stage_{_slug(stage)}" if stage else "",
        f"opening_age_{_slug(age)}" if age else "",
        "opening_age_10-20" if age in ("10대", "20대") else "",
        "opening_age_30-40" if age in ("30대", "40대") else "",
        "opening_age_50-60" if age in ("50대",) else "",
        "opening_age_70대_이상" if "60대" in age or "70" in age else "",
    ):
        found = _lookup(t, key)
        if found:
            base = found
            break
    else:
        base = t("opening")

    if gen:
        note = _lookup(t, f"opening_gender_note_{_slug(gen)}")
        if note:
            return f"{base}\n\n{note}"
    return base


def resolve_opening_placeholder(
    *,
    t: Callable[[str], str],
    age_group: str = "",
    gender: str = "",
    life_stage: str = "",
) -> str:
    """입력창 placeholder — 생애주기·연령 맞춤."""
    stage = (life_stage or "").strip()
    age = (age_group or "").strip()

    for key in (
        f"chat_opening_placeholder_stage_{_slug(stage)}" if stage else "",
        f"chat_opening_placeholder_age_{_slug(age)}" if age else "",
    ):
        found = _lookup(t, key)
        if found:
            return found
    return _lookup(t, "chat_opening_placeholder") or t("chat_ph_collect")
