"""About dlinso — 철학·모듈 안내 다이얼로그."""

from __future__ import annotations

import html

import streamlit as st

from i18n import get_lang, t
from modules.home_registry import LANDING_MODULES


def about_intro_panel_copy() -> dict[str, str]:
    """홈 카드 상단 상시 노출용 짧은 소개."""
    if get_lang() == "ko":
        return {
            "title": "About dlinso",
            "lead": (
                "dlinso는 「모든 삶은 예술이 된다」는 믿음 위에 세워진 "
                "디지털 서사 기록실(Dlinso Narrative Archive)입니다. "
                "검사나 채점이 아니라, 당신의 말과 기억을 인출·기록합니다."
            ),
            "philosophy": (
                "삶의 고비마다 남는 것은 점수가 아니라 이야기입니다. "
                "dlinso는 그 이야기를 예술처럼 정리하고, 스스로를 다시 바라보게 돕습니다."
            ),
        }
    return {
        "title": "About dlinso",
        "lead": (
            "dlinso is a digital Narrative Archive built on the belief that every life becomes art. "
            "We withdraw and record your words—not test or grade."
        ),
        "philosophy": (
            "What remains at turning points is story, not scores. "
            "dlinso helps you arrange that story—warm yet grounded, never distant."
        ),
    }


def about_intro_panel_html() -> str:
    c = about_intro_panel_copy()
    tagline = html.escape(t("brand_tagline"))
    return (
        '<section class="dlinso-about-panel" aria-label="about dlinso">'
        f'<h2 class="dlinso-about-panel-title">{html.escape(c["title"])}</h2>'
        f'<p class="dlinso-about-panel-lead">{html.escape(c["lead"])}</p>'
        f'<p class="dlinso-about-panel-body">{html.escape(c["philosophy"])}</p>'
        f'<p class="dlinso-about-panel-tagline">「{tagline}」</p>'
        "</section>"
    )


def _about_copy() -> dict[str, str]:
    if get_lang() == "ko":
        return {
            "title": "About dlinso",
            "lead": (
                "dlinso는 「모든 삶은 예술이 된다」는 믿음 위에 세워진 "
                "디지털 서사 기록실(Dlinso Narrative Archive)입니다. "
                "검사나 채점이 아니라, 당신의 말과 기억을 인출·기록합니다."
            ),
            "philosophy_h": "철학",
            "philosophy": (
                "삶의 고비마다 남는 것은 점수가 아니라 이야기입니다. "
                "dlinso는 그 이야기를 예술처럼 정리하고, 스스로를 다시 바라보게 돕습니다. "
                "따뜻하지만 가볍지 않고, 신비롭되지만 멀리 두지 않습니다."
            ),
            "modules_h": "서사 기록실",
            "close": "닫기",
        }
    return {
        "title": "About dlinso",
        "lead": (
            "dlinso is a digital Narrative Archive built on the belief that "
            "every life becomes art. We withdraw and record your words—not test or grade."
        ),
        "philosophy_h": "Philosophy",
        "philosophy": (
            "What remains at turning points is story, not scores. "
            "dlinso helps you arrange that story like art—warm yet grounded."
        ),
        "modules_h": "Narrative Archive",
        "close": "Close",
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

    @st.dialog("About dlinso", width="large")  # type: ignore[misc]
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
