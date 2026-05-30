"""배움의 정원사 · Learning Gardener — 학습 서사 전용 엔진 (소크라테스적 산파술)."""

from __future__ import annotations

import json
from typing import Any

import google.generativeai as genai

from env_config import get_gemini_model_name
from modes.learning import MIN_USER_TURNS_FOR_LEARNING_REPORT
from narrative_engine import LANG_NAMES, _extract_json, ensure_gemini_configured
from prompts.learning import build_learning_system_addon

LEARNING_COMPANION_NAME = "배움의 정원사"
LEARNING_COMPANION_NAME_EN = "Learning Gardener"
# 하위 호환 별칭
LEARNING_GARDENER_NAME = LEARNING_COMPANION_NAME

FOUR_THEORY_KEYS = ("bloom", "todd_rose", "pattern_seeker", "dynamics")

GLOBAL_LEARNING_SYSTEM_INSTRUCTION = f"""
=== GLOBAL LEARNING SYSTEM INSTRUCTION ===
(dlinso · {LEARNING_COMPANION_NAME})

[정체성 · 페르소나]
당신은 **소크라테스적 산파술**을 구사하는 **{LEARNING_COMPANION_NAME}**입니다.
단순 챗봇·강사·진단기·채점기가 아닙니다. 스스로를 **{LEARNING_COMPANION_NAME}**라고 소개하세요.
「AI」「LLM」「챗봇」으로 부르지 마세요. (인생 여정 모듈의 「마음의 정원사」와는 별 역할입니다.)

[미션]
학생·보호자(엄마/아빠/조부모)·교사 등 **누구와 대화하든**
대화를 통해 **학습 동역학(Learning Dynamics)** 을 인출하고,
상대에 맞는 **서사적 통찰**을 질문으로 열어 줍니다. 조언·처방·라벨링은 하지 않습니다.

[핵심 가치 — 질문에 녹일 것, 이론명을 나열하지 말 것]
- **평균의 종말**: 한 잣대로 자르지 않고, 영역마다 들쭉날쭉한 강점·취약을 존중
- **인지적 창조**: 암기·이해를 넘어 분석·평가·창조(체계화·저술·발표)로 가는 열망을 탐색
- **체계화 지능**: 흩어진 경험 속 패턴을 찾아 시스템화하려는 기질
- **변화의 에너지**: 동기(추진력)·마찰(환경 저항)·관성(과거 습관)·중력(꿈·목표)의 역학

[대상 식별 · 관계 역학]
- 상담 시작 시 당사자가 **누구인지** 자연스럽게 확인 (초·중·고·대·원생, 엄마, 아빠, 조부모, 교사 등).
- **제3자 상담**(보호자·교사): 학생 특성 + **상담자 본인의 교육적 가치관·불안**을 함께 인출.
  · 강점 먼저: 「○○님이 보시기에 아이가 가장 '폼나게' 집중하던 순간은 언제였나요?」
  · 동역학 마찰: 「교육적 기대와 아이의 에너지가 충돌하는 지점은 어디인가요?」
- **당사자 상담**(학생): 배움을 어떻게 느끼는지, **어떤 환경·맥락에서 가속도가 붙는지**(If-Then)를 묻기.

[질문 기술]
- 진로·삶: 「어떤 삶이 당신(혹은 아이)에게 폼나는/의미 있는 삶인가요?」를 반드시 심도 있게 다룰 것.
- 환경·멘탈: 「엔진이 가장 부드럽게 돌아가는 물리적/심리적 장소는 어디인가요?」
- 산파술: 「그 경험이 왜 소중했나요?」「그 순간 머릿속에선 어떤 패턴이 그려졌나요?」

[동역학(Dynamics) — 대화 전반에 자연스럽게]
- 이론명을 말하지 말고, **추진력(동기)** 과 **마찰(환경·관계 저항)** 을 한 흐름으로 묻기.
- 학생: 「그때 몸이 앞으로 나가게 한 마음은 무엇이었고, 발목을 잡던 건 무엇이었나요?」
- 보호자·교사: 「아이에게 힘이 실리던 순간」과 「기대와 에너지가 부딪히던 지점」을 짝으로 묻기.
- 관성(습관): 「예전 방식이 끌고 가던 힘」 · 중력(목표): 「끌어당기는 꿈·방향」도 장면과 함께 1~2회는 다룰 것.

[대화 방식]
- 참여자 발화 = 배움 서사의 한 줄. 되풀이·표면 동의 금지.
- 응답(2~4문장, 완전한 문장): ① 짧은 인정 ② (있으면) 「인용」 ③ **질문 1개만**
- 출력에 마크다운 별표(*, **) 금지. 강조는 「」·줄바꿈.
- 금지 단어: 평균, 우수, 미달, 정상, 하위, 상위 등 **정형화 평가** 표현.

[리포트 전 단계]
- 아직 최종 서사 리포트 본문을 출력하지 말 것(별도 파이프라인).
=== END GLOBAL LEARNING SYSTEM INSTRUCTION ===
"""

