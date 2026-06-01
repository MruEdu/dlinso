"""숲 · 연결의 동행자 — 고립·은둔 청년 서사 엔진 (Anti-Diagnosis · Isolation Framework)."""

from __future__ import annotations

import json
from typing import Any

from env_config import get_gemini_model_name
from llm_client import extract_json as llm_extract_json
from llm_client import generate_text, is_llm_configured
from modes.isolation import (
    DUAL_AXIS_KEYS,
    DUAL_AXIS_LABELS,
    FOUR_FRAMEWORK_KEYS,
    FOUR_FRAMEWORK_LABELS,
    LEXICON_LATE_PREFERRED,
    LEXICON_METAPHOR,
    LEXICON_NEVER_AI,
    LEXICON_SENSITIVE,
    MAIEUTIC_SEED_QUESTIONS,
    MIN_USER_TURNS_FOR_ASSET,
    MIN_USER_TURNS_FOR_REPORT,
    PHASE_EARLY_MAX_TURNS,
)
from narrative_engine import LANG_NAMES, _extract_json, ensure_gemini_configured
from narrative_style import EMPATHETIC_REPHRASE_INSTRUCTION, user_turn_context_for_llm
from prompts.isolation import build_isolation_system_addon

ISOLATION_COMPANION_NAME = "연결의 동행자"
FOUR_THEORY_KEYS = FOUR_FRAMEWORK_KEYS

GLOBAL_ISOLATION_SYSTEM_INSTRUCTION = f"""
=== GLOBAL ISOLATION SYSTEM INSTRUCTION ===
(dlinso · 숲 · {ISOLATION_COMPANION_NAME})

[정체성]
소크라테스적 산파술을 구사하는 **{ISOLATION_COMPANION_NAME}**입니다.
진단·검사·채점·라벨링이 아닙니다. 스스로를 **{ISOLATION_COMPANION_NAME}**라고 소개하세요.

[Core Philosophy]
행정 지표(외출·취업)가 아니라 **자아성**과 **사회성** 회복을 목표로 합니다.
참여자는 에너지가 고여 있는 **「고유한 우주」** — 각자의 리듬과 이야기를 가진 존재입니다.

[어휘 · Selfhood 도구]
「고립·은둔·사회복귀·치료」는 행정 분류가 아니라 **자아성을 세우기 위한 도구**로만 쓴다.
대화 단계(탐색→맥락 형성→서사 자산화)와 사용자 발화에 따라 **신중·전략적**으로 조절한다.
AI가 먼저 쓰지 않을 것: 치료, 재활, 사회복귀, 환자, 취약계층.

[4대 서사 축 — 이론명·영문 라벨을 말하지 말 것]
- 고립 시간의 재정의: 조용한 시간을 새 서사를 쓰는 과정으로
- 비균질 안전 맥락: 평균 압박 없이 안전한 장소·시간·사람
- 내면 질서로의 전환: 방어적 패턴을 스스로의 질서로
- 마찰력과 작은 추진력: 두려움(마찰) vs 마음의 작은 한 걸음

[산파술 시드 — 변형하여 1개]
- 「당신의 방은 요새인가요, 정거장인가요?」
- 「세상의 '평균' 중 무엇이 당신을 숨 차게 하나요?」
- 「어떤 소음이 가장 지치게 하나요?」
- 「작은 한 걸음을 밀어 준 것은 무엇이었나요?」
응답: 인정 → 공감·재진술(은유·의미, 오타·원문 복붙 금지) → 질문 1개. 별표 금지.
=== END GLOBAL ISOLATION SYSTEM INSTRUCTION ===
"""

