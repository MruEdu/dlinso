"""지능형 서사 통합 — 연령·학력 맞춤 Phase 1 / Phase 2 거장."""

from __future__ import annotations

import re

SERVICE_TITLE = "dlinso"
GUIDE_NAME = "서사 동행자"
GUIDE_EMOJI = "🌿"

AGE_GROUPS = [
    "초등 연령(약 7–12세)",
    "중등 연령(약 13–15세)",
    "고등 연령(약 16–18세)",
    "20대",
    "30대",
    "40대",
    "50대",
    "60대",
    "70대 이상",
]

AGE_LEGACY: dict[str, str] = {
    "10대": "고등 연령(약 16–18세)",
    "10-20대": "고등 연령(약 16–18세)",
    "60대 이상": "60대",
}

DEFAULT_AGE_GROUP = "30대"
GENDER_OPTIONS = ["남", "여", "기타"]

LIFE_STAGE_OPTIONS = [
    "초등학생",
    "중·고등학생 (재학)",
    "청소년 (비재학·홈스쿨·중·고 휴학)",
    "대학·전문대 (재학)",
    "대학·전문대 (휴학)",
    "대학원 (재학)",
    "대학원 (휴학)",
    "일·활동 중",
    "준비·돌봄·쉬는 중",
    "은퇴 후",
]

# 이전 가입·DB 값 → 현재 옵션 (말투·분석 호환)
LIFE_STAGE_LEGACY: dict[str, str] = {
    "중학생": "중·고등학생 (재학)",
    "고등학생": "중·고등학생 (재학)",
    "대학생": "대학·전문대 (재학)",
    "성인(일반)": "일·활동 중",
    "은퇴 후 삶": "은퇴 후",
    "대학·전문대 (휴학·휴지)": "대학·전문대 (휴학)",
}

DEFAULT_LIFE_STAGE = "일·활동 중"

PHASE_COLLECT = "collect"
PHASE_GIANT = "giant"

DISTRESS_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("고민", re.compile(
        r"고민|걱정|불안|막막|두려|worry|anxious|anxiety|stress|stressed",
        re.I,
    )),
    ("무기력", re.compile(
        r"무기력|의욕\s*없|힘이\s*없|지쳐|번아웃|힘들|tired|exhausted|helpless|burnout",
        re.I,
    )),
    ("집중 어려움", re.compile(
        r"집중\s*안|산만|딴생각|멍해|can'?t focus|distracted",
        re.I,
    )),
    ("우울·슬픔", re.compile(
        r"우울|슬프|외로|공허|눈물|sad|depress|lonely|empty",
        re.I,
    )),
    ("관계 갈등", re.compile(
        r"싸웠|갈등|멀어|서운|오해|conflict|fight|argued",
        re.I,
    )),
]

LANG_REPLY: dict[str, str] = {
    "ko": "Korean",
    "en": "English",
    "mn": "Mongolian",
    "ja": "Japanese",
    "zh": "Chinese",
    "vi": "Vietnamese",
}

GIANT_KEYS = ("adler", "jung", "frankl")

GIANTS: dict[str, dict[str, str]] = {
    "adler": {
        "label": "알프레드 아들러",
        "short": "아들러",
        "emoji": "🎯",
        "focus": "소속감, 용기, 사회적 관심, 목표 재설정",
    },
    "jung": {
        "label": "칼 구스타브 융",
        "short": "융",
        "emoji": "🌙",
        "focus": "그림자 통합, 상징, 내면의 목소리",
    },
    "frankl": {
        "label": "빅토르 프랭클",
        "short": "프랭클",
        "emoji": "🕯️",
        "focus": "의미, 선택의 자유, 고통 속 가치",
    },
}

GIANT_SELECT_RULES: dict[str, list[str]] = {
    "adler": ["관계", "소속", "비교", "용기", "목표", "일", "가족", "역할"],
    "jung": ["꿈", "상징", "내면", "그림자", "반복", "무의식"],
    "frankl": ["의미", "상실", "고통", "절망", "가치", "선택"],
}

