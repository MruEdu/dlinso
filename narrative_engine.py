"""비가시적 서사 분석 — 들쭉날쭉 지표·자원 추출·인생 요약본."""

from __future__ import annotations

import json
import re
from typing import Any

import google.generativeai as genai

from env_config import ENV_PATH, get_gemini_api_key, get_gemini_model_name
from personas import LANG_REPLY  # noqa: F401 — re-export (isolation/learning 호환)

_gemini_configured = False

PROFILE_KEYS = (
    "agency",
    "reflection_depth",
    "emotional_richness",
    "relational_connection",
)
PROFILE_LABELS: dict[str, str] = {
    "agency": "자아 주도성",
    "reflection_depth": "성찰 깊이",
    "emotional_richness": "정서적 풍요",
    "relational_connection": "관계성",
}

NARRATIVE_STAGES = [
    "탐색",
    "갈등 인식",
    "재구성",
    "실천 의지",
    "통합",
]

LIFE_CONTEXTS = [
    "가족",
    "일·커리어",
    "자아",
    "관계",
    "건강",
    "과거·기억",
    "미래·꿈",
    "기타",
]

LANG_NAMES = {
    "ko": "Korean",
    "en": "English",
    "mn": "Mongolian",
    "ja": "Japanese",
    "zh": "Chinese",
    "vi": "Vietnamese",
}


def default_profile() -> dict[str, float]:
    return {key: 50.0 for key in PROFILE_KEYS}


def ensure_gemini_configured() -> None:
    global _gemini_configured
    if _gemini_configured:
        return
    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError(
            f"GEMINI_API_KEY가 설정되지 않았습니다. {ENV_PATH} 파일을 확인하세요."
        )
    genai.configure(api_key=api_key)
    _gemini_configured = True


def _extract_json(text: str) -> dict | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None


def _clamp_score(value: object, default: float = 50.0) -> float:
    try:
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return default


def _analysis_model(
    max_tokens: int = 700,
    *,
    temperature: float = 0.2,
) -> genai.GenerativeModel:
    ensure_gemini_configured()
    return genai.GenerativeModel(
        get_gemini_model_name(),
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
    )


def summarize_messages(messages: list[dict], existing_summary: str = "") -> str:
    if not messages:
        return existing_summary

    lines = []
    for msg in messages:
        role = "참여자" if msg["role"] == "user" else "안내자"
        lines.append(f"{role}: {msg['content'][:800]}")

    prior = (
        f"\n[기존 요약]\n{existing_summary}\n"
        if existing_summary.strip()
        else ""
    )
    prompt = (
        "다음 인생 서사 대화를 200~350자로 요약하세요. "
        "긍정적 자원, 갈등, 전환점을 포함합니다."
        f"{prior}\n\n[대화]\n" + "\n".join(lines)
    )
    model = _analysis_model(500)
    response = model.generate_content(prompt)
    return (response.text or "").strip() or existing_summary


def extract_interests(messages: list[dict], current: list[str] | None = None) -> list[str]:
    user_lines = [m["content"] for m in messages if m["role"] == "user"][-12:]
    if not user_lines:
        return current or ["—", "—", "—"]

    context = "\n".join(f"- {line[:400]}" for line in user_lines)
    prev = ", ".join(current) if current else "없음"
    prompt = (
        '참여자 발화에서 핵심 관심사 3개. JSON만: {"interests": ["a","b","c"]}\n'
        f"이전: {prev}\n\n[발화]\n{context}"
    )
    model = _analysis_model(300)
    response = model.generate_content(prompt)
    data = _extract_json(response.text or "")
    if data and isinstance(data.get("interests"), list):
        items = [str(x).strip() for x in data["interests"][:3] if str(x).strip()]
        while len(items) < 3:
            items.append("—")
        return items[:3]
    return current or ["—", "—", "—"]


def extract_positive_resources(
    messages: list[dict],
    existing: list[str] | None = None,
) -> list[str]:
    """Phase 1에서 수집된 긍정적 서사 자원."""
    user_lines = [m["content"] for m in messages if m["role"] == "user"]
    if not user_lines:
        return existing or []

    context = "\n".join(f"- {line[:500]}" for line in user_lines[-15:])
    prev = "; ".join(existing) if existing else "없음"
    prompt = (
        "참여자 발화에서 **긍정적 서사 자원**만 추출(성취·즐거운 기억·자랑·추억·힘). "
        '각 1문장, 최대 6개. JSON만: {"resources": ["...", "..."]}\n'
        f"기존(병합 참고): {prev}\n\n[발화]\n{context}"
    )
    model = _analysis_model(500)
    response = model.generate_content(prompt)
    data = _extract_json(response.text or "")
    merged: list[str] = list(existing or [])
    if data and isinstance(data.get("resources"), list):
        for item in data["resources"]:
            s = str(item).strip()
            if s and s not in merged:
                merged.append(s)
    return merged[:8]


