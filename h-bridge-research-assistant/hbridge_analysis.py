"""
H-가교 특허 기반 중간 분석 — 통계 엔진(비공개) + 인문학적 서술(공개).

화면: 감성 서술만. OR·Jaggedness 등 수치는 stats / Google 시트에만 기록.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from typing import Any

# ── 키워드 군 (LDA·OR 내부용) ────────────────────────────────────────────────
TOPIC_LEXICON: dict[str, tuple[str, ...]] = {
    "agency": (
        "스스로",
        "결정",
        "선택",
        "도전",
        "해냈",
        "극복",
        "주도",
        "책임",
        "용기",
        "노력",
        "성취",
        "이겨",
    ),
    "relation": (
        "가족",
        "친구",
        "동료",
        "스승",
        "부모",
        "아이",
        "배우자",
        "함께",
        "관계",
        "도움",
        "믿",
        "연대",
    ),
    "emotion": (
        "기쁨",
        "슬픔",
        "불안",
        "분노",
        "감사",
        "외로",
        "행복",
        "눈물",
        "설렘",
        "후회",
        "안도",
        "두려",
    ),
    "meaning": (
        "의미",
        "가치",
        "꿈",
        "소명",
        "신념",
        "성찰",
        "깨달",
        "배움",
        "성장",
        "정체",
        "삶",
        "인생",
    ),
    "achievement": (
        "성공",
        "수상",
        "합격",
        "졸업",
        "승진",
        "완성",
        "달성",
        "목표",
        "1등",
        "자랑",
        "뿌듯",
    ),
    "memory": (
        "기억",
        "추억",
        "어릴",
        "학창",
        "그때",
        "당시",
        "옛날",
        "회상",
        "사진",
        "장소",
    ),
}

ACHIEVEMENT_SEGMENT_MARKERS = TOPIC_LEXICON["achievement"] + (
    "잘했",
    "해냈",
    "성취",
    "기쁘",
    "뿌듯",
    "자랑",
    "승리",
    "이겼",
    "완주",
    "합격",
    "칭찬",
    "인정",
)

GENERAL_SEGMENT_MARKERS = (
    "보통",
    "평소",
    "일상",
    "그냥",
    "항상",
    "매일",
    "때때로",
    "가끔",
    "요즘",
    "근래",
)

TOPIC_LABELS_KO: dict[str, str] = {
    "agency": "자아 주도성",
    "relation": "관계·연대",
    "emotion": "정서 표현",
    "meaning": "의미·성찰",
    "achievement": "성취·도전",
    "memory": "기억·서사",
}

WORD_RE = re.compile(r"[가-힣a-zA-Z]{2,}")

TIME_HINTS = (
    "어제",
    "오늘",
    "그제",
    "내일",
    "아침",
    "점심",
    "저녁",
    "밤",
    "새벽",
    "주말",
    "방학",
    "학창",
    "어릴",
    "그때",
    "요즘",
    "최근",
    "옛날",
    "작년",
    "올해",
)

PLACE_HINTS = (
    "집",
    "거실",
    "부엌",
    "학교",
    "교실",
    "운동장",
    "회사",
    "사무실",
    "카페",
    "병원",
    "공원",
    "마당",
    "고향",
    "기숙사",
    "도서관",
)

PEOPLE_HINTS = (
    "엄마",
    "아빠",
    "부모",
    "할머니",
    "할아버지",
    "형",
    "누나",
    "동생",
    "가족",
    "친구",
    "선생님",
    "동료",
    "배우자",
    "아이",
    "아들",
    "딸",
)

EVENT_HINTS = (
    "여행",
    "축제",
    "시험",
    "대회",
    "졸업",
    "입학",
    "이사",
    "면접",
    "싸움",
    "화해",
    "생일",
    "결혼",
    "이별",
)

TITLE_LANDSCAPE = "나만의 마음 풍경"
TITLE_CONNECTION = "우리들의 연결고리"
TITLE_TREASURE = "삶의 보물지도"

MIDPOINT_MAP_PREFACE = (
    "이것은 당신의 전체 서사 중 현재까지의 흐름을 짚어본 **'중간 지도'**입니다."
)

MIDPOINT_PRESENT_STRENGTH_LINE = (
    "지금까지의 대화 맥락에서는 이런 강점이 두드러집니다."
)

MIN_USER_TURNS_FOR_MIDPOINT = 10
MIN_SUBSTANTIVE_TURNS = 5
MIN_TOTAL_SUBSTANTIVE_CHARS = 180
MIN_AVG_SUBSTANTIVE_LEN = 12
MIN_UNIQUE_TOKENS = 12
MIN_AVG_UNIQUE_TOKENS_PER_TURN = 4
MIN_TOPIC_CATEGORIES_HIT = 2

TRIVIAL_UTTERANCE_RE = re.compile(
    r"^(응|네|예|아니|아니요|ㅇ|ㅇㅇ|음+|글쎄|모름|몰라|그래|맞아|ok|okay|yes|no)$",
    re.I,
)

MIDPOINT_SCAFFOLDING_MESSAGE = (
    "조금 더 구체적인 상황을 들려주시면 더 선명한 지도를 그릴 수 있어요. "
    "그때 **어디**에 계셨는지, **누구**와 함께였는지, "
    "마음에 남은 **한 장면**을 조금만 더 들려주실 수 있을까요?"
)


def _tokenize(text: str) -> list[str]:
    return WORD_RE.findall((text or "").lower())


def count_user_turns(messages: list[dict]) -> int:
    return sum(
        1
        for m in messages
        if m.get("role") == "user" and str(m.get("content") or "").strip()
    )


def _user_texts(messages: list[dict]) -> list[str]:
    return [
        str(m.get("content") or m.get("display") or "").strip()
        for m in messages
        if m.get("role") == "user" and str(m.get("content") or "").strip()
    ]


def is_trivial_utterance(text: str) -> bool:
    t = (text or "").strip()
    if len(t) <= 1:
        return True
    if len(t) <= 4 and TRIVIAL_UTTERANCE_RE.match(t):
        return True
    if len(t) < 8 and TRIVIAL_UTTERANCE_RE.match(t.replace(" ", "")):
        return True
    return False


def _topic_categories_hit(texts: list[str]) -> int:
    blob = " ".join(texts)
    hit = 0
    for keywords in TOPIC_LEXICON.values():
        if any(kw in blob for kw in keywords):
            hit += 1
    return hit


def narrative_assetization_progress(messages: list[dict]) -> dict[str, Any]:
    """
    성찰 깊이 게이지 0~100 — 턴 수(10회 만점) + 발화 품질.
    10턴 도달 시 100% → 중간 정리 버튼 노출.
    """
    texts = _user_texts(messages)
    n = len(texts)
    substantive = [t for t in texts if not is_trivial_utterance(t)]
    sub_n = len(substantive)

    if substantive:
        avg_len = sum(len(t) for t in substantive) / len(substantive)
        len_score = min(1.0, avg_len / 40.0)
        tok_score = min(1.0, len(set(_tokenize(" ".join(substantive)))) / 30.0)
        sub_ratio = min(1.0, sub_n / MIN_SUBSTANTIVE_TURNS)
        topic_score = min(1.0, _topic_categories_hit(substantive) / 4.0)
        quality = (
            0.35 * len_score
            + 0.25 * tok_score
            + 0.2 * sub_ratio
            + 0.2 * topic_score
        )
    else:
        quality = 0.0

    if n >= MIN_USER_TURNS_FOR_MIDPOINT:
        percent = 100
    else:
        turn_ratio = min(1.0, n / MIN_USER_TURNS_FOR_MIDPOINT)
        turn_part = turn_ratio * 58.0
        quality_part = quality * 42.0
        percent = int(min(99.0, turn_part + quality_part))

    return {
        "percent": percent,
        "user_turns": n,
        "substantive_turns": sub_n,
        "button_eligible": n >= MIN_USER_TURNS_FOR_MIDPOINT,
        "quality_score": round(quality, 3),
    }


def assess_midpoint_readiness(messages: list[dict]) -> dict[str, Any]:
    """
    중간 정리(OR 정밀 리포트) 실행 가능 여부.
    10턴 미만 → ready=False, reason=insufficient_turns
    10턴 이상이나 발화 빈약 → ready=False, scaffolding
    """
    texts = _user_texts(messages)
    n = len(texts)
    if n < MIN_USER_TURNS_FOR_MIDPOINT:
        return {
            "ready": False,
            "reason": "insufficient_turns",
            "user_turns": n,
            "scaffolding_message": "",
        }

    substantive = [t for t in texts if not is_trivial_utterance(t)]
    total_chars = sum(len(t) for t in substantive)
    unique_tokens = len(set(_tokenize(" ".join(substantive)))) if substantive else 0
    per_turn_unique = (
        sum(len(set(_tokenize(t))) for t in substantive) / len(substantive)
        if substantive
        else 0.0
    )
    avg_len = total_chars / len(substantive) if substantive else 0.0
    topics_hit = _topic_categories_hit(substantive)

    checks = {
        "substantive_turns": len(substantive) >= MIN_SUBSTANTIVE_TURNS,
        "total_chars": total_chars >= MIN_TOTAL_SUBSTANTIVE_CHARS,
        "avg_len": avg_len >= MIN_AVG_SUBSTANTIVE_LEN,
        "unique_tokens": (
            unique_tokens >= MIN_UNIQUE_TOKENS
            or per_turn_unique >= MIN_AVG_UNIQUE_TOKENS_PER_TURN
        ),
        "topics": topics_hit >= MIN_TOPIC_CATEGORIES_HIT,
    }
    ready = all(checks.values())

    return {
        "ready": ready,
        "reason": "ok" if ready else "sparse_content",
        "user_turns": n,
        "substantive_turns": len(substantive),
        "checks": checks,
        "scaffolding_message": MIDPOINT_SCAFFOLDING_MESSAGE if not ready else "",
    }


def _segment_score(text: str, markers: tuple[str, ...]) -> float:
    if not text.strip():
        return 0.0
    hits = sum(1 for m in markers if m in text)
    tokens = max(len(_tokenize(text)), 1)
    return hits / tokens


def split_achievement_vs_general(
    user_texts: list[str],
) -> tuple[list[str], list[str]]:
    if not user_texts:
        return [], []
    if len(user_texts) == 1:
        return user_texts, []

    scored: list[tuple[float, str]] = []
    for t in user_texts:
        ach = _segment_score(t, ACHIEVEMENT_SEGMENT_MARKERS)
        gen = _segment_score(t, GENERAL_SEGMENT_MARKERS)
        scored.append((ach - gen, t))

    scored.sort(key=lambda x: x[0], reverse=True)
    split = max(1, len(scored) // 2)
    achievement = [t for s, t in scored[:split] if s > 0 or split == 1]
    general = [t for _, t in scored[split:]]
    if not achievement:
        achievement = [scored[0][1]]
    if not general:
        general = [scored[-1][1]]
    return achievement, general


def _category_probs(texts: list[str]) -> dict[str, float]:
    if not texts:
        return {k: 0.0 for k in TOPIC_LEXICON}
    blob = " ".join(texts)
    tokens_n = max(len(_tokenize(blob)), 1)
    probs: dict[str, float] = {}
    for cat, keywords in TOPIC_LEXICON.items():
        hits = sum(blob.count(kw) for kw in keywords)
        probs[cat] = min(1.0, hits / tokens_n)
    return probs


def _odds(p: float, eps: float = 1e-4) -> float:
    p = max(eps, min(1.0 - eps, p))
    return p / (1.0 - p)


def intra_individual_odds_ratios(
    achievement_texts: list[str],
    general_texts: list[str],
) -> dict[str, float]:
    p_ach = _category_probs(achievement_texts)
    p_gen = _category_probs(general_texts)
    or_map: dict[str, float] = {}
    for cat in TOPIC_LEXICON:
        o1 = _odds(p_ach.get(cat, 0.0))
        o0 = _odds(p_gen.get(cat, 0.0))
        or_map[cat] = round(o1 / o0, 3) if o0 > 0 else round(o1, 3)
    return or_map


def jaggedness_index(domain_scores: dict[str, float]) -> float:
    vals = [float(v) for v in domain_scores.values() if v is not None]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    if mean <= 1e-6:
        return 0.0
    variance = sum((v - mean) ** 2 for v in vals) / len(vals)
    cv = math.sqrt(variance) / mean
    peak_gap = max(vals) - min(vals)
    raw = 0.55 * min(1.0, cv) + 0.45 * min(1.0, peak_gap / 100.0)
    return round(min(100.0, raw * 100.0), 1)


def lda_topic_ranking(user_texts: list[str]) -> list[tuple[str, float]]:
    probs = _category_probs(user_texts)
    ranked = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    return [(k, round(v, 4)) for k, v in ranked if v > 0]


def sna_keyword_links(
    user_texts: list[str], top_n: int = 5
) -> list[tuple[str, str, int]]:
    co: Counter[tuple[str, str]] = Counter()
    for text in user_texts:
        toks = list(dict.fromkeys(_tokenize(text)))[:40]
        for i, a in enumerate(toks):
            for b in toks[i + 1 : i + 4]:
                if a != b:
                    pair = tuple(sorted((a, b)))
                    co[pair] += 1
    return [(a, b, c) for (a, b), c in co.most_common(top_n)]


def narrative_precision_score(
    messages: list[dict],
    profile: dict[str, float] | None = None,
) -> float:
    user_texts = [
        str(m.get("content") or "") for m in messages if m.get("role") == "user"
    ]
    if not user_texts:
        return 25.0
    lengths = [len(t) for t in user_texts]
    avg_len = sum(lengths) / len(lengths)
    len_score = min(100.0, avg_len / 12.0)

    all_tokens: list[str] = []
    for t in user_texts:
        all_tokens.extend(_tokenize(t))
    diversity = 0.0
    if all_tokens:
        diversity = len(set(all_tokens)) / len(all_tokens) * 100.0

    prof = profile or {}
    reflection = float(prof.get("reflection_depth", 50.0))

    return round(
        min(100.0, 0.4 * len_score + 0.25 * diversity + 0.35 * reflection),
        1,
    )


def _pick_hints(text: str, hints: tuple[str, ...], limit: int = 2) -> list[str]:
    found: list[str] = []
    for h in hints:
        if h in text and h not in found:
            found.append(h)
        if len(found) >= limit:
            break
    return found


def extract_situational_context(user_texts: list[str]) -> dict[str, str]:
    """장소·시간·사건·인물 맥락 추출 — 리포트 첫 문단용."""
    if not user_texts:
        return {
            "time": "",
            "place": "",
            "people": "",
            "event": "",
            "scene_phrase": "지금까지 나누어 주신 이야기 속",
        }

    focus = user_texts[-1]
    if len(focus) < 40 and len(user_texts) > 1:
        focus = user_texts[-2] + " " + focus
    blob = " ".join(user_texts[-4:])

    times = _pick_hints(blob, TIME_HINTS, 2)
    places = _pick_hints(blob, PLACE_HINTS, 2)
    people = _pick_hints(blob, PEOPLE_HINTS, 2)
    events = _pick_hints(blob, EVENT_HINTS, 2)

    time_s = " ".join(times) if times else ""
    place_s = " ".join(places) if places else ""
    people_s = "와 ".join(people) if people else ""
    event_s = events[0] if events else ""

    parts: list[str] = []
    if time_s:
        parts.append(time_s)
    if place_s:
        parts.append(place_s)
    if people_s:
        parts.append(f"{people_s}(와)과 함께")
    if event_s:
        parts.append(event_s)

    if parts:
        scene = " ".join(parts)
        scene_phrase = f"{scene} 있을 때"
    else:
        snippet = focus.strip()[:36] + ("…" if len(focus) > 36 else "")
        scene_phrase = f"「{snippet}」 이야기가 펼쳐지던 그 순간"

    return {
        "time": time_s,
        "place": place_s,
        "people": people_s,
        "event": event_s,
        "scene_phrase": scene_phrase,
    }


def resolve_report_voice(life_stage: str, age_group: str = "") -> str:
    """elementary | secondary | adult"""
    stage = (life_stage or "").strip()
    if stage == "초등학생":
        return "elementary"
    if stage in ("중학생", "고등학생"):
        return "secondary"
    if stage == "대학생":
        return "adult"
    if stage in ("성인(일반)", "은퇴 후 삶"):
        return "adult"
    if "10-20" in age_group:
        return "secondary"
    return "adult"


def compute_midpoint_statistics(
    messages: list[dict],
    profile: dict[str, float] | None = None,
) -> dict[str, Any]:
    """비공개 통계 — UI에 노출하지 않음."""
    user_texts = [
        str(m.get("content") or m.get("display") or "").strip()
        for m in messages
        if m.get("role") == "user" and str(m.get("content") or "").strip()
    ]
    if not user_texts:
        user_texts = ["(발화 없음)"]

    ach, gen = split_achievement_vs_general(user_texts)
    or_map = intra_individual_odds_ratios(ach, gen)
    topics = lda_topic_ranking(user_texts)
    links = sna_keyword_links(user_texts)

    domain_scores = {
        TOPIC_LABELS_KO.get(k, k): round(v * 100, 1)
        for k, v in _category_probs(user_texts).items()
    }
    jagged = jaggedness_index(domain_scores)
    precision = narrative_precision_score(messages, profile)

    top_or = sorted(or_map.items(), key=lambda x: x[1], reverse=True)[:3]
    strength_cats = [c for c, v in top_or if v >= 1.15]
    if not strength_cats and top_or:
        strength_cats = [top_or[0][0]]

    return {
        "jaggedness_index": jagged,
        "narrative_precision": precision,
        "odds_ratios": or_map,
        "topics": topics,
        "sna_links": [{"a": a, "b": b, "w": c} for a, b, c in links],
        "achievement_segments": len(ach),
        "general_segments": len(gen),
        "domain_scores": domain_scores,
        "strength_categories": strength_cats,
        "top_or": top_or,
    }


def _nickname_short(participant_id: str) -> str:
    nick = (participant_id or "").strip()
    if not nick or nick in ("미리보기", "(익명)"):
        return "친구"
    return nick[:8]


def compose_humanistic_sections_fallback(
    *,
    stats: dict[str, Any],
    situational: dict[str, str],
    voice: str,
    nickname: str,
    gender: str,
    positive_resources: list[str] | None,
    life_context: str,
) -> dict[str, str]:
    """Gemini 실패 시 연령 맞춤 규칙 서술."""
    scene = situational.get("scene_phrase", "지금까지의 이야기 속")
    bracket_scene = f"[{scene}]"
    top_cat = stats.get("strength_categories") or ["meaning"]
    strength_ko = TOPIC_LABELS_KO.get(top_cat[0], "의미·성찰")
    jagged_high = float(stats.get("jaggedness_index", 0)) >= 45.0
    resources = positive_resources or []

    or_sentence = (
        f"{MIDPOINT_PRESENT_STRENGTH_LINE} "
        "남과의 비교가 아닌, 당신의 특정 순간이 다른 때보다 더 빛나는 순간을 "
        "발견했습니다."
    )
    jagged_sentence = (
        "모든 면에서 평균인 사람보다, 특정 부분에서 봉우리처럼 솟은 "
        "당신의 개성이 훨씬 귀한 자산입니다."
        if jagged_high
        else "당신 안에는 아직 이름 붙이지 않은 보물이 조용히 자라고 있습니다."
    )

    if voice == "elementary":
        name = nickname or "친구"
        landscape = (
            f"{name}아, 네 마음속 보물상자를 열어보니 {bracket_scene} "
            f"특별한 빛이 반짝이고 있어. {or_sentence}"
        )
        connection = (
            f"너의 이야기 속엔 너만의 특별한 색깔이 담겨 있어. "
            f"{life_context or '가족과 친구'} 이야기가 마음을 따뜻하게 이어 주고 있네."
        )
        treasure = (
            f"{jagged_sentence} "
            f"특히 **{strength_ko}** 쪽에서 네가 빛나는 모습이 보여. "
            + (f"「{resources[0][:50]}」 같은 기억도 소중한 보물이야." if resources else "")
        )
    elif voice == "secondary":
        landscape = (
            f"너의 이야기 속엔 너만의 특별한 색깔이 담겨 있어. "
            f"{bracket_scene} 느꼈던 마음은 분명 의미 있어. {or_sentence}"
        )
        connection = (
            "관계와 감정의 실타래가 서로 묶이며, 네가 소중히 여기는 사람들과의 "
            "연결이 이야기의 중심에 있어."
        )
        treasure = f"{jagged_sentence} 두드러지는 방향은 **{strength_ko}** 쪽이야."
    else:
        landscape = (
            f"당신의 삶의 맥락에서 발견된 고유한 자산은 {bracket_scene} "
            f"피어났던 감정과 연결되어 있습니다. {or_sentence}"
        )
        connection = (
            f"{'생활 영역: ' + life_context + '. ' if life_context and life_context != '—' else ''}"
            "대화 속 관계·정서의 실타래가 맥락적 성격을 드러냅니다."
        )
        treasure = (
            f"{jagged_sentence} "
            f"특히 **{strength_ko}** 영역에서 삶의 보물이 응집되어 있습니다."
        )

    return {
        "midpoint_preface": MIDPOINT_MAP_PREFACE,
        "title_landscape": TITLE_LANDSCAPE,
        "title_connection": TITLE_CONNECTION,
        "title_treasure": TITLE_TREASURE,
        "section_landscape": landscape.strip(),
        "section_connection": connection.strip(),
        "section_treasure": treasure.strip(),
        "situational_opening": bracket_scene,
    }


def run_intra_individual_or_pipeline(
    messages: list[dict],
    profile: dict[str, float] | None = None,
    life_context: str = "",
    positive_resources: list[str] | None = None,
    *,
    age_group: str = "",
    gender: str = "",
    life_stage: str = "",
    participant_id: str = "",
    humanistic: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    통계 산출 + (선택) 인문학적 서술 병합.
    humanistic가 없으면 fallback 서술만 사용.
    """
    user_texts = [
        str(m.get("content") or m.get("display") or "").strip()
        for m in messages
        if m.get("role") == "user" and str(m.get("content") or "").strip()
    ]
    stats = compute_midpoint_statistics(messages, profile)
    situational = extract_situational_context(user_texts)
    voice = resolve_report_voice(life_stage, age_group)
    nick = _nickname_short(participant_id)

    narrative = humanistic or compose_humanistic_sections_fallback(
        stats=stats,
        situational=situational,
        voice=voice,
        nickname=nick,
        gender=gender,
        positive_resources=positive_resources,
        life_context=life_context,
    )

    stats_payload = {
        **stats,
        "situational_context": situational,
        "report_voice": voice,
        "gender": gender,
        "age_group": age_group,
        "life_stage": life_stage,
    }

    return {
        "midpoint_preface": narrative.get("midpoint_preface", MIDPOINT_MAP_PREFACE),
        "title_landscape": narrative.get("title_landscape", TITLE_LANDSCAPE),
        "title_connection": narrative.get("title_connection", TITLE_CONNECTION),
        "title_treasure": narrative.get("title_treasure", TITLE_TREASURE),
        "section_landscape": narrative.get("section_landscape", ""),
        "section_connection": narrative.get("section_connection", ""),
        "section_treasure": narrative.get("section_treasure", ""),
        "situational_opening": narrative.get(
            "situational_opening", situational.get("scene_phrase", "")
        ),
        "jaggedness_index": stats["jaggedness_index"],
        "narrative_precision": stats["narrative_precision"],
        "stats": stats_payload,
        "stats_json": json.dumps(stats_payload, ensure_ascii=False),
        "situational_context": situational,
    }


