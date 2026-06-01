"""나의 지난 이야기 동반자: dlinso — 지능형 서사 통합 시스템."""

from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from collections.abc import Iterator
from typing import Any

import streamlit as st
import streamlit.components.v1 as components
from env_config import (
    APP_DIR,
    ENV_PATH,
    apply_secrets_to_environ,
    get_database_path,
    get_gemini_api_key,
    get_isolation_database_path,
    get_llm_provider,
    get_upstage_api_key,
    is_streamlit_cloud,
)

apply_secrets_to_environ()
from database_manager import DatabaseManager, hash_password
from isolation_database_manager import IsolationDatabaseManager
from llm_client import LLMNotConfiguredError, init_llm_client, is_llm_configured, iter_chat_stream
from narrative_engine import (
    PROFILE_KEYS,
    analyze_narrative_turn,
    default_profile,
    extract_interests,
    extract_positive_resources,
    generate_life_summary,
    pick_summoned_narrative,
    summarize_messages,
)
from narrative_export import build_export_payload, export_json_bytes, export_pdf_bytes
from personas import (
    AGE_GROUPS,
    GENDER_OPTIONS,
    GIANTS,
    LIFE_STAGE_OPTIONS,
    PHASE_COLLECT,
    PHASE_GIANT,
    SERVICE_TITLE,
    build_returning_greeting,
    detect_distress,
    get_active_display,
    phase_label_ko,
    select_giant,
)
from hbridge_analysis import (
    MIN_USER_TURNS_FOR_MIDPOINT,
    assess_midpoint_readiness,
    parse_stored_midpoint_message,
    compute_midpoint_statistics,
    extract_situational_context,
    format_full_midpoint_message,
    format_midpoint_followup,
    format_sheet_stats_summary,
    narrative_assetization_progress,
    narrative_precision_score,
    run_intra_individual_or_pipeline,
)
from i18n import FOOTER_BANNER, get_lang, render_language_selector, t
from maieutic_engine import (
    analyze_uploaded_image,
    build_adaptive_scaffolding_addon,
    build_conversation_phase_addon,
    build_global_maieutic_system_instruction,
    build_maieutic_addon,
    format_image_display_for_user,
    merge_text_and_image,
)
from narrative_engine import (
    generate_humanistic_midpoint_report,
    translate_to_korean,
)
from core.views import VIEW_APP, VIEW_HOME, VIEW_INQUIRY, VIEW_INTRO
from main_home import (
    render_home_footer_minimal,
    render_main_home,
    sync_home_intro_revealed,
)
from ui.dlinso_about import open_dlinso_about, render_dlinso_about_expander_if_needed
from modules.home_registry import (
    apply_landing_module_selection,
    get_landing_module,
    module_app_mode,
    reconcile_landing_module_session,
    sync_landing_module_from_query,
)
from modes.registry import MODE_ISOLATION, MODE_LEARNING, MODE_LIFESPAN
from modes.isolation import (
    MIN_USER_TURNS_FOR_ASSET,
    MIN_USER_TURNS_FOR_REPORT,
    get_isolation_display,
)
from modes.learning import (
    MIN_USER_TURNS_FOR_LEARNING_REPORT,
    audience_opening_i18n_key,
    get_learning_display,
    is_valid_learning_audience,
)
from ui.learning_audience import (
    render_learning_audience_selectbox,
    render_learning_audience_selector,
)
from learning_analysis import (
    format_full_learning_message,
    format_learning_followup,
    TITLE_FOUR_LENSES,
    TITLE_IDENTITY,
    TITLE_JAGGED,
    TITLE_PRESCRIPTION,
)
from learning_engine import (
    extract_learning_signals,
    generate_learning_narrative_report_for_messages,
    iter_learning_reply_stream,
)
from isolation_analysis import (
    format_full_asset_message,
    format_full_isolation_report_message,
)
from isolation_engine import (
    extract_isolation_signals,
    generate_isolation_report_for_messages,
    iter_isolation_reply_stream,
    save_isolation_turn_local,
)
from opening_copy import resolve_opening_message, resolve_opening_placeholder
from prompts.registry import build_mode_system_addon, build_mode_system_addon_for_module
from ui.age_entry import render_current_age_context, render_mode_roadmap

os.chdir(APP_DIR)

PAGE_TITLE = "dlinso | 모든 삶은 예술이 된다"
LANDING_PAGE_PATH = APP_DIR / "landing_page.html"
# VIEW_* → core.views
DB_MANAGER_CACHE_VERSION = 4

# st.html iframe에는 앱 전역 CSS가 적용되지 않음 — 헤더·프로필 칩 전용
HERO_CARD_INLINE_STYLE = """
<style>
  .hero-header {
    font-family: "Source Sans Pro", sans-serif;
    background: linear-gradient(135deg, #fffcf8 0%, #f5efe6 100%);
    border: 1px solid rgba(140, 120, 100, 0.18);
    border-radius: 16px;
    padding: 1.35rem 1.5rem 1.15rem;
    margin: 0 0 1rem 0;
    box-shadow: 0 4px 24px rgba(90, 70, 50, 0.08);
  }
  .hero-eyebrow {
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    color: #9a8a78;
    font-weight: 600;
    margin: 0 0 0.35rem 0;
  }
  .hero-title {
    font-size: clamp(1.2rem, 4vw, 1.55rem);
    font-weight: 700;
    color: #4a4038;
    margin: 0 0 0.45rem 0;
    line-height: 1.35;
  }
  .hero-desc { color: #6b5f55; font-size: 0.94rem; line-height: 1.6; margin: 0; }
  .profile-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-top: 1rem;
    align-items: stretch;
  }
  .profile-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.85rem 0.5rem 0.6rem;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(140, 120, 100, 0.22);
    border-radius: 12px;
    box-shadow: 0 1px 6px rgba(90, 70, 50, 0.07);
    min-height: 2.65rem;
    line-height: 1.25;
    box-sizing: border-box;
  }
  .profile-pill--accent {
    border-color: rgba(108, 92, 231, 0.35);
    background: linear-gradient(135deg, #f6f3ff 0%, #fffcf8 100%);
  }
  .profile-pill-icon { font-size: 1.2rem; line-height: 1; flex-shrink: 0; }
  .profile-pill-body {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.1rem;
    min-width: 0;
  }
  .profile-pill-label {
    font-size: 0.62rem;
    letter-spacing: 0.07em;
    color: #9a8a78;
    font-weight: 600;
  }
  .profile-pill-value {
    font-size: 0.9rem;
    font-weight: 600;
    color: #4a4038;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 10.5rem;
  }
</style>
"""

TOKEN_DIET_MESSAGE_THRESHOLD = 28


def _beta_badge_html() -> str:
    label = html.escape((t("beta_badge") or "Beta").strip())
    return f'<span class="beta-badge" title="{label}">{label}</span>'


