"""About 들니소 — 철학·모듈 안내 다이얼로그."""

from __future__ import annotations

import html

import streamlit as st

from core.brand import (
    ARCHIVE_NAME_EN,
    BRAND_INVITE_KO,
    BRAND_NAME_EN,
    BRAND_NAME_KO,
    BRAND_NAME_STORY_EN,
    BRAND_NAME_STORY_KO,
)
from i18n import get_lang, t
from modules.home_registry import LANDING_MODULES


def _about_title() -> str:
    if get_lang() == "ko":
        return f"About {BRAND_NAME_KO}"
    return f"About {BRAND_NAME_EN}"


def about_intro_panel_copy() -> dict[str, str]:
    """홈 카드 상단 상시 노출용 짧은 소개."""
    if get_lang() == "ko":
        return {
            "title": _about_title(),
            "lead": (
                f"{BRAND_NAME_KO}는 「모든 삶은 예술이 된다」는 믿음 위에 세워진 "
                "디지털 서사 기록실입니다. 검사나 채점이 아니라, "
                "당신의 말과 기억을 인출·기록합니다."
            ),
            "philosophy": (
                f"{BRAND_NAME_STORY_KO} "
                f"{BRAND_INVITE_KO}. "
                "운영은 바이브스타틱스(VibeStatics)입니다."
            ),
            "operator": "바이브스타틱스(VibeStatics) · vibestatics.com",
        }
    return {
        "title": _about_title(),
        "lead": (
            f"{BRAND_NAME_EN} is a digital Narrative Archive built on the belief that "
            "every life becomes art. We withdraw and record your words—not test or grade."
        ),
        "philosophy": (
            f"{BRAND_NAME_STORY_EN} "
            f"{BRAND_INVITE_EN}. "
            "Operated by VibeStatics (vibestatics.com)."
        ),
    }


def about_intro_panel_html() -> str:
    c = about_intro_panel_copy()
    tagline = html.escape(t("brand_tagline"))
    return (
        f'<section class="dlinso-about-panel" aria-label="about {html.escape(BRAND_NAME_EN)}">'
        f'<h2 class="dlinso-about-panel-title">{html.escape(c["title"])}</h2>'
        f'<p class="dlinso-about-panel-lead">{html.escape(c["lead"])}</p>'
        f'<p class="dlinso-about-panel-body">{html.escape(c["philosophy"])}</p>'
        f'<p class="dlinso-about-panel-tagline">「{tagline}」</p>'
        "</section>"
    )


def _about_copy() -> dict[str, str]:
    if get_lang() == "ko":
        return {
            "title": _about_title(),
            "lead": (
                f"{BRAND_NAME_KO}는 「모든 삶은 예술이 된다」는 믿음 위에 세워진 "
                f"디지털 서사 기록실({ARCHIVE_NAME_EN})입니다. "
                "검사나 채점이 아니라, 당신의 말과 기억을 인출·기록합니다."
            ),
            "philosophy_h": "철학",
            "philosophy": (
                f"{BRAND_NAME_STORY_KO} "
                f"{BRAND_NAME_KO}는 {BRAND_INVITE_KO}—"
                "따뜻하지만 가볍지 않고, 이야기만 남깁니다."
            ),
            "modules_h": "서사 기록실",
            "close": "닫기",
            "site": "",
            "operator": "운영 · VibeStatics (vibestatics.com)",
        }
    return {
        "title": _about_title(),
        "lead": (
            f"{BRAND_NAME_EN} is a digital Narrative Archive built on the belief that "
            "every life becomes art. We withdraw and record your words—not test or grade."
        ),
        "philosophy_h": "Philosophy",
        "philosophy": (
            f"{BRAND_NAME_STORY_EN} "
            f"{BRAND_INVITE_EN}—warm, grounded, story first."
        ),
        "modules_h": "Narrative Archive",
        "close": "Close",
        "site": "",
        "operator": "Operated by VibeStatics (vibestatics.com)",
    }


def _render_about_body() -> None:
    c = _about_copy()
    st.markdown(c["lead"])
    st.markdown(f"**{c['philosophy_h']}**")
    st.markdown(c["philosophy"])
    st.markdown(
        f'<p style="color:#333333;font-size:1.02rem;margin:1rem 0;">'
        f"「{html.escape(t('brand_tagline'))}」</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="color:#666;font-size:0.92rem;margin:0.5rem 0;">'
        f'{html.escape(c["operator"])}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(f"**{c['modules_h']}**")
    for spec in LANDING_MODULES:
        parts = spec.title.split(" · ", 1)
        word = parts[0]
        sub = parts[1] if len(parts) > 1 else ""
        extra = ""
        if not spec.enabled:
            extra = " _(coming soon)_"
        st.markdown(f"**{word}** · {sub}{extra}\n\n{spec.description}")


def _dialog_supported() -> bool:
    return hasattr(st, "dialog")


if _dialog_supported():

    @st.dialog(f"About {BRAND_NAME_KO}", width="large")  # type: ignore[misc]
    def dlinso_about_dialog() -> None:
        _render_about_body()
        c = _about_copy()
        if st.button(c["close"], key="dlinso_about_close", use_container_width=True):
            st.rerun()


def open_dlinso_about() -> None:
    """소개 버튼 핸들러."""
    fn = globals().get("dlinso_about_dialog")
    if callable(fn):
        fn()
    else:
        st.session_state["dlinso_about_expanded"] = True


def render_dlinso_about_expander_if_needed() -> None:
    """dialog 미지원 시 expander 폴백."""
    if not st.session_state.pop("dlinso_about_expanded", False):
        return
    c = _about_copy()
    with st.expander(c["title"], expanded=True):
        _render_about_body()
