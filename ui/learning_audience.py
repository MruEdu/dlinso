"""배움 여정 — 이야기 화자(학생·엄마·아빠·조부모·교사) 선택 UI."""

from __future__ import annotations

import html

import streamlit as st

from i18n import t
from modes.learning import (
    AUDIENCE_FATHER,
    AUDIENCE_GRANDPARENT,
    AUDIENCE_MOTHER,
    AUDIENCE_STUDENT,
    AUDIENCE_TEACHER,
    LEARNING_AUDIENCE_IDS,
    audience_i18n_key,
    is_adult_learning_proxy,
    is_valid_learning_audience,
)

LEARNING_AUDIENCE_CSS = """
<style>
.learning-role-panel {
  background: linear-gradient(165deg, #f7f4ef 0%, #eef5ea 100%);
  border: 1px solid rgba(60, 90, 55, 0.14);
  border-radius: 14px;
  padding: 1.1rem 1.15rem 1rem;
  margin: 0.35rem 0 0.85rem;
}
.learning-role-title {
  font-size: clamp(1.05rem, 3.2vw, 1.22rem);
  font-weight: 700;
  color: #2d3a28;
  margin: 0 0 0.35rem;
}
.learning-role-lead {
  font-size: clamp(0.92rem, 2.8vw, 1.02rem);
  color: #444;
  line-height: 1.55;
  margin: 0 0 0.75rem;
}
.learning-role-hint {
  font-size: clamp(0.86rem, 2.6vw, 0.94rem);
  color: #5a5048;
  line-height: 1.5;
  margin: 0.65rem 0 0;
  padding: 0.55rem 0.7rem;
  background: rgba(255,255,255,0.55);
  border-radius: 8px;
  border-left: 3px solid #6c8f5c;
}
.learning-role-card-label {
  font-size: clamp(0.9rem, 2.8vw, 0.98rem) !important;
  font-weight: 600 !important;
}
</style>
"""

def render_learning_audience_selectbox(*, key: str, label: str | None = None) -> str:
    """드롭다운 — 가입 폼·설정용."""
    return st.selectbox(
        label or t("learning_role_title"),
        options=list(LEARNING_AUDIENCE_IDS),
        format_func=lambda aid: t(audience_i18n_key(aid)),
        key=key,
    )


def _role_hint_for(audience: str) -> str:
    if is_adult_learning_proxy(audience):
        return t("learning_role_hint_proxy")
    if audience == AUDIENCE_STUDENT:
        return t("learning_role_hint_student")
    return t("learning_role_intro")


def render_learning_audience_selector() -> bool:
    """
    채팅 전 화자 미선택 시 True (채팅 잠금).
    선택 후 세션 learning_audience 저장.
    """
    aud = (st.session_state.get("learning_audience") or "").strip()
    if is_valid_learning_audience(aud):
        return False

    st.markdown(LEARNING_AUDIENCE_CSS, unsafe_allow_html=True)
    st.markdown(
        f'<div class="learning-role-panel">'
        f'<p class="learning-role-title">{html.escape(t("learning_role_title"))}</p>'
        f'<p class="learning-role-lead">{html.escape(t("learning_role_intro"))}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )

    picked = st.radio(
        t("learning_role_title"),
        options=list(LEARNING_AUDIENCE_IDS),
        format_func=lambda aid: t(audience_i18n_key(aid)),
        key="learning_audience_chat_pick",
        horizontal=True,
        label_visibility="collapsed",
    )
    st.markdown(
        f'<p class="learning-role-hint">{html.escape(_role_hint_for(picked))}</p>',
        unsafe_allow_html=True,
    )

    if st.button(
        t("learning_role_confirm"),
        type="primary",
        use_container_width=True,
        key="learning_audience_confirm",
    ):
        st.session_state.learning_audience = picked
        st.rerun()
    return True
