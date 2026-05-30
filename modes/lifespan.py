"""생애사적 대화 브랜치 — 연령·생애주기 맞춤 회상·서사 인출."""

from __future__ import annotations

from personas import DEFAULT_LIFE_STAGE, LIFE_STAGE_OPTIONS, normalize_age_group

# 연령대 선택 시 가입 폼 기본값 (사용자가 생활 단계는 변경 가능)
AGE_DEFAULT_LIFE_STAGE: dict[str, str] = {
    "초등 연령(약 7–12세)": "초등학생",
    "중등 연령(약 13–15세)": "중·고등학생 (재학)",
    "고등 연령(약 16–18세)": "중·고등학생 (재학)",
    "10대": "중·고등학생 (재학)",
    "20대": "대학·전문대 (재학)",
    "30대": DEFAULT_LIFE_STAGE,
    "40대": DEFAULT_LIFE_STAGE,
    "50대": DEFAULT_LIFE_STAGE,
    "60대": "은퇴 후",
    "60대 이상": "은퇴 후",
    "70대 이상": "은퇴 후",
}


def suggest_life_stage(age_group: str) -> str:
    age_key = normalize_age_group(age_group or "")
    stage = AGE_DEFAULT_LIFE_STAGE.get(age_key)
    if stage and stage in LIFE_STAGE_OPTIONS:
        return stage
    return DEFAULT_LIFE_STAGE

