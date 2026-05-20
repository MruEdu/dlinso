"""지능형 서사 통합 — 연령·학력 맞춤 Phase 1 / Phase 2 거장."""

from __future__ import annotations

import re

SERVICE_TITLE = "dlinso"
GUIDE_NAME = "마음의 정원사"
GUIDE_EMOJI = "🌿"

AGE_GROUPS = ["10-20대", "30-40대", "50-60대", "70대 이상"]
GENDER_OPTIONS = ["남", "여", "기타"]

LIFE_STAGE_OPTIONS = [
    "초등학생",
    "중학생",
    "고등학생",
    "대학생",
    "성인(일반)",
    "은퇴 후 삶",
]

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

# 학력·생애주기 맞춤 말투 (Phase 1·2 공통)
LIFE_STAGE_TONE: dict[str, str] = {
    "초등학생": (
        "짧고 다정한 말투. 어려운 단어 대신 쉬운 말. 칭찬과 호기심을 담아 "
        "한 번에 한 질문만. 어른처럼 무겁게 말하지 않기."
    ),
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

AGE_SUPPLEMENT: dict[str, str] = {
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
    stage_tone = LIFE_STAGE_TONE.get(life_stage, LIFE_STAGE_TONE["성인(일반)"])
    age_note = AGE_SUPPLEMENT.get(age_group, "")
    return f"{stage_tone}\n{age_note}" if age_note else stage_tone


def build_returning_greeting(
    last_topic: str,
    nickname: str = "",
    lang: str = "ko",
) -> str:
    """재방문 시 대화창에 표시할 마음의 정원사 인사."""
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
        f"참여자 맥락: 연령대 {age_group}, 학력·생애주기 「{life_stage}」.\n\n"
        "즐거운 기억·성취·남기고 싶은 추억을 **Elenchus → 공감 → Maieutic question** 으로 수집. "
        "글로벌 정원사 System Instruction을 따르되, 이 Phase는 **희망적 서사 자원(씨앗)** 에 무게.\n\n"
        f"[연령·학력 맞춤 말투]\n{_tone_block(age_group, life_stage)}"
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
        "글로벌 정원사 가이드(Elenchus·Aporia)를 따르되, **{giant['short']}** 의 관점 1줄 + "
        "자원 인용 1회 + Maieutic question 1개. Aporia 시 그 언어의 은유로 길을 열 것.\n\n"
        f"[연령·학력 맞춤 말투]\n{_tone_block(age_group, life_stage)}"
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
