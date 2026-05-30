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
    "이것은 당신의 전체 서사 중 현재까지의 흐름을 짚어본 「중간 지도」입니다."
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

# 상투적·지표식 표현 — 중간 지도 서술에서 지양
MIDPOINT_CLICHE_BAN = (
    "특별한 색깔",
    "보물상자",
    "반짝",
    "소중한 보물",
    "자아 주도성",
    "정서적 풍요",
    "관계성 지표",
    "평범한 사람",
    "숨은 보물",
    "Jagged Profile",
    "Jagged",
    "jagged profile",
)


def _tokenize(text: str) -> list[str]:
    return WORD_RE.findall((text or "").lower())


def count_user_turns(messages: list[dict]) -> int:
    """사용자 발화 턴 — content·display(사진 직접 입력) 모두 인정."""
    return sum(
        1
        for m in messages
        if m.get("role") == "user"
        and (
            str(m.get("content") or "").strip()
            or str(m.get("display") or "").strip()
        )
    )


def _user_texts(messages: list[dict]) -> list[str]:
    """사용자 발화 — 사진 턴은 display(직접 입력)와 content(분석) 중 더 풍부한 쪽."""
    out: list[str] = []
    for m in messages:
        if m.get("role") != "user":
            continue
        content = str(m.get("content") or "").strip()
        display = str(m.get("display") or "").strip()
        if m.get("image_bytes"):
            candidates = [p for p in (display, content) if p]
            text = max(candidates, key=len) if candidates else ""
        else:
            text = content or display
        if text:
            out.append(text)
    return out


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


def narrative_assetization_progress(
    messages: list[dict],
    *,
    user_turns: int | None = None,
) -> dict[str, Any]:
    """
    성찰 깊이 게이지 0~100 — 턴 수(10회 만점) + 발화 품질.
    10턴 도달 시 100% → 중간 정리 버튼 노출.
    user_turns: UI에 남은 메시지보다 많을 때(토큰 다이어트 이후) 누적 턴 수.
    """
    texts = _user_texts(messages)
    n = user_turns if user_turns is not None else len(texts)
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