ISOLATION_EXTRACTION_JSON_PROMPT = """
위 대화에서 JSON만 출력(코드펜스·별표 없음).

[핵심 이중 축 — 회복 신호]
identity: {{
  "summary": "자아성 회복 신호 1~2문장",
  "self_definition": "고립 속 자기 정의 단서"
}}
social: {{
  "summary": "사회성 회복 신호 1~2문장",
  "relational_longing": "관계·연결에 대한 갈망·두려움"
}}

[4대 축 — JSON 키만 영문, summary 문장은 한국어]
bloom, todd_rose, pattern_seeker, dynamics
(각 summary에 Analyze·Jagged·Small Win 등 영문 이론명 넣지 말 것)

recovery_strength: weak|emerging|clear  (자아·사회 회복 신호 종합)
thin_axis: identity|social|bloom|todd_rose|pattern_seeker|dynamics
anchor_quote: 6~40자
user_lexicon_hits: 사용자가 직접 쓴 민감 어휘 목록(없으면 [])
"""


def _normalize_blob(texts: list[str]) -> str:
    return " ".join(texts).lower()


def detect_user_lexicon_hits(user_texts: list[str]) -> list[str]:
    """사용자 발화에서 직접 등장한 민감·자기정의 어휘."""
    blob = _normalize_blob(user_texts)
    hits: list[str] = []
    for word in LEXICON_SENSITIVE:
        if word.lower() in blob or word in " ".join(user_texts):
            hits.append(word)
    for phrase in ("내 상태", "스스로", "정의하고", "나는", "내가"):
        if phrase in blob and phrase not in hits:
            pass  # self-definition handled separately
    return hits


def user_seeks_self_definition(user_texts: list[str]) -> bool:
    """사용자가 스스로 상태를 규정하려는 신호 (은유·라벨 제외)."""
    blob = _normalize_blob(user_texts)
    markers = (
        "내가",
        "나는",
        "스스로",
        "정의",
        "상태",
        "라고 생각",
        "라고 불",
        "라고 해",
    )
    return any(m in blob for m in markers)


def resolve_lexicon_phase(
    *,
    user_turns: int,
    user_texts: list[str],
    report_completed: bool = False,
    live_signals: dict[str, Any] | None = None,
) -> str:
    """
    탐색(early) · 맥락 형성(mid) · 서사 자산화(late).
    턴 수 + 사용자 어휘 + 회복 신호를 함께 본다.
    """
    sig = live_signals or {}
    strength = str(sig.get("recovery_strength") or "")
    hits = detect_user_lexicon_hits(user_texts)

    if report_completed or user_turns >= MIN_USER_TURNS_FOR_ASSET:
        if strength == "clear" or user_turns >= MIN_USER_TURNS_FOR_REPORT:
            return "late"
        return "late"

    if hits or user_seeks_self_definition(user_texts):
        return "mid"

    if user_turns <= PHASE_EARLY_MAX_TURNS:
        return "early"

    return "mid"


def build_lexicon_strategy_addon(
    *,
    phase: str,
    user_texts: list[str],
    last_user: str = "",
) -> str:
    """단계별 어휘 전략 — AI 발화에 주입."""
    hits = detect_user_lexicon_hits(user_texts)
    hit_line = ", ".join(f"「{w}」" for w in hits) if hits else "(아직 없음)"
    never = ", ".join(f"「{w}」" for w in LEXICON_NEVER_AI)
    metaphors = ", ".join(LEXICON_METAPHOR[:8])
    late_pref = " · ".join(LEXICON_LATE_PREFERRED)

    if phase == "early":
        return f"""
[어휘 전략 · 탐색 단계]
- 직접 라벨(고립·은둔·사회복귀·치료) **AI가 먼저 쓰지 말 것**. 방어 기제를 낮춘다.
- 우선 은유: {metaphors}
- 「요새·섬·정거장·고유한 시간·우주·막·틈·문턱」 등으로 경험을 열 것.
- 사용자가 쓴 민감 어휘: {hit_line} — 사용자가 먼저 꺼내기 전에는 따라 쓰지 말 것.
"""

    if phase == "mid":
        accept = ""
        if hits:
            sample = hits[0]
            accept = (
                f'\n- 사용자가 「{sample}」을(를) 꺼냈다 — **의미만 수용**하고 은유·재진술로 대화에 녹일 것.\n'
                f'  (「{sample}」을 답변에 그대로 복사하지 말 것. 오타·깨진 표기도 복붙 금지.)\n'
                f"  (AI가 새로 행정·진단 라벨을 붙이지는 말 것.)"
            )
        return f"""
[어휘 전략 · 맥락 형성 단계]
- 사용자가 먼저 꺼낸 말의 **뜻**을 은유·재진술로 되짚으며 깊이 탐색한다.{accept}
- 사용자가 쓴 민감 어휘: {hit_line}
- AI가 여전히 먼저 쓰지 않을 것: {never}
- 아직 은유·질문으로 열 수 있으면 라벨보다 은유를 우선.
"""

    return f"""
[어휘 전략 · 서사 자산화 단계]
- 사용자가 자아성을 회복해 스스로를 객관화할 때, **사용자가 쓴 단어**로 서사를 정돈한다.
- 사용자가 쓴 민감 어휘: {hit_line} — 사용자 언어를 존중하며 요약·연결.
- 「사회복귀」 **대신** 우선: {late_pref}
- AI가 먼저 쓰지 않을 것: {never}
- 「고립·은둔」은 사용자가 이미 쓴 경우에만, 서사 정리 도구로 **1회 이내** 신중히.
"""


