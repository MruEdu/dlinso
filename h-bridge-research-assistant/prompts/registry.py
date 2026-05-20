"""app_mode + 대화 phase에 맞는 시스템 프롬프트 조각을 반환."""

from __future__ import annotations

from modes.registry import (
    MODE_ASSESSMENT,
    MODE_COUNSELING,
    MODE_LIFESPAN,
    MODE_RESEARCH,
    default_mode,
)
from prompts import assessment as assessment_prompts
from prompts import counseling as counseling_prompts
from prompts import lifespan as lifespan_prompts
from prompts import research as research_prompts
from personas import PHASE_GIANT


def build_mode_system_addon(
    mode_id: str,
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
    mode = (mode_id or default_mode()).strip() or default_mode()

    if mode == MODE_LIFESPAN:
        return lifespan_prompts.build_addon_for_phase(
            phase,
            giant_key=giant_key,
            age_group=age_group,
            life_stage=life_stage,
            positive_resources=positive_resources,
            current_concern=current_concern,
            lang=lang,
            is_returning=is_returning,
            last_topic=last_topic,
            nickname=nickname,
        )
    if mode == MODE_ASSESSMENT:
        return assessment_prompts.build_addon_stub()
    if mode == MODE_COUNSELING:
        return counseling_prompts.build_addon_stub()
    if mode == MODE_RESEARCH:
        return research_prompts.build_addon_stub()

    return lifespan_prompts.build_addon_for_phase(
        phase,
        giant_key=giant_key if phase == PHASE_GIANT else None,
        age_group=age_group,
        life_stage=life_stage,
        positive_resources=positive_resources,
        current_concern=current_concern,
        lang=lang,
        is_returning=is_returning,
        last_topic=last_topic,
        nickname=nickname,
    )