def translate_to_korean(text: str, source_lang: str = "en") -> str:
    """외국어 대화 → 연구용 한국어 번역본 (실패 시 원문 반환)."""
    if not text.strip():
        return ""
    if source_lang == "ko":
        return text.strip()
    try:
        src = LANG_NAMES.get(source_lang, source_lang)
        prompt = (
            f"다음 텍스트를 연구 기록용 **한국어**로 자연스럽게 번역하세요. "
            f"원문 언어: {src}. 번역문만 출력.\n\n{text[:2000]}"
        )
        model = _analysis_model(400)
        response = model.generate_content(prompt)
        return (response.text or "").strip() or text.strip()
    except Exception:  # noqa: BLE001
        return text.strip()


def pick_summoned_narrative(
    resources: list[str],
    user_message: str,
    assistant_message: str,
) -> str:
    """이번 턴에 연결된 과거 서사 한 줄."""
    if not resources:
        return ""
    blob = f"{user_message} {assistant_message}"
    for r in resources:
        if any(word in blob for word in r.split()[:3] if len(word) > 1):
            return r
    return resources[0]


def _format_research_list(value: object, max_items: int = 4) -> str:
    """시트 기록용 — 핵심 테마·은유·전이 지점을 한 줄 문자열로."""
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "; ".join(parts[:max_items])
    if value is None:
        return ""
    return str(value).strip()[:500]


def analyze_narrative_turn(
    user_message: str,
    assistant_message: str,
    context_summary: str = "",
) -> dict[str, float | str]:
    """비가시적 지표 + 네러티브 연구 심층 필드 (UI 미노출, 시트 전용)."""
    stages = " / ".join(NARRATIVE_STAGES)
    contexts = " / ".join(LIFE_CONTEXTS)
    prompt = (
        "당신은 dlinso **네러티브 연구자 지원 허브**의 서사 구조화 도우미입니다. "
        "한 턴의 대화를 토드 로즈 개개인성·들쭉날쭉 서사 연구 관점에서 살펴보세요. "
        "점수는 0~100, 서로 독립(평균·종합 금지). **반드시** 아래 연구 필드를 채우세요.\n\n"
        "JSON만 출력:\n"
        "{\n"
        '  "agency": 0-100,\n'
        '  "reflection_depth": 0-100,\n'
        '  "emotional_richness": 0-100,\n'
        '  "relational_connection": 0-100,\n'
        f'  "life_context": "{contexts}" 중 하나,\n'
        f'  "narrative_stage": "{stages}" 중 하나,\n'
        '  "narrative_themes": ["핵심 테마1", "테마2"],\n'
        '  "metaphors": ["참여자가 쓴 은유·비유1", "은유2"],\n'
        '  "turning_points": ["생애주기적 전이·전환 지점1"]\n'
        "}\n\n"
        "규칙:\n"
        "- narrative_themes: 이번 턴의 **핵심 주제** 1~3개 (한국어 짧은 구)\n"
        "- metaphors: 참여자·안내자가 드러낸 **주요 은유·상징** 0~3개 (없으면 [])\n"
        "- turning_points: 학력·생애주기와 연결된 **전이·갈림길** 0~2개 (없으면 [])\n"
        f"[이전 요약]\n{context_summary or '없음'}\n\n"
        f"[참여자]\n{user_message[:1200]}\n\n[안내자]\n{assistant_message[:1200]}"
    )
    model = _analysis_model(900)
    response = model.generate_content(prompt)
    data = _extract_json(response.text or "") or {}

    profile = {key: _clamp_score(data.get(key), 50.0) for key in PROFILE_KEYS}

    stage = str(data.get("narrative_stage", "탐색")).strip()
    if stage not in NARRATIVE_STAGES:
        stage = "탐색"

    life_context = str(data.get("life_context", "기타")).strip()
    if life_context not in LIFE_CONTEXTS:
        life_context = "기타"

    return {
        **profile,
        "narrative_stage": stage,
        "life_context": life_context,
        "narrative_themes": _format_research_list(data.get("narrative_themes")),
        "metaphors": _format_research_list(data.get("metaphors")),
        "turning_points": _format_research_list(data.get("turning_points")),
    }