def pick_maieutic_seed_question(*, user_turns: int = 0) -> str:
    """미팅용 산파술 시드 — 턴 수에 따라 로테이션."""
    if not MAIEUTIC_SEED_QUESTIONS:
        return ""
    return MAIEUTIC_SEED_QUESTIONS[user_turns % len(MAIEUTIC_SEED_QUESTIONS)]


def _empty_block() -> dict[str, Any]:
    return {
        "identity": {"summary": "", "self_definition": ""},
        "social": {"summary": "", "relational_longing": ""},
        "bloom": {"level": "unknown", "summary": "", "create_aspiration": ""},
        "todd_rose": {
            "summary": "",
            "peak_strengths": [],
            "trough_areas": [],
            "peak_contexts": "",
        },
        "pattern_seeker": {"summary": "", "writing_connection": ""},
        "dynamics": {
            "motivation": "",
            "friction": "",
            "inertia": "",
            "gravity": "",
            "synthesis": "",
        },
        "recovery_strength": "weak",
        "thin_axis": "identity",
        "anchor_quote": "",
        "source": "heuristic",
    }


def _heuristic_depth(user_texts: list[str]) -> dict[str, str]:
    blob = " ".join(user_texts).lower()
    if len(blob) < 10:
        s = "shallow"
        return {k: s for k in (*DUAL_AXIS_KEYS, *FOUR_THEORY_KEYS)}

    def sc(words: tuple[str, ...]) -> str:
        h = sum(1 for w in words if w in blob)
        if h >= 2:
            return "moderate"
        if h >= 1:
            return "shallow"
        return "unknown"

    return {
        "identity": sc(("나", "자아", "누구", "정체", "내가", "자신", "identity", "우주")),
        "social": sc(("사람", "관계", "친구", "가족", "세상", "연결", "외로", "social")),
        "bloom": sc(("이해", "분석", "정의", "의미", "생각", "create", "서사", "쓰")),
        "todd_rose": sc(("안전", "방", "집", "혼자", "편한", "장소", "맥락", "평균")),
        "pattern_seeker": sc(("패턴", "시스템", "세상", "구조", "질서", "부정", "방어")),
        "dynamics": sc(("두려", "마찰", "용기", "작은", "한걸음", "나가", "멈춤", "습관", "틈")),
    }


def _heuristic_signals(user_texts: list[str]) -> dict[str, Any]:
    base = _empty_block()
    if not user_texts:
        return base
    last = user_texts[-1][:120]
    base["identity"]["summary"] = "고유한 시간 속에서 자기를 바라보는 시선이 스며듭니다."
    base["identity"]["self_definition"] = last[:80]
    base["social"]["summary"] = "세상과의 관계에 대한 이야기가 조심스럽게 열리고 있습니다."
    base["social"]["relational_longing"] = "연결에 대한 말이 아직 형성 중입니다."
    base["dynamics"]["friction"] = last
    base["dynamics"]["motivation"] = "작은 추진의 단서를 찾는 중"
    base["anchor_quote"] = last[:40]
    depths = _heuristic_depth(user_texts)
    moderate = sum(1 for d in depths.values() if d == "moderate")
    base["recovery_strength"] = "emerging" if moderate >= 2 else "weak"
    return base


