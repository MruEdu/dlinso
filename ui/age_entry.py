"""현재 연령·생애주기 표시(프로필) — 시기 선택 UI 없음."""

from __future__ import annotations

import streamlit as st

from i18n import t
from modes.registry import APP_MODES, AppModeSpec


def render_mode_roadmap(*, compact: bool = False) -> None:
    """향후 브랜치 미리보기 — 비활성 모드는 준비 중 표시."""
    st.markdown(
        f'<p class="dlinso-section-label">{html_escape(t("mode_roadmap_title"))}</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(APP_MODES), gap="small")
    for col, spec in zip(cols, APP_MODES, strict=True):
        with col:
            _render_mode_chip(spec, compact=compact)


def _render_mode_chip(spec: AppModeSpec, *, compact: bool) -> None:
    label = t(spec.label_key)
    tag = t(spec.tag_key) if spec.tag_key else ""
    desc = "" if compact else t(spec.desc_key)
    state_cls = "dlinso-mode-chip--on" if spec.enabled else "dlinso-mode-chip--off"
    tag_html = f'<span class="dlinso-mode-tag">{html_escape(tag)}</span>' if tag else ""
    desc_html = (
        f'<span class="dlinso-mode-desc">{html_escape(desc)}</span>' if desc else ""
    )
    st.markdown(
        f'<div class="dlinso-mode-chip {state_cls}">'
        f'<span class="dlinso-mode-label">{html_escape(label)}</span>'
        f"{tag_html}{desc_html}</div>",
        unsafe_allow_html=True,
    )


def render_current_age_context(*, placement: str = "chat") -> None:
    """
    가입 시 저장한 **현재** 연령·생애주기를 안내 (시기 선택 아님).
    placement: 'chat' | 'onboarding'
    """
    age = (st.session_state.get("age_group") or "").strip()
    stage = (st.session_state.get("life_stage") or "").strip()
    if placement == "onboarding":
        st.caption(t("profile_save_hint"))
        return
    if not age and not stage:
        return
    line = t("chat_age_context_caption").format(
        age=age or "—",
        stage=stage or "—",
    )
    st.markdown(
        f'<p class="dlinso-current-age-context">{html_escape(line)}</p>',
        unsafe_allow_html=True,
    )


def html_escape(text: str) -> str:
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