def generate_humanistic_midpoint_report(
    messages: list[dict],
    stats: dict[str, Any],
    *,
    age_group: str = "",
    gender: str = "",
    life_stage: str = "",
    participant_id: str = "",
    life_context: str = "",
    positive_resources: list[str] | None = None,
    situational_context: dict[str, str] | None = None,
    lang: str = "ko",
) -> dict[str, str]:
    """
    특허 통계(비공개)를 바탕으로 인문학적 서술형 중간 리포트 생성.
    화면에는 수치·OR·Jaggedness를 절대 넣지 않음.
    """
    from hbridge_analysis import (
        MIDPOINT_MAP_PREFACE,
        TITLE_CONNECTION,
        TITLE_LANDSCAPE,
        TITLE_TREASURE,
        build_midpoint_report_prompt,
        compose_humanistic_sections_fallback,
        polish_midpoint_report,
        resolve_report_voice,
    )

    user_lines = []
    for msg in messages:
        if msg.get("role") != "user":
            continue
        text = str(msg.get("content") or msg.get("display") or "").strip()
        if text:
            user_lines.append(text[:600])
    if not user_lines:
        user_lines = ["(아직 이야기가 짧습니다)"]

    situational = situational_context or {}
    scene = situational.get("scene_phrase", "지금까지 나누어 주신 이야기 속")
    voice = resolve_report_voice(life_stage, age_group)
    nick = (participant_id or "").strip()[:12] or "참여자"
    resources = "\n".join(f"- {r}" for r in (positive_resources or [])[:5]) or "없음"

    voice_guide = {
        "elementary": (
            f'초등 맞춤: 서사 동행자 dlinso. "{nick}아/야" 다정한 입말체. '
            "참여자 말을 「」로 1~2회 인용. 은유는 쉬운 말로."
        ),
        "secondary": (
            "중·고 맞춤: 서사 동행자. 친근한 존댓말·반말. "
            "관계의 태도·부채감을 짚되 훈계 금지. 핵심 구절 인용 필수."
        ),
        "adult": (
            "대학·성인: 서사 동행자로서 격조 있고 따뜻한 인문학적 존댓말. "
            "한 사람의 인생 전체를 존중. 심리검사·지표식 라벨·별표 강조 금지."
        ),
    }[voice]

    lang_name = LANG_NAMES.get(lang, "Korean")
    prompt = build_midpoint_report_prompt(
        user_lines=user_lines,
        stats=stats,
        voice_guide=voice_guide,
        scene=scene,
        gender=gender,
        resources=resources,
        life_context=life_context or "—",
        lang=lang,
        lang_name=lang_name,
    )

    try:
        model = _analysis_model(max_tokens=2000, temperature=0.42)
        response = model.generate_content(prompt)
        data = _extract_json(response.text or "")
        if data and data.get("section_landscape"):
            return polish_midpoint_report(
                {
                    "midpoint_preface": str(
                        data.get("midpoint_preface", MIDPOINT_MAP_PREFACE)
                    ).strip(),
                    "title_landscape": str(
                        data.get("title_landscape", TITLE_LANDSCAPE)
                    ),
                    "title_connection": str(
                        data.get("title_connection", TITLE_CONNECTION)
                    ),
                    "title_treasure": str(
                        data.get("title_treasure", TITLE_TREASURE)
                    ),
                    "section_landscape": str(
                        data.get("section_landscape", "")
                    ).strip(),
                    "section_connection": str(
                        data.get("section_connection", "")
                    ).strip(),
                    "section_treasure": str(
                        data.get("section_treasure", "")
                    ).strip(),
                    "situational_opening": str(
                        data.get("situational_opening", f"[{scene}]")
                    ).strip(),
                }
            )
    except Exception:  # noqa: BLE001
        pass

    return compose_humanistic_sections_fallback(
        stats=stats,
        situational=situational,
        voice=voice,
        nickname=nick,
        gender=gender,
        positive_resources=positive_resources,
        life_context=life_context,
        user_texts=user_lines,
    )