def _pick_thin_axis(depths: dict[str, str]) -> str:
    order = (*DUAL_AXIS_KEYS, *FOUR_THEORY_KEYS)
    for k in order:
        if depths.get(k) in ("shallow", "unknown"):
            return k
    return "identity"


def _merge_llm_block(base: dict[str, Any], data: dict[str, Any]) -> None:
    for k in ("identity", "social", *FOUR_THEORY_KEYS):
        if isinstance(data.get(k), dict):
            base[k] = {**base.get(k, {}), **data[k]}
        elif data.get(k):
            base[k] = {"summary": str(data[k])}
    for key in ("thin_axis", "anchor_quote", "recovery_strength"):
        if data.get(key):
            base[key] = str(data[key])


def extract_isolation_signals(
    messages: list[dict],
    *,
    lang: str = "ko",
    use_llm: bool = True,
) -> dict[str, Any]:
    user_texts = [
        str(m.get("content") or m.get("display") or "").strip()
        for m in messages
        if m.get("role") == "user"
        and str(m.get("content") or m.get("display") or "").strip()
    ]
    depths = _heuristic_depth(user_texts)
    base = _heuristic_signals(user_texts)
    base["axis_depth"] = depths
    base["thin_axis"] = _pick_thin_axis(depths)
    base["user_lexicon_hits"] = detect_user_lexicon_hits(user_texts)
    base["lexicon_phase"] = resolve_lexicon_phase(
        user_turns=len(user_texts),
        user_texts=user_texts,
        live_signals=base,
    )
    if not user_texts or not use_llm:
        return base

    transcript = "\n".join(f"- {t[:300]}" for t in user_texts[-12:])
    prompt = f"{ISOLATION_EXTRACTION_JSON_PROMPT}\n\n[발화]\n{transcript}\n언어:{lang}"

    try:
        if is_llm_configured():
            text = generate_text(prompt, temperature=0.35, max_tokens=1200)
            data = llm_extract_json(text) or {}
        else:
            ensure_gemini_configured()
            import google.generativeai as genai

            model = genai.GenerativeModel(
                get_gemini_model_name(),
                generation_config=genai.GenerationConfig(
                    temperature=0.35, max_output_tokens=1200
                ),
            )
            data = _extract_json(model.generate_content(prompt).text or "") or {}

        if data:
            _merge_llm_block(base, data)
            base["source"] = "llm"
    except Exception:  # noqa: BLE001
        pass
    return base


_STORAGE_EN_KO: tuple[tuple[str, str], ...] = (
    ("Analyze→Create", "분석에서 창조로의 전환"),
    ("Analyze->Create", "분석에서 창조로의 전환"),
    ("Jagged", "비균질"),
    ("jagged", "비균질"),
    ("Small Win", "작은 추진"),
    ("small win", "작은 추진"),
    ("Todd Rose", "수평적 개성·맥락"),
    ("Bloom", "인지적 재정의"),
)


def _sanitize_storage_text(text: str) -> str:
    out = text or ""
    for en, ko in _STORAGE_EN_KO:
        if en and en in out:
            out = out.replace(en, ko)
    return out.strip()


def _sanitize_storage_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _sanitize_storage_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_storage_value(v) for v in value]
    if isinstance(value, str):
        return _sanitize_storage_text(value)
    return value


