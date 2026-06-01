"""숲 · 연결의 서사 — 고립·은둔 청년 서사 (Anti-Diagnosis)."""

from __future__ import annotations

MODE_ID = "isolation"

ISOLATION_COMPANION = {
    "label": "연결의 동행자",
    "short": "연결의 동행자",
    "emoji": "🌲",
}

MIN_USER_TURNS_FOR_ASSET = 6
MIN_USER_TURNS_FOR_REPORT = 10

# 4대 Isolation Framework + 핵심 이중 축
FOUR_FRAMEWORK_KEYS = ("bloom", "todd_rose", "pattern_seeker", "dynamics")
DUAL_AXIS_KEYS = ("identity", "social")

# 미팅용 산파술 시드 — 그대로 쓰지 말고 변형·맥락에 맞게
MAIEUTIC_SEED_QUESTIONS: tuple[str, ...] = (
    "당신의 방은 당신을 지키는 요새인가요, 아니면 언젠가 떠날 정거장인가요?",
    "세상이 당신에게 요구하는 '평균' 중에서 가장 당신을 숨차게 만드는 것은 무엇인가요?",
)

FOUR_FRAMEWORK_LABELS: dict[str, str] = {
    "bloom": "고립 시간의 재정의",
    "todd_rose": "비균질 안전 맥락",
    "pattern_seeker": "내면 질서로의 전환",
    "dynamics": "마찰력과 작은 추진력",
}

# 내담자 화면: 실시간 회복 신호·4대 렌즈 패널 비노출 (Supabase·LLM 백엔드만 유지)
SHOW_CLINICAL_SIGNALS_IN_UI = False

DUAL_AXIS_LABELS: dict[str, str] = {
    "identity": "자아성 · 내가 누구인가",
    "social": "사회성 · 관계 맺는 능력",
}

# AI 발화용 — 단계·맥락에 따라 신중·전략적으로 사용할 어휘
LEXICON_SENSITIVE: tuple[str, ...] = (
    "고립",
    "은둔",
    "사회복귀",
    "치료",
    "재활",
    "hikikomori",
    "히키코모리",
    "사회공포",
    "코모",
    "취약",
    "환자",
)
LEXICON_NEVER_AI: tuple[str, ...] = (
    "치료",
    "재활",
    "사회복귀",
    "환자",
    "취약계층",
    "정상",
    "비정상",
    "입원",
    "퇴원",
)
LEXICON_METAPHOR: tuple[str, ...] = (
    "요새",
    "정거장",
    "섬",
    "고유한 시간",
    "고유한 우주",
    "숨결",
    "막",
    "틈",
    "문턱",
    "고요",
    "안식",
    "나만의 속도",
    "새로운 연결",
)
LEXICON_LATE_PREFERRED: tuple[str, ...] = (
    "세상과의 새로운 연결",
    "나만의 속도로 걷기",
    "관계의 작은 문",
)

# 탐색(초기) · 맥락 형성(중기) · 서사 자산화(후기)
PHASE_EARLY_MAX_TURNS = 3


def get_isolation_display() -> dict[str, str]:
    return dict(ISOLATION_COMPANION)
