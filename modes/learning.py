"""학습 서사: 배움의 등고선 — 이야기 화자(역할) 분기."""

from __future__ import annotations

from dataclasses import dataclass

MODE_ID = "learning"

# 이야기 화자 ID (DB·세션에 저장)
AUDIENCE_STUDENT = "student"
AUDIENCE_MOTHER = "mother"
AUDIENCE_FATHER = "father"
AUDIENCE_GRANDPARENT = "grandparent"
AUDIENCE_TEACHER = "teacher"
# 구 가입·DB 호환
AUDIENCE_PARENT = "parent"

LEARNING_AUDIENCE_IDS: tuple[str, ...] = (
    AUDIENCE_STUDENT,
    AUDIENCE_MOTHER,
    AUDIENCE_FATHER,
    AUDIENCE_GRANDPARENT,
    AUDIENCE_TEACHER,
)

# i18n 키 (learning_role_*)
AUDIENCE_I18N_KEYS: dict[str, str] = {
    AUDIENCE_STUDENT: "learning_role_student",
    AUDIENCE_MOTHER: "learning_role_mother",
    AUDIENCE_FATHER: "learning_role_father",
    AUDIENCE_GRANDPARENT: "learning_role_grandparent",
    AUDIENCE_TEACHER: "learning_role_teacher",
    AUDIENCE_PARENT: "learning_role_parent",
}

AUDIENCE_OPENING_KEYS: dict[str, str] = {
    AUDIENCE_STUDENT: "learning_opening_student",
    AUDIENCE_MOTHER: "learning_opening_mother",
    AUDIENCE_FATHER: "learning_opening_father",
    AUDIENCE_GRANDPARENT: "learning_opening_grandparent",
    AUDIENCE_TEACHER: "learning_opening_teacher",
    AUDIENCE_PARENT: "learning_opening_parent",
}

LEARNING_COMPANION = {
    "label": "배움의 정원사",
    "short": "배움의 정원사",
    "emoji": "🌱",
}

MIN_USER_TURNS_FOR_LEARNING_REPORT = 10

# 하위 호환
LEARNING_AUDIENCES = LEARNING_AUDIENCE_IDS


@dataclass(frozen=True, slots=True)
class LearningAudienceSpec:
    id: str
    label_key: str
    opening_key: str


def learning_audience_specs() -> tuple[LearningAudienceSpec, ...]:
    return tuple(
        LearningAudienceSpec(aid, AUDIENCE_I18N_KEYS[aid], AUDIENCE_OPENING_KEYS[aid])
        for aid in LEARNING_AUDIENCE_IDS
    )


def audience_i18n_key(audience: str) -> str:
    return AUDIENCE_I18N_KEYS.get((audience or "").strip(), "learning_role_student")


def audience_opening_i18n_key(audience: str) -> str:
    return AUDIENCE_OPENING_KEYS.get((audience or "").strip(), "learning_role_intro")


def is_valid_learning_audience(audience: str) -> bool:
    a = (audience or "").strip()
    return a in LEARNING_AUDIENCE_IDS or a == AUDIENCE_PARENT


def is_student_audience(audience: str) -> bool:
    return (audience or "").strip() == AUDIENCE_STUDENT


def is_adult_learning_proxy(audience: str) -> bool:
    """학생이 아닌 화자(보호자·교사 등)."""
    a = (audience or "").strip()
    return a in (
        AUDIENCE_MOTHER,
        AUDIENCE_FATHER,
        AUDIENCE_GRANDPARENT,
        AUDIENCE_TEACHER,
        AUDIENCE_PARENT,
    )


def normalize_learning_audience(value: str) -> str:
    v = (value or "").strip().lower()
    if v in ("student", "학생", "본인", "아이", "학생 본인"):
        return AUDIENCE_STUDENT
    if v in ("mother", "mom", "엄마", "어머니"):
        return AUDIENCE_MOTHER
    if v in ("father", "dad", "아빠", "아버지"):
        return AUDIENCE_FATHER
    if v in ("grandparent", "grandparents", "조부모", "조모", "할머니", "할아버지"):
        return AUDIENCE_GRANDPARENT
    if v in ("teacher", "교사", "선생", "선생님", "담임"):
        return AUDIENCE_TEACHER
    if v in ("parent", "parents", "학부모", "보호자"):
        return AUDIENCE_PARENT
    return ""


def audience_label_ko(audience: str) -> str:
    labels = {
        AUDIENCE_STUDENT: "학생 본인",
        AUDIENCE_MOTHER: "엄마",
        AUDIENCE_FATHER: "아빠",
        AUDIENCE_GRANDPARENT: "조부모·조모",
        AUDIENCE_TEACHER: "학교 교사",
        AUDIENCE_PARENT: "학부모",
    }
    return labels.get((audience or "").strip(), "")


def get_learning_display(audience: str) -> dict[str, str]:
    base = dict(LEARNING_COMPANION)
    a = (audience or "").strip()
    suffix = {
        AUDIENCE_STUDENT: " (학생)",
        AUDIENCE_MOTHER: " (엄마)",
        AUDIENCE_FATHER: " (아빠)",
        AUDIENCE_GRANDPARENT: " (조부모·조모)",
        AUDIENCE_TEACHER: " (교사)",
        AUDIENCE_PARENT: " (학부모)",
    }.get(a, "")
    if suffix:
        base["label"] = f"배움의 정원사{suffix}"
    return base