# 현재 생활 단계 맞춤 말투 (Phase 1·2 공통)
LIFE_STAGE_TONE: dict[str, str] = {
    "초등학생": (
        "짧고 다정한 말투. 어려운 단어 대신 쉬운 말. 칭찬과 호기심을 담아 "
        "한 번에 한 질문만. 어른처럼 무겁게 말하지 않기."
    ),
    "중·고등학생 (재학)": (
        "친근한 존댓말. 학교·친구·꿈·진로를 부드럽게. "
        "비난 없이 성장의 이야기를 함께 쓰게 이끌기."
    ),
    "청소년 (비재학·홈스쿨·중·고 휴학)": (
        "따뜻한 존댓말. 학교·성적·반 친구를 전제하지 않기. "
        "홈스쿨·비재학·휴학 이유를 캐묻지 않고, 관계·자기주도·미래·가족을 존중. "
        "한 번에 한 질문."
    ),
    "대학·전문대 (재학)": (
        "정중한 존댓말. 자아·관계·미래 가능성을 존중. "
        "조언보다 성찰 질문 중심."
    ),
    "대학·전문대 (휴학)": (
        "정중하고 부드러운 존댓말. 휴학·쉼을 낙인으로 다루지 않기. "
        "선택·관계·불안·다음 계획을 존중하며 한 번에 한 질문."
    ),
    "대학원 (재학)": (
        "정중한 존댓말. 연구·지도교수·진로 압박을 전제하되 평가하지 않기. "
        "고립·번아웃·의미를 함께 짚으며 한 번에 한 질문."
    ),
    "대학원 (휴학)": (
        "정중하고 부드러운 존댓말. 휴학·전환을 낙인으로 다루지 않기. "
        "선택·관계·다음 계획을 존중하며 한 번에 한 질문."
    ),
    "일·활동 중": (
        "차분하고 정중한 존댓말. 책임·성취·관계를 깊이 있게, "
        "평가나 진단 없이 동행."
    ),
    "준비·돌봄·쉬는 중": (
        "따뜻한 존댓말. 구직·돌봄·휴식·전환기를 '게으름'으로 단정하지 않기. "
        "지금의 속도와 선택을 존중하며 한 번에 한 질문."
    ),
    "은퇴 후": (
        "느린 호흡, 품위 있는 존댓말. 기억·유산·지혜를 경건하게. "
        "말의 속도를 기다리며 한 번에 한 질문."
    ),
    # 이전 DB·시트 값 (normalize 전 직접 조회 호환)
    "중학생": (
        "친근한 존댓말. 학교·친구·꿈 이야기를 부드럽게. "
        "비난 없이 성장의 이야기를 함께 쓰게 이끌기."
    ),
    "고등학생": (
        "따뜻한 존댓말. 진로·관계·압박을 가볍게 짚되 진지함은 유지. "
        "스스로 답을 찾게 한 가지 질문."
    ),
    "대학생": (
        "정중한 존댓말. 자아·관계·미래 가능성을 존중. "
        "조언보다 성찰 질문 중심."
    ),
    "성인(일반)": (
        "차분하고 정중한 존댓말. 책임·성취·관계를 깊이 있게, "
        "평가나 진단 없이 동행."
    ),
    "은퇴 후 삶": (
        "느린 호흡, 품위 있는 존댓말. 기억·유산·지혜를 경건하게. "
        "말의 속도를 기다리며 한 번에 한 질문."
    ),
}


def normalize_life_stage(life_stage: str) -> str:
    s = (life_stage or "").strip()
    if not s:
        return DEFAULT_LIFE_STAGE
    if s in LIFE_STAGE_LEGACY:
        return LIFE_STAGE_LEGACY[s]
    if s in LIFE_STAGE_OPTIONS:
        return s
    if s in LIFE_STAGE_TONE:
        return LIFE_STAGE_LEGACY.get(s, s)
    return DEFAULT_LIFE_STAGE


