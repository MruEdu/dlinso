"""서사 동행자 · Narrative Companion — System Instruction · 사진 상징 분석."""

from __future__ import annotations

import json
from typing import Any

import google.generativeai as genai

from env_config import get_gemini_model_name
from narrative_engine import LANG_NAMES, _extract_json, ensure_gemini_configured
from narrative_style import EMPATHETIC_REPHRASE_INSTRUCTION, user_turn_context_for_llm
from personas import GUIDE_NAME, LANG_REPLY

NARRATIVE_COMPANION_NAME = GUIDE_NAME
GARDEN_KEEPER_NAME = NARRATIVE_COMPANION_NAME

# System Instruction — 모든 모듈 공통 최소 제약
GLOBAL_MAIEUTIC_SYSTEM_INSTRUCTION = """
너는 참여자의 내러티브를 경청하고 자연스럽게 생각을 따라가는 들니소(dlniso) 엔진이다.
[치명적 절대 규칙 - 위반 시 시스템 오류]
- **Elenchus**, **공감**, **Maieutic question** 같은 학술용어 태그를 절대 화면에 출력하지 마라.
- 문장에 번호(①, ②, ③, 1), 2))를 매겨서 질문하지 마라. 자연스러운 하나의 구어체로만 대화하라.
- 모든 답변은 절대 두 문장을 넘지 않는 '담백한 단문'으로만 구성하라. 친절한 설명조나 훈계는 엄격히 금지한다.
"""

_MODULE_INSTRUCTIONS: dict[str, str] = {
    "lifespan": """
[서사 수집 모듈 지시: 자서전 쓰기]
- 이 방의 본질은 자서전 집필을 위한 이야기 수집이다. 참여자가 자신의 삶을 돌아보게 하라.
- "당신의 색깔은 무엇인가요?", "그 장면의 씨앗은?" 같은 지나치게 추상적이고 사색적인 메타포 질문을 절대 던지지 마라.
- 참여자가 겪은 '당시의 구체적인 상황, 주변 환경, 날씨, 행동, 만났던 인물' 등 사실(Fact)을 따라가며 구체적인 회상을 촉진하라.
- 참여자가 일상적인 대화를 건네면 너도 즉시 친구처럼 격식 없는 편안한 톤으로 어조를 동적 미러링하라.
- 직전 턴에 던진 질문 구조를 반복하지 마라. 참여자가 "질문이 같다"고 느끼면 즉시 프레임을 바꾸어라.
""",
    "learning": """
[학습 모듈 지시: 메타인지 자극]
- 감정적, 추상적 질문을 전면 배제하고, 오직 구체적인 학습 상황과 행동 팩트 위주로 질문하라.
- 어제 공부한 시간, 스마트폰 차단 여부 등 구체적 맥락을 단문으로 거울처럼 비추어주어 스스로 학습 걸림돌을 깨닫게 하라.
""",
    "isolation": """
[숲 모듈 지시: 고립과 외로움]
- 깊은 고독과 외로움을 겪는 청소년의 이야기를 100% 온전히 수용하되 절대 조언하거나 훈계하지 마라.
- 참여자의 대화 속에서 미세하게 포착되는 '작은 추진력(예: 방 청소를 했다, 밖을 보았다 등 행동의 의지)'을 예민하게 낚아채어, 세상 밖으로 한 걸음 나아갈 방향성을 온기 있게 제시하라.
""",
    "mindfulness": """
[마음챙김 모듈 지시: 현존과 신체 이완]
- 이 방의 본질은 판단 없이 현재의 호흡, 신체 감각, 감정을 그대로 알아차리게 돕는 마음챙김(Mindfulness) 가이드이다.
- 질문을 통해 참여자의 생각을 복잡하게 만들지 마라. 생각을 멈추고 '느낌'으로 돌아오게 하라.
- 참여자에게 "지금 숨이 들어오고 나가는 느낌은 어떠니?", "어깨나 목에 힘이 들어가 있진 않으니?" 처럼 신체적 감각에 집중하는 담백한 단문 가이드를 제공하라.
- 참여자의 불안이나 거친 호흡을 있는 그대로 안전하게 수용하고, 서두르지 말고 천천히 호흡의 리듬을 따라가라.
- 훈계, 평가, 조언은 엄격히 금지하며, 오직 평온하고 고요한 안전 기지의 톤을 유지하라.
""",
}

