"""생애사적 대화 브랜치 — 연령·생애주기 맞춤 회상·서사 인출."""

from __future__ import annotations

from personas import LIFE_STAGE_OPTIONS

# 연령대 버튼 선택 시 가입 폼 기본값 (사용자가 학력은 변경 가능)
AGE_DEFAULT_LIFE_STAGE: dict[str, str] = {
    "10대": "고등학생",
    "20대": "대학생",
    "30대": "성인(일반)",
    "40대": "성인(일반)",
    "50대": "성인(일반)",
    "60대 이상": "은퇴 후 삶",
}


def suggest_life_stage(age_group: str) -> str:
    stage = AGE_DEFAULT_LIFE_STAGE.get((age_group or "").strip())
    if stage and stage in LIFE_STAGE_OPTIONS:
        return stage
    return "성인(일반)"


def select_age_entry(age_group: str) -> None:
    """연령대 진입 — 세션에 생애사 모드·프로필 초안을 기록."""
    import streamlit as st

    from modes.registry import MODE_LIFESPAN

    age = (age_group or "").strip()
    st.session_state.app_mode = MODE_LIFESPAN
    st.session_state.entry_age_group = age
    st.session_state.age_group = age
    st.session_state.life_stage = suggest_life_stage(age)
