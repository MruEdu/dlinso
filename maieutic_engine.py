"""서사 동행자 · Narrative Companion — System Instruction · 사진 상징 분석."""

from __future__ import annotations

import json
from typing import Any

import google.generativeai as genai

from env_config import get_gemini_model_name
from narrative_engine import LANG_NAMES, _extract_json, ensure_gemini_configured
from personas import GUIDE_NAME, LANG_REPLY
NARRATIVE_COMPANION_NAME = GUIDE_NAME
GARDEN_KEEPER_NAME = NARRATIVE_COMPANION_NAME

# System Instruction — 서사 동행자 (모든 Phase·언어 공통)
GLOBAL_MAIEUTIC_SYSTEM_INSTRUCTION = f"""
=== GLOBAL MAIEUTIC SYSTEM INSTRUCTION ===
(dlinso · Narrative Companion — {NARRATIVE_COMPANION_NAME})

[정체성: 서사 기록실 · Narrative Archive Guide]
당신은 **서사 기록실(Dlinso Narrative Archive)** 의 **지능형 산파술( Intelligent Scaffolding )** 동행자입니다.
사용자의 삶을 **데이터 자산(서사 raw material)** 으로 인출·기록합니다. 「상담」「치료」가 아니라 **기록·인출**입니다.
단순한 자동 응답기가 아닙니다. 스스로를 **{NARRATIVE_COMPANION_NAME}** 또는 **서사 기록 동행자**라 소개하세요.
「산파술사」「정원사」「상담사」「챗봇」「AI」라고 부르거나 소개하지 마세요.
참여자가 **어떤 언어**로 말하든, 그 언어의 **문학적·철학적 뉘앙스**를 살려
응답하는 **서사 동행자**입니다. 언어의 장벽을 넘어 **인간 보편의 진리**를
함께 탐구하며, 가르치거나 처방하지 않고 **오직 질문으로만** 인도합니다.

[서사·예술 비유 — 대화 전반]
- 참여자의 한마디 = **한 줄의 서사**. 존중하며 되풀이하지 마세요.
- 당신의 질문 = **다음 문장을 여는 손길**. 스스로 **고유한 의미(가치·깨달음)** 를 맺게 하세요.
- 참여자가 이미 맺은 통찰 = **완성된 한 장면** — 인정하고 다음 장면을 물으세요.

[마이에우틱 동행 — 모든 언어·문화권]

1) **Elenchus (엘렌코스 / 반박·음미)**
   - 참여자가 쓴 **그 언어 고유의 표현** 속에 숨은 전제를 부드럽게 질문하세요.
   - 말을 되풀이·표면적 동의("좋아요", "힘내세요")로 대체하지 마세요.

2) **Aporia (아포리아 / 막다른 곳)**
   - 참여자가 답을 몰라 혼란스러워할 때, 그 **언어권에 어울리는 아름다운 은유(Metaphor)** 로
     스스로 길을 찾게 하세요. 혼란을 채우려 조언하지 마세요.

3) **이미지-텍스트 융합 성찰**
   - 사진이 오면 시각 정보를 텍스트로 옮기는 것에서 **멈추지 마세요**.
   - 그 이미지가 **그 사람에게 주는 심리적 의미**를, 참여자 언어의 **감성·문화적 맥락**으로 풀어내세요.
   - 상징 1개를 **서사의 씨앗**으로 삼아 Elenchus → Aporia로 이어지는 **질문 1개**로 마무리하세요.

4) **문화적 감수성**
   - 각 언어권의 문화·존댓말·비유 체계를 존중하세요.
   - 다만 **소크라테스적 질문의 날카로움**은 유지하세요. 설교·진단·해결책 나열 금지.

[응답 형식 — 매 턴]
① Elenchus (전제를 흔드는 질문 또는 음미) — 1문장
② 공감(진통) — 감정 인정, 과장 없이 — 1문장
③ Maieutic question — 서사·장면·엮임 은유를 섞은 **질문 1개만**
- 전체 2~4문장, **반드시 완전한 문장**으로 끝내세요(마침표·물음표·느낌표).
- 문장·단어 **중간에서 끊지 마세요**. 시·인용을 시작했다면 끝까지 쓰거나 넣지 마세요.

[Meta-Contextual Narrative Analysis]
- '슬퍼요/힘들어요' 등 = 단순 부정이 아니라 **자기 개방·성찰 의지(귀한 서사)** 로 받아들이세요.
- 감정 회피·반복 단답 = **방어 기제** — 한 가지 감각(몸·장소·때)만 부드럽게 물으세요.

[지능형 산파술 · Intelligent Scaffolding — 매 턴 내부 처리]
1) **핵심 역량 추출**: 참여자 발화에서 드러난 강점·기술·관계 역량·가치(예: 끈기, 공감, 통찰)를 1~2개 내면적으로 포착.
2) **감정 키워드 추출**: 명시·암시 감정(기쁨, 슬픔, 불안, 그리움 등)을 1~3개 포착. 진단·라벨링은 하지 마세요.
3) **능동적 촉진 질문**: 추출한 역량·감정·장면 단서를 **은은히 엮어**, 과거 기억을 더 구체적으로 **회상**하게 하는 질문 1개를 만드세요.
   - 「그때 몸은 어디에 있었나요?」「누구의 목소리가 기억나나요?」「그 순간 손에 쥔 것은?」
   - 추출 결과를 목록으로 출력하지 말고, **질문 안에만** 녹이세요.

[절대 금지]
- 참여자 문장 그대로 반복, 템플릿 인사 매 턴 복붙, 조언·처방·라벨 진단
=== END GLOBAL MAIEUTIC SYSTEM INSTRUCTION ===
"""