def enrich_isolation_signals_for_storage(signals: dict[str, Any] | None) -> dict[str, Any]:
    """
    Supabase isolation_narratives.signals_json — 관리·연구용 한글 메타 + 원본 신호.
    내담자 UI에는 노출하지 않음.
    """
    if not isinstance(signals, dict):
        return {}
    out = _sanitize_storage_value(dict(signals))
    thin = str(out.get("thin_axis") or "").strip()
    phase = str(out.get("lexicon_phase") or "").strip()
    phase_ko = {"early": "탐색", "mid": "맥락 형성", "late": "서사 자산화"}.get(phase, phase)
    strength = str(out.get("recovery_strength") or "").strip()
    strength_ko = {
        "weak": "씨앗",
        "emerging": "싹틂",
        "clear": "선명",
    }.get(strength, strength)
    out["framework_labels_ko"] = {
        k: FOUR_FRAMEWORK_LABELS.get(k, k) for k in FOUR_FRAMEWORK_KEYS
    }
    out["dual_axis_labels_ko"] = {k: DUAL_AXIS_LABELS.get(k, k) for k in DUAL_AXIS_KEYS}
    if thin:
        out["thin_axis_label_ko"] = (
            DUAL_AXIS_LABELS.get(thin) or FOUR_FRAMEWORK_LABELS.get(thin, thin)
        )
    if phase:
        out["lexicon_phase_ko"] = phase_ko
    if strength:
        out["recovery_strength_ko"] = strength_ko
    recap = summarize_recovery_signals(out)
    out["admin_recap_ko"] = {
        "identity": recap.get("identity", ""),
        "social": recap.get("social", ""),
        "framework_lines": recap.get("framework_block", ""),
        "anchor_quote": recap.get("anchor_quote", ""),
    }
    return out


def summarize_recovery_signals(signals: dict[str, Any] | None) -> dict[str, str]:
    """
    H-Bridge 중간 요약 — 자아성/사회성 회복 신호 + 4대 렌즈 한 줄.
    점수·진단 라벨 없음.
    """
    sig = signals or {}
    id_block = sig.get("identity") or {}
    soc_block = sig.get("social") or {}

    def _line(block: Any, fallback: str) -> str:
        if isinstance(block, dict):
            for key in ("summary", "self_definition", "relational_longing"):
                val = str(block.get(key) or "").strip()
                if val:
                    return val[:220]
        return fallback

    identity_line = _line(id_block, "고유한 시간 속에서 「나는 누구인가」를 스스로 묻는 단서가 보입니다.")
    social_line = _line(
        soc_block,
        "타인·세상과의 관계에 대한 말이 조심스럽게 스며들고 있습니다.",
    )

    framework_lines: list[str] = []
    for key in FOUR_FRAMEWORK_KEYS:
        block = sig.get(key) or {}
        label = FOUR_FRAMEWORK_LABELS.get(key, key)
        snippet = ""
        if isinstance(block, dict):
            snippet = str(block.get("summary") or block.get("synthesis") or "").strip()
            if not snippet and key == "dynamics":
                fr = str(block.get("friction") or "").strip()
                mo = str(block.get("motivation") or "").strip()
                if fr or mo:
                    snippet = f"마찰: {fr[:60]} · 추진: {mo[:60]}".strip(" ·")
            if not snippet and key == "todd_rose":
                snippet = str(block.get("peak_contexts") or "").strip()
        if snippet:
            framework_lines.append(f"**{label}** — {snippet[:120]}")
        else:
            framework_lines.append(f"**{label}** — 아직 이 축의 이야기를 열어 가는 중")

    strength = str(sig.get("recovery_strength") or "weak")
    strength_ko = {
        "weak": "씨앗",
        "emerging": "싹틂",
        "clear": "선명",
    }.get(strength, strength)

    thin = str(sig.get("thin_axis") or "")
    thin_label = DUAL_AXIS_LABELS.get(thin) or FOUR_FRAMEWORK_LABELS.get(thin, thin)

    phase = str(sig.get("lexicon_phase") or "")
    phase_ko = {
        "early": "탐색",
        "mid": "맥락 형성",
        "late": "서사 자산화",
    }.get(phase, "")

    return {
        "identity": identity_line,
        "social": social_line,
        "framework_block": "\n".join(f"- {ln}" for ln in framework_lines),
        "recovery_strength": strength_ko,
        "thin_axis_label": thin_label,
        "anchor_quote": str(sig.get("anchor_quote") or "").strip(),
        "lexicon_phase": phase_ko,
        "user_lexicon_hits": ", ".join(sig.get("user_lexicon_hits") or []) or "",
    }