def generate_life_summary(
    messages: list[dict],
    positive_resources: list[str],
    age_group: str,
    participant_id: str = "",
    life_stage: str = "",
) -> str:
    """대화가 충분히 진행되면 선물하는 짧은 인생 요약본."""
    lines = []
    for msg in messages[-20:]:
        role = "나" if msg["role"] == "user" else "동반자"
        lines.append(f"{role}: {msg['content'][:600]}")

    resources = "\n".join(f"- {r}" for r in positive_resources[:6]) or "- (수집 중)"
    prompt = (
        f"참여자({participant_id or '익명'}, {age_group}, {life_stage or '미상'})와 "
        "나눈 인생 서사 대화를 바탕으로 **한 편의 짧은 인생 요약본**(400~600자).\n"
        "형식: 따뜻한 편지체, 2~3문단, 제목 한 줄. "
        f"학력·생애주기({life_stage})에 맞는 어휘와 톤.\n"
        "Phase 1 긍정 자원을 반드시 녹이고, 평가·점수·진단 용어 금지.\n"
        "마지막에 '오늘의 당신에게' 한 문장.\n\n"
        f"[긍정적 서사 자원]\n{resources}\n\n[대화]\n" + "\n".join(lines)
    )
    model = _analysis_model(900)
    response = model.generate_content(prompt)
    return (response.text or "").strip() or "오늘 나눈 이야기가 당신 안에 차곡차곡 남았습니다. 🌿"


def generate_learning_narrative_report(
    messages: list[dict],
    stats: dict[str, Any],
    *,
    learning_audience: str = "",
    age_group: str = "",
    life_stage: str = "",
    participant_id: str = "",
    situational_context: dict[str, str] | None = None,
    lang: str = "ko",
    learning_signals: dict[str, Any] | None = None,
) -> dict[str, str]:
    """학습 서사 검사 리포트 — 4대 이론 기반 서술 (수치·별표 미노출)."""
    from learning_analysis import (
        LEARNING_MAP_PREFACE,
        TITLE_FOUR_LENSES,
        TITLE_IDENTITY,
        TITLE_JAGGED,
        TITLE_PRESCRIPTION,
        build_learning_report_prompt,
        compose_learning_report_fallback,
        polish_learning_report,
        build_learning_voice_guide,
        resolve_learning_voice,
    )

    user_lines = []
    for msg in messages:
        if msg.get("role") != "user":
            continue
        text = str(msg.get("content") or msg.get("display") or "").strip()
        if text:
            user_lines.append(text[:600])
    if not user_lines:
        user_lines = ["(아직 이야기가 짧습니다)"]

    situational = situational_context or {}
    scene = situational.get("scene_phrase", "지금까지의 배움 이야기")
    voice = resolve_learning_voice(learning_audience, life_stage, age_group)
    nick = (participant_id or "").strip()[:12] or "참여자"

    voice_guide = build_learning_voice_guide(
        learning_audience,
        voice=voice,
        nick=nick,
    )

    lang_name = LANG_NAMES.get(lang, "Korean")
    prompt = build_learning_report_prompt(
        user_lines=user_lines,
        stats=stats,
        voice_guide=voice_guide,
        scene=scene,
        learning_audience=learning_audience,
        age_group=age_group,
        life_stage=life_stage,
        lang_name=lang_name,
        learning_signals=learning_signals,
    )

    try:
        model = _analysis_model(max_tokens=2000, temperature=0.42)
        response = model.generate_content(prompt)
        data = _extract_json(response.text or "")
        if data and data.get("section_identity"):
            return polish_learning_report(
                {
                    "learning_preface": str(
                        data.get("learning_preface", LEARNING_MAP_PREFACE)
                    ).strip(),
                    "title_identity": str(
                        data.get("title_identity", TITLE_IDENTITY)
                    ),
                    "title_four_lenses": str(
                        data.get("title_four_lenses", TITLE_FOUR_LENSES)
                    ),
                    "title_jagged": str(data.get("title_jagged", TITLE_JAGGED)),
                    "title_prescription": str(
                        data.get("title_prescription", TITLE_PRESCRIPTION)
                    ),
                    "section_identity": str(
                        data.get("section_identity", "")
                    ).strip(),
                    "section_four_lenses": str(
                        data.get("section_four_lenses", "")
                    ).strip(),
                    "section_jagged": str(
                        data.get("section_jagged", "")
                    ).strip(),
                    "section_prescription": str(
                        data.get("section_prescription", "")
                    ).strip(),
                    "jagged_profile_sentence": str(
                        data.get("jagged_profile_sentence", "")
                    ).strip(),
                    "learning_tactic": str(data.get("learning_tactic", "")).strip(),
                    "situational_opening": str(
                        data.get("situational_opening", f"[{scene}]")
                    ).strip(),
                }
            )
    except Exception:  # noqa: BLE001
        pass

    return compose_learning_report_fallback(
        stats=stats,
        situational=situational,
        voice=voice,
        learning_audience=learning_audience,
        user_texts=user_lines,
    )