def assess_midpoint_readiness(
    messages: list[dict],
    *,
    user_turns: int | None = None,
) -> dict[str, Any]:
    """
    중간 정리(OR 정밀 리포트) 실행 가능 여부.
    10턴 미만 → ready=False
    10턴 이상 → ready=True (버튼 노출과 동일; 품질은 checks·quality_ok에만 기록)
    """
    texts = _user_texts(messages)
    n = user_turns if user_turns is not None else len(texts)
    if n < MIN_USER_TURNS_FOR_MIDPOINT:
        return {
            "ready": False,
            "reason": "insufficient_turns",
            "user_turns": n,
            "scaffolding_message": "",
            "quality_ok": False,
            "checks": {},
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
    quality_ok = all(checks.values())

    return {
        "ready": True,
        "reason": "ok" if quality_ok else "sparse_content",
        "user_turns": n,
        "substantive_turns": len(substantive),
        "checks": checks,
        "quality_ok": quality_ok,
        "scaffolding_message": "",
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
    from personas import normalize_age_group, normalize_life_stage

    stage = normalize_life_stage(life_stage or "")
    if stage == "초등학생":
        return "elementary"
    if stage in (
        "중·고등학생 (재학)",
        "청소년 (비재학·홈스쿨·중·고 휴학)",
        "중학생",
        "고등학생",
    ):
        return "secondary"
    if stage in (
        "대학·전문대 (재학)",
        "대학·전문대 (휴학)",
        "대학원 (재학)",
        "대학원 (휴학)",
        "대학생",
    ):
        return "adult"
    if stage in (
        "일·활동 중",
        "준비·돌봄·쉬는 중",
        "은퇴 후",
        "성인(일반)",
        "은퇴 후 삶",
    ):
        return "adult"
    ag = normalize_age_group(age_group or "")
    if ag in (
        "초등 연령(약 7–12세)",
        "중등 연령(약 13–15세)",
        "고등 연령(약 16–18세)",
        "10대",
    ):
        return "elementary" if ag == "초등 연령(약 7–12세)" else "secondary"
    if ag == "20대":
        return "adult"
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


def extract_anchor_phrases(user_texts: list[str], *, max_phrases: int = 5) -> list[str]:
    """참여자 발화에서 인용할 핵심 구절 후보 (중간 지도 신뢰도·깊이용)."""
    if not user_texts:
        return []

    seen: set[str] = set()
    candidates: list[str] = []

    def _add(phrase: str) -> None:
        p = re.sub(r"\s+", " ", (phrase or "").strip())
        if len(p) < 6 or len(p) > 72 or p in seen:
            return
        if any(b in p for b in MIDPOINT_CLICHE_BAN):
            return
        seen.add(p)
        candidates.append(p)

    blob = "\n".join(user_texts)
    for match in re.finditer(r"[「『\"']([^」』\"']{4,60})[」』\"']", blob):
        _add(match.group(1))

    vivid_markers = (
        "빚",
        "책임",
        "배움",
        "나눔",
        "세상",
        "황혼",
        "책",
        "휴학",
        "관계",
        "부모",
        "후회",
        "의미",
        "전환",
        "조급",
        "외로",
        "감사",
        "죄책",
        "부채",
    )
    for text in user_texts[-10:]:
        for part in re.split(r"[.!?。\n]+", text):
            part = part.strip()
            if len(part) < 8:
                continue
            if any(m in part for m in vivid_markers) or len(part) >= 18:
                _add(part)

    return candidates[:max_phrases]


MIDPOINT_PROSE_KEYS = (
    "midpoint_preface",
    "section_landscape",
    "section_connection",
    "section_treasure",
    "situational_opening",
)

# 인용구 내 흔한 깨진 표기 — 가독용 순화(LLM·후처리 공통)
_QUOTE_TYPO_FIXES: list[tuple[re.Pattern[str], str]] = [
    (re.compile("맣군"), "많군"),
    (re.compile("ㅓㄱ당한"), "적당한"),
    (re.compile("ㅓㄱ당"), "적당"),
    (re.compile("ㅇㅐ"), "왜"),
    (re.compile("ㅎㅏ"), "하"),
]


def _polish_text_inside_quotes(text: str) -> str:
    """「인용구」 안 명백한 오타만 순화 — 말투는 유지."""

    def _fix_inner(match: re.Match[str]) -> str:
        inner = match.group(1)
        for pattern, replacement in _QUOTE_TYPO_FIXES:
            inner = pattern.sub(replacement, inner)
        return f"「{inner}」"

    return re.sub(r"「([^」]+)」", _fix_inner, text)


def sanitize_midpoint_prose(text: str) -> str:
    """마크다운 별표 제거·공백 정리."""
    if not text:
        return ""
    cleaned = (text or "").replace("**", "").replace("*", "")
    cleaned = _polish_text_inside_quotes(cleaned)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def format_midpoint_section_body(text: str) -> str:
    """에세이형 단락 — 문단 사이 빈 줄."""
    body = sanitize_midpoint_prose(text)
    if not body:
        return ""
    if "\n\n" in body:
        return body
    sentences = [s.strip() for s in re.split(r"(?<=[.!?。])\s+", body) if s.strip()]
    if len(sentences) <= 2:
        return body
    paragraphs: list[str] = []
    chunk: list[str] = []
    for sentence in sentences:
        chunk.append(sentence)
        if len(chunk) >= 2:
            paragraphs.append(" ".join(chunk))
            chunk = []
    if chunk:
        paragraphs.append(" ".join(chunk))
    return "\n\n".join(paragraphs)


def polish_midpoint_report(report: dict[str, Any]) -> dict[str, Any]:
    """중간 지도 본문 — 별표 제거·인용 순화·단락 간격."""
    polished = dict(report)
    for key in MIDPOINT_PROSE_KEYS:
        raw = polished.get(key)
        if not isinstance(raw, str) or not raw.strip():
            continue
        if key.startswith("section_"):
            polished[key] = format_midpoint_section_body(raw)
        else:
            polished[key] = sanitize_midpoint_prose(raw)
    return polished


def _uneven_strength_hint(stats: dict[str, Any]) -> str:
    """비균질적 역량 지형 — 수치 없이 모델·fallback용 힌트."""
    domain = stats.get("domain_scores") or {}
    if not domain:
        return (
            "대화 속에서 특정 축(지식·관계·책임 등)만 유난히 높게 솟은 "
            "들쭉날쭉한 강점 지형이 보입니다."
        )
    ranked = sorted(domain.items(), key=lambda x: -float(x[1]))
    peaks = [k for k, _ in ranked[:2]]
    trough = ranked[-1][0] if len(ranked) > 2 else ""
    parts = [f"높은 봉우리: {' · '.join(peaks)}"]
    if trough and trough not in peaks:
        parts.append(f"상대적으로 완만한 축: {trough}")
    parts.append(
        "평균적인 사람이 아니라, 특정 축에서만 솟은 봉우리가 "
        "당신만의 지형을 이룹니다."
    )
    return " ".join(parts)


def build_midpoint_report_prompt(
    *,
    user_lines: list[str],
    stats: dict[str, Any],
    voice_guide: str,
    scene: str,
    gender: str,
    resources: str,
    life_context: str,
    lang: str,
    lang_name: str,
) -> str:
    """인문학적 중간 지도 생성용 LLM 프롬프트."""
    anchors = extract_anchor_phrases(user_lines)
    anchor_block = (
        "\n".join(
            f"- 반드시 인용 후보(원문): {a}\n  → 인용 시 「」로 감싸고, "
            f"명백한 오타만 표준어로 순화"
            for a in anchors
        )
        if anchors
        else (
            "- 참여자 발화에서 2~3개의 핵심 구절을 「」로 직접 인용 (6~40자)."
        )
    )
    ban_line = " · ".join(f"「{c}」" for c in MIDPOINT_CLICHE_BAN[:8])

    stats_for_model = {
        "strength_categories": stats.get("strength_categories"),
        "top_or": stats.get("top_or"),
        "domain_scores": stats.get("domain_scores"),
        "jaggedness_index": stats.get("jaggedness_index"),
        "narrative_precision": stats.get("narrative_precision"),
    }

    return (
        "당신은 dlinso의 **서사 동행자**이자, 한 사람의 인생 서사를 존중하는 "
        "**인문학적 서사 해석가**입니다.\n"
        "아래 **내부 통계**는 해석 재료일 뿐, 출력에 숫자·OR·P-value·%·지표명·"
        f"딱딱한 심리학 라벨({ban_line} 등)을 **절대 쓰지 마세요**.\n\n"
        "[중간 지도 정체성]\n"
        "「이것은 당신의 전체 서사 중 현재까지의 흐름을 짚어본 '중간 지도'입니다.」\n"
        "— 리포트 서두(midpoint_preface)에 반드시 담을 것.\n\n"
        "[분석 가이드라인 — 각 섹션 3~5문장, 상투어 금지]\n\n"
        f"■ {TITLE_LANDSCAPE}\n"
        "- 장소·사건 나열 금지. **현재 심리 상태**를 은유적 풍경으로 그릴 것.\n"
        "- 예시 톤: '황혼의 조급함을 책이라는 결과물로 승화시키려는 책임감의 풍경'\n"
        "- 참여자가 쓴 감각어·비유를 풍경 메타포에 녹일 것.\n\n"
        f"■ {TITLE_CONNECTION}\n"
        "- 관계 **대상 이름 나열**만 하지 말 것.\n"
        "- 그 관계를 대하는 **태도**, **부채감**, **기대**, **거리두기** 등 "
        "감정의 실타래를 따라갈 것.\n"
        "- '누구와 좋다/나쁘다' 수준이 아니라, 말투·침묵·책임의 방향을 짚을 것.\n\n"
        f"■ {TITLE_TREASURE}\n"
        "- '자아 주도성' 같은 용어 대신, 평생 쌓아온 **지식·경험**과 "
        "그것을 **나눔·전환**으로 옮기려는 **서사적 전환점**을 구체적으로 명명.\n"
        "- 비균질적 역량: 평균형이 아니라 특정 축의 **봉우리**가 "
        "어떻게 당신만의 지형을 만드는지 서술. 수치·%·영문 용어 없이 비유로.\n"
        f"- 내부 힌트: {_uneven_strength_hint(stats)}\n\n"
        "[인용 규칙 — 신뢰도]\n"
        f"{anchor_block}\n"
        "- 세 섹션 합쳐 최소 2회 참여자 말을 「」로 직접 인용.\n"
        "- 인용구 안의 명백한 오타·깨진 표기(예: 맣군→많군, ㅓㄱ당한→적당한)는 "
        "문맥에 맞게 표준어로 순화해 읽기 쉽게. 말투·감정·뉘앙스는 유지.\n"
        "- 인용 없이 일반론만 쓰면 실패.\n\n"
        "[출력 형식 — 필수]\n"
        "- JSON 본문 값에 마크다운 별표(*, **)를 절대 넣지 말 것.\n"
        "- 강조는 「인용구」, [상황], 섹션 제목 구조로만. 별표로 강조 금지.\n"
        "- section_landscape / section_connection / section_treasure 각각 "
        "2~3개 단락, 단락 사이는 반드시 빈 줄(\\n\\n) — 인쇄된 에세이처럼.\n"
        "- 문장은 완결형으로, 딱딱한 심리학 라벨·영문 용어·수치 금지.\n\n"
        "[말투]\n"
        f"{voice_guide}\n"
        "격조 있고 따뜻하며, 한 사람의 인생 전체를 존중하는 인문학적 어조. "
        "진단·조언·훈계 금지.\n"
        f"성별 참고: {gender or '미입력'} (고정관념·조롱 금지)\n\n"
        f"[상황 맥락 — {TITLE_LANDSCAPE} 첫 문장에 [상황] 괄호로 짧게]\n"
        f"예: [{scene}] …\n\n"
        f"[내부 통계 — 출력 금지]\n{json.dumps(stats_for_model, ensure_ascii=False)}\n\n"
        f"[긍정 서사 자원]\n{resources}\n"
        f"[생활 맥락] {life_context or '—'}\n\n"
        "[참여자 발화 — 여기서만 근거를 가져올 것]\n"
        + "\n".join(f"- {line}" for line in user_lines[-16:])
        + "\n\n"
        "JSON만 출력:\n"
        "{\n"
        '  "midpoint_preface": "중간 지도 서두 1~2문장",\n'
        f'  "title_landscape": "{TITLE_LANDSCAPE}",\n'
        f'  "title_connection": "{TITLE_CONNECTION}",\n'
        f'  "title_treasure": "{TITLE_TREASURE}",\n'
        f'  "section_landscape": "{TITLE_LANDSCAPE} 본문(단락\\n\\n구분, 별표 없음)",\n'
        f'  "section_connection": "{TITLE_CONNECTION} 본문(단락\\n\\n구분, 별표 없음)",\n'
        f'  "section_treasure": "{TITLE_TREASURE} 본문(단락\\n\\n구분, 별표 없음)",\n'
        '  "situational_opening": "[상황]만 짧게"\n'
        "}\n"
        f"언어: {lang_name} (코드 {lang})"
    )


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
    user_texts: list[str] | None = None,
) -> dict[str, str]:
    """Gemini 실패 시 — 대화 인용·은유·비균질 강점 지형 기반 규칙 서술."""
    scene = situational.get("scene_phrase", "지금까지의 이야기 속")
    bracket_scene = f"[{scene}]"
    top_cat = stats.get("strength_categories") or ["meaning"]
    strength_ko = TOPIC_LABELS_KO.get(top_cat[0], "의미·성찰")
    strength_hint = _uneven_strength_hint(stats)
    resources = positive_resources or []
    anchors = extract_anchor_phrases(user_texts or [])
    q1 = f"「{anchors[0]}」" if len(anchors) > 0 else "당신이 건넨 말"
    q2 = f"「{anchors[1]}」" if len(anchors) > 1 else q1
    people = situational.get("people") or "가까운 사람"

    if voice == "elementary":
        name = nickname or "친구"
        landscape = (
            f"{bracket_scene} 네 마음에는 조용한 바람과 따뜻한 빛이 함께 있어. "
            f"{q1}라고 말해 준 순간이, 지금 네 마음 풍경의 중심이야."
        )
        connection = (
            f"{people}와의 이야기에서, 네가 상대를 어떻게 대하는지가 보여. "
            f"서운함도, 고마움도 실타래처럼 이어져 있어."
        )
        treasure = (
            f"{strength_hint} "
            f"특히 {strength_ko} 쪽에서 눈에 띄게 높아. "
            + (f"{q2} 같은 말은 앞으로의 나눔으로 이어질 씨앗이야." if anchors else "")
        )
    elif voice == "secondary":
        landscape = (
            f"{bracket_scene} 지금 네 안의 풍경은, 말로 옮기기 어려운 무게와 "
            f"동시에 {q1}에서 드러난 빛이 공존하는 모습이야."
        )
        connection = (
            f"관계는 이름이 아니라 태도로 드러나. {people}를 향한 네 마음에는 "
            f"기대와 부채감이 함께 엮여 있는 것 같아."
        )
        treasure = (
            f"{strength_hint} "
            f"{strength_ko} 축에서 봉우리가 높아. "
            f"{q2}는 배움을 나눔으로 바꾸려는 서사의 전환점에 가깝다."
        )
    else:
        landscape = (
            f"{bracket_scene} 당신의 마음 풍경에는, 조급함과 책임이 한 줄기로 "
            f"겹쳐 있습니다. {q1}라고 하신 말은, 그 감정을 결과물이나 관계로 "
            f"승화하려는 시도를 비춥니다."
        )
        connection = (
            f"{'생활 맥락(' + life_context + ') 속에서, ' if life_context and life_context != '—' else ''}"
            f"{people}와의 연결은 사건이 아니라 태도로 남아 있습니다. "
            f"거리, 기대, 미안함이 실타래처럼 엮여 있으며, "
            f"{q2}에서 그 방향이 드러납니다."
        )
        res_note = (
            f" 대화 속 자원으로 {resources[0][:40]}…도 포착됩니다."
            if resources
            else ""
        )
        treasure = (
            f"{strength_hint} "
            f"평생 쌓아 온 지식과 경험이 {strength_ko} 축에서 높은 봉우리를 이루고, "
            f"그것을 나눔으로 전환하려는 서사적 전환점이 {q1}에 담겨 있습니다."
            f"{res_note}"
        )

    return polish_midpoint_report(
        {
            "midpoint_preface": MIDPOINT_MAP_PREFACE,
            "title_landscape": TITLE_LANDSCAPE,
            "title_connection": TITLE_CONNECTION,
            "title_treasure": TITLE_TREASURE,
            "section_landscape": landscape.strip(),
            "section_connection": connection.strip(),
            "section_treasure": treasure.strip(),
            "situational_opening": bracket_scene,
        }
    )


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
        user_texts=user_texts,
    )

    stats_payload = {
        **stats,
        "situational_context": situational,
        "report_voice": voice,
        "gender": gender,
        "age_group": age_group,
        "life_stage": life_stage,
    }

    return polish_midpoint_report(
        {
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
    )


def parse_stored_midpoint_message(text: str) -> dict[str, Any] | None:
    """시트·채팅에 저장된 중간 정리 본문 → last_midpoint_report 복원."""
    body = (text or "").strip()
    if not body or "마음 지도" not in body:
        return None
    preface = MIDPOINT_MAP_PREFACE
    pre_m = re.search(
        r"###\s*지금까지의 대화[^\n]*\n+(.*?)(?=\n####|\Z)",
        body,
        re.S,
    )
    if pre_m:
        preface = pre_m.group(1).strip() or preface

    sections: dict[str, str] = {}
    for m in re.finditer(r"####\s*\[([^\]]+)\]\s*\n(.*?)(?=\n####|\Z)", body, re.S):
        sections[m.group(1).strip()] = m.group(2).strip()

    landscape = sections.get(TITLE_LANDSCAPE, "")
    connection = sections.get(TITLE_CONNECTION, "")
    treasure = sections.get(TITLE_TREASURE, "")
    if not any((landscape, connection, treasure)):
        return None

    return polish_midpoint_report(
        {
            "midpoint_preface": preface,
            "title_landscape": TITLE_LANDSCAPE,
            "section_landscape": landscape,
            "title_connection": TITLE_CONNECTION,
            "section_connection": connection,
            "title_treasure": TITLE_TREASURE,
            "section_treasure": treasure,
        }
    )


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
