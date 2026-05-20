"""생애사적 대화 프롬프트 — personas 빌더의 단일 진입점."""

from __future__ import annotations

from personas import (
    PHASE_COLLECT,
    PHASE_GIANT,
    build_giant_system_prompt,
    build_phase1_system_prompt,
)


def build_collect_addon(
    age_group: str,
    life_stage: str,
    *,
    lang: str = "ko",
    is_returning: bool = False,
    last_topic: str = "",
    nickname: str = "",
) -> str:
    return build_phase1_system_prompt(
        age_group,
        life_stage,
        lang=lang,
        is_returning=is_returning,
        last_topic=last_topic,
        nickname=nickname,
    )


def build_giant_addon(
    giant_key: str,
    age_group: str,
    life_stage: str,
    positive_resources: list[str],
    current_concern: str,
    *,
    lang: str = "ko",
) -> str:
    return build_giant_system_prompt(
        giant_key,
        age_group,
        life_stage,
        positive_resources,
        current_concern,
        lang=lang,
    )


def build_addon_for_phase(
    phase: str,
    *,
    giant_key: str | None,
    age_group: str,
    life_stage: str,
    positive_resources: list[str],
    current_concern: str,
    lang: str = "ko",
    is_returning: bool = False,
    last_topic: str = "",
    nickname: str = "",
) -> str:
    if phase == PHASE_GIANT and giant_key:
        return build_giant_addon(
            giant_key,
            age_group,
            life_stage,
            positive_resources,
            current_concern,
            lang=lang,
        )
    return build_collect_addon(
        age_group,
        life_stage,
        lang=lang,
        is_returning=is_returning,
        last_topic=last_topic,
        nickname=nickname,
    )
