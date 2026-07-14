"""심플 영어 판권 푸터 — 홈·로그인·서비스 공통."""

from __future__ import annotations

import html

import streamlit as st

from core.brand import BRAND_DOMAIN, BRAND_NAME_KO, BRAND_URL, COPYRIGHT_HOLDER
from core.public_urls import VIBESTATICS_HOME


def render_copyright_footer() -> None:
    vs = html.escape(VIBESTATICS_HOME)
    brand_url = html.escape(BRAND_URL)
    st.markdown("---")
    st.markdown(
        f"""
    <div style="text-align: center; color: #888888; font-size: 0.82rem; line-height: 1.65;
                margin-top: 15px; margin-bottom: 4px; font-family: sans-serif;">
        <p style="margin: 0; font-weight: 500;">
            {html.escape(BRAND_NAME_KO)} · <a href="{vs}" style="color:#6b849e;text-decoration:underline;"
            target="_blank" rel="noopener">VibeStatics (바이브스타틱스)</a>
        </p>
        <p style="margin: 4px 0 0 0; font-size: 0.75rem; color: #999;">
            <a href="{brand_url}" style="color:#888;text-decoration:underline;"
            target="_blank" rel="noopener">{html.escape(BRAND_DOMAIN)}</a>
            · Copyright © 2026 {html.escape(COPYRIGHT_HOLDER)}
        </p>
        <p style="margin: 3px 0 0 0; font-size: 0.75rem; color: #aaaaaa;">
            Dr. Hyun · <a href="mailto:hyc6999@gmail.com"
            style="color: #888888; text-decoration: underline;">hyc6999@gmail.com</a>
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