LEARNING_TURN_ADDON_HEADER = """
[이번 턴 — 배움의 정원사 · 직전 발화만 인용]
"""

LEARNING_EXTRACTION_JSON_PROMPT = """
위 대화 맥락을 바탕으로, 아래 JSON만 출력하세요(코드펜스·별표 없음).

[4대 이론 축 — 필수]
1) bloom (수직적 위계): remember|understand|apply|analyze|evaluate|create|unknown
   - 암기·이해를 넘어 분석·평가·창조(Create: 체계화·저술·발표) 열망
2) todd_rose (수평적 개성): 평균 잣대 없이 Jagged 강점·취약, 극대화되는 장소·사람
3) pattern_seeker (시스템 지능): 패턴 발견·시스템화 기질, 저술·연결 가능성
4) dynamics (변화의 흐름): motivation(추진력), friction(마찰), inertia(관성), gravity(목표·꿈), synthesis(종합)

[대화 축 요약 — 하위 호환]
motivation, metacognition, career_values, thin_axis, anchor_quote

스키마:
{
  "bloom": {
    "level": "create",
    "summary": "1~2문장, 「」 인용 포함",
    "create_aspiration": "창조·체계화·저술 향한 열망 1문장"
  },
  "todd_rose": {
    "summary": "Jagged 프로필 요약 1~2문장",
    "peak_strengths": ["강점 영역 1", "강점 영역 2"],
    "trough_areas": ["보완 영역 1"],
    "peak_contexts": "역량이 커지는 장소·사람·맥락"
  },
  "pattern_seeker": {
    "summary": "패턴·시스템화 기질 1~2문장",
    "writing_connection": "저술·발표·연결 가능성 1문장"
  },
  "dynamics": {
    "motivation": "추진력",
    "friction": "환경·관계 마찰",
    "inertia": "과거 습관·관성",
    "gravity": "꿈·목표·중력",
    "synthesis": "네 요소 역학 종합 1~2문장"
  },
  "motivation": "학습 동기 요약( dynamics.motivation 과 맞출 것)",
  "metacognition": "메타인지·전략 요약",
  "career_values": "폼나는 삶·가치 1~2문장",
  "thin_axis": "bloom|todd_rose|pattern_seeker|dynamics 중 다음에 더 물어야 할 축",
  "anchor_quote": "참여자 말 핵심 인용 6~40자"
}
"""


def _empty_four_theory_block() -> dict[str, Any]:
    return {
        "bloom": {
            "level": "unknown",
            "summary": "",
            "create_aspiration": "",
        },
        "todd_rose": {
            "summary": "",
            "peak_strengths": [],
            "trough_areas": [],
            "peak_contexts": "",
        },
        "pattern_seeker": {
            "summary": "",
            "writing_connection": "",
        },
        "dynamics": {
            "motivation": "",
            "friction": "",
            "inertia": "",
            "gravity": "",
            "synthesis": "",
        },
    }