TURN_ADDON_HEADER = """
[이번 턴 — 직전 맥락 반영, 질문은 새로]
"""


def build_global_maieutic_system_instruction(lang: str = "ko") -> str:
    """Gemini system_instruction 최상단 — 언어별 응답 언어 명시."""
    reply_lang = LANG_REPLY.get(lang, "Korean")
    native = LANG_NAMES.get(lang, reply_lang)
    return (
        GLOBAL_MAIEUTIC_SYSTEM_INSTRUCTION
        + f"\n\n[응답 언어 — 필수]\n"
        f"참여자 UI 언어: **{native}** ({reply_lang}). "
        f"반드시 **{reply_lang}** 로만 답하세요. "
        "다른 언어로 섞지 마세요(고유명사·인용 제외)."
    )


def build_system_instruction(module_type: str, lang: str = "ko") -> str:
    """모듈별 독립 프롬프트 — lifespan / learning / isolation / mindfulness 4진 분기."""
    base = build_global_maieutic_system_instruction(lang)
    module = (module_type or "lifespan").strip().lower()
    addon = _MODULE_INSTRUCTIONS.get(module, _MODULE_INSTRUCTIONS["lifespan"])
    return base + "\n\n" + addon.strip()


def build_maieutic_addon(*, last_user: str = "", user_turns: int = 0) -> str:
    block = TURN_ADDON_HEADER + EMPATHETIC_REPHRASE_INSTRUCTION
    if user_turns:
        block += f"\n- 참여자 발화 누적: {user_turns}회."
    block += user_turn_context_for_llm(last_user, max_len=180)
    block += (
        "\n- 담백한 단문 2개 이내. 직전과 다른 질문. "
        "원문·오타 복붙 금지. 학술 태그·번호 매기기 금지."
    )
    return block


def build_conversation_phase_addon(
    user_turns: int,
    *,
    midpoint_completed: bool = False,
    min_turns: int = 10,
) -> str:
    """
    10턴 미만: 인사·공감 위주. 10턴 이상·중간정리 전: 분석 리포트 금지.
    중간정리 후: 정밀 동행(리포트는 이미 공유됨).
    """
    if midpoint_completed:
        return (
            "\n\n[대화 단계 · 마음 지도 이후]\n"
            "- 중간 정리 리포트는 이미 나누었음. **수치·OR·지표는 말하지 말 것**.\n"
            "- 참여자가 지도에 대한 생각·추가 장면을 말하도록 짧게 초대.\n"
        )
    if user_turns < min_turns:
        return (
            f"\n\n[대화 단계 · 서사 자산화 전 ({min_turns}회 미만)]\n"
            "- **가벼운 인사·공감** 위주. 짧고 따뜻하게.\n"
            "- 특성 진단·통계·리포트 형식·들쭉날쭉 해석 **금지**.\n"
            "- 장소·사람을 무겁게 캐묻지 말 것.\n"
        )
    return (
        f"\n\n[대화 단계 · 서사 충분 ({min_turns}회 이상, 중간정리 전)]\n"
        "- 아직 **중간 정리 리포트 본문을 출력하지 말 것**(버튼으로만 제공).\n"
        "- 공감 + 구체 장면을 부드럽게 유도. 심화 질문은 가볍게 1개.\n"
    )


def build_adaptive_scaffolding_addon(narrative_precision: float) -> str:
    """서사 정밀도가 낮을 때만 구체화 질문으로 개입."""
    p = max(0.0, min(100.0, float(narrative_precision)))
    if p < 45.0:
        return (
            "\n\n[적응형 비계 · 서사 정밀도 낮음]\n"
            f"- 현재 서사 정밀도: {p:.0f}/100 — **반드시** 구체화 질문 1개.\n"
            "- 참여자가 방금 쓴 **인물·장소·사건·감정 단어** 하나를 짚어, "
            "언제·어디·누구 중 **하나만** 담백히 물으세요.\n"
            "- **소리·향기·냄새·촉감·작은 문** 같은 표현을 매 턴 쓰지 마세요.\n"
            "- 조언·처방·요약 대신 짧은 질문 하나로 마무리."
        )
    if p < 65.0:
        return (
            "\n\n[적응형 비계 · 서사 정밀도 보통]\n"
            f"- 현재 서사 정밀도: {p:.0f}/100 — 필요할 때만 가벼운 심화 1개.\n"
            "- 참여자가 이미 풍부하게 쓴 부분은 되풀이하지 마세요."
        )
    return (
        "\n\n[적응형 비계 · 서사 정밀도 높음]\n"
        f"- 현재 서사 정밀도: {p:.0f}/100 — **과잉 개입 금지**.\n"
        "- 심화 질문은 짧게 하거나, 인정 위주로 동행하세요.\n"
        "- 참여자의 리듬을 존중하고 문장을 끊지 마세요."
    )


