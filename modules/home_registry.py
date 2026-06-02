"""메인 홈 4모듈 — 서사 상담실 · app_mode 라우팅."""

from __future__ import annotations

from dataclasses import dataclass

from modes.registry import MODE_ISOLATION, MODE_LEARNING, MODE_LIFESPAN

MODULE_NARRATIVE = "narrative"
MODULE_LEARNING = "learning"
MODULE_FOREST = "forest"
MODULE_EMOTION = "emotion"

SALON_SECTION_TITLE = "서사 기록실"
SALON_GUIDE_LINE = "dlinso — Dlinso Narrative Archive · 당신의 삶을 데이터 자산으로"
SALON_GUIDE_SUB = "검사나 채점이 아닌, 말과 기억을 인출·기록하는 디지털 아카이브입니다. 아래에서 기록실을 선택하세요."
BRAND_TAGLINE = "모든 삶은 예술이 된다"
JOURNEY_CTA_KO = "여정 시작하기"
JOURNEY_CTA_EN = "Begin the Narrative"
MODULE_CTA_KO: dict[str, str] = {
    MODULE_NARRATIVE: "동행 시작하기",
    MODULE_LEARNING: "여정 시작하기",
    MODULE_FOREST: "숲으로 들어가기",
}
MODULE_CTA_ICON: dict[str, str] = {
    MODULE_NARRATIVE: "✦",
    MODULE_LEARNING: "◇",
    MODULE_FOREST: "🌲",
}
MODULE_CTA_EN: dict[str, str] = {
    MODULE_NARRATIVE: "Begin Companion",
    MODULE_LEARNING: "Begin Learning Journey",
    MODULE_FOREST: "Enter the Forest",
}

# ?module=learning 딥링크 전용 카피
LEARNING_SPOTLIGHT_TITLE_KO = "여정 · 배움의 등고선"
LEARNING_SPOTLIGHT_LEAD_KO = (
    "나만의 봉우리를 찾아가는 배움의 지형입니다. "
    "습관·동기·환경을 함께 탐색하고, 10번의 대화 뒤 배움 지도 리포트를 받을 수 있습니다."
)
LEARNING_SPOTLIGHT_STEPS_KO = (
    "① 기록 주체 확인 → ② 배움 이야기 인출 → ③ 배움 지도 아카이브"
)
LEARNING_SPOTLIGHT_CTA_KO = "배움 여정 시작하기"
LEARNING_SPOTLIGHT_TITLE_EN = "Journey · Contour of Learning"
LEARNING_SPOTLIGHT_LEAD_EN = (
    "Trace your learning horizon—habits, motivation, and context—"
    "then receive a learning map report after ten turns."
)
LEARNING_SPOTLIGHT_STEPS_EN = (
    "① Student or parent → ② Learning dialogue → ③ Learning map report"
)
LEARNING_SPOTLIGHT_CTA_EN = "Start learning journey"


@dataclass(frozen=True, slots=True)
class LandingModuleSpec:
    id: str
    title: str
    description: str
    app_mode: str | None
    enabled: bool
    status_badge: str = ""
    prompt_channel: str = ""
    title_en: str = ""
    description_en: str = ""
    outcome_line1: str = ""
    outcome_line2: str = ""


LANDING_MODULES: tuple[LandingModuleSpec, ...] = (
    LandingModuleSpec(
        MODULE_NARRATIVE,
        "동행 · 삶의 기록",
        "지나온 길을 예술로 엮어 가는 시간",
        MODE_LIFESPAN,
        True,
        prompt_channel="lifespan",
        title_en="Companion · Life as Record",
        description_en="Weaving the path you have walked into art",
        outcome_line1="대화가 쌓이면 당신만의 서사가 선명해집니다.",
        outcome_line2="10턴 이후, 마음 지도 리포트로 삶의 흐름을 돌아볼 수 있습니다.",
    ),
    LandingModuleSpec(
        MODULE_LEARNING,
        "여정 · 배움의 등고선",
        "나만의 봉우리를 찾아가는 배움의 지형",
        MODE_LEARNING,
        True,
        prompt_channel="learning",
        title_en="Journey · Contour of Learning",
        description_en="Tracing your summit along the learning horizon",
        outcome_line1="배움 습관·동기·환경을 깊이 이해하게 됩니다.",
        outcome_line2="학습 서사 리포트로 강점과 보완 영역을 확인합니다.",
    ),
    LandingModuleSpec(
        MODULE_FOREST,
        "숲 · 연결의 서사",
        "고요함 속에 자아와 연결이 숨 쉬는 숲",
        MODE_ISOLATION,
        True,
        prompt_channel="forest",
        title_en="Forest · Narrative of Connection",
        description_en="A forest where selfhood and connection breathe in stillness",
        outcome_line1="자아성·사회성 궤적을 검사 없이 이야기로 열어 갑니다.",
        outcome_line2="6턴 자산 · 10턴 내면 항해 일지 · data/isolation.db 로컬 저장.",
    ),
    LandingModuleSpec(
        MODULE_EMOTION,
        "숨결 · 마음 챙김",
        "내면의 물결을 마주하는 섬세한 대화",
        None,
        False,
        status_badge="coming soon",
        prompt_channel="emotion",
        title_en="Breath · Mindful Presence",
        description_en="A delicate dialogue with the tides within",
        outcome_line1="정서의 결을 섬세하게 따라가는 공간입니다.",
        outcome_line2="곧 문을 열 예정입니다.",
    ),
)