def _heuristic_axis_depth(user_texts: list[str]) -> dict[str, str]:
    """규칙 기반 축 깊이 (대화 축 + 4대 이론)."""
    blob = " ".join(user_texts).lower()
    if len(blob) < 12:
        shallow = "shallow"
        return {
            "motivation": shallow,
            "metacognition": shallow,
            "career_values": shallow,
            **{k: shallow for k in FOUR_THEORY_KEYS},
        }

    def score(keywords: tuple[str, ...]) -> str:
        hits = sum(1 for k in keywords if k in blob)
        if hits >= 2 or (len(blob) > 120 and hits >= 1):
            return "moderate"
        if hits >= 1:
            return "shallow"
        return "unknown"

    motivation_kw = (
        "왜", "하고 싶", "동기", "재미", "흥미", "목표", "꿈", "의미", "because", "motivat",
    )
    meta_kw = (
        "방법", "공부법", "복습", "정리", "계획", "루틴", "습관", "이해", "암기", "strategy",
    )
    career_kw = (
        "진로", "직업", "폼나", "삶", "가치", "미래", "되고 싶", "career", "values", "life",
    )
    bloom_kw = (
        "분석", "평가", "창조", "글", "저술", "발표", "체계", "만들", "설명", "create", "analyze",
    )
    jagged_kw = (
        "잘", "못", "특히", "반면", "어려", "강점", "약점", "들쭉", "다른 과목", "장소", "친구",
    )
    pattern_kw = (
        "패턴", "규칙", "연결", "구조", "정리", "지도", "틀", "시스템", "관계", "pattern",
    )
    dynamics_kw = (
        "마찰", "부모", "선생", "환경", "습관", "관성", "멈춤", "가속", "집중", "장소", "목표",
    )

    legacy = {
        "motivation": score(motivation_kw),
        "metacognition": score(meta_kw),
        "career_values": score(career_kw),
    }
    four = {
        "bloom": score(bloom_kw),
        "todd_rose": score(jagged_kw),
        "pattern_seeker": score(pattern_kw),
        "dynamics": score(dynamics_kw),
    }
    return {**legacy, **four}


def _heuristic_four_theory_signals(user_texts: list[str]) -> dict[str, Any]:
    """LLM 없이 4대 이론 신호 골격."""
    block = _empty_four_theory_block()
    if not user_texts:
        return block

    blob = " ".join(user_texts)
    last = user_texts[-1][:120]
    block["bloom"]["summary"] = last
    block["todd_rose"]["summary"] = (
        "영역마다 강약이 다를 수 있는 배움 지형이 이야기에 스며 있습니다."
    )
    block["pattern_seeker"]["summary"] = (
        "경험을 연결·정리하려는 시도가 대화에 보입니다."
    )
    block["dynamics"]["motivation"] = last
    block["dynamics"]["synthesis"] = "동기·환경·습관·목표가 함께 언급되고 있습니다."

    low = blob.lower()
    if any(k in low for k in ("창조", "저술", "발표", "글 쓰", "만들어")):
        block["bloom"]["level"] = "create"
        block["bloom"]["create_aspiration"] = "지식을 체계화하거나 밖으로 표현하려는 열망"
    elif any(k in low for k in ("분석", "비교", "평가")):
        block["bloom"]["level"] = "analyze"
    elif any(k in low for k in ("이해", "설명")):
        block["bloom"]["level"] = "understand"
    else:
        block["bloom"]["level"] = "unknown"

    if any(k in low for k in ("잘 되", "집중", "몰입", "재미")):
        block["todd_rose"]["peak_strengths"] = ["집중·몰입이 보이는 영역"]
    if any(k in low for k in ("어렵", "막히", "힘들")):
        block["todd_rose"]["trough_areas"] = ["지금 막히는 영역"]
    if any(k in low for k in ("도서관", "방", "학원", "친구", "선생")):
        block["todd_rose"]["peak_contexts"] = "말씀하신 장소·관계 맥락"

    return block


def _pick_thin_axis(depths: dict[str, str]) -> str:
    for key in (*FOUR_THEORY_KEYS, "motivation", "metacognition", "career_values"):
        if depths.get(key) in ("shallow", "unknown"):
            return key
    return "dynamics"


def _merge_llm_four_theory(base: dict[str, Any], data: dict[str, Any]) -> None:
    """LLM JSON의 4대 이론·레거시 필드를 base에 병합."""
    for key in ("motivation", "metacognition", "career_values", "thin_axis", "anchor_quote"):
        if data.get(key):
            base[key] = str(data.get(key, "")).strip()

    thin = str(data.get("thin_axis") or "").strip()
    if thin:
        base["thin_axis"] = thin

    for theory in FOUR_THEORY_KEYS:
        raw = data.get(theory)
        if isinstance(raw, dict):
            merged = dict(base.get(theory) or {})
            for sub_k, sub_v in raw.items():
                if isinstance(sub_v, list):
                    merged[sub_k] = sub_v
                else:
                    merged[sub_k] = str(sub_v or "").strip()
            base[theory] = merged
        elif raw:
            base[theory] = {**(base.get(theory) or {}), "summary": str(raw).strip()}

    # 레거시 동기 ← dynamics
    dyn = base.get("dynamics") or {}
    if not base.get("motivation") and dyn.get("motivation"):
        base["motivation"] = str(dyn["motivation"])
    if not base.get("career_values") and dyn.get("gravity"):
        base["career_values"] = str(dyn["gravity"])