def build_global_isolation_system_instruction(lang: str = "ko") -> str:
    from personas import LANG_REPLY

    reply = LANG_REPLY.get(lang, "Korean")
    native = LANG_NAMES.get(lang, reply)
    return (
        GLOBAL_ISOLATION_SYSTEM_INSTRUCTION
        + f"\n\n[응답 언어] **{native}** ({reply})만 사용."
    )


def build_isolation_depth_addon(
    *,
    four_depth: dict[str, str] | None = None,
    dual_depth: dict[str, str] | None = None,
) -> str:
    labels = {**DUAL_AXIS_LABELS, **FOUR_FRAMEWORK_LABELS}
    shallow = []
    for k in (*DUAL_AXIS_KEYS, *FOUR_THEORY_KEYS):
        d = (dual_depth or four_depth or {}).get(k, "unknown")
        if d in ("shallow", "unknown"):
            shallow.append(labels.get(k, k))
    if not shallow:
        return "\n\n[서사 깊이 · 충분] 인정·음미 위주, 과잉 캐묻기 금지.\n"
    focus = shallow[0]
    hint = ""
    if "dynamics" in str(focus).lower() or "추진" in focus:
        hint = " 마찰·추진·마음의 틈을 한 질문에."
    elif "평균" in focus or "비균질" in focus or "안전 맥락" in focus:
        hint = " 가장 편안한 장소·시간·사람을 한 질문에."
    return f"\n\n[서사 깊이 · 보강] **{focus}** 축만 질문 1개.{hint}\n"


def build_full_isolation_system_instruction(
    *,
    lang: str = "ko",
    age_group: str = "",
    life_stage: str = "",
    nickname: str = "",
    last_user: str = "",
    user_turns: int = 0,
    user_texts: list[str] | None = None,
    report_completed: bool = False,
    context_summary: str = "",
    live_signals: dict[str, Any] | None = None,
) -> str:
    texts = list(user_texts or [])
    if last_user.strip() and (not texts or texts[-1] != last_user.strip()):
        texts = texts + [last_user.strip()]
    lexicon_phase = resolve_lexicon_phase(
        user_turns=user_turns,
        user_texts=texts,
        report_completed=report_completed,
        live_signals=live_signals,
    )
    depths = _heuristic_depth([last_user] if last_user else texts[-1:])
    parts = [
        build_global_isolation_system_instruction(lang),
        build_isolation_system_addon(
            age_group=age_group,
            life_stage=life_stage,
            lang=lang,
            nickname=nickname,
            lexicon_phase=lexicon_phase,
        ),
        build_lexicon_strategy_addon(
            phase=lexicon_phase,
            user_texts=texts,
            last_user=last_user,
        ),
        build_isolation_depth_addon(dual_depth=depths, four_depth=depths),
    ]
    if user_turns < MIN_USER_TURNS_FOR_ASSET:
        seed = pick_maieutic_seed_question(user_turns=user_turns)
        parts.append(
            "\n\n[단계 · 자산 전] 리포트·진단 형식 금지. "
            "자아·사회·경험을 하나씩 열기. "
            f"어휘 단계={lexicon_phase}.\n"
        )
        if user_turns <= 1 and seed and lexicon_phase == "early":
            parts.append(f"\n[산파술 시드 참고] 「{seed}」 — 변형하여 1개만.\n")
    elif not report_completed:
        parts.append(
            f"\n\n[단계 · 자산 가능] {MIN_USER_TURNS_FOR_ASSET}턴 이상 — "
            f"어휘 단계={lexicon_phase}. "
            "최종 서사 리포트 본문은 출력하지 말 것.\n"
        )
    if context_summary.strip():
        parts.append(f"\n\n[지금까지의 서사 요약]\n{context_summary.strip()}")
    if live_signals:
        recap = summarize_recovery_signals(live_signals)
        parts.append(
            "\n\n[실시간 회복 신호 — 수치·라벨로 말하지 말 것]\n"
            f"- 자아성: {recap['identity'][:160]}\n"
            f"- 사회성: {recap['social'][:160]}\n"
        )
    thin = str((live_signals or {}).get("thin_axis") or "")
    if thin:
        label = DUAL_AXIS_LABELS.get(thin) or FOUR_FRAMEWORK_LABELS.get(thin, thin)
        parts.append(f"\n\n[실시간 우선 축] {label} — 질문 1개에 반영.\n")
    parts.append(EMPATHETIC_REPHRASE_INSTRUCTION)
    parts.append(user_turn_context_for_llm(last_user, max_len=200))
    return "\n".join(parts)