def _html_layout_marker(*css_classes: str) -> None:
    """위젯 사이에 HTML div를 열고 닫으면 Streamlit이 `</div>`를 화면에 그립니다."""
    cls = " ".join(css_classes)
    st.markdown(
        f'<span class="layout-marker {cls}" hidden aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )


def _render_html_fragment(fragment: str) -> None:
    """HTML 조각 렌더 — 구버전 Streamlit은 st.html(height=…) 미지원."""
    html_fn = getattr(st, "html", None)
    if callable(html_fn):
        try:
            html_fn(fragment)
            return
        except TypeError:
            pass
    st.markdown(fragment, unsafe_allow_html=True)


def _llm_user_error(exc: BaseException) -> str:
    msg = str(exc)
    low = msg.lower()
    if isinstance(exc, LLMNotConfiguredError):
        has_upstage = bool(get_upstage_api_key())
        has_gemini = bool(get_gemini_api_key())
        if is_streamlit_cloud():
            if not has_upstage and not has_gemini:
                return (
                    "대화 LLM API 키가 없습니다.\n\n"
                    "Streamlit Cloud → **Settings → Secrets** 에 아래처럼 추가하세요:\n\n"
                    "```toml\n"
                    'UPSTAGE_API_KEY = "up_여기에_Upstage_키"\n'
                    'UPSTAGE_MODEL = "solar-pro3"\n'
                    'LLM_PROVIDER = "upstage"\n'
                    "```\n\n"
                    "Upstage 키: [console.upstage.ai/api-keys](https://console.upstage.ai/api-keys)\n\n"
                    "또는 Gemini 사용 시:\n"
                    '```toml\nGEMINI_API_KEY = "AI..."\nLLM_PROVIDER = "gemini"\n```\n\n'
                    "저장 후 **Manage app → Reboot app** 을 꼭 실행하세요."
                )
            if get_llm_provider() == "upstage" and not has_upstage:
                return (
                    "UPSTAGE_API_KEY가 비어 있습니다. Secrets에 실제 키(`up_...`)를 넣었는지 확인하고 "
                    "**Reboot app** 하세요. (템플릿 `UPSTAGE_API_KEY = \"\"` 그대로면 동작하지 않습니다.)"
                )
        elif not has_upstage and not has_gemini:
            return (
                "UPSTAGE_API_KEY 또는 GEMINI_API_KEY가 필요합니다. "
                f"`.env` 또는 `.streamlit/secrets.toml` ({ENV_PATH.name})을 확인하세요."
            )
        if get_llm_provider() == "upstage" and not has_upstage:
            return (
                "UPSTAGE_API_KEY가 설정되지 않았습니다. "
                f"`.env` 또는 `.streamlit/secrets.toml` ({ENV_PATH.name})을 확인하세요."
            )
        return t("err_dialogue_unavailable")
    if "leaked" in low or ("403" in msg and "api key" in low):
        return t("err_gemini_leaked")
    return f"{t('err_gemini_reply')}: {msg}"


TOKEN_DIET_KEEP_RECENT = 20
MAX_STORED_MESSAGES = 48
DEFAULT_INPUT_CHAR_LIMIT = 1000
EXTENDED_INPUT_CHAR_LIMIT = 5000

# 메인 영역 전체 너비 (사이드바 제외)
FULL_WIDTH_LAYOUT_CSS = """
<style>
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    section.main iframe {
        width: 100% !important;
        max-width: 100% !important;
        border: none !important;
        display: block !important;
    }
</style>
"""

# 낮막(황혼) 톤 + 미리보기용 CSS
CUSTOM_CSS = """
<style>
    /* header 전체 숨김 시 사이드바 열기(≡) 버튼도 사라짐 — MainMenu·footer만 숨김 */
    #MainMenu, footer { visibility: hidden; height: 0; }
  /* 홈 랜딩(intro/salon)은 main_home.py BRAND_LANDING_CSS가 배경·색을 담당 */
    div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) .stApp,
    div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) .main {
        background: transparent !important;
    }
    div[data-testid="stAppViewContainer"]:not(:has(.dlinso-landing-root-marker)) .stApp {
        background: linear-gradient(165deg, #0a1628 0%, #122238 40%, #1a2d4a 100%);
    }
    div[data-testid="stAppViewContainer"]:not(:has(.dlinso-landing-root-marker)) section.main > div.block-container {
        background: linear-gradient(180deg, #faf7f0 0%, #f3ede3 100%);
        border-radius: 0 0 12px 12px;
        box-shadow: 0 8px 32px rgba(10, 22, 40, 0.35);
    }
    section.main > div.block-container {
        padding-top: 0;
        padding-bottom: 0;
        max-width: 100%;
    }
    div[data-testid="stVerticalBlock"]:has(.app-content-pad-marker),
    div[data-testid="stVerticalBlock"]:has(.chat-content-pad-marker) {
        padding: clamp(0.75rem, 2.5vw, 1.25rem) clamp(0.65rem, 3vw, 1.5rem) clamp(1.25rem, 4vw, 2rem);
        max-width: min(900px, 100%);
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
    }
    div[data-testid="stAppViewContainer"]:not(:has(.dlinso-landing-root-marker)) .stMarkdown,
    div[data-testid="stAppViewContainer"]:not(:has(.dlinso-landing-root-marker)) p,
    div[data-testid="stAppViewContainer"]:not(:has(.dlinso-landing-root-marker)) label,
    div[data-testid="stAppViewContainer"]:not(:has(.dlinso-landing-root-marker)) span {
        font-size: clamp(0.94rem, 2.4vw, 1.06rem);
        color: #3a342e;
        line-height: 1.62;
    }
    div[data-testid="stAppViewContainer"]:not(:has(.dlinso-landing-root-marker)) h1,
    div[data-testid="stAppViewContainer"]:not(:has(.dlinso-landing-root-marker)) h2,
    div[data-testid="stAppViewContainer"]:not(:has(.dlinso-landing-root-marker)) h3,
    div[data-testid="stAppViewContainer"]:not(:has(.dlinso-landing-root-marker)) .hero-title {
        font-size: clamp(1.3rem, 4.2vw, 1.75rem) !important;
        color: #2e2824 !important;
    }
    div[data-testid="stChatMessage"] .stMarkdown p {
        font-size: clamp(0.96rem, 2.6vw, 1.08rem) !important;
        line-height: 1.68 !important;
    }
    .archive-progress-label {
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        color: #5a5248;
        margin: 0.35rem 0 0.15rem;
        font-weight: 600;
    }
    .archive-room-title {
        font-family: "Cormorant Garamond", "Noto Serif KR", serif;
        color: #0a1628;
        letter-spacing: 0.04em;
    }
    .opening-guide, .midpoint-encourage-msg {
        font-size: clamp(0.95rem, 2.8vw, 1.08rem) !important;
        color: #3d3630 !important;
        line-height: 1.65 !important;
    }
    /* 모바일 우선 — 사이드바 완전 제거, 메인 전체 너비 */
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        min-width: 0 !important;
    }
    [data-testid="stAppViewContainer"] > section.main {
        width: 100% !important;
        max-width: 100vw !important;
    }
    /* ── 하이브리드 네비 (첫 vertical block) ── */
    section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type {
        position: sticky !important;
        top: 0 !important;
        z-index: 1001 !important;
        background: rgba(10, 22, 40, 0.97) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: clamp(0.35rem, 1.5vw, 0.65rem) clamp(0.5rem, 2vw, 1.25rem) !important;
        margin: 0 0 0.65rem 0 !important;
        border-bottom: 1px solid rgba(201, 169, 98, 0.35);
        box-shadow: 0 2px 18px rgba(10, 22, 40, 0.25);
    }
    .hybrid-brand {
        font-size: clamp(0.95rem, 2.8vw, 1.15rem);
        font-weight: 700;
        color: #c9a962;
        letter-spacing: 0.04em;
        line-height: 2.75rem;
        white-space: nowrap;
    }
    section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type button {
        font-size: clamp(0.82rem, 2.6vw, 1rem) !important;
        font-weight: 600 !important;
        border-radius: clamp(10px, 2vw, 14px) !important;
        min-height: clamp(2.6rem, 8vw, 3rem) !important;
        padding: clamp(0.5rem, 2vw, 0.75rem) clamp(0.2rem, 1vw, 0.45rem) !important;
        white-space: nowrap !important;
    }
    section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type [data-testid="column"] {
        padding-left: 0.12rem !important;
        padding-right: 0.12rem !important;
    }
    section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type [data-testid="stHorizontalBlock"] {
        gap: clamp(0.12rem, 0.45vw, 0.28rem) !important;
    }
    section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type button[kind="primary"],
    section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type button[data-testid="baseButton-primary"] {
        background: linear-gradient(180deg, #c9a962 0%, #a8863a 100%) !important;
        color: #fff !important;
        border: 1px solid #5b4cdb !important;
        box-shadow: 0 2px 10px rgba(108, 92, 231, 0.3) !important;
    }
    /* PC — 브랜드 좌측, 메뉴 우측 정렬 */
    @media (min-width: 601px) {
        section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type [data-testid="stHorizontalBlock"] {
            justify-content: flex-end !important;
            gap: clamp(0.12rem, 0.45vw, 0.28rem) !important;
        }
        section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type [data-testid="column"]:first-child {
            flex: 0 0 auto !important;
            min-width: 5.5rem !important;
        }
        section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type [data-testid="column"]:nth-child(2) {
            flex: 1 1 auto !important;
            max-width: none !important;
        }
        section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type [data-testid="column"]:nth-child(4) {
            flex: 1.25 0 auto !important;
            min-width: 6.5rem !important;
        }
    }
    /* Streamlit 기본 빨간 primary → dlinso 보라색 (전역) */
    section.main button[kind="primary"],
    section.main button[kind="primaryFormSubmit"],
    section.main [data-testid="stFormSubmitButton"] button,
    section.main .stButton > button[kind="primary"],
    section.main button[data-testid="baseButton-primary"],
    section.main [data-testid="baseButton-primary"] {
        background-color: #6c5ce7 !important;
        background: linear-gradient(180deg, #c9a962 0%, #a8863a 100%) !important;
        color: #ffffff !important;
        border: 1px solid #5b4cdb !important;
        box-shadow: 0 2px 12px rgba(108, 92, 231, 0.32) !important;
    }
    section.main button[kind="primary"]:hover,
    section.main button[kind="primaryFormSubmit"]:hover,
    section.main [data-testid="stFormSubmitButton"] button:hover,
    section.main .stButton > button[kind="primary"]:hover {
        background-color: #5b4cdb !important;
        background: linear-gradient(180deg, #6c5ce7 0%, #5b4cdb 100%) !important;
        border-color: #4a3ec9 !important;
        color: #ffffff !important;
    }
    section.main button[kind="primary"]:active,
    section.main button[kind="primaryFormSubmit"]:active,
    section.main [data-testid="stFormSubmitButton"] button:active {
        background-color: #4a3ec9 !important;
        border-color: #3d32b8 !important;
    }
    /* 가입 제출 — 크기·패딩 (signup-form-wrap은 DOM 형제라 전역 규칙 사용) */
    section.main form[data-testid="stForm"] [data-testid="stFormSubmitButton"] button,
    section.main [data-testid="stFormSubmitButton"] button {
        font-size: clamp(0.95rem, 3.2vw, 1.1rem) !important;
        font-weight: 700 !important;
        min-height: clamp(3rem, 10vw, 3.5rem) !important;
        padding: clamp(0.85rem, 3vw, 1.1rem) clamp(1rem, 4vw, 1.5rem) !important;
        border-radius: clamp(12px, 3vw, 16px) !important;
    }
    /* 네비 secondary — 회색 톤 (빨간 기본색 방지) */
    section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type button[kind="secondary"],
    section.main button[kind="secondary"] {
        background-color: rgba(255, 252, 248, 0.9) !important;
        background: rgba(255, 252, 248, 0.92) !important;
        color: #5c5048 !important;
        border: 1px solid rgba(108, 92, 231, 0.25) !important;
    }
    section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type button[kind="secondary"]:hover,
    section.main button[kind="secondary"]:hover {
        background-color: #f0ebff !important;
        border-color: #6c5ce7 !important;
        color: #5b4cdb !important;
    }
    /* 하단 채팅 입력 — 상단 메뉴와 겹치지 않음 */
    [data-testid="stBottomBlockContainer"] {
        background: rgba(255, 252, 248, 0.98) !important;
        border-top: 1px solid rgba(120, 100, 80, 0.12);
        padding-bottom: max(0.5rem, env(safe-area-inset-bottom)) !important;
        z-index: 999 !important;
    }
    section.main .block-container {
        padding-bottom: 1rem !important;
    }
    div[data-testid="stVerticalBlock"]:has(.chat-toolbar-marker) {
        margin-bottom: 0.75rem;
    }
    div[data-testid="stVerticalBlock"]:has(.chat-toolbar-lang-marker) label {
        font-size: 0.78rem !important;
        color: #7a6e62 !important;
    }
    div[data-testid="stVerticalBlock"]:has(.intro-foot-marker) {
        padding: 0.75rem 1rem 1.5rem;
        max-width: 900px;
        margin: 0 auto;
    }
    /* 모바일 — 상단 큼직한 버튼 + 본문·채팅 여백 */
    /* 하단 문의 바 — 앵커 직후 버튼 블록 고정 */
    .inquiry-fab-anchor.fab-above-chat ~ div[data-testid="stElementContainer"] {
        bottom: calc(5.25rem + env(safe-area-inset-bottom, 0px)) !important;
    }
    .inquiry-fab-anchor.fab-low ~ div[data-testid="stElementContainer"] {
        bottom: calc(1.15rem + env(safe-area-inset-bottom, 0px)) !important;
    }
    .inquiry-fab-anchor ~ div[data-testid="stElementContainer"] {
        position: fixed !important;
        left: 50% !important;
        right: auto !important;
        transform: translateX(-50%) !important;
        z-index: 998 !important;
        width: min(92vw, 22rem) !important;
        max-width: 22rem !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .inquiry-fab-anchor ~ div[data-testid="stElementContainer"] button {
        width: 100% !important;
        min-height: 2.75rem !important;
        border-radius: 999px !important;
        background: linear-gradient(145deg, #8b7df5 0%, #6c5ce7 55%, #5b4cdb 100%) !important;
        color: #fff !important;
        border: 2px solid rgba(255, 255, 255, 0.45) !important;
        box-shadow: 0 6px 22px rgba(108, 92, 231, 0.4) !important;
        font-size: clamp(0.82rem, 3.2vw, 0.95rem) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        white-space: nowrap !important;
    }
    /* 데스크톱 — 모바일 전용 입력은 서버 UA로만 그림(:has 숨김은 대화 패널 오동작 유발) */
    @media (min-width: 601px) {
        [data-testid="stBottomBlockContainer"] {
            display: none !important;
        }
        div[data-testid="stVerticalBlock"]:has(.unified-chat-panel-marker) {
            min-height: 10rem !important;
        }
        div[data-testid="stVerticalBlock"]:has(.desktop-chat-composer-marker) {
            margin-top: 0.35rem !important;
            padding-top: 0.4rem !important;
            border-top: 1px solid rgba(120, 100, 80, 0.12) !important;
        }
        div[data-testid="column"]:has(.desktop-chat-send-marker) button {
            min-height: 2.85rem !important;
            width: 100% !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
        }
        div[data-testid="column"]:has(.desktop-chat-send-marker) {
            display: flex !important;
            align-items: flex-end !important;
        }
        button[data-testid="baseButton-secondary"][aria-label*="문의"],
        button[data-testid="baseButton-primary"][aria-label*="문의"] {
            font-size: 0.82rem !important;
        }
    }
    .inquiry-page-mail {
        margin-bottom: 1rem;
    }
    /* 대화 + 입력을 한 카드로 (카톡/문자 느낌) */
    div[data-testid="stVerticalBlock"]:has(.unified-chat-panel-marker) {
        background: rgba(255, 252, 248, 0.97) !important;
        border: 1px solid rgba(140, 120, 100, 0.2) !important;
        border-radius: 14px !important;
        padding: 0.4rem 0.45rem 0.45rem !important;
        margin-bottom: 0.35rem !important;
        box-shadow: 0 2px 14px rgba(90, 70, 50, 0.06) !important;
    }
    div[data-testid="stVerticalBlock"]:has(.unified-chat-panel-marker) > div[data-testid="stVerticalBlock"] {
        gap: 0.2rem !important;
    }
    @media (max-width: 600px) {
        /* 대화 카드·메시지 영역 높이 제한 없음 — 52vh 캡은 화면이 반으로 줄어드는 원인이었음 */
        div[data-testid="stVerticalBlock"]:has(.unified-chat-panel-marker) {
            max-height: none !important;
            overflow: visible !important;
        }
        div[data-testid="stVerticalBlock"]:has(.chat-messages-scroll-marker) {
            max-height: none !important;
            overflow: visible !important;
            min-height: 0 !important;
        }
        section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type {
            position: sticky !important;
            top: 0 !important;
            padding: 0.45rem 0.35rem 0.55rem !important;
        }
        section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type [data-testid="column"]:first-child {
            display: none !important;
        }
        section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type [data-testid="column"]:nth-child(2) {
            display: none !important;
        }
        /* 모바일: 고정 문의 버튼·네이티브 chat_input(전송·아바타 겹침) 숨김 */
        .inquiry-fab-anchor.fab-above-chat ~ div[data-testid="stElementContainer"] {
            display: none !important;
        }
        [data-testid="stBottomBlockContainer"] {
            display: none !important;
        }
        div[data-testid="stVerticalBlock"]:has(.mobile-chat-composer-marker) {
            position: sticky !important;
            bottom: 0 !important;
            z-index: 1000 !important;
            background: rgba(255, 252, 248, 0.98) !important;
            border-top: 1px solid rgba(120, 100, 80, 0.15) !important;
            padding: 0.35rem 0.35rem calc(0.65rem + env(safe-area-inset-bottom, 0px)) !important;
            margin: -0.15rem -0.35rem 0 !important;
            box-shadow: 0 -4px 18px rgba(90, 70, 50, 0.08) !important;
        }
        div[data-testid="column"]:has(.mobile-chat-send-marker) button {
            min-height: 3.1rem !important;
            width: 100% !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
        }
        div[data-testid="column"]:has(.mobile-chat-send-marker) {
            display: flex !important;
            align-items: flex-end !important;
        }
        div[data-testid="stVerticalBlock"]:has(.mobile-chat-composer-marker) [data-testid="stExpander"] {
            margin-bottom: 0.25rem !important;
            border: none !important;
        }
        div[data-testid="stVerticalBlock"]:has(.mobile-chat-composer-marker) [data-testid="stExpander"] summary {
            font-size: 0.86rem !important;
            padding: 0.4rem 0.45rem !important;
            min-height: 2.4rem !important;
        }
        div[data-testid="stVerticalBlock"]:has(.mobile-chat-composer-marker) [data-testid="stFileUploader"] {
            padding: 0.15rem 0 !important;
        }
        div[data-testid="stVerticalBlock"]:has(.mobile-chat-composer-marker) [data-testid="stFileUploader"] small {
            font-size: 0.72rem !important;
        }
        div[data-testid="stVerticalBlock"]:has(.mobile-chat-composer-marker) textarea {
            min-height: 4.25rem !important;
            font-size: 1rem !important;
            line-height: 1.45 !important;
        }
        div[data-testid="column"]:has(.mobile-chat-send-marker) button {
            min-height: 2.85rem !important;
            padding: 0.55rem 0.35rem !important;
        }
        section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type button {
            font-size: clamp(0.88rem, 3.8vw, 1.05rem) !important;
            min-height: clamp(3rem, 11vw, 3.4rem) !important;
            padding: clamp(0.65rem, 2.5vw, 0.9rem) 0.5rem !important;
        }
        div[data-testid="stVerticalBlock"]:has(.app-content-pad-marker),
        div[data-testid="stVerticalBlock"]:has(.chat-content-pad-marker) {
            padding-left: 0.4rem !important;
            padding-right: 0.4rem !important;
            max-width: 100% !important;
        }
        section.main .block-container {
            padding-bottom: 0.5rem !important;
        }
        [data-testid="stBottomBlockContainer"] {
            padding-left: 0.25rem !important;
            padding-right: 0.25rem !important;
            padding-bottom: max(0.65rem, env(safe-area-inset-bottom)) !important;
        }
        section.main [data-testid="stFormSubmitButton"] button {
            min-height: 3.35rem !important;
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
    }
    .status-card {
        background: rgba(255, 252, 248, 0.85);
        border: 1px solid rgba(140, 120, 100, 0.2);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
        font-size: 0.88rem;
    }
    .status-ok { color: #5a7a6a !important; font-weight: 600; }
    .status-fail { color: #a86a5a !important; font-weight: 600; }
    .gentle-record {
        text-align: center;
        padding: 1.25rem 1rem;
        background: linear-gradient(135deg, #fff9f2 0%, #f0ebe3 100%);
        border: 1px solid rgba(160, 140, 110, 0.25);
        border-radius: 14px;
        font-size: 1.05rem;
        color: #5c5048;
        line-height: 1.6;
        margin: 0.5rem 0 1rem 0;
    }
    .phase-badge {
        display: inline-block;
        background: rgba(180, 150, 110, 0.2);
        color: #6b5a48;
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    .hero-header {
        background: linear-gradient(135deg, #fffcf8 0%, #f5efe6 100%);
        border: 1px solid rgba(140, 120, 100, 0.18);
        border-radius: 16px;
        padding: 1.5rem 1.75rem 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 24px rgba(90, 70, 50, 0.08);
    }
    .hero-eyebrow {
        font-size: 0.8rem;
        letter-spacing: 0.12em;
        color: #9a8a78;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .hero-title {
        font-size: 1.65rem;
        font-weight: 700;
        color: #4a4038;
        margin: 0 0 0.5rem 0;
        line-height: 1.35;
    }
    .hero-salon-module {
        font-size: 1.02rem;
        font-weight: 600;
        color: #5c5348;
        margin: 0 0 0.45rem 0;
        letter-spacing: -0.01em;
    }
    .hero-desc { color: #6b5f55; font-size: 0.96rem; line-height: 1.65; margin: 0; }
    .hub-slogan-info {
        background: linear-gradient(135deg, rgba(108, 92, 231, 0.09) 0%, rgba(255, 252, 248, 0.95) 100%);
        border: 1px solid rgba(108, 92, 231, 0.22);
        border-left: 4px solid #6c5ce7;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.75rem 0 1rem 0;
        color: #5c5048;
        font-size: 0.95rem;
        line-height: 1.7;
        box-shadow: 0 2px 12px rgba(108, 92, 231, 0.08);
    }
    .hub-slogan-info .beta-emphasis {
        display: inline-block;
        font-weight: 700;
        color: #5b4cdb;
        background: rgba(108, 92, 231, 0.12);
        padding: 0.1rem 0.45rem;
        border-radius: 6px;
        letter-spacing: -0.02em;
    }
    .profile-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1rem;
        align-items: stretch;
    }
    .profile-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.85rem 0.5rem 0.6rem;
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(140, 120, 100, 0.2);
        border-radius: 12px;
        box-shadow: 0 1px 6px rgba(90, 70, 50, 0.07);
        min-height: 2.65rem;
        line-height: 1.25;
        box-sizing: border-box;
    }
    .profile-pill--accent {
        border-color: rgba(108, 92, 231, 0.32);
        background: linear-gradient(135deg, #f6f3ff 0%, #fffcf8 100%);
    }
    .profile-pill-icon {
        font-size: 1.2rem;
        line-height: 1;
        flex-shrink: 0;
    }
    .profile-pill-body {
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 0.12rem;
        min-width: 0;
    }
    .profile-pill-label {
        font-size: 0.62rem;
        letter-spacing: 0.08em;
        color: #9a8a78;
        font-weight: 600;
        text-transform: uppercase;
    }
    .profile-pill-value {
        font-size: 0.9rem;
        font-weight: 600;
        color: #4a4038;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: min(28vw, 9rem);
    }
    @media (min-width: 480px) {
        .profile-pill-value { max-width: 11rem; }
    }
    .onboarding-card, .consent-box {
        background: #fffcf8;
        border: 1px solid rgba(140, 120, 100, 0.2);
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    .consent-box { border-left: 4px solid #b8a088; }
    .dlinso-onboarding-module-hint {
        text-align: center;
        color: #5c5048;
        font-size: 0.95rem;
        margin: 0 0 0.75rem 0;
        letter-spacing: 0.02em;
    }
    .opening-guide {
        background: #fff9f4;
        border: 1px dashed rgba(160, 140, 110, 0.4);
        border-radius: 12px;
        padding: 1.25rem 1.1rem;
        color: #5c5048;
        text-align: left;
        line-height: 1.75;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    @media (max-width: 768px) {
        .opening-guide {
            font-size: 0.92rem;
            padding: 1rem 0.95rem;
        }
        div[data-testid="stVerticalBlock"]:has(.mobile-chat-composer-marker) textarea {
            scroll-margin-bottom: 6rem;
        }
    }
    .life-summary-box {
        background: linear-gradient(160deg, #fffef9 0%, #f5ebe0 100%);
        border: 1px solid #c9b8a0;
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        margin: 1rem 0;
        color: #4a4038;
        line-height: 1.85;
    }
    .preview-banner {
        background: #e8dfd0;
        color: #5c5048;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-bottom: 0.75rem;
        text-align: center;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #fffcf8;
        border-color: rgba(140, 120, 100, 0.2) !important;
        border-radius: 16px !important;
    }
    .diet-banner {
        background: #f5efe6;
        border-left: 3px solid #b8a088;
        padding: 0.45rem 0.75rem;
        border-radius: 6px;
        font-size: 0.82rem;
        color: #6b5f55;
        margin-bottom: 0.75rem;
    }
    .input-hint {
        background: #fff9f2;
        border: 1px solid #d4c4b0;
        border-radius: 10px;
        padding: 0.65rem 1rem;
        font-size: 0.88rem;
        color: #6b5a48;
        margin: 0.75rem 0 0.25rem 0;
    }
    .lab-footer-wrap {
        margin-top: 0.35rem;
        padding: 0 0.25rem 0.85rem;
        text-align: center;
    }
    .lab-footer-panel {
        background: linear-gradient(165deg, #f4faf6 0%, #e8f0eb 48%, #eef2ee 100%);
        border: 1px solid rgba(90, 130, 105, 0.2);
        border-radius: 12px;
        padding: 0.5rem 0.85rem 0.55rem;
        max-width: 42rem;
        margin: 0 auto;
        box-shadow: 0 1px 8px rgba(60, 90, 70, 0.06);
    }
    .lab-footer-panel p {
        margin: 0;
        padding: 0;
    }
    .lab-footer-primary {
        font-size: 0.8rem;
        font-weight: 600;
        color: #3d5244;
        line-height: 1.25;
        letter-spacing: 0.02em;
    }
    .lab-footer-secondary {
        font-size: 0.72rem;
        font-weight: 500;
        color: #5a6d62;
        margin-top: 0.12rem;
        line-height: 1.2;
        font-style: italic;
        letter-spacing: 0.01em;
    }
    .lab-footer-divider {
        border: none;
        border-top: 1px solid rgba(90, 130, 105, 0.14);
        margin: 0.32rem 0 0.28rem;
        height: 0;
    }
    .lab-footer-meta {
        font-size: 0.65rem;
        color: #7a8f84;
        line-height: 1.2;
        letter-spacing: 0.02em;
    }
    .lab-footer-powered {
        font-size: 0.62rem;
        color: #8a9d93;
        margin-top: 0.1rem;
        line-height: 1.15;
    }
    .hub-beta-row {
        margin: 0.35rem 0 0.5rem;
    }
    .hub-page-title {
        margin: 0 0 0.35rem;
        font-size: 1.35rem;
        font-weight: 600;
        color: #4a3f6b;
    }
    .dlinso-intro-headline .beta-badge {
        margin-left: 0.5rem;
        vertical-align: 0.2em;
    }
    .beta-badge {
        display: inline-block;
        vertical-align: middle;
        margin-left: 0.45rem;
        padding: 0.12rem 0.55rem;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6b5a48;
        background: linear-gradient(135deg, #f0ebe3 0%, #e0d6c8 100%);
        border: 1px solid rgba(140, 120, 100, 0.35);
        border-radius: 999px;
    }
    .research-reply-box {
        background: linear-gradient(135deg, #f4faf6 0%, #e8f2ec 100%);
        border: 1px solid #8ab89a;
        border-left: 4px solid #5a9a6e;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        margin: 0.75rem 0 1rem 0;
        color: #3d5244;
        line-height: 1.7;
        box-shadow: 0 2px 12px rgba(90, 130, 100, 0.12);
    }
    .research-reply-box h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        color: #2d5a3d;
    }
    @keyframes midpoint-reward-pop {
        0% {
            opacity: 0;
            transform: translateY(10px) scale(0.94);
        }
        65% {
            transform: translateY(-3px) scale(1.02);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    .midpoint-encourage-msg {
        font-size: 0.86rem;
        color: #5c5048;
        line-height: 1.65;
        padding: 0.65rem 0.85rem;
        margin: 0.35rem 0 0.5rem;
        background: linear-gradient(135deg, #fff9f2 0%, #f5efe6 100%);
        border: 1px dashed rgba(160, 140, 110, 0.45);
        border-radius: 10px;
        text-align: center;
    }
    .isolation-recovery-panel {
        padding: 0.55rem 0.75rem;
        margin: 0.25rem 0 0.45rem;
        background: linear-gradient(135deg, #f4faf5 0%, #e8f2ea 100%);
        border: 1px solid rgba(76, 120, 90, 0.22);
        border-radius: 10px;
    }
    .isolation-recovery-title {
        font-size: 0.88rem;
        font-weight: 600;
        color: #2d4a35;
        margin: 0 0 0.25rem;
    }
    .isolation-recovery-meta {
        font-size: 0.78rem;
        color: #5a6b5e;
        margin: 0;
    }
    .isolation-signal-quote {
        font-size: 0.82rem;
        color: #3d5244;
        font-style: italic;
        margin: 0.35rem 0 0;
    }
    div[data-testid="stVerticalBlock"]:has(.midpoint-section-marker) {
        margin-bottom: 0.5rem !important;
        padding-bottom: 0.35rem !important;
        border-bottom: 1px solid rgba(157, 142, 207, 0.12);
    }
    div[data-testid="stVerticalBlock"]:has(.midpoint-actions-below-chat-marker) {
        margin-top: 0.65rem !important;
        padding-top: 0.5rem !important;
        border-top: 1px solid rgba(157, 142, 207, 0.14);
    }
    div[data-testid="stVerticalBlock"]:has(.midpoint-btn-marker) {
        margin-top: 0.35rem !important;
    }
    div[data-testid="stVerticalBlock"]:has(.midpoint-btn-reveal-marker) {
        margin-top: 0.35rem !important;
        animation: midpoint-reward-pop 0.7s cubic-bezier(0.34, 1.35, 0.64, 1) both;
    }
    div[data-testid="stVerticalBlock"]:has(.midpoint-btn-marker) button,
    div[data-testid="stVerticalBlock"]:has(.midpoint-btn-reveal-marker) button {
        width: 100% !important;
        background: linear-gradient(180deg, #1e3a8a 0%, #0f172a 100%) !important;
        color: #ffffff !important;
        border: 2px solid #d4af37 !important;
        font-weight: 700 !important;
        min-height: 2.85rem !important;
        border-radius: 10px !important;
        letter-spacing: -0.02em !important;
        box-shadow:
            0 0 0 1px rgba(212, 175, 55, 0.35),
            0 6px 22px rgba(212, 175, 55, 0.28),
            0 4px 14px rgba(15, 23, 42, 0.32) !important;
    }
    .midpoint-essay-block {
        margin: 0.85rem 0 1.15rem;
        padding: 1rem 1.15rem 1.05rem;
        border-radius: 12px;
        background: linear-gradient(
            165deg,
            rgba(255, 252, 248, 0.98) 0%,
            rgba(246, 243, 255, 0.92) 100%
        );
        border: 1px solid rgba(157, 142, 207, 0.22);
        box-shadow: 0 2px 14px rgba(90, 70, 50, 0.06);
    }
    .midpoint-essay-section-title {
        margin: 0 0 0.7rem;
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: #4a3f6b;
    }
    .midpoint-essay-body {
        margin: 0;
    }
    .midpoint-essay-p {
        margin: 0 0 0.85rem;
        font-size: 0.94rem;
        line-height: 1.78;
        color: #4a4038;
        letter-spacing: -0.01em;
    }
    .midpoint-essay-p:last-child {
        margin-bottom: 0;
    }
    .midpoint-essay-preface {
        margin: 0 0 1rem;
        font-size: 0.96rem;
        line-height: 1.75;
        color: #5c5048;
    }
    div[data-testid="stVerticalBlock"]:has(.midpoint-btn-marker) button:hover,
    div[data-testid="stVerticalBlock"]:has(.midpoint-btn-reveal-marker) button:hover {
        background: linear-gradient(180deg, #1d4ed8 0%, #172554 100%) !important;
        color: #ffffff !important;
        border-color: #f0d78c !important;
        box-shadow:
            0 0 0 2px rgba(240, 215, 140, 0.45),
            0 8px 26px rgba(212, 175, 55, 0.35) !important;
    }
    .char-counter-hint {
        font-size: 0.78rem;
        color: #7a6e62;
        margin-top: 0.15rem;
        line-height: 1.4;
    }
    .narrative-asset-progress-marker + div[data-testid="stMarkdown"] p {
        font-size: 0.88rem;
        font-weight: 600;
        color: #4a4038;
        margin-bottom: 0.2rem;
    }
    .dlinso-intro-panel {
        text-align: center;
        padding: clamp(1.5rem, 5vh, 2.5rem) clamp(1.25rem, 4vw, 2rem);
        margin: 0 auto 0.75rem;
        max-width: min(42rem, 96vw);
        background: radial-gradient(
            ellipse 90% 70% at 50% 28%,
            #2a2438 0%,
            #1a1625 88%
        );
        border-radius: 18px;
        border: 1px solid rgba(157, 142, 207, 0.18);
        box-shadow: 0 12px 40px rgba(26, 22, 37, 0.35);
    }
    .dlinso-intro-headline {
        color: #ece6f8;
        font-size: clamp(1.2rem, 4.2vw, 1.55rem);
        font-weight: 600;
        letter-spacing: -0.02em;
        line-height: 1.4;
        margin: 0 0 1.1rem;
        text-wrap: balance;
    }
    .dlinso-intro-headline-line {
        display: block;
        white-space: nowrap;
    }
    @media (max-width: 380px) {
        .dlinso-intro-headline-line {
            white-space: normal;
        }
    }
    .dlinso-intro-headline-brand {
        display: block;
        margin-top: 0.5rem;
        font-size: clamp(0.95rem, 3vw, 1.1rem);
        font-weight: 500;
        letter-spacing: 0.12em;
        color: #9d8ecf;
    }
    .dlinso-intro-sub {
        color: #b8b0cc;
        font-size: clamp(0.88rem, 2.8vw, 0.98rem);
        font-weight: 300;
        line-height: 1.7;
        margin: 0 0 1.1rem;
        text-align: center;
        text-wrap: pretty;
        max-width: 34rem;
        margin-left: auto;
        margin-right: auto;
    }
    .dlinso-intro-sub-line {
        display: block;
        margin-top: 0.35rem;
    }
    .dlinso-intro-guide {
        text-align: left;
        padding: 0.85rem 1rem;
        margin: 0 auto 1rem;
        max-width: 34rem;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(157, 142, 207, 0.22);
    }
    .dlinso-intro-guide-label {
        color: #9d8ecf;
        font-size: 0.72rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin: 0 0 0.45rem;
    }
    .dlinso-intro-guide-body {
        color: #c9c0dc;
        font-size: clamp(0.84rem, 2.6vw, 0.92rem);
        line-height: 1.65;
        margin: 0;
    }
    .dlinso-intro-whisper {
        color: #7d758f;
        font-size: 0.82rem;
        letter-spacing: 0.12em;
        margin: 0;
        padding-top: 0.75rem;
        border-top: 1px solid rgba(157, 142, 207, 0.2);
    }
    .hub-slogan-hero {
        text-align: center;
        max-width: min(42rem, 96vw);
        margin: 0 auto 1rem;
        padding: 0.25rem 0.5rem 0.75rem;
    }
    .hub-slogan-hero .dlinso-intro-headline {
        color: #3d3548;
    }
    .hub-slogan-hero .dlinso-intro-headline-brand {
        color: #6c5ce7;
    }
    .hub-slogan-hero .dlinso-intro-sub {
        color: #5c5048;
    }
    .intro-footer-bridge {
        margin-top: 0.25rem;
        padding-top: 0;
    }
    .intro-footer-bridge .lab-footer-panel {
        background: linear-gradient(165deg, #f0f5f2 0%, #e4ece7 100%);
        border-color: rgba(90, 130, 105, 0.25);
    }
    .dlinso-section-label {
        color: #c4b8e8;
        font-size: 0.78rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin: 1.25rem 0 0.5rem;
        font-weight: 600;
    }
    .dlinso-mode-chip {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
        padding: 0.55rem 0.45rem;
        border-radius: 10px;
        border: 1px solid rgba(157, 142, 207, 0.25);
        min-height: 3.2rem;
    }
    .dlinso-mode-chip--on {
        background: rgba(120, 180, 140, 0.12);
        border-color: rgba(120, 180, 140, 0.45);
    }
    .dlinso-mode-chip--off {
        opacity: 0.55;
    }
    .dlinso-mode-label {
        color: #ebe6f8;
        font-size: 0.72rem;
        font-weight: 600;
        line-height: 1.25;
    }
    .dlinso-mode-tag {
        color: #8fd4a8;
        font-size: 0.62rem;
        letter-spacing: 0.06em;
    }
    .dlinso-mode-chip--off .dlinso-mode-tag {
        color: #9a92b0;
    }
    .dlinso-mode-desc {
        display: none;
    }
    @media (min-width: 720px) {
        .dlinso-mode-desc {
            display: block;
            color: #8a829c;
            font-size: 0.65rem;
            line-height: 1.35;
        }
    }
    .dlinso-current-age-context {
        color: #9a92b0;
        font-size: 0.82rem;
        line-height: 1.55;
        margin: 0 0 0.75rem;
        padding: 0.5rem 0.65rem;
        border-radius: 8px;
        background: rgba(157, 142, 207, 0.08);
        border: 1px solid rgba(157, 142, 207, 0.15);
    }
</style>
"""

INQUIRY_TYPE_OPTIONS: list[tuple[str, str]] = [
    ("general", "inquiry_type_general"),
    ("research_collab", "inquiry_type_research"),
    ("interview", "inquiry_type_interview"),
]

def render_lab_footer(*, intro_bridge: bool = False) -> None:
    """온보딩·대화·소개 화면 공통 하단 연구소 배너 (한/영 병기)."""
    wrap_cls = "lab-footer-wrap intro-footer-bridge" if intro_bridge else "lab-footer-wrap"
    st.divider()
    st.markdown(
        f"""
        <div class="{wrap_cls}">
            <div class="lab-footer-panel">
                <p class="lab-footer-primary">{FOOTER_BANNER["primary"]}</p>
                <p class="lab-footer-secondary">{FOOTER_BANNER["secondary"]}</p>
                <hr class="lab-footer-divider" />
                <p class="lab-footer-meta">{FOOTER_BANNER["copyright"]}</p>
                <p class="lab-footer-powered">{FOOTER_BANNER["powered"]}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _simple_bold_html(text: str) -> str:
    """i18n **bold** → safe <strong> (intro 안내 박스용)."""
    out: list[str] = []
    rest = text or ""
    while "**" in rest:
        before, _, rest = rest.partition("**")
        if before:
            out.append(html.escape(before))
        if "**" not in rest:
            out.append(html.escape("**" + rest))
            break
        bold, _, rest = rest.partition("**")
        out.append(f"<strong>{html.escape(bold)}</strong>")
    if rest:
        out.append(html.escape(rest))
    return "".join(out)


def _intro_headline_html() -> str:
    line1 = t("intro_headline_line1").strip()
    line2 = t("intro_headline_line2").strip()
    if line1 and line2 and line1 != "intro_headline_line1":
        return (
            '<h2 class="dlinso-intro-headline">'
            f'<span class="dlinso-intro-headline-line">{html.escape(line1)}</span>'
            f'<span class="dlinso-intro-headline-line">{html.escape(line2)}</span>'
            f'<span class="dlinso-intro-headline-brand">{html.escape(t("app_title"))}</span>'
            "</h2>"
        )
    return (
        f'<h2 class="dlinso-intro-headline">{html.escape(t("intro_headline"))}</h2>'
    )


def _intro_sub_html() -> str:
    sub1 = t("intro_sub").strip()
    sub2 = t("intro_sub_line2").strip()
    if sub2 and sub2 != "intro_sub_line2":
        return (
            '<p class="dlinso-intro-sub">'
            f"{html.escape(sub1)}"
            f'<span class="dlinso-intro-sub-line">{html.escape(sub2)}</span>'
            "</p>"
        )
    return f'<p class="dlinso-intro-sub">{html.escape(sub1)}</p>'


def render_intro() -> None:
    """홈(소개) — 소개 문구, 브랜치 로드맵."""
    _html_layout_marker("dlinso-intro-marker")
    guide_inner = _simple_bold_html(t("intro_guide_body"))
    panel = (
        '<div class="dlinso-intro-panel" role="region" aria-label="dlinso">'
        f"{_intro_headline_html()}"
        f"{_intro_sub_html()}"
        '<div class="dlinso-intro-guide">'
        f'<p class="dlinso-intro-guide-label">{html.escape(t("intro_guide_label"))}</p>'
        f'<p class="dlinso-intro-guide-body">{guide_inner}</p>'
        "</div>"
        f'<p class="dlinso-intro-whisper">{html.escape(t("intro_whisper"))}</p>'
        "</div>"
    )
    _render_html_fragment(panel)
    render_mode_roadmap(compact=True)


def _apply_view_nav(target: str) -> None:
    if target != VIEW_INQUIRY:
        st.session_state.inquiry_return_view = st.session_state.get(
            "current_view", VIEW_APP
        )
    st.session_state.current_view = target
    st.rerun()


def render_hybrid_nav(*, include_lang: bool = True) -> None:
    """하이브리드 네비 — 안내 | 나의 이야기 | 문의하기 (+ 언어·초기화)."""
    current = st.session_state.get("current_view", VIEW_APP)
    show_reset = is_ready_for_chat() or st.session_state.get("onboarding_complete")
    on_brand_home = current in (VIEW_HOME, VIEW_INTRO) and st.session_state.get(
        "home_intro_revealed", False
    )

    ratios: list[float] = [1.0, 0.5]
    if on_brand_home:
        ratios.append(0.78)
    ratios.extend([0.95, 1.1, 0.82])
    if show_reset:
        ratios.append(0.38)
    if include_lang:
        ratios.append(0.62)

    cols = st.columns(ratios, gap="small")
    idx = 0

    with cols[idx]:
        st.markdown(
            f'<span class="hybrid-brand">🌿 dlinso</span>{_beta_badge_html()}',
            unsafe_allow_html=True,
        )
    idx += 1

    with cols[idx]:
        st.empty()
    idx += 1

    if on_brand_home and idx < len(cols):
        with cols[idx]:
            if st.button(
                t("nav_about"),
                use_container_width=True,
                type="secondary",
                key="hybrid_nav_about",
            ):
                open_dlinso_about()
        idx += 1

    with cols[idx]:
        if st.button(
            t("nav_home"),
            use_container_width=True,
            type="primary" if current in (VIEW_HOME, VIEW_INTRO) else "secondary",
            key="hybrid_nav_home",
        ):
            _apply_view_nav(VIEW_HOME)
    idx += 1

    with cols[idx]:
        if st.button(
            t("nav_consult"),
            use_container_width=True,
            type="primary" if current == VIEW_APP else "secondary",
            key="hybrid_nav_story",
        ):
            _apply_view_nav(VIEW_APP)
    idx += 1

    with cols[idx]:
        if st.button(
            t("nav_inquiry"),
            use_container_width=True,
            type="primary" if current == VIEW_INQUIRY else "secondary",
            key="hybrid_nav_inquiry",
        ):
            _apply_view_nav(VIEW_INQUIRY)
    idx += 1

    if show_reset:
        with cols[idx]:
            if st.button(
                "🔄",
                use_container_width=True,
                help=t("reset_session"),
                key="hybrid_nav_reset",
            ):
                reset_user_session()
                st.rerun()
        idx += 1

    if include_lang:
        with cols[idx]:
            render_language_selector(key="nav_lang", compact=True)

    render_dlinso_about_expander_if_needed()


def render_inquiry_fab(*, above_chat_input: bool = True) -> None:
    """하단 문의 바 — 모든 화면에서 원클릭 접근."""
    if st.session_state.get("current_view") == VIEW_INQUIRY:
        return
    pos_cls = "fab-above-chat" if above_chat_input else "fab-low"
    st.markdown(
        f'<div class="inquiry-fab-anchor {pos_cls}" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    if st.button(
        t("inquiry_fab_label"),
        key="inquiry_fab",
        use_container_width=True,
    ):
        st.session_state.inquiry_return_view = st.session_state.get(
            "current_view", VIEW_APP
        )
        st.session_state.current_view = VIEW_INQUIRY
        st.rerun()


def _db_save_warning(err: str) -> str:
    return f"저장 실패: {err}"


def _db_error_message(db: DatabaseManager) -> str:
    lines = ["로컬 데이터베이스에 연결할 수 없습니다."]
    if db.error_message:
        lines.append(f"`{db.error_message}`")
    lines.append(f"DB 경로: `{db.database_label()}`")
    lines.append("프로젝트 폴더에 쓰기 권한이 있는지 확인하세요.")
    return "\n\n".join(lines)


def render_db_status(db: DatabaseManager) -> None:
    if db.is_connected:
        st.caption(f"🟢 로컬 DB 연결됨 · `{db.database_label()}`")
        return
    with st.expander("⚠️ 데이터베이스 연결 안 됨", expanded=True):
        st.markdown(_db_error_message(db))


def render_inquiry_page(db: DatabaseManager) -> None:
    """문의하기 전용 — SQLite 기록 폼."""
    st.markdown(f"## {t('inquiry_page_title')}")
    st.caption(t("inquiry_page_intro"))
    render_researcher_inquiry(db)

    if st.button(t("inquiry_back"), use_container_width=True, key="inquiry_back_btn"):
        prev = st.session_state.get("inquiry_return_view", VIEW_APP)
        st.session_state.current_view = prev
        st.rerun()


render_sticky_top_nav = render_hybrid_nav


def _is_preview_mode() -> bool:
    from modules.home_registry import query_param_str

    return query_param_str("preview").lower() in ("1", "true", "yes")


def _apply_preview_session() -> None:
    st.session_state.consent_agreed = True
    st.session_state.onboarding_complete = True
    st.session_state.participant_id = "미리보기"
    st.session_state.gender = "기타"
    st.session_state.age_group = "30대"
    st.session_state.life_stage = "일·활동 중"
    st.session_state.password_hash = hash_password("preview")
    st.session_state.is_returning_user = False
    st.session_state.last_visit_topic = ""
    st.session_state.lang = "ko"
    st.session_state.preview_mode = True


def _init_session_state() -> None:
    defaults = {
        "messages": [],
        "context_summary": "",
        "interests": ["—", "—", "—"],
        "profile": default_profile(),
        "narrative_stage": "탐색",
        "life_context": "—",
        "diet_applied_count": 0,
        "consent_agreed": False,
        "onboarding_complete": False,
        "participant_id": "",
        "gender": "",
        "age_group": "",
        "life_stage": "",
        "password_hash": "",
        "is_returning_user": False,
        "last_visit_topic": "",
        "phase": PHASE_COLLECT,
        "active_giant": None,
        "current_concern": "",
        "positive_resources": [],
        "summoned_narrative": "",
        "life_summary": "",
        "conversation_closed": False,
        "preview_mode": False,
        "lang": "ko",
        "pending_admin_reply": "",
        "pending_admin_reply_type": "general",
        "narrative_themes": "",
        "metaphors": "",
        "turning_points": "",
        "app_mode": "lifespan",
        "selected_module_id": "",
        "home_intro_revealed": False,
        "current_view": VIEW_HOME,
        "pending_user_prompt": "",
        "pending_turn": None,
        "story_thread": "",
        "chat_composer_nonce": 0,
        "total_user_turns": 0,
        "extended_input_unlocked": False,
        "midpoint_analysis_count": 0,
        "last_midpoint_report": None,
        "narrative_precision": 50.0,
        "jaggedness_index": 0.0,
        "pending_midpoint_analysis": False,
        "learning_audience": "",
        "last_learning_report": None,
        "learning_report_count": 0,
        "pending_learning_report": False,
        "learning_signals": None,
        "isolation_signals": None,
        "last_isolation_asset": None,
        "isolation_asset_count": 0,
        "last_isolation_report": None,
        "isolation_report_count": 0,
        "pending_isolation_asset": False,
        "pending_isolation_report": False,
        "conversation_restored": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not int(st.session_state.get("total_user_turns", 0)):
        from hbridge_analysis import count_user_turns

        st.session_state.total_user_turns = count_user_turns(
            st.session_state.get("messages") or []
        )

    profile = st.session_state.get("profile")
    if not isinstance(profile, dict):
        st.session_state.profile = default_profile()
    else:
        sanitized = default_profile()
        for k in PROFILE_KEYS:
            try:
                sanitized[k] = float(profile.get(k, sanitized[k]))
            except (TypeError, ValueError):
                pass
        st.session_state.profile = sanitized

    # 미리보기는 URL ?preview=1 만으로는 가입 화면을 건너뛰지 않음 (동의·가입 유지)


def is_ready_for_chat() -> bool:
    if not st.session_state.get("onboarding_complete"):
        return False
    return bool(
        st.session_state.get("participant_id", "").strip()
        and st.session_state.get("password_hash")
        and st.session_state.get("gender")
        and st.session_state.get("age_group")
        and st.session_state.get("life_stage")
    )


def _activate_session(
    *,
    participant_id: str,
    password_hash_value: str,
    gender: str,
    age_group: str,
    life_stage: str,
    lang: str = "ko",
    is_returning: bool = False,
    recent_turns: list[dict[str, str]] | None = None,
    restored_messages: list[dict[str, Any]] | None = None,
    total_turn_count: int = 0,
    has_midpoint: bool = False,
    last_topic: str = "",
    admin_reply: str = "",
    admin_reply_type: str = "general",
) -> None:
    """로그인 성공 후 세션·대화 복원 (시트 누적 턴·중간 마음 지도 포함)."""
    from hbridge_analysis import count_user_turns

    st.session_state.participant_id = participant_id
    st.session_state.password_hash = password_hash_value
    st.session_state.gender = gender
    st.session_state.age_group = age_group
    st.session_state.life_stage = life_stage
    st.session_state.lang = lang
    st.session_state.consent_agreed = True
    st.session_state.is_returning_user = is_returning
    st.session_state.last_visit_topic = last_topic
    st.session_state.pending_admin_reply = admin_reply if is_returning else ""
    st.session_state.pending_admin_reply_type = (
        admin_reply_type if is_returning else "general"
    )

    if restored_messages is not None:
        st.session_state.messages = [dict(m) for m in restored_messages]
    else:
        st.session_state.messages = []
        st.session_state.pop("_chat_input_focused", None)
        for turn in recent_turns or []:
            st.session_state.messages.append(
                {"role": "user", "content": turn["user"], "display": turn["user"]}
            )
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": turn["assistant"],
                    "display": turn["assistant"],
                }
            )

    if has_midpoint:
        st.session_state.extended_input_unlocked = True
        st.session_state.midpoint_analysis_count = max(
            1, int(st.session_state.get("midpoint_analysis_count", 0))
        )
        for msg in reversed(st.session_state.messages):
            if not msg.get("midpoint"):
                continue
            parsed = parse_stored_midpoint_message(
                str(msg.get("content") or msg.get("display") or "")
            )
            if parsed:
                st.session_state.last_midpoint_report = parsed
            break

    st.session_state.total_user_turns = max(
        int(total_turn_count or 0),
        count_user_turns(st.session_state.messages),
    )

    if is_returning:
        greeting = build_returning_greeting(
            last_topic, participant_id, lang=lang
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": greeting, "display": greeting}
        )
        if restored_messages or recent_turns:
            st.session_state.conversation_restored = True

    st.session_state.onboarding_complete = True
    st.session_state.current_view = VIEW_APP


def show_admin_reply_banner() -> None:
    reply = st.session_state.pop("pending_admin_reply", "") or ""
    reply_type = st.session_state.pop("pending_admin_reply_type", "general") or "general"
    if not reply.strip():
        return
    if reply_type == "research_collab":
        title = t("admin_reply_title_research")
        safe = reply.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        st.markdown(
            f'<div class="research-reply-box">'
            f"<h4>{title}</h4><p>{safe}</p></div>",
            unsafe_allow_html=True,
        )
    elif reply_type == "interview":
        st.info(f"**{t('admin_reply_title_interview')}**\n\n{reply}")
    else:
        st.info(f"**{t('admin_reply_title')}**\n\n{reply}")


def render_researcher_inquiry(db: DatabaseManager) -> None:
    """연구자·일반 문의 — SQLite inquiries 테이블."""
    if not db.is_connected:
        st.warning(_db_error_message(db))
        return

    participant = (st.session_state.get("participant_id") or "").strip()
    if not participant:
        st.text_input(
            t("inquiry_guest_nick"),
            key="inquiry_guest_nick",
            placeholder=t("nickname"),
        )

    labels = [t(label_key) for _, label_key in INQUIRY_TYPE_OPTIONS]
    choice = st.selectbox(t("inquiry_type_label"), labels, key="inquiry_type_sel")
    type_map = {t(lk): tk for tk, lk in INQUIRY_TYPE_OPTIONS}
    inquiry_type = type_map.get(choice, "general")

    affiliation = ""
    contact = ""
    if inquiry_type in ("research_collab", "interview"):
        affiliation = st.text_input(
            t("researcher_affiliation"), key="inquiry_affiliation"
        )
        contact = st.text_input(t("researcher_contact"), key="inquiry_contact")

    inquiry = st.text_area(
        "inquiry_body",
        key="inquiry_text",
        placeholder=t("inquiry_placeholder"),
        height=80,
        label_visibility="collapsed",
    )
    if st.button(t("inquiry_send"), use_container_width=True, key="inquiry_send_btn"):
        if not inquiry.strip():
            st.warning(t("inquiry_empty"))
            return
        participant_id = (
            st.session_state.get("participant_id", "").strip()
            or str(st.session_state.get("inquiry_guest_nick", "")).strip()
        )
        if not participant_id:
            st.warning(t("err_nick"))
            return
        lang = get_lang()
        try:
            msg_ko = (
                inquiry.strip()
                if lang == "ko"
                else translate_to_korean(inquiry.strip(), lang)
            )
        except Exception:  # noqa: BLE001
            msg_ko = inquiry.strip()
        ok, err = db.log_inquiry(
            participant_id,
            inquiry.strip(),
            lang=lang,
            inquiry_type=inquiry_type,
            message_ko=msg_ko,
            researcher_affiliation=affiliation.strip(),
            researcher_contact=contact.strip(),
        )
        if ok:
            st.success(t("inquiry_ok"))
        elif err:
            st.warning(err)


def _status_label(ok: bool) -> str:
    return "연결됨" if ok else "연결 안 됨"


def _status_class(ok: bool) -> str:
    return "status-ok" if ok else "status-fail"


def _db_manager_mtime() -> float:
    path = APP_DIR / "database_manager.py"
    return path.stat().st_mtime if path.is_file() else 0.0


@st.cache_resource
def get_db_manager(
    _db_path: str,
    _manager_mtime: float,
    _cache_version: int,
) -> DatabaseManager:
    """database_manager.py 수정·DB 경로 변경 시 캐시 갱신."""
    return DatabaseManager()


@st.cache_resource
def get_isolation_db_manager(
    _db_path: str,
    _manager_mtime: float,
    _cache_version: int,
) -> IsolationDatabaseManager:
    """숲 모듈 — data/isolation.db (로컬·Cloud 공통, Cloud는 Supabase로 영속화 권장)."""
    return IsolationDatabaseManager()


def resolve_active_db() -> DatabaseManager | IsolationDatabaseManager:
    if _is_isolation_mode():
        return get_isolation_db_manager(
            str(get_isolation_database_path()),
            _isolation_db_manager_mtime(),
            DB_MANAGER_CACHE_VERSION,
        )
    return get_db_manager(
        str(get_database_path()),
        _db_manager_mtime(),
        DB_MANAGER_CACHE_VERSION,
    )


def _isolation_db_manager_mtime() -> float:
    path = APP_DIR / "isolation_database_manager.py"
    return path.stat().st_mtime if path.is_file() else 0.0


def nickname_exists(db: DatabaseManager, nickname: str) -> bool:
    return db.nickname_exists(nickname.strip())


def init_gemini() -> tuple[bool, str | None]:
    """
    대화 LLM 준비 — Upstage Solar(기본) 또는 Gemini.
    키: .env / Streamlit Secrets (UPSTAGE_API_KEY 또는 GEMINI_API_KEY).
    """
    if not is_llm_configured():
        return False, _llm_user_error(LLMNotConfiguredError("not configured"))
    provider = get_llm_provider()
    cache_key = f"llm_init_{provider}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    try:
        init_llm_client()
        result: tuple[bool, str | None] = (True, None)
    except Exception as exc:  # noqa: BLE001
        result = (False, _llm_user_error(exc))
    st.session_state[cache_key] = result
    return result


def _is_learning_mode() -> bool:
    return st.session_state.get("app_mode", MODE_LIFESPAN) == MODE_LEARNING


def _is_isolation_mode() -> bool:
    return st.session_state.get("app_mode", MODE_LIFESPAN) == MODE_ISOLATION


def _refresh_isolation_signals(*, force_llm: bool = False) -> dict[str, Any] | None:
    """대화 중 회복 신호 — 기본 휴리스틱(즉시), LLM은 4턴마다 또는 강제 시만."""
    if not _is_isolation_mode():
        return None
    turns = effective_user_turn_count()
    use_llm = force_llm or (turns >= 2 and turns % 4 == 0)
    try:
        signals = extract_isolation_signals(
            st.session_state.messages,
            lang=get_lang(),
            use_llm=use_llm,
        )
    except Exception:  # noqa: BLE001
        return st.session_state.get("isolation_signals")
    st.session_state.isolation_signals = signals
    return signals


def _refresh_learning_signals(*, force_llm: bool = False) -> dict[str, Any] | None:
    """대화 중 4대 이론 신호 — 턴마다 휴리스틱, 3턴마다 LLM 보강."""
    if not _is_learning_mode():
        return None
    turns = effective_user_turn_count()
    use_llm = force_llm or (turns >= 2 and turns % 3 == 0)
    try:
        signals = extract_learning_signals(
            st.session_state.messages,
            lang=get_lang(),
            use_llm=use_llm,
        )
    except Exception:  # noqa: BLE001
        return st.session_state.get("learning_signals")
    st.session_state.learning_signals = signals
    return signals


def resolve_companion_display() -> dict[str, str]:
    if _is_learning_mode():
        return get_learning_display(st.session_state.get("learning_audience", ""))
    if _is_isolation_mode():
        return get_isolation_display()
    return get_active_display(
        st.session_state.phase, st.session_state.active_giant
    )


def build_system_instruction() -> str:
    age = st.session_state.age_group or "30대"
    life_stage = st.session_state.life_stage or "일·활동 중"
    phase = st.session_state.phase
    summary = st.session_state.get("context_summary", "").strip()

    lang = get_lang()
    base = build_global_maieutic_system_instruction(lang)

    module_id = (st.session_state.get("selected_module_id") or "").strip()
    if module_id and get_landing_module(module_id):
        base += "\n\n" + build_mode_system_addon_for_module(
            module_id,
            phase,
            giant_key=st.session_state.active_giant,
            age_group=age,
            life_stage=life_stage,
            positive_resources=st.session_state.positive_resources,
            current_concern=st.session_state.current_concern,
            lang=lang,
            is_returning=st.session_state.get("is_returning_user", False),
            last_topic=st.session_state.get("last_visit_topic", ""),
            nickname=st.session_state.get("participant_id", ""),
            learning_audience=st.session_state.get("learning_audience", ""),
        )
    else:
        base += "\n\n" + build_mode_system_addon(
            st.session_state.get("app_mode", MODE_LIFESPAN),
            phase,
            giant_key=st.session_state.active_giant,
            age_group=age,
            life_stage=life_stage,
            positive_resources=st.session_state.positive_resources,
            current_concern=st.session_state.current_concern,
            lang=lang,
            is_returning=st.session_state.get("is_returning_user", False),
            last_topic=st.session_state.get("last_visit_topic", ""),
            nickname=st.session_state.get("participant_id", ""),
            learning_audience=st.session_state.get("learning_audience", ""),
        )

    if summary:
        base += f"\n\n[지금까지의 이야기 요약]\n{summary}"
    thread = st.session_state.get("story_thread", "").strip()
    if thread:
        base += f"\n\n[대화 실타래 — 맥락 유지]\n{thread}"

    user_turns = effective_user_turn_count()
    if _is_learning_mode():
        min_turns = MIN_USER_TURNS_FOR_LEARNING_REPORT
        report_done = bool(st.session_state.get("learning_report_count", 0))
    elif _is_isolation_mode():
        min_turns = MIN_USER_TURNS_FOR_REPORT
        report_done = bool(st.session_state.get("isolation_report_count", 0))
    else:
        min_turns = MIN_USER_TURNS_FOR_MIDPOINT
        report_done = bool(st.session_state.get("midpoint_analysis_count", 0))
    base += build_conversation_phase_addon(
        user_turns,
        midpoint_completed=report_done,
        min_turns=min_turns,
    )

    precision = float(st.session_state.get("narrative_precision", 50.0))
    if st.session_state.messages:
        precision = narrative_precision_score(
            st.session_state.messages, st.session_state.profile
        )
        st.session_state.narrative_precision = precision
    if user_turns >= min_turns or report_done:
        base += build_adaptive_scaffolding_addon(precision)

    if _is_isolation_mode():
        ireport = st.session_state.get("last_isolation_report")
        if isinstance(ireport, dict) and ireport.get("section_inner_strength"):
            base += (
                "\n\n[내면 항해 일지 — 공유됨 · 점수 금지]\n"
                f"{str(ireport.get('section_inner_strength', ''))[:280]}\n"
            )
    elif _is_learning_mode():
        lreport = st.session_state.get("last_learning_report")
        if isinstance(lreport, dict) and lreport.get("section_prescription"):
            base += (
                "\n\n[배움 지도 리포트 — 참여자와 공유됨 · 수치는 말하지 말 것]\n"
                f"- [{lreport.get('title_prescription', TITLE_PRESCRIPTION)}] "
                f"{str(lreport.get('section_prescription', ''))[:280]}\n"
                f"- {format_learning_followup()}\n"
                "- 대화를 종료하지 말고 이어갈 것."
            )
    else:
        report = st.session_state.get("last_midpoint_report")
        if isinstance(report, dict) and report.get("section_treasure"):
            base += (
                "\n\n[중간 마음 지도 — 참여자와 공유됨 · 수치는 말하지 말 것]\n"
                f"- [{report.get('title_treasure', '삶의 보물지도')}] "
                f"{str(report.get('section_treasure', ''))[:280]}\n"
                '- 마무리 질문: "이 지도가 당신의 마음과 닮았나요? '
                '조금 더 들려주고 싶은 장면이 있다면 말씀해 주세요."\n'
                "- 대화를 종료하지 말고 이어갈 것."
            )

    base += _conversation_style_addon()
    return base


def _conversation_style_addon() -> str:
    """턴당 맥락 보강 (서사 동행자 System Instruction은 최상단에 고정)."""
    user_turns = effective_user_turn_count()
    last_user = _last_user_display_text()
    return build_maieutic_addon(last_user=last_user, user_turns=user_turns)


def _message_text(msg: dict) -> str:
    return str(msg.get("content") or "").strip()


def _user_visible_text(msg: dict) -> str:
    """사진 메시지는 display만 보여 주고, AI용 content(분석 블록)는 숨김."""
    if msg.get("role") == "user" and msg.get("image_bytes"):
        return str(msg.get("display") or "").strip()
    return _message_text(msg)


def _last_user_display_text() -> str:
    for msg in reversed(st.session_state.messages):
        if msg.get("role") == "user":
            return str(msg.get("display") or msg.get("content") or "").strip()[:160]
    return ""


def _append_message(role: str, content: str, **extra: object) -> None:
    entry: dict = {"role": role, "content": content, "display": extra.pop("display", content)}
    entry.update(extra)
    st.session_state.messages.append(entry)
    if role == "user" and (
        str(content or "").strip() or str(entry.get("display") or "").strip()
    ):
        st.session_state.total_user_turns = (
            int(st.session_state.get("total_user_turns", 0)) + 1
        )
    _trim_message_history()


def effective_user_turn_count() -> int:
    """화면·중간정리용 — 토큰 다이어트로 메시지가 줄어도 턴 수는 유지."""
    stored = int(st.session_state.get("total_user_turns", 0))
    from hbridge_analysis import count_user_turns

    return max(stored, count_user_turns(st.session_state.messages))


def messages_for_gemini_api() -> list[dict]:
    """LLM API 전송용 — 최근 N턴만. UI messages 는 그대로 둠."""
    msgs = list(st.session_state.messages)
    if len(msgs) <= TOKEN_DIET_MESSAGE_THRESHOLD:
        return msgs
    return msgs[-TOKEN_DIET_KEEP_RECENT:]


def _trim_message_history() -> None:
    msgs = st.session_state.messages
    if len(msgs) <= MAX_STORED_MESSAGES:
        return
    st.session_state.messages = msgs[-MAX_STORED_MESSAGES:]


def _update_story_thread(user_text: str, assistant_text: str) -> None:
    u = (user_text or "").strip()[:80]
    a = (assistant_text or "").strip()[:120]
    if u and a:
        st.session_state.story_thread = f"최근: 씨앗 「{u}」 → 서사 동행자 「{a}」"


def _chat_max_output_tokens() -> int:
    return 4096 if st.session_state.get("extended_input_unlocked") else 2048


def build_gemini_history(messages: list[dict]) -> list[dict]:
    history = []
    for msg in messages[:-1]:
        text = _message_text(msg)
        if not text:
            continue
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [text]})
    return history


def apply_token_diet() -> bool:
    """
    긴 대화 시 **요약만** 갱신. messages 는 삭제하지 않음(모바일·PC 채팅·10턴 카운트 유지).
    """
    messages = st.session_state.messages
    if len(messages) <= TOKEN_DIET_MESSAGE_THRESHOLD:
        return False
    split_at = len(messages) - TOKEN_DIET_KEEP_RECENT
    try:
        st.session_state.context_summary = summarize_messages(
            messages[:split_at],
            st.session_state.context_summary,
        )
    except Exception:  # noqa: BLE001
        return False
    st.session_state.diet_applied_count += 1
    return True


def maybe_switch_to_giant(user_text: str) -> None:
    if st.session_state.phase == PHASE_GIANT:
        return
    distressed, concern = detect_distress(user_text)
    if not distressed:
        return
    st.session_state.phase = PHASE_GIANT
    st.session_state.current_concern = concern or "현재의 어려움"
    st.session_state.active_giant = select_giant(
        user_text, st.session_state.current_concern
    )


def _reset_chat_state() -> None:
    for key in (
        "messages",
        "context_summary",
        "interests",
        "profile",
        "narrative_stage",
        "life_context",
        "diet_applied_count",
        "phase",
        "active_giant",
        "current_concern",
        "positive_resources",
        "summoned_narrative",
        "life_summary",
        "conversation_closed",
        "pending_turn",
        "story_thread",
        "total_user_turns",
        "extended_input_unlocked",
        "midpoint_analysis_count",
        "last_midpoint_report",
        "pending_midpoint_analysis",
        "last_learning_report",
        "learning_report_count",
        "pending_learning_report",
        "learning_audience",
        "learning_signals",
        "isolation_signals",
        "last_isolation_asset",
        "isolation_asset_count",
        "last_isolation_report",
        "isolation_report_count",
        "pending_isolation_asset",
        "pending_isolation_report",
        "narrative_precision",
        "jaggedness_index",
    ):
        if key == "phase":
            st.session_state[key] = PHASE_COLLECT
        elif key in ("interests",):
            st.session_state[key] = ["—", "—", "—"]
        elif key in ("profile",):
            st.session_state[key] = default_profile()
        elif key in ("positive_resources", "life_summary"):
            st.session_state[key] = [] if key == "positive_resources" else ""
        elif key == "conversation_closed":
            st.session_state[key] = False
        elif key == "active_giant":
            st.session_state[key] = None
        elif key in ("narrative_stage",):
            st.session_state[key] = "탐색"
        elif key in ("life_context", "current_concern", "summoned_narrative"):
            st.session_state[key] = "—" if key == "life_context" else ""
        elif key == "pending_turn":
            st.session_state[key] = None
        elif key == "total_user_turns":
            st.session_state[key] = 0
        elif key == "extended_input_unlocked":
            st.session_state[key] = False
        elif key == "midpoint_analysis_count":
            st.session_state[key] = 0
        elif key == "last_midpoint_report":
            st.session_state[key] = None
        elif key == "pending_midpoint_analysis":
            st.session_state[key] = False
        elif key == "narrative_precision":
            st.session_state[key] = 50.0
        elif key == "jaggedness_index":
            st.session_state[key] = 0.0
        elif key in ("last_midpoint_report", "last_learning_report"):
            st.session_state[key] = None
        elif key in ("midpoint_analysis_count", "learning_report_count"):
            st.session_state[key] = 0
        elif key == "learning_audience":
            st.session_state[key] = ""
        elif key in ("learning_signals", "isolation_signals"):
            st.session_state[key] = None
        elif key in ("last_isolation_asset", "last_isolation_report"):
            st.session_state[key] = None
        elif key in ("isolation_asset_count", "isolation_report_count"):
            st.session_state[key] = 0
        elif key in ("pending_isolation_asset", "pending_isolation_report"):
            st.session_state[key] = False
        else:
            st.session_state[key] = 0 if key == "diet_applied_count" else ""
    st.session_state.pop("_chat_input_focused", None)


def _asset_progress_pct() -> float:
    """10턴 기준 자산화 진척도 (0~100)."""
    return min(100.0, effective_user_turn_count() / 10.0 * 100.0)


def render_chat_toolbar(
    gemini_ok: bool,
    gemini_error: str | None,
    db: DatabaseManager,
) -> None:
    """기록 화면 상단 — 언어(우측)·진척도·내보내기."""
    with st.container():
        _html_layout_marker("chat-toolbar-marker")
        st.markdown(
            f'<p class="archive-room-title">{html.escape(t("archive_title"))} · '
            f'<span style="font-size:0.85em;opacity:0.75">{html.escape(t("archive_subtitle"))}</span></p>',
            unsafe_allow_html=True,
        )
        left, right = st.columns([2.2, 1], gap="small")
        with left:
            if _is_learning_mode():
                companion = resolve_companion_display()["short"]
            else:
                companion = phase_label_ko(
                    st.session_state.phase, st.session_state.active_giant
                )
            st.markdown(
                f'<span class="phase-badge">{html.escape(companion)}와 함께</span>',
                unsafe_allow_html=True,
            )
            if st.session_state.preview_mode:
                st.markdown(
                    '<p class="preview-banner">🌅 낮막 미리보기 모드</p>',
                    unsafe_allow_html=True,
                )
        with right:
            _html_layout_marker("chat-toolbar-lang-marker")
            render_language_selector(key="chat_lang")

        st.markdown(
            f'<div class="gentle-record">{t("gentle_record")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="archive-progress-label">{html.escape(t("asset_progress_label"))}</p>',
            unsafe_allow_html=True,
        )
        st.progress(_asset_progress_pct() / 100.0)
        if st.session_state.phase == PHASE_GIANT and st.session_state.active_giant:
            gk = st.session_state.active_giant
            st.caption(f"지금은 {GIANTS[gk]['label']}의 관점으로 이어갑니다.")

        act1, act2, act3 = st.columns(3, gap="small")
        with act1:
            if st.button(t("reset_chat"), use_container_width=True, key="chat_reset"):
                _reset_chat_state()
                st.rerun()
        with act2:
            if st.session_state.conversation_closed:
                if st.button(
                    t("new_story"),
                    use_container_width=True,
                    type="primary",
                    key="chat_new_story",
                ):
                    st.session_state.conversation_closed = False
                    st.session_state.life_summary = ""
                    st.session_state._request_summary = False
                    st.rerun()
            elif st.session_state.messages:
                if st.button(t("finish_chat"), use_container_width=True, key="chat_finish"):
                    st.session_state._request_summary = True
                    st.rerun()
        with act3:
            db_ok = db.is_connected
            gem_icon = "🟢" if gemini_ok else "🔴"
            db_icon = "🟢" if db_ok else "🔴"
            st.caption(
                f"{gem_icon} {t('status_dialogue')} · {db_icon} {t('status_record')}"
            )

        with st.expander(t("btn_view_life_archive"), expanded=False):
            mod = (
                "learning"
                if _is_learning_mode()
                else ("isolation" if _is_isolation_mode() else "lifespan")
            )
            payload = build_export_payload(
                nickname=st.session_state.participant_id,
                messages=st.session_state.messages,
                profile=st.session_state.profile,
                narrative_stage=st.session_state.narrative_stage or "",
                life_context=st.session_state.life_context or "",
                narrative_themes=st.session_state.get("narrative_themes", ""),
                metaphors=st.session_state.get("metaphors", ""),
                module_type=mod,
            )
            col_j, col_t = st.columns(2, gap="small")
            with col_j:
                st.download_button(
                    t("export_json_btn"),
                    data=export_json_bytes(payload),
                    file_name="dlinso_narrative_archive.json",
                    mime="application/json",
                    use_container_width=True,
                    key="export_narrative_json",
                )
            with col_t:
                st.download_button(
                    t("export_archive_btn"),
                    data=export_pdf_bytes(payload),
                    file_name="dlinso_narrative_archive.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="export_narrative_text",
                )

        with st.expander(t("sidebar_inquiry"), expanded=False):
            if st.button(t("nav_inquiry"), key="chat_open_inquiry", use_container_width=True):
                st.session_state.inquiry_return_view = VIEW_APP
                st.session_state.current_view = VIEW_INQUIRY
                st.rerun()
            render_researcher_inquiry(db)
        if not gemini_ok and gemini_error:
            st.caption(gemini_error)
        if not db.is_connected and db.error_message:
            st.warning(db.error_message)

def _login_restore_payload(found: dict[str, Any]) -> tuple[list[dict[str, Any]] | None, list[dict[str, str]]]:
    """
    랜딩에서 고른 모듈과 DB 마지막 모듈이 다르면 복원하지 않음.
    (여정 카드 → 동행 대화가 붙는 현상 방지)
    """
    restore_msgs = found.get("restored_messages")
    restore_turns = list(found.get("recent_turns") or [])
    landing_id = (st.session_state.get("selected_module_id") or "").strip()

    if landing_id:
        want_mode = module_app_mode(landing_id) or MODE_LIFESPAN
        db_mod = (found.get("last_module_type") or "lifespan").strip()
        if want_mode != db_mod:
            return None, []
        return restore_msgs, restore_turns

    db_mod = (found.get("last_module_type") or "lifespan").strip()
    if db_mod == "isolation":
        apply_landing_module_selection("forest")
    elif db_mod == "learning":
        apply_landing_module_selection("learning")
        aud = (found.get("last_learning_audience") or "").strip()
        if aud:
            st.session_state.learning_audience = aud
    else:
        apply_landing_module_selection("narrative")
    return restore_msgs, restore_turns


def reset_user_session() -> None:
    """가입·로그인 화면을 다시 보이게 세션 초기화."""
    for key, val in {
        "messages": [],
        "context_summary": "",
        "onboarding_complete": False,
        "consent_agreed": False,
        "participant_id": "",
        "gender": "",
        "age_group": "",
        "life_stage": "",
        "app_mode": "lifespan",
        "selected_module_id": "",
        "home_intro_revealed": False,
        "learning_audience": "",
        "password_hash": "",
        "is_returning_user": False,
        "preview_mode": False,
        "conversation_closed": False,
        "life_summary": "",
        "phase": PHASE_COLLECT,
        "active_giant": None,
        "current_view": VIEW_HOME,
    }.items():
        st.session_state[key] = val


def render_onboarding(db: DatabaseManager) -> None:
    reconcile_landing_module_session()
    st.markdown(f"## {t('consent_title')}")
    render_db_status(db)
    mod = get_landing_module(st.session_state.get("selected_module_id", ""))
    if mod:
        st.markdown(
            f'<p class="dlinso-onboarding-module-hint">「{html.escape(mod.title)}」 여정을 시작합니다.</p>',
            unsafe_allow_html=True,
        )
        if _is_learning_mode():
            from modules.home_registry import (
                LEARNING_SPOTLIGHT_LEAD_EN,
                LEARNING_SPOTLIGHT_LEAD_KO,
                LEARNING_SPOTLIGHT_STEPS_EN,
                LEARNING_SPOTLIGHT_STEPS_KO,
            )

            if get_lang() == "ko":
                lead = LEARNING_SPOTLIGHT_LEAD_KO
                steps = LEARNING_SPOTLIGHT_STEPS_KO
            else:
                lead = LEARNING_SPOTLIGHT_LEAD_EN
                steps = LEARNING_SPOTLIGHT_STEPS_EN
            st.markdown(
                f'<p class="dlinso-onboarding-learning-detail">'
                f"{html.escape(lead)}<br>"
                f"<span style='font-size:0.9em;color:#666;'>{html.escape(steps)}</span>"
                f"</p>",
                unsafe_allow_html=True,
            )
        elif _is_isolation_mode():
            st.markdown(
                f'<p class="dlinso-onboarding-learning-detail">'
                f"{html.escape(t('mode_isolation_desc'))}"
                f"</p>",
                unsafe_allow_html=True,
            )
    st.info(
        t("onboarding_banner").format(
            tab_new=t("tab_new"),
            tab_return=t("tab_return"),
        )
    )
    tab_new, tab_return = st.tabs([t("tab_new"), t("tab_return")])

    with tab_new:
        st.markdown(t("key_hint"))
        render_current_age_context(placement="onboarding")
        consent = st.checkbox(t("consent_check"), key="consent_new")
        with st.form("signup_form", clear_on_submit=False):
            nickname = st.text_input(
                t("nickname"),
                placeholder="…",
                key="signup_nickname",
            )
            password = st.text_input(
                t("password"),
                type="password",
                key="signup_password",
            )
            password2 = st.text_input(
                t("password_confirm"),
                type="password",
                key="signup_password_confirm",
            )
            gender = st.selectbox(
                t("gender"),
                GENDER_OPTIONS,
                key="signup_gender",
            )
            age_group = st.selectbox(
                t("age_current"),
                AGE_GROUPS,
                key="signup_age_group",
            )
            st.caption(t("age_field_help"))

            signup_learning_audience = ""
            if _is_learning_mode():
                st.markdown(f"**{t('learning_signup_section')}**")
                st.caption(t("learning_role_intro"))
                signup_learning_audience = render_learning_audience_selectbox(
                    key="signup_learning_audience",
                    label=t("learning_role_title"),
                )

            st.markdown(f"**{t('life_stage_signup_section') if _is_learning_mode() else t('education')}**")
            life_stage = st.selectbox(
                t("education"),
                LIFE_STAGE_OPTIONS,
                key="signup_life_stage",
                label_visibility="collapsed",
            )
            st.caption(t("education_field_help"))
            signup = st.form_submit_button(
                t("btn_start"),
                type="primary",
                use_container_width=True,
            )

        if signup:
            nick = nickname.strip()
            lang = get_lang()
            if not consent:
                st.error(t("err_consent"))
            elif not nick:
                st.error(t("err_nick"))
            elif not password:
                st.error(t("err_pw"))
            elif password != password2:
                st.error(t("err_pw_match"))
            elif nickname_exists(db, nick):
                st.error(t("err_nick_taken"))
            elif _is_learning_mode() and not is_valid_learning_audience(
                signup_learning_audience
            ):
                st.error(t("err_learning_audience"))
            else:
                pw_hash = hash_password(password)
                if not db.is_connected:
                    st.error(_db_error_message(db))
                else:
                    db.ensure_schema()
                    db.log_registration(
                        participant_id=nick,
                        password_hash=pw_hash,
                        lang=lang,
                        gender=gender,
                        age_group=age_group,
                        education=life_stage,
                    )
                    _activate_session(
                        participant_id=nick,
                        password_hash_value=pw_hash,
                        gender=gender,
                        age_group=age_group,
                        life_stage=life_stage,
                        lang=lang,
                        is_returning=False,
                    )
                    if _is_learning_mode():
                        st.session_state.learning_audience = signup_learning_audience
                    st.rerun()

    with tab_return:
        st.markdown(t("return_hint"))
        with st.form("login_form"):
            nickname = st.text_input(t("nickname"), key="return_nick")
            password = st.text_input(t("password"), type="password", key="return_pw")
            login = st.form_submit_button(
                t("btn_continue"),
                type="primary",
                use_container_width=True,
            )

        if login:
            nick = nickname.strip()
            if not nick or not password:
                st.error(t("err_login_both"))
            elif not db.is_connected:
                st.error(_db_error_message(db))
            else:
                db.ensure_schema()
                found = db.find_returning_user(nick, password)
                if not found:
                    st.error(t("err_login"))
                else:
                    profile = found["profile"]
                    db.record_visit(
                        participant_id=profile["participant_id"],
                        password_hash=profile["password_hash"],
                        lang=profile.get("lang", get_lang()) or "ko",
                        gender=profile.get("gender", ""),
                        age_group=profile.get("age_group", ""),
                        life_stage=profile.get("life_stage", ""),
                    )
                    restored_msgs, recent_turns = _login_restore_payload(found)
                    reconcile_landing_module_session()
                    _activate_session(
                        participant_id=profile["participant_id"],
                        password_hash_value=profile["password_hash"],
                        gender=profile.get("gender", ""),
                        age_group=profile.get("age_group", ""),
                        life_stage=profile.get("life_stage", ""),
                        lang=profile.get("lang", get_lang()) or "ko",
                        is_returning=True,
                        recent_turns=recent_turns,
                        restored_messages=restored_msgs,
                        total_turn_count=int(found.get("total_turn_count") or 0),
                        has_midpoint=bool(found.get("has_midpoint")),
                        last_topic=found.get("last_topic", ""),
                        admin_reply=found.get("admin_reply", ""),
                        admin_reply_type=found.get("admin_reply_type", "general"),
                    )
                    st.rerun()


def render_hub_slogan_banner() -> None:
    """서비스 슬로건 — 베타 뱃지는 상단 네비에만 표시."""
    _html_layout_marker("hub-slogan-hero-marker")
    fragment = (
        '<div class="hub-slogan-hero">'
        f"{_intro_headline_html()}"
        f"{_intro_sub_html()}"
        "</div>"
    )
    _render_html_fragment(fragment)


def _profile_pill_html(icon: str, label: str, value: str, *, accent: bool = False) -> str:
    extra = " profile-pill--accent" if accent else ""
    label_html = (
        f'<span class="profile-pill-label">{html.escape(label)}</span>'
        if label
        else ""
    )
    return (
        f'<div class="profile-pill{extra}">'
        f'<span class="profile-pill-icon" aria-hidden="true">{icon}</span>'
        f'<div class="profile-pill-body">{label_html}'
        f'<span class="profile-pill-value">{html.escape(str(value or "—"))}</span>'
        f"</div></div>"
    )


def render_main_header(display: dict) -> None:
    reconcile_landing_module_session()
    phase_txt = (
        t("phase_collect")
        if st.session_state.phase == PHASE_COLLECT
        else f"{display.get('short', display['label'])}"
    )
    mod = get_landing_module(st.session_state.get("selected_module_id", ""))
    salon_html = ""
    if mod:
        salon_html = (
            f'<p class="hero-salon-module">「{html.escape(mod.title)}」</p>'
        )
    pills = [
        _profile_pill_html("🪪", t("profile_nick"), st.session_state.participant_id),
        _profile_pill_html("📅", t("profile_age"), st.session_state.age_group),
        _profile_pill_html("📚", t("profile_stage"), st.session_state.life_stage),
        _profile_pill_html(
            display["emoji"],
            t("profile_companion"),
            display["label"],
            accent=True,
        ),
    ]
    if st.session_state.get("is_returning_user"):
        pills.append(_profile_pill_html("🔄", "", t("returning_badge")))

    hero_html = (
        HERO_CARD_INLINE_STYLE
        + f'<section class="hero-header">'
        f'<div class="hero-eyebrow">{html.escape(t("hub_eyebrow"))}</div>'
        f'<h2 class="hero-title">{html.escape(t("app_title"))}</h2>'
        f"{salon_html}"
        f'<p class="hero-desc">{display["emoji"]} <strong>'
        f"{html.escape(display['label'])}</strong> — "
        f"{html.escape(phase_txt)}.</p>"
        f'<div class="profile-strip">{"".join(pills)}</div>'
        f"</section>"
    )
    _render_html_fragment(hero_html)
    render_hub_slogan_banner()


def render_chat_area(display: dict) -> None:
    if st.session_state.life_summary:
        st.markdown(
            f'<div class="life-summary-box">{st.session_state.life_summary}</div>',
            unsafe_allow_html=True,
        )
        if st.session_state.conversation_closed:
            st.caption("오늘의 인생 요약본을 선물로 드렸습니다. 언제든 다시 이야기해 주세요. 🌿")
            return

    if not st.session_state.messages:
        render_current_age_context(placement="chat")
        if _is_isolation_mode():
            opening = t("isolation_opening")
        elif _is_learning_mode():
            aud = str(st.session_state.get("learning_audience") or "").strip()
            if is_valid_learning_audience(aud):
                opening = t(audience_opening_i18n_key(aud))
            else:
                opening = t("learning_role_intro")
        else:
            opening = resolve_opening_message(
                t=t,
                age_group=st.session_state.get("age_group", ""),
                gender=st.session_state.get("gender", ""),
                life_stage=st.session_state.get("life_stage", ""),
            )
        opening = opening.replace("\n\n", "<br><br>").replace("\n", "<br>")
        st.markdown(
            f'<div class="opening-guide">{opening}</div>',
            unsafe_allow_html=True,
        )
    for message in st.session_state.messages:
        avatar = "🧑" if message["role"] == "user" else display["emoji"]
        with st.chat_message(message["role"], avatar=avatar):
            if message.get("image_bytes"):
                st.image(message["image_bytes"], use_container_width=True)
                caption = _user_visible_text(message)
                if caption:
                    st.markdown(caption)
            else:
                body = _user_visible_text(message)
                if body:
                    st.markdown(body)


def iter_reply_stream(
    messages: list[dict],
    user_prompt: str,
    *,
    image_bytes: bytes | None = None,
    image_mime: str | None = None,
) -> Iterator[str]:
    """Solar/Gemini 스트리밍 — 배움 모드는 learning_engine 전용."""
    if _is_isolation_mode():
        yield from iter_isolation_reply_stream(
            messages,
            user_prompt,
            lang=get_lang(),
            age_group=st.session_state.age_group or "",
            life_stage=st.session_state.life_stage or "",
            nickname=str(st.session_state.get("participant_id") or ""),
            report_completed=bool(st.session_state.get("isolation_report_count", 0)),
            context_summary=str(st.session_state.get("context_summary") or ""),
            live_signals=st.session_state.get("isolation_signals"),
        )
        return

    if _is_learning_mode():
        yield from iter_learning_reply_stream(
            messages,
            user_prompt,
            lang=get_lang(),
            learning_audience=str(st.session_state.get("learning_audience") or ""),
            age_group=st.session_state.age_group or "",
            life_stage=st.session_state.life_stage or "",
            nickname=str(st.session_state.get("participant_id") or ""),
            report_completed=bool(st.session_state.get("learning_report_count", 0)),
            context_summary=str(st.session_state.get("context_summary") or ""),
            live_signals=st.session_state.get("learning_signals"),
        )
        return

    api_messages = messages
    yield from iter_chat_stream(
        api_messages,
        user_prompt,
        system=build_system_instruction(),
        temperature=0.82,
        top_p=0.92,
        max_tokens=_chat_max_output_tokens(),
        gemini_history=build_gemini_history(api_messages),
        image_bytes=image_bytes,
        image_mime=image_mime,
    )


def deliver_life_summary(gemini_ok: bool) -> None:
    if not gemini_ok or st.session_state.life_summary:
        return
    with st.spinner("오늘의 인생 요약본을 쓰고 있어요…"):
        try:
            st.session_state.life_summary = generate_life_summary(
                st.session_state.messages,
                st.session_state.positive_resources,
                st.session_state.age_group,
                st.session_state.participant_id,
                st.session_state.life_stage,
            )
            st.session_state.conversation_closed = True
        except Exception as exc:  # noqa: BLE001
            st.warning(f"요약본 생성 중 문제가 있었습니다: {exc}")


def handle_chat_turn(
    user_text: str,
    display: dict,
    gemini_ok: bool,
    db: DatabaseManager,
    *,
    image_bytes: bytes | None = None,
    image_mime: str | None = None,
) -> None:
    if not gemini_ok:
        st.error(t("err_dialogue_not_connected"))
        return
    if st.session_state.conversation_closed:
        st.info("오늘의 대화는 마무리되었습니다. '대화 기록 초기화'로 새 이야기를 시작할 수 있어요.")
        return

    apply_token_diet()

    image_analysis: dict[str, str] | None = None
    if image_bytes:
        with st.spinner("📷 사진 속 이야기를 읽고 있어요…"):
            image_analysis = analyze_uploaded_image(
                image_bytes,
                image_mime or "image/jpeg",
                user_text,
                lang=get_lang(),
            )

    if image_bytes:
        display_text = format_image_display_for_user(image_analysis, user_text)
    else:
        display_text = (user_text or "").strip()

    model_prompt = merge_text_and_image(user_text, image_analysis)
    if not model_prompt.strip():
        st.warning("메시지 또는 사진을 보내 주세요.")
        return

    if st.session_state.phase == PHASE_COLLECT:
        try:
            st.session_state.positive_resources = extract_positive_resources(
                st.session_state.messages
                + [{"role": "user", "content": model_prompt}],
                st.session_state.positive_resources,
            )
        except Exception:  # noqa: BLE001
            pass

    if not _is_learning_mode() and not _is_isolation_mode():
        maybe_switch_to_giant(model_prompt)

    user_extra: dict[str, Any] = {}
    if image_bytes:
        user_extra["image_bytes"] = image_bytes
        user_extra["image_mime"] = image_mime or "image/jpeg"
    _append_message(
        "user",
        model_prompt,
        display=display_text,
        **user_extra,
    )

    with st.chat_message("user", avatar="🧑"):
        if image_bytes:
            st.image(image_bytes, use_container_width=True)
            if display_text:
                st.markdown(display_text)
        elif display_text:
            st.markdown(display_text)

    def _reply_token_stream() -> Iterator[str]:
        try:
            yield from iter_reply_stream(
                messages_for_gemini_api(),
                model_prompt,
                image_bytes=image_bytes,
                image_mime=image_mime,
            )
        except Exception as exc:  # noqa: BLE001
            yield _llm_user_error(exc)

    try:
        with st.chat_message("assistant", avatar=display["emoji"]):
            streamed = st.write_stream(_reply_token_stream())
            full_reply = (streamed or "").strip() if isinstance(streamed, str) else ""
    except Exception as exc:  # noqa: BLE001
        full_reply = _llm_user_error(exc)
        with st.chat_message("assistant", avatar=display["emoji"]):
            st.markdown(full_reply)

    if not full_reply.strip():
        full_reply = (
            "잠시 연결이 불안정해요. 방금 하신 말을 조금만 다른 표현으로 "
            "다시 적어 주실 수 있을까요?"
        )

    _append_message("assistant", full_reply, display=full_reply)
    _update_story_thread(display_text, full_reply)

    if st.session_state.phase == PHASE_COLLECT:
        try:
            st.session_state.positive_resources = extract_positive_resources(
                st.session_state.messages,
                st.session_state.positive_resources,
            )
        except Exception:  # noqa: BLE001
            pass

    summoned = ""
    if st.session_state.phase == PHASE_GIANT:
        summoned = pick_summoned_narrative(
            st.session_state.positive_resources,
            model_prompt,
            full_reply,
        )
        st.session_state.summoned_narrative = summoned

    learning_signals_json = ""
    isolation_signals_json = ""
    if _is_isolation_mode():
        signals = _refresh_isolation_signals()
        if isinstance(signals, dict):
            isolation_signals_json = json.dumps(signals, ensure_ascii=False)[:8000]
    elif _is_learning_mode():
        signals = _refresh_learning_signals()
        if isinstance(signals, dict):
            learning_signals_json = json.dumps(signals, ensure_ascii=False)[:8000]
    else:
        with st.spinner(""):
            try:
                metrics = analyze_narrative_turn(
                    model_prompt, full_reply, st.session_state.context_summary
                )
                st.session_state.profile = {k: float(metrics[k]) for k in PROFILE_KEYS}
                st.session_state.narrative_stage = str(metrics["narrative_stage"])
                st.session_state.life_context = str(metrics["life_context"])
                st.session_state.narrative_themes = str(
                    metrics.get("narrative_themes", "")
                )
                st.session_state.metaphors = str(metrics.get("metaphors", ""))
                st.session_state.turning_points = str(metrics.get("turning_points", ""))
            except Exception:  # noqa: BLE001
                pass
            try:
                st.session_state.interests = extract_interests(
                    st.session_state.messages, st.session_state.interests
                )
            except Exception:  # noqa: BLE001
                pass

    apply_token_diet()

    giant_name = phase_label_ko(st.session_state.phase, st.session_state.active_giant)
    lang = get_lang()
    try:
        user_ko = (
            model_prompt if lang == "ko" else translate_to_korean(model_prompt, lang)
        )
        reply_ko = (
            full_reply if lang == "ko" else translate_to_korean(full_reply, lang)
        )
    except Exception:  # noqa: BLE001
        user_ko = model_prompt
        reply_ko = full_reply
    if db.is_connected:
        if _is_isolation_mode():
            ok, err = save_isolation_turn_local(
                db,
                nickname=st.session_state.participant_id,
                user_message=model_prompt,
                assistant_message=full_reply,
                participant_id=st.session_state.participant_id,
                password_hash=st.session_state.password_hash,
                lang=lang,
                gender=st.session_state.gender,
                age_group=st.session_state.age_group,
                education=st.session_state.life_stage,
                user_message_ko=user_ko,
                assistant_message_ko=reply_ko,
                giant_name=display.get("label", "연결의 동행자"),
                current_concern=st.session_state.current_concern or "",
                summoned_narrative=summoned or "",
                profile=st.session_state.profile,
                life_context=st.session_state.life_context or "",
                narrative_stage=st.session_state.narrative_stage or "",
                narrative_themes=st.session_state.get("narrative_themes", ""),
                metaphors=st.session_state.get("metaphors", ""),
                turning_points=st.session_state.get("turning_points", ""),
                module_type="isolation",
                isolation_signals_json=isolation_signals_json,
            )
        else:
            db.ensure_schema()
            ok, err = db.log_conversation(
                user_message=model_prompt,
                assistant_message=full_reply,
                participant_id=st.session_state.participant_id,
                password_hash=st.session_state.password_hash,
                lang=lang,
                gender=st.session_state.gender,
                age_group=st.session_state.age_group,
                education=st.session_state.life_stage,
                user_message_ko=user_ko,
                assistant_message_ko=reply_ko,
                giant_name=giant_name,
                current_concern=st.session_state.current_concern or "",
                summoned_narrative=summoned or "",
                profile=st.session_state.profile,
                life_context=st.session_state.life_context or "",
                narrative_stage=st.session_state.narrative_stage or "",
                narrative_themes=st.session_state.get("narrative_themes", ""),
                metaphors=st.session_state.get("metaphors", ""),
                turning_points=st.session_state.get("turning_points", ""),
                module_type=(
                    "learning" if _is_learning_mode() else "lifespan"
                ),
                learning_audience=st.session_state.get("learning_audience", ""),
                learning_signals_json=learning_signals_json,
            )
        if not ok:
            st.warning(_db_save_warning(err))

    if st.session_state.get("is_returning_user"):
        st.session_state.is_returning_user = False

    st.session_state.narrative_precision = narrative_precision_score(
        st.session_state.messages, st.session_state.profile
    )

    if st.session_state.get("_request_summary"):
        st.session_state.pop("_request_summary", None)
        deliver_life_summary(gemini_ok)

    st.rerun()


def _bump_chat_composer_nonce() -> None:
    """입력창 비우기 — nonce를 올려 다음 rerun에 새 위젯 key로 다시 그린다."""
    st.session_state.chat_composer_nonce = (
        int(st.session_state.get("chat_composer_nonce", 0)) + 1
    )
    for key in ("chat_photo_upload", "main_chat_input"):
        if key in st.session_state:
            del st.session_state[key]


def _enqueue_chat_turn(
    text: str,
    *,
    image_bytes: bytes | None = None,
    image_mime: str | None = None,
) -> None:
    st.session_state.pending_turn = {
        "text": (text or "").strip(),
        "image_bytes": image_bytes,
        "image_mime": image_mime,
    }
    st.session_state.pending_user_prompt = ""


def _take_pending_turn() -> dict[str, Any] | None:
    turn = st.session_state.get("pending_turn")
    st.session_state.pending_turn = None
    if not turn or not isinstance(turn, dict):
        legacy = (st.session_state.get("pending_user_prompt") or "").strip()
        st.session_state.pending_user_prompt = ""
        if legacy:
            return {"text": legacy, "image_bytes": None, "image_mime": None}
        return None
    if not turn.get("text") and not turn.get("image_bytes"):
        return None
    return turn


def _input_char_limit() -> int:
    if st.session_state.get("extended_input_unlocked"):
        return EXTENDED_INPUT_CHAR_LIMIT
    return DEFAULT_INPUT_CHAR_LIMIT


def _deliver_midpoint_scaffolding(
    display: dict,
    db: DatabaseManager,
    message: str,
) -> None:
    """발화 품질 부족 시 적응형 비계 — 리포트·5000자 해제 없음."""
    with st.chat_message("assistant", avatar=display["emoji"]):
        st.info(message)
    _append_message("assistant", message, display=message)

    if db.is_connected:
        db.ensure_schema()
        db.log_conversation(
            user_message="[중간정리·데이터부족]",
            assistant_message=message,
            participant_id=st.session_state.participant_id,
            password_hash=st.session_state.password_hash,
            lang=get_lang(),
            gender=st.session_state.gender,
            age_group=st.session_state.age_group,
            education=st.session_state.life_stage,
            user_message_ko="[중간정리·데이터부족]",
            assistant_message_ko=message,
            giant_name=phase_label_ko(
                st.session_state.phase, st.session_state.active_giant
            ),
            profile=st.session_state.profile,
            life_context=st.session_state.life_context or "",
            narrative_stage="자산화_비계",
            narrative_themes="sparse_content",
        )
    st.rerun()


def execute_midpoint_analysis(display: dict, db: DatabaseManager) -> None:
    """특허 기반 중간 분석 — 10턴 달성 시 마음 지도 리포트 생성."""
    turn_count = effective_user_turn_count()
    if turn_count < MIN_USER_TURNS_FOR_MIDPOINT:
        st.warning(
            t("midpoint_need_turns").format(
                need=MIN_USER_TURNS_FOR_MIDPOINT,
                current=turn_count,
            )
        )
        return

    user_turns = [
        m
        for m in st.session_state.messages
        if m.get("role") == "user"
        and (
            str(m.get("content") or "").strip()
            or str(m.get("display") or "").strip()
        )
    ]
    user_texts = [str(m.get("content") or "").strip() for m in user_turns]

    with st.spinner("지금까지의 이야기로 당신만의 마음 지도를 그리고 있어요…"):
        stats = compute_midpoint_statistics(
            st.session_state.messages, st.session_state.profile
        )
        situational = extract_situational_context(user_texts)
        humanistic: dict[str, str] | None = None
        try:
            humanistic = generate_humanistic_midpoint_report(
                st.session_state.messages,
                stats,
                age_group=st.session_state.age_group,
                gender=st.session_state.gender,
                life_stage=st.session_state.life_stage,
                participant_id=st.session_state.participant_id,
                life_context=st.session_state.get("life_context", ""),
                positive_resources=st.session_state.get("positive_resources") or [],
                situational_context=situational,
                lang=get_lang(),
            )
        except Exception:  # noqa: BLE001
            humanistic = None

        report = run_intra_individual_or_pipeline(
            st.session_state.messages,
            profile=st.session_state.profile,
            life_context=st.session_state.get("life_context", ""),
            positive_resources=st.session_state.get("positive_resources") or [],
            age_group=st.session_state.age_group,
            gender=st.session_state.gender,
            life_stage=st.session_state.life_stage,
            participant_id=st.session_state.participant_id,
            humanistic=humanistic,
        )

    st.session_state.last_midpoint_report = report
    st.session_state.extended_input_unlocked = True
    st.session_state.midpoint_analysis_count = (
        int(st.session_state.get("midpoint_analysis_count", 0)) + 1
    )
    st.session_state.jaggedness_index = float(report.get("jaggedness_index", 0))
    st.session_state.narrative_precision = float(
        report.get("narrative_precision", 50.0)
    )

    with st.chat_message("assistant", avatar=display["emoji"]):
        _render_midpoint_report_blocks(report)

    full_reply = format_full_midpoint_message(report)
    _append_message("assistant", full_reply, display=full_reply, midpoint=True)

    lang = get_lang()
    giant_name = phase_label_ko(st.session_state.phase, st.session_state.active_giant)
    stats_json = str(report.get("stats_json", ""))[:2000]
    scene = (report.get("situational_context") or {}).get("scene_phrase", "")
    if db.is_connected:
        db.ensure_schema()
        ok, err = db.log_conversation(
            user_message="[중간정리·마음지도·OR내부]",
            assistant_message=full_reply,
            participant_id=st.session_state.participant_id,
            password_hash=st.session_state.password_hash,
            lang=lang,
            gender=st.session_state.gender,
            age_group=st.session_state.age_group,
            education=st.session_state.life_stage,
            user_message_ko="[중간정리·마음지도]",
            assistant_message_ko=full_reply,
            giant_name=giant_name,
            current_concern=st.session_state.current_concern or "",
            summoned_narrative=st.session_state.summoned_narrative or "",
            profile=st.session_state.profile,
            life_context=st.session_state.life_context or "",
            narrative_stage=st.session_state.narrative_stage or "",
            narrative_themes=(scene or "상황맥락")[:500],
            metaphors=format_sheet_stats_summary(report)[:500],
            turning_points=stats_json,
        )
        if not ok:
            st.warning(_db_save_warning(err))

    st.rerun()


def _midpoint_section_body_html(body: str) -> str:
    paragraphs = [p.strip() for p in (body or "").split("\n\n") if p.strip()]
    if not paragraphs and (body or "").strip():
        paragraphs = [(body or "").strip()]
    return "".join(
        f'<p class="midpoint-essay-p">{html.escape(p)}</p>' for p in paragraphs
    )


def _render_midpoint_essay_section(title: str, body: str) -> None:
    st.markdown(
        f'<section class="midpoint-essay-block">'
        f'<h4 class="midpoint-essay-section-title">[{html.escape(title)}]</h4>'
        f'<div class="midpoint-essay-body">{_midpoint_section_body_html(body)}</div>'
        f"</section>",
        unsafe_allow_html=True,
    )


def _render_midpoint_report_blocks(report: dict[str, Any]) -> None:
    """마음 지도 리포트 본문 (채팅·expander 공용) — 에세이형 단락."""
    from hbridge_analysis import (
        TITLE_CONNECTION,
        TITLE_LANDSCAPE,
        TITLE_TREASURE,
        polish_midpoint_report,
    )

    polished = polish_midpoint_report(report)
    st.markdown("### 지금까지의 대화, 나를 돌아보는 마음 지도")
    preface = str(polished.get("midpoint_preface", "")).strip()
    if preface:
        st.markdown(
            f'<p class="midpoint-essay-preface">{html.escape(preface)}</p>',
            unsafe_allow_html=True,
        )
    _render_midpoint_essay_section(
        str(polished.get("title_landscape", TITLE_LANDSCAPE)),
        str(polished.get("section_landscape", "")),
    )
    _render_midpoint_essay_section(
        str(polished.get("title_connection", TITLE_CONNECTION)),
        str(polished.get("section_connection", "")),
    )
    _render_midpoint_essay_section(
        str(polished.get("title_treasure", TITLE_TREASURE)),
        str(polished.get("section_treasure", "")),
    )
    st.markdown(format_midpoint_followup())


def execute_learning_report_analysis(display: dict, db: DatabaseManager) -> None:
    """학습 서사 검사 리포트 — 10턴 이후."""
    turn_count = effective_user_turn_count()
    if turn_count < MIN_USER_TURNS_FOR_LEARNING_REPORT:
        st.warning(
            t("learning_report_need_turns").format(
                need=MIN_USER_TURNS_FOR_LEARNING_REPORT,
                current=turn_count,
            )
        )
        return
    if not is_valid_learning_audience(
        str(st.session_state.get("learning_audience") or "")
    ):
        st.warning(t("learning_role_intro"))
        return

    with st.spinner(t("learning_report_spinner")):
        report = generate_learning_narrative_report_for_messages(
            st.session_state.messages,
            learning_audience=st.session_state.learning_audience,
            age_group=st.session_state.age_group,
            life_stage=st.session_state.life_stage,
            participant_id=st.session_state.participant_id,
            lang=get_lang(),
            profile=st.session_state.profile,
        )
        learning_signals = report.get("learning_signals")
        if isinstance(learning_signals, dict):
            st.session_state.learning_signals = learning_signals

    st.session_state.last_learning_report = report
    st.session_state.extended_input_unlocked = True
    st.session_state.learning_report_count = (
        int(st.session_state.get("learning_report_count", 0)) + 1
    )
    st.session_state.jaggedness_index = float(report.get("jaggedness_index", 0))
    st.session_state.narrative_precision = float(
        report.get("narrative_precision", 50.0)
    )

    with st.chat_message("assistant", avatar=display["emoji"]):
        _render_learning_report_blocks(report)

    full_reply = format_full_learning_message(report)
    _append_message("assistant", full_reply, display=full_reply, learning_report=True)

    lang = get_lang()
    if db.is_connected:
        db.ensure_schema()
        ok, err = db.log_conversation(
            user_message="[학습리포트·배움지도·내부]",
            assistant_message=full_reply,
            participant_id=st.session_state.participant_id,
            password_hash=st.session_state.password_hash,
            lang=lang,
            gender=st.session_state.gender,
            age_group=st.session_state.age_group,
            education=st.session_state.life_stage,
            user_message_ko="[학습리포트·배움지도]",
            assistant_message_ko=full_reply,
            giant_name=display.get("label", "배움 동행자"),
            profile=st.session_state.profile,
            life_context=st.session_state.life_context or "",
            narrative_stage="학습_리포트",
            narrative_themes=st.session_state.learning_audience,
            metaphors=str(report.get("hbridge_summary", ""))[:500],
            turning_points=json.dumps(
                report.get("learning_signals") or {},
                ensure_ascii=False,
            )[:2000],
            turn_type="learning_report",
            module_type="learning",
            learning_audience=st.session_state.learning_audience,
            learning_signals_json=json.dumps(
                report.get("learning_signals") or {},
                ensure_ascii=False,
            )[:8000],
        )
        if not ok:
            st.warning(_db_save_warning(err))
    st.rerun()


def _render_learning_report_blocks(report: dict[str, Any]) -> None:
    from learning_analysis import render_learning_report_blocks

    render_learning_report_blocks(report)


def execute_isolation_asset_analysis(display: dict, db: DatabaseManager) -> None:
    """숲 · 6턴 이후 자아성/사회성 자산."""
    turn_count = effective_user_turn_count()
    if turn_count < MIN_USER_TURNS_FOR_ASSET:
        st.warning(
            t("isolation_asset_need_turns").format(
                need=MIN_USER_TURNS_FOR_ASSET,
                current=turn_count,
            )
        )
        return
    with st.spinner(t("isolation_asset_spinner")):
        from isolation_analysis import run_isolation_asset_pipeline

        signals = extract_isolation_signals(st.session_state.messages, lang=get_lang())
        asset = run_isolation_asset_pipeline(
            st.session_state.messages,
            st.session_state.profile,
            signals=signals,
        )
    st.session_state.last_isolation_asset = asset
    st.session_state.isolation_asset_count = (
        int(st.session_state.get("isolation_asset_count", 0)) + 1
    )
    if isinstance(signals, dict):
        st.session_state.isolation_signals = signals

    with st.chat_message("assistant", avatar=display["emoji"]):
        from isolation_analysis import render_isolation_asset_blocks

        render_isolation_asset_blocks(asset)

    full_reply = format_full_asset_message(asset)
    _append_message("assistant", full_reply, display=full_reply, midpoint=True)

    if db.is_connected:
        ok, err = save_isolation_turn_local(
            db,
            nickname=st.session_state.participant_id,
            user_message="[숲·자아성사회성자산·내부]",
            assistant_message=full_reply,
            participant_id=st.session_state.participant_id,
            password_hash=st.session_state.password_hash,
            lang=get_lang(),
            gender=st.session_state.gender,
            age_group=st.session_state.age_group,
            education=st.session_state.life_stage,
            user_message_ko="[숲·자아성사회성자산]",
            assistant_message_ko=full_reply,
            giant_name=display.get("label", "연결의 동행자"),
            profile=st.session_state.profile,
            narrative_stage="숲_자산",
            narrative_themes=str(asset.get("section_identity_asset", ""))[:500],
            metaphors=str(asset.get("hbridge_summary", ""))[:500],
            turning_points=json.dumps(signals or {}, ensure_ascii=False)[:2000],
            turn_type="isolation_asset",
            module_type="isolation",
            isolation_signals_json=json.dumps(signals or {}, ensure_ascii=False)[:8000],
        )
        if not ok:
            st.warning(_db_save_warning(err))
    st.rerun()


def execute_isolation_report_analysis(display: dict, db: DatabaseManager) -> None:
    """숲 · 10턴 이후 내면 항해 일지."""
    turn_count = effective_user_turn_count()
    if turn_count < MIN_USER_TURNS_FOR_REPORT:
        st.warning(
            t("isolation_report_need_turns").format(
                need=MIN_USER_TURNS_FOR_REPORT,
                current=turn_count,
            )
        )
        return
    with st.spinner(t("isolation_report_spinner")):
        report = generate_isolation_report_for_messages(
            st.session_state.messages,
            age_group=st.session_state.age_group,
            life_stage=st.session_state.life_stage,
            participant_id=st.session_state.participant_id,
            lang=get_lang(),
            profile=st.session_state.profile,
        )
        sig = report.get("signals") or report.get("learning_signals")
        if isinstance(sig, dict):
            st.session_state.isolation_signals = sig

    st.session_state.last_isolation_report = report
    st.session_state.extended_input_unlocked = True
    st.session_state.isolation_report_count = (
        int(st.session_state.get("isolation_report_count", 0)) + 1
    )
    st.session_state.jaggedness_index = float(report.get("jaggedness_index", 0))
    st.session_state.narrative_precision = float(
        report.get("narrative_precision", 50.0)
    )

    with st.chat_message("assistant", avatar=display["emoji"]):
        from isolation_analysis import render_isolation_report_blocks

        render_isolation_report_blocks(report)

    full_reply = format_full_isolation_report_message(report)
    _append_message("assistant", full_reply, display=full_reply, learning_report=True)

    if db.is_connected:
        sig = report.get("signals") or {}
        ok, err = save_isolation_turn_local(
            db,
            nickname=st.session_state.participant_id,
            user_message="[숲·내면항해일지·내부]",
            assistant_message=full_reply,
            participant_id=st.session_state.participant_id,
            password_hash=st.session_state.password_hash,
            lang=get_lang(),
            gender=st.session_state.gender,
            age_group=st.session_state.age_group,
            education=st.session_state.life_stage,
            user_message_ko="[숲·내면항해일지]",
            assistant_message_ko=full_reply,
            giant_name=display.get("label", "연결의 동행자"),
            profile=st.session_state.profile,
            narrative_stage="숲_리포트",
            metaphors=str(report.get("hbridge_summary", ""))[:500],
            turning_points=json.dumps(sig, ensure_ascii=False)[:2000],
            turn_type="isolation_report",
            module_type="isolation",
            isolation_signals_json=json.dumps(sig, ensure_ascii=False)[:8000],
        )
        if not ok:
            st.warning(_db_save_warning(err))
    st.rerun()


def _render_isolation_progress_header() -> dict[str, Any] | None:
    if st.session_state.conversation_closed:
        return None
    _html_layout_marker("isolation-progress-marker")
    prog = _render_reflection_depth_gauge()
    turns = effective_user_turn_count()
    asset = st.session_state.get("last_isolation_asset")
    report = st.session_state.get("last_isolation_report")
    if turns < MIN_USER_TURNS_FOR_ASSET and not asset and not report:
        st.markdown(
            f'<p class="midpoint-encourage-msg">{html.escape(t("isolation_encourage_before_unlock"))}</p>',
            unsafe_allow_html=True,
        )
    # 회복 신호·4대 렌즈: 내담자 UI 비노출 — Supabase signals_json·LLM 백엔드만 유지
    return dict(prog)


def _render_isolation_actions(prog: dict[str, Any] | None) -> None:
    if st.session_state.conversation_closed or prog is None:
        return
    _html_layout_marker("isolation-actions-marker")
    turns = effective_user_turn_count()
    asset = st.session_state.get("last_isolation_asset")
    report = st.session_state.get("last_isolation_report")

    if isinstance(asset, dict) and asset.get("section_identity_asset"):
        with st.expander(t("isolation_asset_btn"), expanded=False):
            from isolation_analysis import render_isolation_asset_blocks

            render_isolation_asset_blocks(asset)

    if turns >= MIN_USER_TURNS_FOR_ASSET and not isinstance(asset, dict):
        if st.button(
            t("isolation_asset_btn"),
            key="isolation_asset_btn",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.pending_isolation_asset = True
            st.rerun()

    if turns < MIN_USER_TURNS_FOR_REPORT:
        return

    btn = (
        t("isolation_report_btn_rerun")
        if st.session_state.get("isolation_report_count", 0)
        else t("isolation_report_btn")
    )
    if st.button(btn, key="isolation_report_btn", use_container_width=True, type="primary"):
        st.session_state.pending_isolation_report = True
        st.rerun()


def _render_learning_progress_header() -> dict[str, Any] | None:
    if st.session_state.conversation_closed:
        return None
    _html_layout_marker("learning-progress-marker")
    prog = _render_reflection_depth_gauge()
    turns = effective_user_turn_count()
    need = MIN_USER_TURNS_FOR_LEARNING_REPORT
    eligible = turns >= need or bool(prog.get("button_eligible"))
    report = st.session_state.get("last_learning_report")
    if not eligible and not report:
        st.markdown(
            f'<p class="midpoint-encourage-msg">{html.escape(t("learning_encourage_before_unlock"))}</p>',
            unsafe_allow_html=True,
        )
    # 학습 모듈: 대화 중 렌즈 축 캡션 비노출 (백엔드 신호·리포트만 유지)
    prog = dict(prog)
    prog["button_eligible"] = turns >= need
    return prog


def _render_learning_actions(prog: dict[str, Any] | None) -> None:
    if st.session_state.conversation_closed or prog is None:
        return
    if not is_valid_learning_audience(
        str(st.session_state.get("learning_audience") or "")
    ):
        return
    _html_layout_marker("learning-actions-marker")
    turns = effective_user_turn_count()
    need = MIN_USER_TURNS_FOR_LEARNING_REPORT
    eligible = turns >= need or bool(prog.get("button_eligible"))
    report = st.session_state.get("last_learning_report")
    unlocked = bool(st.session_state.get("extended_input_unlocked"))

    if isinstance(report, dict) and report:
        with st.expander(t("learning_report_view_expand"), expanded=False):
            _render_learning_report_blocks(report)

    if not eligible:
        return

    btn_label = (
        t("learning_report_btn_rerun")
        if unlocked
        else t("learning_report_btn")
    )
    if st.button(
        btn_label,
        key="learning_report_btn",
        use_container_width=True,
        type="primary" if not unlocked else "secondary",
    ):
        st.session_state.pending_learning_report = True
        st.rerun()


def _render_midpoint_progress_header() -> dict[str, Any] | None:
    """대화 패널 상단 — 성찰 게이지·잠금 전 안내."""
    if st.session_state.conversation_closed:
        return None
    _html_layout_marker("midpoint-section-marker")
    prog = _render_reflection_depth_gauge()
    turns = effective_user_turn_count()
    need = MIN_USER_TURNS_FOR_MIDPOINT
    eligible = turns >= need or bool(prog.get("button_eligible"))
    report = st.session_state.get("last_midpoint_report")
    if not eligible and not report:
        st.markdown(
            f'<p class="midpoint-encourage-msg">{t("midpoint_encourage_before_unlock")}</p>',
            unsafe_allow_html=True,
        )
    return prog


def _render_midpoint_actions(prog: dict[str, Any] | None) -> None:
    """채팅 메시지 아래 — 마음 지도 버튼·리포트 다시 보기."""
    if st.session_state.conversation_closed or prog is None:
        return
    _html_layout_marker("midpoint-actions-below-chat-marker")
    _render_midpoint_unlock_ui(prog)


def _render_reflection_depth_gauge() -> dict[str, Any]:
    """성찰의 깊이 게이지 (10회 대화 기준)."""
    turns = effective_user_turn_count()
    prog = narrative_assetization_progress(
        st.session_state.messages,
        user_turns=turns,
    )
    _html_layout_marker("narrative-asset-progress-marker")
    st.markdown(f"**{t('reflection_depth_gauge_label')}**")
    st.progress(min(prog["percent"] / 100.0, 1.0))

    n = prog["user_turns"]
    need = MIN_USER_TURNS_FOR_MIDPOINT
    unlocked = bool(st.session_state.get("extended_input_unlocked"))
    if unlocked or n >= need:
        st.caption(t("narrative_asset_progress_ready"))
    else:
        st.caption(
            t("narrative_asset_progress_turns").format(
                current=n, need=need, percent=prog["percent"]
            )
        )
    # 턴 수 기준으로 버튼 노출 (게이지 품질 점수와 분리)
    prog = dict(prog)
    prog["button_eligible"] = n >= need
    return prog


def _render_midpoint_unlock_ui(prog: dict[str, Any]) -> None:
    """10회 이상: 중간 정리 버튼 (완료 후에도 다시 보기·재생성)."""
    turns = effective_user_turn_count()
    need = MIN_USER_TURNS_FOR_MIDPOINT
    eligible = turns >= need or bool(prog.get("button_eligible"))
    report = st.session_state.get("last_midpoint_report")
    unlocked = bool(st.session_state.get("extended_input_unlocked"))

    if isinstance(report, dict) and report:
        with st.expander(t("midpoint_view_expand"), expanded=False):
            _render_midpoint_report_blocks(report)

    if not eligible:
        return

    _html_layout_marker("midpoint-btn-marker", "midpoint-btn-reveal-marker")
    btn_label = (
        t("midpoint_analysis_btn_rerun")
        if unlocked
        else t("midpoint_analysis_btn")
    )
    if st.button(
        btn_label,
        key="midpoint_analysis_btn",
        use_container_width=True,
        type="primary" if not unlocked else "secondary",
    ):
        st.session_state.pending_midpoint_analysis = True
        st.rerun()


def _inject_chat_input_focus() -> None:
    """첫 대화 화면 — 하단 입력창으로 포커스·스크롤."""
    components.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;
            const areas = doc.querySelectorAll("textarea");
            for (let i = areas.length - 1; i >= 0; i--) {
                const ta = areas[i];
                if (!ta || ta.offsetParent === null) continue;
                const ph = (ta.getAttribute("placeholder") || "").trim();
                if (!ph) continue;
                ta.focus({ preventScroll: false });
                try {
                    ta.scrollIntoView({ behavior: "smooth", block: "center" });
                } catch (e) {
                    ta.scrollIntoView();
                }
                break;
            }
        })();
        </script>
        """,
        height=0,
    )


def _is_mobile_client() -> bool:
    """모바일·태블릿으로 확실할 때만 True. PC는 본문 텍스트 입력(데스크톱 작성기)."""
    try:
        ctx = getattr(st, "context", None)
        headers = getattr(ctx, "headers", None) if ctx is not None else None
        if headers is None:
            return False
        ch_mobile = (
            headers.get("sec-ch-ua-mobile") or headers.get("Sec-CH-UA-Mobile") or ""
        ).strip()
        if ch_mobile == "?1":
            return True
        if ch_mobile == "?0":
            return False
        ua = (headers.get("user-agent") or headers.get("User-Agent") or "").lower()
        if not ua:
            return False
    except Exception:  # noqa: BLE001
        return False
    if any(
        s in ua
        for s in (
            "mobi",
            "android",
            "iphone",
            "ipad",
            "ipod",
            "iemobile",
            "blackberry",
            "webos",
        )
    ):
        return True
    return False


def _render_composer_text_row(
    *,
    layout_marker: str,
    send_marker: str,
    input_key: str,
    send_key: str,
    placeholder: str,
    input_height: int = 88,
) -> str:
    """텍스트 영역 + 보내기 — PC·모바일 공통(Cloud PC에서 st.chat_input 미표시 대응)."""
    max_chars = _input_char_limit()
    if layout_marker:
        _html_layout_marker(layout_marker)
    text_col, send_col = st.columns([5.2, 1], gap="small")
    with text_col:
        draft = st.text_area(
            "chat_message",
            key=input_key,
            height=input_height,
            placeholder=placeholder,
            label_visibility="collapsed",
            max_chars=max_chars,
        )
        current_len = len(st.session_state.get(input_key, "") or "")
        st.markdown(
            f'<p class="char-counter-hint">({current_len:,} / {max_chars:,}자)</p>',
            unsafe_allow_html=True,
        )
        if st.session_state.get("extended_input_unlocked"):
            st.caption(t("midpoint_char_mobile_hint"))
    with send_col:
        _html_layout_marker(send_marker)
        submitted = st.button(
            t("chat_alt_send"),
            key=send_key,
            type="primary",
            use_container_width=True,
        )
    if not submitted:
        return ""
    text = (draft or "").strip()
    if len(text) > max_chars:
        st.warning(t("midpoint_char_over").format(limit=max_chars))
        return ""
    return text


def render_chat_composer_body() -> bool:
    """사진 + PC/모바일 텍스트 입력·보내기 (st.chat_input 미사용)."""
    if st.session_state.conversation_closed:
        return False

    alt_nonce = int(st.session_state.get("chat_composer_nonce", 0))
    if not st.session_state.messages:
        guide_placeholder = resolve_opening_placeholder(
            t=t,
            age_group=st.session_state.get("age_group", ""),
            gender=st.session_state.get("gender", ""),
            life_stage=st.session_state.get("life_stage", ""),
        )
    else:
        guide_placeholder = t("chat_composer_guide")
    photo = None

    if _is_mobile_client():
        _html_layout_marker("mobile-chat-composer-marker")
        with st.expander(t("chat_photo_row_caption"), expanded=False):
            photo = st.file_uploader(
                t("chat_photo_label"),
                type=["jpg", "jpeg", "png", "webp"],
                key="chat_photo_upload",
                label_visibility="collapsed",
            )
        text = _render_composer_text_row(
            layout_marker="",
            send_marker="mobile-chat-send-marker",
            input_key=f"mobile_chat_input_{alt_nonce}",
            send_key=f"mobile_send_{alt_nonce}",
            placeholder=guide_placeholder,
            input_height=76,
        )
    else:
        st.caption(t("chat_photo_row_caption"))
        photo = st.file_uploader(
            t("chat_photo_label"),
            type=["jpg", "jpeg", "png", "webp"],
            key="chat_photo_upload",
            label_visibility="collapsed",
        )
        desktop_placeholder = (
            t("chat_ph_giant")
            if st.session_state.phase != PHASE_COLLECT
            else guide_placeholder
        )
        text = _render_composer_text_row(
            layout_marker="desktop-chat-composer-marker",
            send_marker="desktop-chat-send-marker",
            input_key=f"desktop_chat_input_{alt_nonce}",
            send_key=f"desktop_send_{alt_nonce}",
            placeholder=desktop_placeholder,
        )

    image_bytes: bytes | None = None
    image_mime: str | None = None
    if photo is not None:
        image_bytes = photo.getvalue()
        image_mime = photo.type or "image/jpeg"

    if text or image_bytes:
        _enqueue_chat_turn(text, image_bytes=image_bytes, image_mime=image_mime)
        _bump_chat_composer_nonce()
        st.rerun()
        return True

    if not st.session_state.messages and not st.session_state.get(
        "_chat_input_focused"
    ):
        st.session_state._chat_input_focused = True
        _inject_chat_input_focus()
    return False


def main() -> None:
    try:
        _run_app()
    except Exception as exc:  # noqa: BLE001
        st.error(
            "화면을 불러오는 중 오류가 났습니다. "
            "브라우저를 **새로고침(F5)** 하거나, 상단 **🔄** 버튼으로 처음부터 다시 시작해 주세요."
        )
        with st.expander("오류 상세 (개발자용)"):
            st.code(str(exc))


def _run_app() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(FULL_WIDTH_LAYOUT_CSS, unsafe_allow_html=True)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    _init_session_state()
    sync_landing_module_from_query()
    reconcile_landing_module_session()
    sync_home_intro_revealed()
    if _is_preview_mode():
        st.session_state.home_intro_revealed = True

    db = resolve_active_db()

    view = st.session_state.get("current_view", VIEW_HOME)
    chat_screen = is_ready_for_chat() and view == VIEW_APP
    home_gate = view in (VIEW_HOME, VIEW_INTRO) and not st.session_state.get(
        "home_intro_revealed", False
    )
    if not home_gate:
        render_hybrid_nav(include_lang=not chat_screen)

    if view == VIEW_INQUIRY:
        with st.container():
            _html_layout_marker("app-content-pad-marker")
            render_inquiry_page(db)
            render_lab_footer()
        return

    if view in (VIEW_HOME, VIEW_INTRO):
        show_footer = render_main_home()
        if show_footer:
            with st.container():
                _html_layout_marker("home-foot-marker")
                render_home_footer_minimal()
            render_inquiry_fab(above_chat_input=False)
        return

    if not is_ready_for_chat():
        with st.container():
            _html_layout_marker("app-content-pad-marker")
            st.markdown(
                f'<h3 class="hub-page-title">🌿 {html.escape(t("app_title"))}</h3>',
                unsafe_allow_html=True,
            )
            render_hub_slogan_banner()
            render_onboarding(db)
            render_lab_footer()
        render_inquiry_fab(above_chat_input=False)
        return

    gemini_ok, gemini_error = init_gemini()
    display = resolve_companion_display()
    render_chat_toolbar(gemini_ok, gemini_error, db)

    with st.container():
        _html_layout_marker("app-content-pad-marker", "chat-content-pad-marker")
        if _is_preview_mode():
            if st.button("🌅 미리보기 세션 시작 (가입 생략)", key="start_preview_session"):
                _apply_preview_session()
                st.rerun()
        if st.session_state.preview_mode:
            st.markdown(
                '<p class="preview-banner">🌅 낮막 미리보기 — UI 흐름 확인용 (실제 저장·API는 동작)</p>',
                unsafe_allow_html=True,
            )
        render_main_header(display)
        show_admin_reply_banner()
        if st.session_state.pop("conversation_restored", False):
            st.info(
                "이전에 나눈 대화와 마음 지도를 불러왔어요. 이어서 이야기해 주세요. 🌿"
            )
        if st.session_state.diet_applied_count > 0:
            st.markdown(
                f'<div class="diet-banner">이전 이야기는 요약해 두었어요 '
                f"({st.session_state.diet_applied_count}회).</div>",
                unsafe_allow_html=True,
            )
        if not gemini_ok:
            st.warning(gemini_error or t("err_dialogue_unavailable"))
            if gemini_error and "leaked" in gemini_error.lower():
                st.markdown(t("err_gemini_leaked"))

        composer_queued = False
        if st.session_state.conversation_closed:
            render_chat_area(display)
        else:
            with st.container(border=True):
                _html_layout_marker("unified-chat-panel-marker")
                audience_locked = (
                    render_learning_audience_selector() if _is_learning_mode() else False
                )
                if _is_isolation_mode():
                    iso_prog = _render_isolation_progress_header()
                    render_chat_area(display)
                    _render_isolation_actions(iso_prog)
                    composer_queued = render_chat_composer_body()
                elif _is_learning_mode():
                    learning_prog = (
                        None
                        if audience_locked
                        else _render_learning_progress_header()
                    )
                    if not audience_locked:
                        render_chat_area(display)
                        _render_learning_actions(learning_prog)
                        composer_queued = render_chat_composer_body()
                    else:
                        composer_queued = False
                else:
                    midpoint_prog = _render_midpoint_progress_header()
                    render_chat_area(display)
                    _render_midpoint_actions(midpoint_prog)
                    composer_queued = render_chat_composer_body()

    if not st.session_state.conversation_closed and not composer_queued:
        if st.session_state.pop("pending_isolation_report", False):
            execute_isolation_report_analysis(display, db)
        elif st.session_state.pop("pending_isolation_asset", False):
            execute_isolation_asset_analysis(display, db)
        elif st.session_state.pop("pending_learning_report", False):
            execute_learning_report_analysis(display, db)
        elif st.session_state.pop("pending_midpoint_analysis", False):
            execute_midpoint_analysis(display, db)
        pending = _take_pending_turn()
        if pending:
            if gemini_ok:
                handle_chat_turn(
                    pending.get("text") or "",
                    display,
                    gemini_ok,
                    db,
                    image_bytes=pending.get("image_bytes"),
                    image_mime=pending.get("image_mime"),
                )
            else:
                st.error(gemini_error or t("err_dialogue_unavailable"))

    render_inquiry_fab()
    with st.container():
        _html_layout_marker("app-content-pad-marker")
        render_lab_footer()


# Streamlit Cloud는 스크립트를 매 rerun마다 실행 — main()을 항상 호출
main()