def build_global_learning_system_instruction(lang: str = "ko") -> str:
    from personas import LANG_REPLY

    reply_lang = LANG_REPLY.get(lang, "Korean")
    native = LANG_NAMES.get(lang, reply_lang)
    name = LEARNING_COMPANION_NAME if lang == "ko" else LEARNING_COMPANION_NAME_EN
    return (
        GLOBAL_LEARNING_SYSTEM_INSTRUCTION
        + f"\n\n[응답 언어 — 필수]\n"
        f"참여자 UI 언어: **{native}** ({reply_lang}). "
        f"반드시 **{reply_lang}** 로만 답하세요. "
        f"자칭은 **{name}** ({reply_lang}로 자연스럽게). "
        "다른 언어로 섞지 마세요(고유명사·인용 제외)."
    )


def build_learning_turn_addon(*, last_user: str = "", user_turns: int = 0) -> str:
    block = LEARNING_TURN_ADDON_HEADER
    if user_turns:
        block += f"\n- 참여자 배움 발화 누적: {user_turns}회."
    if last_user:
        block += f"\n- 방금 말(1회만 인용): 「{last_user[:200]}」"
    block += (
        "\n- 공감 → (선택) 「」 인용 → **질문 1개**. "
        "4대 렌즈(Bloom·Jagged·패턴·동역학) 중 아직 얇은 축을 우선. "
        "동역학 축일 때는 추진력·마찰을 **한 질문**에 녹일 것(이론명 금지). "
        "평균·우수·미달 등 평가 라벨 금지."
    )
    return block


def build_learning_conversation_phase_addon(
    user_turns: int,
    *,
    report_completed: bool = False,
    min_turns: int = MIN_USER_TURNS_FOR_LEARNING_REPORT,
) -> str:
    if report_completed:
        return (
            "\n\n[대화 단계 · 배움 지도 이후]\n"
            "- 학습 서사 리포트는 이미 공유됨. **수치·OR·지표·별표는 말하지 말 것**.\n"
            "- 리포트에 대한 생각·추가 배움 장면을 따뜻하게 초대.\n"
        )
    if user_turns < min_turns:
        return (
            f"\n\n[대화 단계 · 배움 지도 전 ({min_turns}회 미만)]\n"
            "- 가벼운 인사·공감. **리포트 형식·통계·진단 라벨 금지**.\n"
            "- 당사자 확인 후, 동역학·폼나는 삶·환경(If-Then) 중 하나씩 열기. 질문 1개.\n"
        )
    return (
        f"\n\n[대화 단계 · 배움 서사 충분 ({min_turns}회 이상, 리포트 전)]\n"
        "- 아직 **최종 서사 리포트 본문을 출력하지 말 것**(별도 버튼·파이프라인).\n"
        "- 4대 이론 축이 고르게 쌓였는지 보고, 얇은 축만 질문 1개.\n"
    )


def build_learning_depth_addon(
    *,
    motivation_depth: str = "unknown",
    metacognition_depth: str = "unknown",
    career_values_depth: str = "unknown",
    four_theory_depth: dict[str, str] | None = None,
) -> str:
    """대화·4대 이론 축 깊이 힌트."""
    labels = {
        "bloom": "Bloom(인지적 창조·위계)",
        "todd_rose": "Jagged 강점·맥락",
        "pattern_seeker": "패턴·시스템화",
        "dynamics": "학습 동역학",
        "motivation": "동기",
        "metacognition": "메타인지",
        "career_values": "폼나는 삶",
    }
    shallow: list[str] = []
    ft = four_theory_depth or {}
    for key in FOUR_THEORY_KEYS:
        if ft.get(key) in ("shallow", "unknown"):
            shallow.append(labels[key])
    for key, depth in (
        ("동기", motivation_depth),
        ("메타인지", metacognition_depth),
        ("폼나는 삶·가치", career_values_depth),
    ):
        if depth in ("shallow", "unknown") and key not in shallow:
            shallow.append(key)

    if not shallow:
        return (
            "\n\n[배움 서사 깊이 · 충분]\n"
            "- 여러 축이 어느 정도 쌓임. **과잉 캐묻기 금지**, 인정·음미 위주.\n"
        )
    focus = shallow[0]
    dynamics_hint = ""
    if focus == labels["dynamics"] or ft.get("dynamics") in ("shallow", "unknown"):
        dynamics_hint = (
            "\n- 동역학 질문 예: 「그때 앞으로 밀어 준 마음은 무엇이었고, "
            "동시에 발목을 잡던 건 무엇이었나요?」(추진력·마찰, 이론명 없이)"
        )
    return (
        f"\n\n[배움 서사 깊이 · 보강]\n"
        f"- 아직 얇은 축: **{focus}**. 이 축으로만 구체 장면·감각 질문 1개.\n"
        f"{dynamics_hint}\n"
        "- 다른 축은 이번 턴에서 건드리지 말 것.\n"
    )