def normalize_age_group(age_group: str) -> str:
    s = (age_group or "").strip()
    if not s:
        return DEFAULT_AGE_GROUP
    if s in AGE_LEGACY:
        return AGE_LEGACY[s]
    if s in AGE_GROUPS:
        return s
    if s in AGE_SUPPLEMENT:
        return AGE_LEGACY.get(s, s)
    return DEFAULT_AGE_GROUP


AGE_SUPPLEMENT: dict[str, str] = {
    "초등 연령(약 7–12세)": (
        "초등 연령 맥락: 짧고 쉬운 말, 호기심·칭찬, 한 번에 한 질문."
    ),
    "중등 연령(약 13–15세)": (
        "중등 연령 맥락: 친근한 존댓말, 친구·성장·꿈을 가볍게."
    ),
    "고등 연령(약 16–18세)": (
        "고등 연령 맥락: 진로·관계·압박을 부드럽게, 스스로 생각할 여지."
    ),
    "10대": "10대 맥락: 성장·친구·꿈을 가볍고 따뜻하게.",
    "20대": "20대 맥락: 정체성·선택·관계를 함께 탐색.",
    "30대": "30대 맥락: 일·관계·균형 속 의미를 함께 짚기.",
    "40대": "40대 맥락: 책임·전환·다음 챕터를 존중하며.",
    "50대": "50대 맥락: 재시작·경험·남은 시간의 의미.",
    "60대": "60대 맥락: 전환·재시작·남은 시간의 의미를 경건하게.",
    "60대 이상": "60대 이상 맥락: 통합·기억·유산을 경건하게.",
    # 이전 가입자 시트 값 호환
    "10-20대": "청년기 맥락: 정체성·미래를 가볍게 열어 두기.",
    "30-40대": "중년기 맥락: 책임·균형·선택의 무게를 함께 짚기.",
    "50-60대": "장년기 맥락: 전환·재시작·남은 시간의 의미.",
    "70대 이상": "노년기 맥락: 통합·기억·후대와의 연결.",
}


def detect_distress(text: str) -> tuple[bool, str]:
    for label, pattern in DISTRESS_PATTERNS:
        if pattern.search(text):
            return True, label
    return False, ""


def select_giant(text: str, concern: str = "") -> str:
    blob = f"{text} {concern}".lower()
    scores = {key: 0 for key in GIANT_KEYS}
    for key, keywords in GIANT_SELECT_RULES.items():
        for kw in keywords:
            if kw in blob:
                scores[key] += 1
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "frankl" if any(k in blob for k in ("의미", "절망", "상실")) else "adler"
    return best


def _tone_block(age_group: str, life_stage: str) -> str:
    stage_key = normalize_life_stage(life_stage)
    stage_tone = LIFE_STAGE_TONE.get(
        stage_key, LIFE_STAGE_TONE[DEFAULT_LIFE_STAGE]
    )
    age_key = normalize_age_group(age_group)
    age_note = AGE_SUPPLEMENT.get(age_key) or AGE_SUPPLEMENT.get(age_group, "")
    return f"{stage_tone}\n{age_note}" if age_note else stage_tone


def build_returning_greeting(
    last_topic: str,
    nickname: str = "",
    lang: str = "ko",
) -> str:
    """재방문 시 대화창에 표시할 서사 동행자 인사."""
    topic = (last_topic or "").strip()
    if len(topic) > 60:
        topic = topic[:57] + "…"
    templates = {
        "ko": (
            f"🌿 {nickname + '님, ' if nickname else ''}오랜만이에요. "
            f"지난번에 「{topic or '그때 나눈 이야기'}」에 대해 이야기 나누었죠? "
            "그때의 마음을 이어서, 오늘도 한 줄씩 써 볼까요?"
        ),
        "en": (
            f"🌿 Welcome back{', ' + nickname if nickname else ''}. "
            f"Last time we talked about 「{topic or 'your story'}」. "
            "Shall we continue today?"
        ),
    }
    return templates.get(lang, templates["en"])


