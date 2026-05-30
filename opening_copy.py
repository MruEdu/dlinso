"""가입 시 선택한 연령·성별·생애주기에 맞는 첫 안내 문구."""

from __future__ import annotations

from collections.abc import Callable

from personas import normalize_age_group, normalize_life_stage


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
    stage_raw = (life_stage or "").strip()
    stage = normalize_life_stage(stage_raw) if stage_raw else ""
    age_raw = (age_group or "").strip()
    age = normalize_age_group(age_raw) if age_raw else ""
    gen = (gender or "").strip()

    for key in (
        f"opening_stage_{_slug(stage_raw)}" if stage_raw else "",
        f"opening_stage_{_slug(stage)}" if stage and stage != stage_raw else "",
        f"opening_age_{_slug(age_raw)}" if age_raw else "",
        f"opening_age_{_slug(age)}" if age and age != age_raw else "",
        "opening_age_10대" if age_raw == "10대" else "",
        "opening_age_30-40" if age in ("30대", "40대") else "",
        "opening_age_50-60" if age in ("50대",) else "",
        "opening_age_60대_이상" if age_raw == "60대 이상" else "",
        "opening_age_70대_이상" if age == "70대 이상" else "",
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
    stage_raw = (life_stage or "").strip()
    stage = normalize_life_stage(stage_raw) if stage_raw else ""
    age_raw = (age_group or "").strip()
    age = normalize_age_group(age_raw) if age_raw else ""

    for key in (
        f"chat_opening_placeholder_stage_{_slug(stage_raw)}" if stage_raw else "",
        f"chat_opening_placeholder_stage_{_slug(stage)}" if stage and stage != stage_raw else "",
        f"chat_opening_placeholder_age_{_slug(age_raw)}" if age_raw else "",
        f"chat_opening_placeholder_age_{_slug(age)}" if age and age != age_raw else "",
        "chat_opening_placeholder_age_10대" if age_raw == "10대" else "",
    ):
        found = _lookup(t, key)
        if found:
            return found
    return _lookup(t, "chat_opening_placeholder") or t("chat_ph_collect")