def build_full_learning_system_instruction(
    *,
    lang: str = "ko",
    learning_audience: str = "",
    age_group: str = "",
    life_stage: str = "",
    nickname: str = "",
    last_user: str = "",
    user_turns: int = 0,
    report_completed: bool = False,
    context_summary: str = "",
    motivation_depth: str = "unknown",
    metacognition_depth: str = "unknown",
    career_values_depth: str = "unknown",
    four_theory_depth: dict[str, str] | None = None,
    live_signals: dict[str, Any] | None = None,
) -> str:
    """샌드박스·앱 공통 — 배움의 정원사 전체 system instruction."""
    parts = [
        build_global_learning_system_instruction(lang),
        build_learning_system_addon(
            learning_audience=learning_audience,
            age_group=age_group,
            life_stage=life_stage,
            lang=lang,
            nickname=nickname,
        ),
        build_learning_conversation_phase_addon(
            user_turns, report_completed=report_completed
        ),
        build_learning_depth_addon(
            motivation_depth=motivation_depth,
            metacognition_depth=metacognition_depth,
            career_values_depth=career_values_depth,
            four_theory_depth=four_theory_depth,
        ),
        build_learning_turn_addon(last_user=last_user, user_turns=user_turns),
    ]
    if context_summary.strip():
        parts.append(f"\n\n[지금까지의 배움 이야기 요약]\n{context_summary.strip()}")
    thin = ""
    if isinstance(live_signals, dict):
        thin = str(live_signals.get("thin_axis") or "").strip()
    if thin:
        labels = {
            "bloom": "Bloom(인지적 창조)",
            "todd_rose": "Jagged 강점·맥락",
            "pattern_seeker": "패턴·체계화",
            "dynamics": "학습 동역학(추진·마찰)",
        }
        label = labels.get(thin, thin)
        parts.append(
            f"\n\n[실시간 인출 · 이번 턴 우선 축]\n"
            f"- **{label}** — 참여자 말에 녹여 질문 1개(이론명·JSON 금지)."
        )
    return "\n".join(parts)


def build_learning_chat_history(messages: list[dict]) -> list[dict]:
    """Gemini/Upstage history — 마지막 user 턴 제외."""
    history: list[dict] = []
    for msg in messages[:-1]:
        text = str(msg.get("content") or msg.get("display") or "").strip()
        if not text:
            continue
        role = "user" if msg.get("role") == "user" else "model"
        history.append({"role": role, "parts": [text]})
    return history


def extract_learning_signals(
    messages: list[dict],
    *,
    lang: str = "ko",
    use_llm: bool = True,
) -> dict[str, Any]:
    """
    대화에서 4대 이론(Bloom·Todd Rose·Pattern Seeker·Dynamics) 신호를 JSON으로 인출.
    레거시 motivation/metacognition/career_values 필드 유지.
    """
    user_texts = [
        str(m.get("content") or m.get("display") or "").strip()
        for m in messages
        if m.get("role") == "user" and str(m.get("content") or m.get("display") or "").strip()
    ]
    depths = _heuristic_axis_depth(user_texts)
    four_block = _heuristic_four_theory_signals(user_texts)

    base: dict[str, Any] = {
        **four_block,
        "motivation": "",
        "metacognition": "",
        "career_values": "",
        "thin_axis": _pick_thin_axis(depths),
        "anchor_quote": user_texts[-1][:40] if user_texts else "",
        "axis_depth": depths,
        "source": "heuristic",
    }
    if not user_texts or not use_llm:
        base["thin_axis"] = _pick_thin_axis(depths)
        return base

    dyn = base["dynamics"]
    if dyn.get("motivation"):
        base["motivation"] = str(dyn["motivation"])
    if dyn.get("gravity"):
        base["career_values"] = str(dyn["gravity"])
    bloom = base.get("bloom") or {}
    if bloom.get("summary"):
        base["metacognition"] = str(bloom.get("summary", ""))[:200]

    try:
        ensure_gemini_configured()
    except Exception:  # noqa: BLE001
        base["thin_axis"] = _pick_thin_axis(depths)
        return base

    transcript = "\n".join(f"- {t[:300]}" for t in user_texts[-12:])
    prompt = (
        f"{LEARNING_EXTRACTION_JSON_PROMPT}\n\n"
        f"[참여자 발화]\n{transcript}\n"
        f"언어: {lang}"
    )
    model = genai.GenerativeModel(
        get_gemini_model_name(),
        generation_config=genai.GenerationConfig(
            temperature=0.35,
            max_output_tokens=1200,
        ),
    )
    try:
        response = model.generate_content(prompt)
        data = _extract_json(response.text or "") or {}
        if data:
            _merge_llm_four_theory(base, data)
            base["source"] = "llm"
            base["axis_depth"] = depths
            if not base.get("thin_axis"):
                base["thin_axis"] = _pick_thin_axis(depths)
    except Exception:  # noqa: BLE001
        pass
    return base


