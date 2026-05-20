"""연령대 버튼·브랜치 로드맵 UI."""

from __future__ import annotations

import streamlit as st

from i18n import t
from modes.lifespan import select_age_entry
from modes.registry import APP_MODES, AppModeSpec
from personas import AGE_GROUPS


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


def render_age_group_picker(
    *,
    key_prefix: str = "age_entry",
    navigate_on_select: bool = True,
) -> str | None:
    """
    연령대 그리드 버튼.
    선택 시 select_age_entry() 후 선택된 연령대 문자열 반환.
    """
    st.markdown(
        f'<p class="dlinso-section-label">{html_escape(t("age_entry_title"))}</p>',
        unsafe_allow_html=True,
    )
    st.caption(t("age_entry_sub"))

    selected: str | None = None
    n = len(AGE_GROUPS)
    row_size = 3 if n > 4 else n
    for row_start in range(0, n, row_size):
        row_ages = AGE_GROUPS[row_start : row_start + row_size]
        cols = st.columns(len(row_ages), gap="small")
        for col, age in zip(cols, row_ages, strict=True):
            with col:
                if st.button(
                    age,
                    key=f"{key_prefix}_{age}",
                    use_container_width=True,
                    type="primary"
                    if st.session_state.get("entry_age_group") == age
                    else "secondary",
                ):
                    select_age_entry(age)
                    selected = age
                    if navigate_on_select:
                        from core.views import VIEW_APP

                        st.session_state.current_view = VIEW_APP
                    st.rerun()

    preset = (st.session_state.get("entry_age_group") or "").strip()
    if preset:
        st.caption(t("age_entry_selected").format(age=preset))
    return selected


def html_escape(text: str) -> str:
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
