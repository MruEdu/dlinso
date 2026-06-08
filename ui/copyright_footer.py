"""심플 영어 판권 푸터 — 홈·로그인·서비스 공통."""

from __future__ import annotations

import streamlit as st


def render_copyright_footer() -> None:
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #888888; font-size: 0.82rem; line-height: 1.6; margin-top: 15px; margin-bottom: 4px; font-family: sans-serif;">
        <p style="margin: 0; font-weight: 500;">
            Copyright © 2026 <b>DLINSO</b>. All Rights Reserved.
        </p>
        <p style="margin: 3px 0 0 0; font-size: 0.75rem; color: #aaaaaa;">
            Designed and Developed by <b>Dr. Hyun</b> (Contact: <a href="mailto:hyc6999@gmail.com" style="color: #888888; text-decoration: underline;">hyc6999@gmail.com</a>)
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