def generate_learning_narrative_report_for_messages(
    messages: list[dict],
    *,
    learning_audience: str = "",
    age_group: str = "",
    life_stage: str = "",
    participant_id: str = "",
    lang: str = "ko",
    profile: dict[str, float] | None = None,
) -> dict[str, Any]:
    """샌드박스·앱 — 학습 서사 리포트 파이프라인 진입점."""
    from hbridge_analysis import extract_situational_context
    from learning_analysis import compute_learning_statistics, run_learning_report_pipeline
    from narrative_engine import generate_learning_narrative_report

    user_texts = [
        str(m.get("content") or m.get("display") or "").strip()
        for m in messages
        if m.get("role") == "user"
        and str(m.get("content") or m.get("display") or "").strip()
    ]
    stats = compute_learning_statistics(messages, profile)
    situational = extract_situational_context(user_texts)
    signals = extract_learning_signals(messages, lang=lang)
    humanistic = None
    try:
        humanistic = generate_learning_narrative_report(
            messages,
            stats,
            learning_audience=learning_audience,
            age_group=age_group,
            life_stage=life_stage,
            participant_id=participant_id,
            situational_context=situational,
            lang=lang,
            learning_signals=signals,
        )
    except Exception:  # noqa: BLE001
        humanistic = None

    report = run_learning_report_pipeline(
        messages,
        profile,
        learning_audience=learning_audience,
        life_stage=life_stage,
        age_group=age_group,
        humanistic=humanistic,
        situational=situational,
        user_texts=user_texts,
        learning_signals=signals,
    )
    if isinstance(report, dict):
        report["learning_signals"] = signals
        from hbridge_analysis import format_sheet_stats_summary

        report["hbridge_summary"] = format_sheet_stats_summary(report)
        report["report_title"] = "서사적 항해 일지"
    return report


def iter_learning_reply_stream(
    messages: list[dict],
    user_prompt: str,
    *,
    lang: str = "ko",
    learning_audience: str = "",
    age_group: str = "",
    life_stage: str = "",
    nickname: str = "",
    report_completed: bool = False,
    context_summary: str = "",
    live_signals: dict[str, Any] | None = None,
    temperature: float = 0.78,
    top_p: float = 0.92,
    max_tokens: int = 2048,
):
    """배움의 정원사 스트리밍 응답."""
    from llm_client import iter_chat_stream

    user_texts = [
        str(m.get("content") or "").strip()
        for m in messages
        if m.get("role") == "user"
    ]
    if user_prompt.strip():
        user_texts.append(user_prompt.strip())
    depths = _heuristic_axis_depth(user_texts)
    system = build_full_learning_system_instruction(
        lang=lang,
        learning_audience=learning_audience,
        age_group=age_group,
        life_stage=life_stage,
        nickname=nickname,
        last_user=user_prompt,
        user_turns=len(user_texts),
        report_completed=report_completed,
        context_summary=context_summary,
        motivation_depth=depths["motivation"],
        metacognition_depth=depths["metacognition"],
        career_values_depth=depths["career_values"],
        four_theory_depth={k: depths[k] for k in FOUR_THEORY_KEYS},
        live_signals=live_signals,
    )
    history = build_learning_chat_history(
        messages + [{"role": "user", "content": user_prompt}]
    )
    yield from iter_chat_stream(
        messages,
        user_prompt,
        system=system,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        gemini_history=history,
    )
