"""
H-가교 특허 기반 중간 분석 — 자기 내적 OR · Jaggedness Index · 서사 정밀도.

PDF 4~8페이지: LDA(주제) → SNA(맥락 구조) → Intra-individual OR(성취 vs 일반 구간)
→ 들쭉날쭉 지표(Jaggedness Index). 평균·집단 비교가 아닌 개인 내 맥락 비교.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from typing import Any

# ── 1단계(LDA 대체): 주제·강점 키워드 군 ─────────────────────────────────────
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
        "합격",
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

WORD_RE = re.compile(r"[가-힣a-zA-Z]{2,}")


def _tokenize(text: str) -> list[str]:
    return WORD_RE.findall((text or "").lower())


def _segment_score(text: str, markers: tuple[str, ...]) -> float:
    if not text.strip():
        return 0.0
    hits = sum(1 for m in markers if m in text)
    tokens = max(len(_tokenize(text)), 1)
    return hits / tokens


def split_achievement_vs_general(
    user_texts: list[str],
) -> tuple[list[str], list[str]]:
    """개인 발화를 성취·고조 구간 vs 일반 구간으로 분할 (개인 내 참조)."""
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
    """구간별 키워드 군 출현 확률 P(category|segment)."""
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
    """자기 내적 OR: 성취 구간 vs 일반 구간 키워드 군 확률 비."""
    p_ach = _category_probs(achievement_texts)
    p_gen = _category_probs(general_texts)
    or_map: dict[str, float] = {}
    for cat in TOPIC_LEXICON:
        o1 = _odds(p_ach.get(cat, 0.0))
        o0 = _odds(p_gen.get(cat, 0.0))
        or_map[cat] = round(o1 / o0, 3) if o0 > 0 else round(o1, 3)
    return or_map


def jaggedness_index(domain_scores: dict[str, float]) -> float:
    """
    들쭉날쭉 지표 — 영역 점수의 변동성(집단 평균 대비 개인 내 봉우리).
    0~100 스케일, 높을수록 특정 영역에 강점이 치우침.
    """
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
    """1단계: 주제 군별 가중 빈도 (LDA 대체)."""
    probs = _category_probs(user_texts)
    ranked = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    return [(k, round(v, 4)) for k, v in ranked if v > 0]


def sna_keyword_links(user_texts: list[str], top_n: int = 5) -> list[tuple[str, str, int]]:
    """2단계: 공출현 키워드 쌍 (SNA 간이)."""
    co: Counter[tuple[str, str]] = Counter()
    for text in user_texts:
        toks = list(dict.fromkeys(_tokenize(text)))[:40]
        for i, a in enumerate(toks):
            for b in toks[i + 1 : i + 4]:
                if a != b:
                    pair = tuple(sorted((a, b)))
                    co[pair] += 1
    return [
        (a, b, c)
        for (a, b), c in co.most_common(top_n)
    ]


def narrative_precision_score(
    messages: list[dict],
    profile: dict[str, float] | None = None,
) -> float:
    """
    서사 정밀도 0~100 — 적응형 비계 개입 여부 판단.
    발화 길이·어휘 다양성·성찰 깊이(프로필) 종합.
    """
    user_texts = [str(m.get("content") or "") for m in messages if m.get("role") == "user"]
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


TOPIC_LABELS_KO: dict[str, str] = {
    "agency": "자아 주도성",
    "relation": "관계·연대",
    "emotion": "정서 표현",
    "meaning": "의미·성찰",
    "achievement": "성취·도전",
    "memory": "기억·서사",
}


def run_intra_individual_or_pipeline(
    messages: list[dict],
    profile: dict[str, float] | None = None,
    life_context: str = "",
    positive_resources: list[str] | None = None,
) -> dict[str, Any]:
    """전체 파이프라인 → 리포트 3영역 + 통계 메타."""
    user_texts = [
        str(m.get("content") or m.get("display") or "").strip()
        for m in messages
        if m.get("role") == "user" and str(m.get("content") or "").strip()
    ]
    if not user_texts:
        user_texts = ["(아직 발화 없음)"]

    ach, gen = split_achievement_vs_general(user_texts)
    or_map = intra_individual_odds_ratios(ach, gen)
    topics = lda_topic_ranking(user_texts)
    links = sna_keyword_links(user_texts)

    domain_scores = {
        TOPIC_LABELS_KO.get(k, k): round(v * 100, 1)
        for k, v in _category_probs(user_texts).items()
    }
    jagged = jaggedness_index(domain_scores)

    top_or = sorted(or_map.items(), key=lambda x: x[1], reverse=True)[:3]
    strength_cats = [c for c, v in top_or if v >= 1.15]
    if not strength_cats:
        strength_cats = [top_or[0][0]] if top_or else ["meaning"]

    precision = narrative_precision_score(messages, profile)

  # ── ① 개개인성 상황 ──
    ach_preview = ach[0][:120] + ("…" if len(ach[0]) > 120 else "")
    or_lines = [
        f"· {TOPIC_LABELS_KO.get(cat, cat)}: OR={ratio:.2f} "
        f"(성취 구간 P={_category_probs(ach).get(cat, 0):.3f} / "
        f"일반 구간 P={_category_probs(gen).get(cat, 0):.3f})"
        for cat, ratio in top_or
    ]
    individuality = (
        "당신의 발화를 **개인 안에서만** 비교한 자기 내적 오즈비(Intra-individual OR)입니다. "
        "타인·평균과 비교하지 않습니다.\n\n"
        f"**성취·고조 구간** ({len(ach)}개 발화)과 **일반·일상 구간** ({len(gen)}개 발화)에서 "
        "키워드 군 출현 확률을 나누어 산출했습니다.\n\n"
        + "\n".join(or_lines)
        + f"\n\n대표 성취 구간 발화: 「{ach_preview}」"
    )

  # ── ② 맥락적 성격 ──
    topic_str = ", ".join(
        f"{TOPIC_LABELS_KO.get(k, k)}({p:.2%})" for k, p in topics[:4]
    ) or "주제 추출 중"
    link_str = (
        " · ".join(f"{a}↔{b}({c})" for a, b, c in links[:4]) if links else "연결 패턴 수집 중"
    )
    ctx = life_context if life_context and life_context != "—" else "대화에서 드러난 맥락"
    contextual = (
        f"**맥락(생활 영역):** {ctx}\n\n"
        f"**주제 구조(1단계·LDA 대체):** {topic_str}\n\n"
        f"**의미 연결망(2단계·SNA):** {link_str}\n\n"
        f"**서사 정밀도:** {precision:.0f}/100 "
        f"({'심화 질문이 도움이 되는 단계' if precision < 55 else '이미 풍부한 서사 — 가벼운 동행'})"
    )

  # ── ③ 강점 서사 ──
    strength_labels = [TOPIC_LABELS_KO.get(c, c) for c in strength_cats]
    resources = positive_resources or []
    res_block = (
        "\n".join(f"· {r}" for r in resources[:4])
        if resources
        else "· 대화 속에서 긍정적 자원이 차곡차곡 쌓이고 있습니다."
    )
    strength_narr = (
        f"**들쭉날쭉 지표(Jaggedness Index): {jagged:.1f} / 100**\n"
        f"평균에 맞추지 않고, 특정 영역에서 **봉우리처럼 솟는 강점**이 "
        f"{'뚜렷합니다' if jagged >= 45 else '점차 드러나고 있습니다'}.\n\n"
        f"**통계적으로 두드러진 강점 영역:** {', '.join(strength_labels)}\n"
        f"(OR≥1.15 또는 상대 최고치 기준)\n\n"
        f"**이미 수집된 긍정 서사 자원:**\n{res_block}"
    )

    stats = {
        "jaggedness_index": jagged,
        "narrative_precision": precision,
        "odds_ratios": or_map,
        "topics": topics,
        "sna_links": [{"a": a, "b": b, "w": c} for a, b, c in links],
        "achievement_segments": len(ach),
        "general_segments": len(gen),
        "domain_scores": domain_scores,
    }

    return {
        "individuality_situation": individuality,
        "contextual_personality": contextual,
        "strength_narrative": strength_narr,
        "jaggedness_index": jagged,
        "narrative_precision": precision,
        "stats_json": json.dumps(stats, ensure_ascii=False),
        "stats": stats,
    }


def format_midpoint_followup() -> str:
    return (
        "이 분석에 대해 어떻게 생각하시나요? "
        "더 깊은 이야기를 들려주세요."
    )


def format_full_midpoint_message(report: dict[str, Any]) -> str:
    """채팅 기록·시트용 전체 본문."""
    parts = [
        "### 지금까지의 대화 중간 정리 및 나의 특성 분석",
        "",
        "#### ① 개개인성 상황",
        report["individuality_situation"],
        "",
        "#### ② 맥락적 성격",
        report["contextual_personality"],
        "",
        "#### ③ 강점 서사",
        report["strength_narrative"],
        "",
        f"_(들쭉날쭉 지표 {report.get('jaggedness_index', 0):.1f} · "
        f"서사 정밀도 {report.get('narrative_precision', 0):.0f})_",
        "",
        format_midpoint_followup(),
    ]
    return "\n".join(parts)