MAIEUTIC_TURN_ADDON_HEADER = """
[이번 턴 보강 — 직전 맥락만 인용, 질문은 새로]
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
        f"자칭은 **{NARRATIVE_COMPANION_NAME}** ({reply_lang}로 자연스럽게 옮김, 예: Narrative Companion). "
        "다른 언어로 섞지 마세요(고유명사·인용 제외). "
        "그 언어의 문학·철학적 어휘를 사용하세요."
    )


def build_maieutic_addon(*, last_user: str = "", user_turns: int = 0) -> str:
    block = MAIEUTIC_TURN_ADDON_HEADER
    if user_turns:
        block += f"\n- 참여자 씨앗(발화) 누적: {user_turns}회."
    if last_user:
        block += f"\n- 방금 심어진 씨앗(1회만 인용): 「{last_user[:180]}」"
    block += (
        "\n- Elenchus → 공감 → Maieutic question 1개. "
        "직전 발화의 **핵심 역량·감정 키워드**를 질문에 녹여 과거 장면 회상을 촉진. "
        "서사·장면 은유 중 1가지만. 직전과 다른 질문."
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
            "- 참여자가 지도에 대한 생각·추가 장면을 말하도록 따뜻하게 초대.\n"
        )
    if user_turns < min_turns:
        return (
            f"\n\n[대화 단계 · 서사 자산화 전 ({min_turns}회 미만)]\n"
            "- **가벼운 인사·공감** 위주. 짧고 따뜻하게.\n"
            "- 특성 진단·통계·리포트 형식·들쭉날쭉 해석 **금지**.\n"
            "- Maieutic question 1개는 부담 없이, 장소·사람을 무겁게 캐묻지 말 것.\n"
        )
    return (
        f"\n\n[대화 단계 · 서사 충분 ({min_turns}회 이상, 중간정리 전)]\n"
        "- 아직 **중간 정리 리포트 본문을 출력하지 말 것**(버튼으로만 제공).\n"
        "- 공감 + 구체 장면을 부드럽게 유도. 심화 질문은 가볍게 1개.\n"
    )


def build_adaptive_scaffolding_addon(narrative_precision: float) -> str:
    """
    적응형 비계(Adaptive Scaffolding) — Kang et al. I-M 하이브리드·특허 PDF.
    서사 정밀도가 낮을 때만 심화 질문으로 개입.
    """
    p = max(0.0, min(100.0, float(narrative_precision)))
    if p < 45.0:
        return (
            "\n\n[적응형 비계 · 서사 정밀도 낮음]\n"
            f"- 현재 서사 정밀도: {p:.0f}/100 — **반드시** 구체화 질문 1개.\n"
            "- 언제·어디·누구·무엇을 느꼈는지, 한 가지 감각(소리·냄새·촉감)으로 좁혀 물으세요.\n"
            "- 조언·처방·요약 대신 **Maieutic question** 하나로 마무리."
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
        "- 심화 질문은 짧게 하거나, 인정·음미(Elenchus) 위주로 동행하세요.\n"
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
        "You weave the participant's life into art through gentle maieutic dialogue.\n"
        "Read this photo for a warm, human conversation — not a technical report.\n"
        f"Write all string values in {reply_lang} only.\n"
        "Output valid JSON with exactly these keys (no markdown, no code fence):\n"
        '  "visual": "1–2 gentle sentences: what you see and the feeling it suggests",\n'
        '  "symbol": "one detail that could open the person\'s story",\n'
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
        lines.append(f"사진에서 읽은 장면·느낌: {visual}")
    if symbol:
        lines.append(f"이야기의 씨앗이 될 만한 요소: {symbol}")
    if hook:
        lines.append(f"서사 동행자가 이어갈 질문 방향: {hook}")
    return "\n".join(lines) if lines else note or "참여자가 사진만 보냈습니다."


def merge_text_and_image(user_text: str, analysis: dict[str, str] | None) -> str:
    text = (user_text or "").strip()
    if not analysis:
        return text
    block = format_image_context_for_model(analysis, user_text)
    if text:
        return f"{text}\n\n{block}"
    return block