def analyze_uploaded_image(
    image_bytes: bytes,
    mime_type: str,
    user_note: str = "",
    *,
    lang: str = "ko",
) -> dict[str, str]:
    """
    이미지-텍스트 융합: 시각 분석 + 다국어적·문화적 심리 상징 해석.
    """
    ensure_gemini_configured()
    note = (user_note or "").strip()[:500]
    reply_lang = LANG_REPLY.get(lang, "Korean")
    prompt = (
        f"You are {NARRATIVE_COMPANION_NAME} (Narrative Companion) for dlinso.\n"
        "Read this photo for a warm, human conversation — not a technical report.\n"
        f"Write all string values in {reply_lang} only.\n"
        "Output valid JSON with exactly these keys (no markdown, no code fence):\n"
        '  "visual": "1–2 gentle sentences: what you see and the feeling it suggests",\n'
        '  "symbol": "one concrete detail that could open the person\'s story",\n'
        '  "hook": "one open question to invite their story (do not answer it)"\n'
        f"{f'Participant note with the photo: {note}' if note else ''}"
    )
    model = genai.GenerativeModel(
        get_gemini_model_name(),
        generation_config=genai.GenerationConfig(
            temperature=0.45,
            max_output_tokens=600,
        ),
    )
    try:
        response = model.generate_content(
            [
                {"mime_type": mime_type or "image/jpeg", "data": image_bytes},
                prompt,
            ]
        )
        data = _extract_json(response.text or "") or {}
        visual = str(data.get("visual", "")).strip()
        symbol = str(data.get("symbol", "")).strip()
        hook = str(data.get("hook", "")).strip()
        if not visual and response.text:
            visual = response.text.strip()[:400]
        return {
            "visual": visual or "—",
            "symbol": symbol or "—",
            "hook": hook or "—",
        }
    except Exception:  # noqa: BLE001
        return {
            "visual": "—",
            "symbol": "—",
            "hook": "—",
        }


def _clean_analysis_field(value: str) -> str:
    text = (value or "").strip()
    if not text or text in ("—", "-"):
        return ""
    if text.startswith("{"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return _clean_analysis_field(str(parsed.get("visual", "")))
        except json.JSONDecodeError:
            pass
    return text


def format_image_display_for_user(
    analysis: dict[str, str] | None,
    user_text: str,
) -> str:
    """채팅 말풍선에 보이는 짧은 문장 — 기계적 메타데이터는 숨김."""
    text = (user_text or "").strip()
    if text:
        return text
    if not analysis:
        return "📷 사진"
    visual = _clean_analysis_field(str(analysis.get("visual", "")))
    if visual:
        return visual[:240]
    return "📷 사진을 보냈어요"


def format_image_context_for_model(
    analysis: dict[str, str],
    user_text: str = "",
) -> str:
    """Gemini 대화용 맥락 — UI에 노출하지 않음."""
    lines: list[str] = []
    note = (user_text or "").strip()
    if note:
        lines.append(f"참여자가 함께 적은 말: {note}")
    visual = _clean_analysis_field(str(analysis.get("visual", "")))
    symbol = _clean_analysis_field(str(analysis.get("symbol", "")))
    hook = _clean_analysis_field(str(analysis.get("hook", "")))
    if visual:
        lines.append(f"사진에서 읽은 장면: {visual}")
    if symbol:
        lines.append(f"이야기로 이어갈 구체적 요소: {symbol}")
    if hook:
        lines.append(f"이어갈 질문 방향: {hook}")
    return "\n".join(lines) if lines else note or "참여자가 사진만 보냈습니다."


def merge_text_and_image(user_text: str, analysis: dict[str, str] | None) -> str:
    text = (user_text or "").strip()
    if not analysis:
        return text
    block = format_image_context_for_model(analysis, user_text)
    if text:
        return f"{text}\n\n{block}"
    return block