_MODULE_BY_ID = {m.id: m for m in LANDING_MODULES}


def get_landing_module(module_id: str) -> LandingModuleSpec | None:
    return _MODULE_BY_ID.get((module_id or "").strip())


def module_app_mode(module_id: str) -> str | None:
    spec = get_landing_module(module_id)
    return spec.app_mode if spec else None


def _reset_module_conversation_state() -> None:
    """살롱(모듈) 전환 시 이전 모드 대화·리포트 상태를 비움."""
    import streamlit as st

    from personas import PHASE_COLLECT

    st.session_state.messages = []
    st.session_state.context_summary = ""
    st.session_state.story_thread = ""
    st.session_state.conversation_closed = False
    st.session_state.conversation_restored = False
    st.session_state.total_user_turns = 0
    st.session_state.phase = PHASE_COLLECT
    st.session_state.active_giant = None
    st.session_state.pending_midpoint_analysis = False
    st.session_state.pending_learning_report = False
    st.session_state.last_midpoint_report = None
    st.session_state.midpoint_analysis_count = 0
    st.session_state.last_learning_report = None
    st.session_state.learning_report_count = 0
    st.session_state.learning_signals = None
    st.session_state.isolation_signals = None
    st.session_state.last_isolation_asset = None
    st.session_state.isolation_asset_count = 0
    st.session_state.last_isolation_report = None
    st.session_state.isolation_report_count = 0
    st.session_state.pending_isolation_asset = False
    st.session_state.pending_isolation_report = False
    st.session_state.pop("_chat_input_focused", None)


def apply_landing_module_selection(module_id: str) -> bool:
    import streamlit as st

    spec = get_landing_module(module_id)
    if not spec or not spec.enabled or not spec.app_mode:
        return False

    prev_id = (st.session_state.get("selected_module_id") or "").strip()
    prev_mode = (st.session_state.get("app_mode") or MODE_LIFESPAN).strip()
    module_changed = prev_id != spec.id or prev_mode != spec.app_mode

    st.session_state.selected_module_id = spec.id
    st.session_state.app_mode = spec.app_mode

    if spec.app_mode == MODE_LEARNING:
        if module_changed:
            st.session_state.learning_audience = ""
    elif spec.app_mode != MODE_ISOLATION:
        st.session_state.learning_audience = ""
    if spec.app_mode == MODE_ISOLATION and module_changed:
        st.session_state.isolation_signals = None
        st.session_state.last_isolation_asset = None
        st.session_state.last_isolation_report = None

    if module_changed:
        _reset_module_conversation_state()

    try:
        st.query_params["module"] = spec.id
    except Exception:  # noqa: BLE001
        pass

    return True


def module_cta_label(module_id: str, *, lang: str = "ko") -> str:
    table = MODULE_CTA_KO if lang == "ko" else MODULE_CTA_EN
    return table.get(module_id, JOURNEY_CTA_KO if lang == "ko" else JOURNEY_CTA_EN)


def reconcile_landing_module_session() -> None:
    """selected_module_id ↔ app_mode 불일치 시 모듈 스펙 기준으로 맞춤."""
    import streamlit as st

    module_id = (st.session_state.get("selected_module_id") or "").strip()
    if not module_id:
        return
    spec = get_landing_module(module_id)
    if not spec or not spec.app_mode:
        return
    if st.session_state.get("app_mode") != spec.app_mode:
        st.session_state.app_mode = spec.app_mode


def query_param_str(name: str) -> str:
    """Streamlit query_params — 스칼라·리스트 모두 처리."""
    import streamlit as st

    try:
        raw = st.query_params.get(name, "")
    except Exception:  # noqa: BLE001
        return ""
    if isinstance(raw, list):
        return str(raw[0] if raw else "").strip()
    return str(raw or "").strip()


def _query_param_flag(name: str) -> bool:
    return query_param_str(name).lower() in ("1", "true", "yes")


def active_deep_link_module_id() -> str:
    """URL ?module= 또는 세션 선택 모듈."""
    import streamlit as st

    raw = query_param_str("module").lower()
    if raw in ("learning", "narrative", "forest", "emotion"):
        return raw
    return (st.session_state.get("selected_module_id") or "").strip().lower()


def sync_learning_deep_link_entry() -> None:
    """?revealed=1&module=learning — 살롱 노출 + 여정 모듈 고정(최초만)."""
    import streamlit as st

    if _query_param_flag("revealed"):
        st.session_state.home_intro_revealed = True
    raw = query_param_str("module").lower()
    if raw != MODULE_LEARNING:
        return
    if (st.session_state.get("selected_module_id") or "").strip():
        reconcile_landing_module_session()
        return
    apply_landing_module_selection(MODULE_LEARNING)


def sync_landing_module_from_query() -> None:
    """URL ?module=… → 세션(최초 진입·선택 없을 때만)."""
    import streamlit as st

    sync_learning_deep_link_entry()
    if (st.session_state.get("selected_module_id") or "").strip():
        return
    raw = query_param_str("module").lower()
    if raw in ("learning", "narrative", "forest", "emotion"):
        apply_landing_module_selection(raw)


def navigate_to_landing_module(module_id: str) -> None:
    """홈 카드 CTA — 모듈 확정, URL·화면 전환."""
    import streamlit as st

    from core.views import VIEW_APP

    if not apply_landing_module_selection(module_id):
        return
    reconcile_landing_module_session()
    st.session_state.current_view = VIEW_APP
    st.rerun()