def format_midpoint_followup() -> str:
    return (
        "이 지도가 당신의 마음과 닮았나요? "
        "조금 더 들려주고 싶은 장면이 있다면 말씀해 주세요."
    )


def format_full_midpoint_message(report: dict[str, Any]) -> str:
    """채팅·시트용 — 수치 없는 서술형 본문."""
    preface = report.get("midpoint_preface", MIDPOINT_MAP_PREFACE)
    parts = [
        "### 지금까지의 대화, 나를 돌아보는 마음 지도",
        "",
        preface,
        "",
        f"#### [{report.get('title_landscape', TITLE_LANDSCAPE)}]",
        report.get("section_landscape", ""),
        "",
        f"#### [{report.get('title_connection', TITLE_CONNECTION)}]",
        report.get("section_connection", ""),
        "",
        f"#### [{report.get('title_treasure', TITLE_TREASURE)}]",
        report.get("section_treasure", ""),
        "",
        format_midpoint_followup(),
    ]
    return "\n".join(parts)


def format_sheet_stats_summary(report: dict[str, Any]) -> str:
    """연구용 시트 메타 — 수치는 여기만."""
    s = report.get("stats") or {}
    return (
        f"OR분석|Jaggedness:{s.get('jaggedness_index')}|"
        f"Precision:{s.get('narrative_precision')}|"
        f"OR:{json.dumps(s.get('odds_ratios', {}), ensure_ascii=False)[:200]}"
    )