def build_isolation_chat_history(messages: list[dict]) -> list[dict]:
    history: list[dict] = []
    for msg in messages[:-1]:
        text = str(msg.get("content") or msg.get("display") or "").strip()
        if not text:
            continue
        role = "user" if msg.get("role") == "user" else "model"
        history.append({"role": role, "parts": [text]})
    return history


def iter_isolation_reply_stream(
    messages: list[dict],
    user_prompt: str,
    *,
    lang: str = "ko",
    age_group: str = "",
    life_stage: str = "",
    nickname: str = "",
    report_completed: bool = False,
    context_summary: str = "",
    live_signals: dict[str, Any] | None = None,
):
    from llm_client import iter_chat_stream

    user_texts = [
        str(m.get("content") or "").strip()
        for m in messages
        if m.get("role") == "user"
    ]
    if user_prompt.strip():
        user_texts.append(user_prompt.strip())
    system = build_full_isolation_system_instruction(
        lang=lang,
        age_group=age_group,
        life_stage=life_stage,
        nickname=nickname,
        last_user=user_prompt,
        user_turns=len(user_texts),
        user_texts=user_texts,
        report_completed=report_completed,
        context_summary=context_summary,
        live_signals=live_signals,
    )
    history = build_isolation_chat_history(
        messages + [{"role": "user", "content": user_prompt}]
    )
    yield from iter_chat_stream(
        messages,
        user_prompt,
        system=system,
        temperature=0.78,
        top_p=0.92,
        max_tokens=2048,
        gemini_history=history,
    )


def generate_isolation_report_for_messages(
    messages: list[dict],
    *,
    age_group: str = "",
    life_stage: str = "",
    participant_id: str = "",
    lang: str = "ko",
    profile: dict[str, float] | None = None,
) -> dict[str, Any]:
    from isolation_analysis import run_isolation_report_pipeline

    signals = extract_isolation_signals(messages, lang=lang)
    return run_isolation_report_pipeline(
        messages,
        profile,
        signals=signals,
        age_group=age_group,
        life_stage=life_stage,
        participant_id=participant_id,
        lang=lang,
    )


def notify_local_db_saved(nickname: str) -> None:
    """터미널 확인용 — 대화 턴 저장 직후."""
    nick = (nickname or "").strip() or "(닉네임 없음)"
    msg = f"✅ 로컬 DB 저장 완료: {nick}"
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(f"[OK] 로컬 DB 저장 완료: {nick}", flush=True)


def save_isolation_turn_local(
    db: Any,
    *,
    nickname: str = "",
    **log_kwargs: Any,
) -> tuple[bool, str | None]:
    """
    숲 모듈 — 로컬 SQLite + Supabase 이중 저장.
    로컬 실패 시 중단. Supabase 실패 시에도 대화는 계속.
    """
    from database_manager import log_isolation_turn_dual

    ok, err = log_isolation_turn_dual(db, nickname=nickname, **log_kwargs)
    if ok:
        notify_local_db_saved(
            nickname or str(log_kwargs.get("participant_id") or "")
        )
    return ok, err