def build_returning_system_addon(last_topic: str, nickname: str = "") -> str:
    """재방문 참여자용 시스템 프롬프트 보강."""
    topic = (last_topic or "이전 대화").strip()[:120]
    return (
        "\n\n[재방문 참여자]\n"
        f"닉네임: {nickname or '참여자'}. 마지막 주제: {topic}\n"
        "첫 응답은 반드시 '오랜만이에요, 지난번에 ~에 대해 이야기 나누었죠? "
        "계속해볼까요?' 톤으로 짧게 인사한 뒤, 한 가지 질문만 이어가세요."
    )


def build_phase1_system_prompt(
    age_group: str,
    life_stage: str,
    *,
    lang: str = "ko",
    is_returning: bool = False,
    last_topic: str = "",
    nickname: str = "",
) -> str:
    reply_lang = LANG_REPLY.get(lang, "Korean")
    base = (
        f"[Phase 1 · {GUIDE_NAME}] {SERVICE_TITLE}\n\n"
        f"참여자 맥락: 연령대 {age_group}, 현재 생활 단계 「{life_stage}」.\n\n"
        "첫 대화는 **자유롭게**—오늘의 일상·현재 마음·과거 기억 모두 환영. "
        "연령·현재 생활 단계는 **말투와 맥락**만 맞추고, '어느 시기 이야기'를 정하지 마세요. "
        "내면의 질문으로 대화를 이끌되(산파술·엘렌코스), 그 방법론 이름은 드러내지 마세요. "
        "희망적 서사 자원(씨앗)을 천천히 모으되, 회상·과거는 대화가 이어지며 자연스럽게.\n\n"
        f"[연령·생활 단계 맞춤 말투]\n{_tone_block(age_group, life_stage)}"
    )
    if is_returning:
        base += build_returning_system_addon(last_topic, nickname)
    return base


def build_giant_system_prompt(
    giant_key: str,
    age_group: str,
    life_stage: str,
    positive_resources: list[str],
    current_concern: str,
    lang: str = "ko",
) -> str:
    giant = GIANTS.get(giant_key, GIANTS["adler"])
    resources = positive_resources or ["아직 수집된 긍정적 이야기가 없습니다"]
    resource_block = "\n".join(f"- {r}" for r in resources[:8])

    return (
        f"[Phase 2 · {giant['label']}] **거장 상담** ({giant['focus']}).\n\n"
        f"참여자: {age_group}, 「{life_stage}」. 현재 고민: {current_concern or '난관'}\n\n"
        "[Phase 1 긍정적 서사 자원 — 반드시 1개 이상 구체 인용]\n"
        f"{resource_block}\n\n"
        "글로벌 서사 동행(Elenchus·Aporia)를 따르되, **{giant['short']}** 의 관점 1줄 + "
        "긍정 자원은 재진술·은유로 1회 반영(원문·오타 복붙 금지) + Maieutic question 1개. "
        "Aporia 시 그 언어의 은유로 길을 열 것.\n\n"
        f"[연령·생활 단계 맞춤 말투]\n{_tone_block(age_group, life_stage)}"
    )


def get_active_display(phase: str, giant_key: str | None = None) -> dict[str, str]:
    if phase == PHASE_GIANT and giant_key and giant_key in GIANTS:
        g = GIANTS[giant_key]
        return {"label": g["label"], "short": g["short"], "emoji": g["emoji"]}
    return {"label": GUIDE_NAME, "short": GUIDE_NAME, "emoji": GUIDE_EMOJI}


def phase_label_ko(phase: str, giant_key: str | None = None) -> str:
    if phase == PHASE_GIANT and giant_key:
        return GIANTS.get(giant_key, GIANTS["adler"])["short"]
    return GUIDE_NAME
