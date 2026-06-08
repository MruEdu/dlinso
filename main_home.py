"""dlinso.com 브랜드 랜딩 — 신비주의 · 서사 기록실."""

from __future__ import annotations

import html

import streamlit as st
import streamlit.components.v1 as components

from core.version import APP_VERSION_LABEL
from i18n import get_lang, render_language_selector, t
from modules.home_registry import (
    LEARNING_SPOTLIGHT_CTA_EN,
    LEARNING_SPOTLIGHT_CTA_KO,
    LEARNING_SPOTLIGHT_LEAD_EN,
    LEARNING_SPOTLIGHT_LEAD_KO,
    LEARNING_SPOTLIGHT_STEPS_EN,
    LEARNING_SPOTLIGHT_STEPS_KO,
    LEARNING_SPOTLIGHT_TITLE_EN,
    LEARNING_SPOTLIGHT_TITLE_KO,
    LANDING_MODULES,
    MODULE_CTA_ICON,
    MODULE_LEARNING,
    active_deep_link_module_id,
    get_landing_module,
    module_cta_label,
    navigate_to_landing_module,
    query_param_str,
)
from ui.dlinso_about import (
    about_intro_panel_html,
    open_dlinso_about,
    render_dlinso_about_expander_if_needed,
)
from ui.copyright_footer import render_copyright_footer

INTRO_BG_TOP = "#faf8f4"
INTRO_BG = "#f0ebe3"
INTRO_BG_EDGE = "#e4ddd2"
SALON_BG_TOP = "#faf9f6"
SALON_BG_BOTTOM = "#e8e4dc"
INTRO_TEXT = "#1f1c18"
INTRO_MUTED = "#5c554c"
TEXT_DARK = "#222222"
TEXT_MID = "#3a3a3a"
TEXT_BODY = "#222222"
FONT_SANS = '"Pretendard Variable", Pretendard, "NanumSquare", "Nanum Square", -apple-system, sans-serif'
FONT_SERIF = '"Noto Serif KR", "Cormorant Garamond", Georgia, serif'

BRAND_LANDING_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Noto+Serif+KR:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
@import url('https://hangeul.pstatic.net/hangeul_static/css/nanum-square.css');

div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) .block-container {{
    font-family: {FONT_SANS};
    color: {TEXT_BODY};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}}

div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker):not(:has(.dlinso-landing-revealed-marker)),
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker):not(:has(.dlinso-landing-revealed-marker)) .main {{
    background: linear-gradient(
        168deg,
        {INTRO_BG_TOP} 0%,
        {INTRO_BG} 45%,
        {INTRO_BG_EDGE} 100%
    ) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker),
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .main {{
    background: linear-gradient(
        168deg,
        {SALON_BG_TOP} 0%,
        #f6f3ed 38%,
        {SALON_BG_BOTTOM} 100%
    ) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-home-mininav-marker) header {{
    visibility: visible !important;
    height: auto !important;
    background: transparent !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-intro-gate-active):not(:has(.dlinso-home-mininav-marker)) header,
div[data-testid="stAppViewContainer"]:has(.dlinso-intro-gate-active):not(:has(.dlinso-home-mininav-marker)) [data-testid="stToolbar"] {{
    visibility: hidden !important;
    height: 0 !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) .block-container {{
    padding-top: 0 !important;
    padding-left: max(0.5rem, env(safe-area-inset-left)) !important;
    padding-right: max(0.5rem, env(safe-area-inset-right)) !important;
    padding-bottom: 1rem !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .block-container {{
    max-width: 940px !important;
    padding-top: 0 !important;
    padding-bottom: 1.75rem !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) header[data-testid="stHeader"],
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) [data-testid="stToolbar"],
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) [data-testid="stStatusWidget"] {{
    height: 0 !important;
    min-height: 0 !important;
    visibility: hidden !important;
    display: none !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) > section.main {{
    padding-top: 0 !important;
}}
/* 하이브리드 네비 — 랜딩 전용 초소형 · 상단 고정 */
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type {{
    position: sticky !important;
    top: 0 !important;
    z-index: 200 !important;
    padding: 0.35rem 0.35rem 0.4rem !important;
    margin: 0 0 0.15rem !important;
    background: rgba(250, 249, 246, 0.94) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    box-shadow: 0 1px 8px rgba(50, 40, 70, 0.08) !important;
    border-bottom: 1px solid rgba(80, 70, 60, 0.08) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type
[data-testid="stSelectbox"] {{
    min-width: 5.25rem !important;
    flex-shrink: 0 !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type
[data-testid="stSelectbox"] div[data-baseweb="select"] {{
    min-height: 2rem !important;
    min-width: 5.25rem !important;
    font-size: 0.78rem !important;
    border-radius: 999px !important;
    background: #fff !important;
    border: 1px solid rgba(60, 50, 40, 0.14) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) .hybrid-brand {{
    line-height: 1.1 !important;
    font-size: clamp(0.8rem, 2.4vw, 0.92rem) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type button {{
    min-height: 1.85rem !important;
    padding: 0.22rem 0.18rem !important;
    font-size: clamp(0.68rem, 2.6vw, 0.84rem) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type [data-testid="stHorizontalBlock"] {{
    gap: 0.08rem !important;
    align-items: center !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) [data-testid="stVerticalBlock"] {{
    gap: 0 !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) div.element-container {{
    margin-bottom: 0 !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-hero--lifted {{
    animation: none !important;
    transform: none !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-domain {{
    font-size: clamp(2.65rem, 8vw, 4.75rem) !important;
    line-height: 1.06 !important;
    letter-spacing: 0.05em !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-tagline {{
    margin-top: clamp(0.45rem, 1.5vw, 0.75rem) !important;
    font-size: clamp(1.35rem, 4.5vw, 2.35rem) !important;
    line-height: 1.28 !important;
    font-weight: 600 !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-plaque {{
    padding: clamp(1.15rem, 4vw, 2rem) clamp(1rem, 4.5vw, 2.35rem) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-about-panel {{
    margin: 0.15rem auto 0.55rem !important;
    padding: 0.75rem 0.85rem 0.7rem !important;
}}
@media (max-width: 600px) {{
    div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
    section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type {{
        padding: 0 0.15rem 0.08rem !important;
    }}
    div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
    section.main .block-container > div[data-testid="stVerticalBlock"]:first-of-type button {{
        min-height: 1.65rem !important;
        padding: 0.15rem 0.08rem !important;
        font-size: 0.62rem !important;
    }}
    div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) .hybrid-brand {{
        font-size: 0.72rem !important;
    }}
    div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker) .block-container {{
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
    }}
    div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-domain {{
        font-size: clamp(2.15rem, 8.5vw, 4.75rem) !important;
    }}
    div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-tagline {{
        font-size: clamp(1.2rem, 4.8vw, 2.1rem) !important;
    }}
    .dlinso-brand-hero--gate .dlinso-brand-domain {{
        font-size: clamp(2.25rem, 9vw, 3.65rem) !important;
    }}
    .dlinso-brand-hero--gate .dlinso-brand-gate-lead {{
        font-size: clamp(1.2rem, 4.8vw, 1.85rem) !important;
    }}
    div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-plaque {{
        padding: clamp(1rem, 3.5vw, 1.65rem) clamp(0.85rem, 4vw, 1.75rem) !important;
    }}
    div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-hero-panel {{
        padding: 0 0.35rem 0 !important;
    }}
}}

.dlinso-intro-atmosphere {{
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
}}
.dlinso-intro-atmosphere::before {{
    content: "";
    position: absolute;
    width: 55vw;
    height: 55vw;
    top: -15%;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 50%;
    background: radial-gradient(circle, rgba(180, 155, 120, 0.22) 0%, transparent 68%);
    animation: dlinsoOrbDrift 14s ease-in-out infinite alternate;
}}
.dlinso-intro-atmosphere::after {{
    content: "";
    position: absolute;
    width: 40vw;
    height: 40vw;
    bottom: 5%;
    right: -8%;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(140, 125, 105, 0.14) 0%, transparent 70%);
    animation: dlinsoOrbDrift 18s ease-in-out infinite alternate-reverse;
}}
.dlinso-brand-noise {{
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 1;
    opacity: 0.035;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}}
.dlinso-premium-bg {{
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
    background: linear-gradient(165deg, #fbfaf7 0%, #f3efe6 42%, #e6e0d4 100%);
}}
.dlinso-bg-vignette {{
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 85% 75% at 50% 45%, transparent 40%, rgba(62, 56, 48, 0.07) 100%);
}}
.dlinso-bg-linen {{
    position: absolute;
    inset: 0;
    opacity: 0.22;
    background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M60 0H0V60' fill='none' stroke='%23b8a99a' stroke-width='0.35' opacity='0.5'/%3E%3C/svg%3E");
}}
.dlinso-bg-arc {{
    position: absolute;
    inset: -10% -5%;
    opacity: 0.14;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 800'%3E%3Cpath d='M0 520 Q300 380 600 450 T1200 400' fill='none' stroke='%23a89582' stroke-width='0.8'/%3E%3Cpath d='M0 580 Q400 480 700 520 T1200 500' fill='none' stroke='%23c4b5a5' stroke-width='0.5'/%3E%3C/svg%3E");
    background-size: cover;
    background-position: center;
}}
.dlinso-bg-orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(40px);
    animation: dlinsoOrbDrift 12s ease-in-out infinite alternate;
}}
.dlinso-bg-orb--1 {{
    width: min(420px, 55vw);
    height: min(420px, 55vw);
    top: -8%;
    left: 12%;
    background: rgba(214, 195, 168, 0.45);
}}
.dlinso-bg-orb--2 {{
    width: min(360px, 48vw);
    height: min(360px, 48vw);
    bottom: 8%;
    right: 8%;
    background: rgba(196, 186, 170, 0.35);
    animation-duration: 16s;
    animation-direction: alternate-reverse;
}}
.dlinso-bg-orb--3 {{
    width: min(280px, 38vw);
    height: min(280px, 38vw);
    top: 42%;
    left: 55%;
    background: rgba(232, 220, 200, 0.3);
    animation-duration: 20s;
}}
@keyframes dlinsoOrbDrift {{
    0% {{ transform: translate(0, 0) scale(1); }}
    100% {{ transform: translate(12px, -18px) scale(1.04); }}
}}
.dlinso-premium-grain {{
    position: fixed;
    inset: 0;
    z-index: 1;
    pointer-events: none;
    opacity: 0.04;
    mix-blend-mode: multiply;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)'/%3E%3C/svg%3E");
}}
.dlinso-brand-hero-panel {{
    position: relative;
    z-index: 2;
    max-width: 42rem;
    margin: 0 auto 0.25rem;
    padding: 1.25rem 1rem 0.15rem;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-hero-panel {{
    padding: 0 0.65rem 0 !important;
    margin: 0 auto !important;
}}
.dlinso-brand-hero {{
    position: relative; z-index: 2;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center;
    transition: min-height 0.85s cubic-bezier(0.4,0,0.2,1), padding 0.85s ease;
}}
.dlinso-brand-hero--gate {{ min-height: 78vh; cursor: pointer; }}
.dlinso-brand-hero--lifted {{
    min-height: auto;
    padding: 0;
    animation: dlinsoHeroLift 0.9s cubic-bezier(0.4,0,0.2,1) forwards;
}}
@keyframes dlinsoHeroLift {{
    from {{ transform: translateY(10vh); }}
    to {{ transform: translateY(0); }}
}}
.dlinso-brand-domain {{
    font-family: "Cormorant Garamond", "Playfair Display", serif;
    font-size: clamp(2.65rem, 7.5vw, 4rem);
    font-weight: 400;
    letter-spacing: 0.02em;
    color: {INTRO_TEXT};
    margin: 0;
    line-height: 1.12;
    font-feature-settings: "kern" 1, "liga" 1;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-domain {{
    color: {TEXT_DARK};
    font-size: clamp(2.85rem, 8.5vw, 4.85rem);
    font-weight: 500;
    letter-spacing: 0.04em;
}}
.dlinso-brand-plaque {{
    position: relative;
    display: block;
    width: min(100%, 38rem);
    margin: 0 auto;
    padding: clamp(1.4rem, 4.5vw, 2.35rem) clamp(1.35rem, 5vw, 2.85rem);
    text-align: center;
    background: linear-gradient(
        158deg,
        rgba(255, 253, 249, 0.96) 0%,
        rgba(248, 242, 233, 0.92) 48%,
        rgba(241, 234, 223, 0.9) 100%
    );
    border: 1px solid rgba(72, 62, 50, 0.28);
    border-radius: 3px;
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.72) inset,
        0 2px 0 rgba(255, 255, 255, 0.35) inset,
        0 18px 48px rgba(48, 40, 32, 0.1),
        0 4px 14px rgba(48, 40, 32, 0.05);
}}
.dlinso-brand-plaque::before {{
    content: "";
    position: absolute;
    inset: clamp(5px, 1.2vw, 9px);
    border: 1px solid rgba(120, 102, 82, 0.22);
    border-radius: 1px;
    pointer-events: none;
}}
.dlinso-brand-plaque::after {{
    content: "";
    position: absolute;
    left: 12%;
    right: 12%;
    top: 0;
    height: 1px;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(180, 155, 120, 0.45) 20%,
        rgba(180, 155, 120, 0.45) 80%,
        transparent
    );
    pointer-events: none;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-plaque {{
    margin-bottom: 0.15rem;
}}
.dlinso-brand-plaque .dlinso-brand-domain {{
    color: {TEXT_DARK};
}}
.dlinso-brand-plaque .dlinso-brand-gate-lead {{
    margin-top: clamp(0.45rem, 1.5vw, 0.75rem);
    color: {TEXT_DARK};
    opacity: 0.9;
}}
.dlinso-brand-hero--gate .dlinso-brand-plaque {{
    width: min(100%, 40rem);
}}
.dlinso-brand-hero--gate .dlinso-brand-domain {{
    font-size: clamp(2.85rem, 9vw, 4.65rem);
    font-weight: 500;
    letter-spacing: 0.04em;
}}
.dlinso-brand-hero--gate .dlinso-brand-gate-lead {{
    font-size: clamp(1.4rem, 4.8vw, 2.25rem);
    max-width: none;
}}
.dlinso-brand-gate-lead {{
    display: block;
    margin: clamp(0.65rem, 2vw, 1rem) auto 0;
    max-width: 26rem;
    font-family: {FONT_SERIF};
    font-size: clamp(1.15rem, 3.6vw, 1.65rem);
    font-weight: 600;
    line-height: 1.42;
    color: {INTRO_TEXT};
    letter-spacing: 0.01em;
}}
.dlinso-brand-soon {{
    display: block;
    margin-top: 1.15rem;
    font-family: "Cormorant Garamond", "Playfair Display", serif;
    font-size: 0.78rem;
    letter-spacing: 0.28em;
    text-transform: lowercase;
    color: {INTRO_MUTED};
    font-weight: 300;
    font-style: italic;
}}
.dlinso-gate-enter-wrap {{
    position: relative;
    z-index: 40;
    max-width: 22rem;
    margin: 1.5rem auto 0;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-soon {{
    display: none;
}}
.dlinso-brand-tagline {{
    display: none;
    margin: clamp(0.55rem, 1.8vw, 0.85rem) auto 0;
    max-width: 26rem;
    font-size: clamp(1.45rem, 4.8vw, 2.55rem);
    letter-spacing: 0.02em;
    color: {TEXT_DARK};
    font-family: {FONT_SERIF};
    font-weight: 600;
    line-height: 1.32;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-revealed-marker) .dlinso-brand-tagline {{
    display: block;
}}

.dlinso-about-panel {{
    position: relative;
    z-index: 2;
    max-width: 44rem;
    margin: 0.5rem auto 1.25rem;
    padding: 1.15rem 1.2rem 1.1rem;
    text-align: left;
    background: linear-gradient(135deg, #f3ede4 0%, #ebe5da 100%);
    border: 1px solid rgba(34, 34, 34, 0.1);
    border-radius: 8px;
    box-shadow: 0 8px 28px rgba(34, 34, 34, 0.08), 0 2px 6px rgba(34, 34, 34, 0.04);
    animation: dlinsoSalonIn 0.85s ease 0.05s both;
}}
.dlinso-about-panel-title {{
    font-family: {FONT_SERIF};
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    color: {TEXT_MID};
    margin: 0 0 0.55rem 0;
    text-transform: none;
}}
.dlinso-about-panel-lead {{
    font-family: {FONT_SANS};
    font-size: 1.02rem;
    font-weight: 600;
    color: {TEXT_DARK};
    line-height: 1.62;
    margin: 0 0 0.5rem 0;
}}
.dlinso-about-panel-body {{
    font-family: {FONT_SANS};
    font-size: 0.95rem;
    font-weight: 400;
    color: {TEXT_BODY};
    line-height: 1.65;
    margin: 0;
}}
.dlinso-about-panel-tagline {{
    font-family: {FONT_SERIF};
    font-size: 1rem;
    font-weight: 600;
    color: {TEXT_DARK};
    margin: 0.65rem 0 0 0;
    letter-spacing: -0.01em;
}}

.dlinso-salon-guide {{
    position: relative;
    z-index: 2;
    text-align: center;
    max-width: 44rem;
    margin: 0 auto 1.35rem;
    padding: 1rem 1.1rem;
    animation: dlinsoSalonIn 0.9s ease 0.1s both;
    background: rgba(255, 255, 255, 0.55);
    border: 1px solid rgba(34, 34, 34, 0.08);
    border-radius: 8px;
    box-shadow: 0 10px 32px rgba(34, 34, 34, 0.07);
}}
.dlinso-salon-guide-title {{
    font-family: {FONT_SERIF};
    font-size: clamp(1.35rem, 3.2vw, 1.75rem);
    font-weight: 600;
    color: {TEXT_DARK};
    margin: 0 0 0.45rem 0;
    line-height: 1.48;
    letter-spacing: -0.02em;
}}
.dlinso-salon-guide-sub {{
    font-size: clamp(0.98rem, 2.1vw, 1.08rem);
    color: {TEXT_BODY};
    margin: 0;
    line-height: 1.62;
    font-family: {FONT_SANS};
    font-weight: 500;
}}
.dlinso-salon-section {{
    position: relative;
    z-index: 2;
    animation: dlinsoSalonIn 1s ease 0.12s both;
}}
@keyframes dlinsoSalonIn {{
    from {{ opacity: 0; transform: translateY(28px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.dlinso-salon-heading {{
    text-align: center;
    font-family: {FONT_SANS};
    font-size: 0.78rem;
    letter-spacing: 0.28em;
    color: {TEXT_MID};
    margin: 0 0 1.1rem 0;
    font-weight: 600;
    text-transform: uppercase;
}}
.dlinso-brand-title-row {{
    display: inline-flex;
    align-items: baseline;
    justify-content: center;
    gap: 0.42em;
    flex-wrap: nowrap;
    width: 100%;
    margin: 0;
}}
.dlinso-brand-title-row .dlinso-brand-domain {{
    margin: 0;
    display: inline;
}}
.dlinso-version-pill {{
    display: inline-block;
    vertical-align: baseline;
    margin: 0;
    padding: 0.06rem 0.38rem;
    font-family: {FONT_SANS};
    font-size: clamp(0.5rem, 1.5vw, 0.65rem);
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #fff;
    background: linear-gradient(135deg, #9aadc4 0%, #6b849e 100%);
    border: 1px solid rgba(74, 92, 112, 0.35);
    border-radius: 999px;
    box-shadow: 0 1px 3px rgba(92, 112, 136, 0.18);
    transform: translateY(-0.12em);
    flex-shrink: 0;
}}
.dlinso-brand-hero .dlinso-version-pill {{
    display: inline-block;
}}
.dlinso-salon-grid {{
    position: relative;
    z-index: 2;
    max-width: 820px;
    margin: 0 auto;
    padding: 0 0.5rem 1.75rem;
}}
.dlinso-salon-card {{
    background: #ffffff;
    border: 1px solid rgba(34, 34, 34, 0.14);
    border-radius: 8px;
    padding: 1.1rem 1.05rem 0.65rem;
    min-height: 11rem;
    box-shadow: 0 14px 40px rgba(34, 34, 34, 0.1),
                0 4px 12px rgba(34, 34, 34, 0.06),
                0 1px 0 rgba(255, 255, 255, 0.9) inset;
    display: flex; flex-direction: column; height: 100%;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}}
.dlinso-salon-card--live:hover {{
    transform: translateY(-4px);
    box-shadow: 0 22px 52px rgba(34, 34, 34, 0.14),
                0 8px 20px rgba(34, 34, 34, 0.08);
    border-color: rgba(34, 34, 34, 0.22);
}}
.dlinso-salon-card--soon {{ opacity: 0.58; filter: grayscale(0.8); }}
.dlinso-salon-card--spotlight {{
    border: 2px solid rgba(92, 78, 58, 0.35);
    box-shadow: 0 18px 48px rgba(34, 34, 34, 0.12),
                0 0 0 4px rgba(214, 195, 168, 0.25);
}}
.dlinso-salon-col--narrative.dlinso-salon-card--live {{
    border-top: 4px solid #c9a962;
}}
.dlinso-salon-col--learning.dlinso-salon-card--live {{
    border-top: 4px solid #3d5a80;
}}
.dlinso-salon-col--forest.dlinso-salon-card--live {{
    border-top: 4px solid #3d7a5c;
}}
.dlinso-salon-col--emotion.dlinso-salon-card--live {{
    border-top: 4px solid #7a8fa8;
}}
.dlinso-learning-spotlight {{
    position: relative;
    z-index: 2;
    max-width: 44rem;
    margin: 0 auto 1.15rem;
    padding: 1.15rem 1.2rem 1rem;
    background: linear-gradient(145deg, #f0e8dc 0%, #e8dfd2 55%, #e2d6c6 100%);
    border: 1px solid rgba(92, 78, 58, 0.2);
    border-radius: 10px;
    box-shadow: 0 12px 36px rgba(34, 34, 34, 0.09);
    animation: dlinsoSalonIn 0.85s ease both;
}}
.dlinso-learning-spotlight-badge {{
    display: inline-block;
    font-family: {FONT_SANS};
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6a5c48;
    margin-bottom: 0.45rem;
}}
.dlinso-learning-spotlight-title {{
    font-family: {FONT_SERIF};
    font-size: clamp(1.35rem, 3vw, 1.65rem);
    font-weight: 700;
    color: {TEXT_DARK};
    margin: 0 0 0.4rem 0;
}}
.dlinso-learning-spotlight-lead {{
    font-family: {FONT_SANS};
    font-size: 0.98rem;
    font-weight: 500;
    color: {TEXT_BODY};
    line-height: 1.62;
    margin: 0 0 0.45rem 0;
}}
.dlinso-learning-spotlight-steps {{
    font-family: {FONT_SANS};
    font-size: 0.88rem;
    font-weight: 600;
    color: {TEXT_MID};
    margin: 0;
    letter-spacing: 0.01em;
}}
.dlinso-salon-card-word {{
    font-family: {FONT_SERIF};
    font-size: clamp(2rem, 4.5vw, 2.45rem);
    font-weight: 600;
    letter-spacing: -0.02em;
    color: {TEXT_DARK};
    margin: 0 0 0.1rem 0;
    line-height: 1.15;
}}
.dlinso-salon-card-sub {{
    font-family: {FONT_SANS};
    font-size: 0.92rem;
    font-weight: 600;
    color: {TEXT_MID};
    margin: 0 0 0.55rem 0;
    letter-spacing: 0.01em;
}}
.dlinso-salon-card-desc {{
    font-size: 1rem;
    color: {TEXT_BODY};
    line-height: 1.58;
    margin: 0;
    font-family: {FONT_SANS};
    font-weight: 500;
}}
.dlinso-salon-card-desc-en {{
    font-size: 1.02rem;
    color: #333333;
    margin-top: 0.35rem;
    line-height: 1.55;
    font-style: italic;
    font-weight: 500;
    -webkit-font-smoothing: antialiased;
    font-family: "Cormorant Garamond", {FONT_SERIF};
}}
.dlinso-salon-outcomes {{
    margin-top: 0.55rem;
    padding-top: 0.55rem;
    border-top: 1px solid rgba(34, 34, 34, 0.1);
}}
.dlinso-salon-outcome {{
    font-size: 0.88rem;
    color: {TEXT_BODY};
    line-height: 1.5;
    margin: 0 0 0.25rem 0;
    font-family: {FONT_SANS};
    font-weight: 500;
}}
.dlinso-salon-badge {{
    font-size: 0.65rem; letter-spacing: 0.16em;
    text-transform: lowercase; color: {TEXT_MID};
    margin-bottom: 0.55rem; display: block;
}}

div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--narrative) [data-testid="stFormSubmitButton"],
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--learning) [data-testid="stFormSubmitButton"],
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--forest) [data-testid="stFormSubmitButton"],
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--emotion) [data-testid="stFormSubmitButton"] {{
    width: 100% !important;
    margin-top: 0.55rem !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--narrative) button,
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--learning) button,
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--forest) button,
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--emotion) button {{
    width: 100% !important;
    display: block !important;
    margin-top: 0 !important;
    border-radius: 8px !important;
    font-size: 0.96rem !important;
    letter-spacing: 0.03em !important;
    font-weight: 700 !important;
    padding: 0.82rem 1rem !important;
    min-height: 3rem !important;
    font-family: {FONT_SANS} !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--narrative) button {{
    background: linear-gradient(180deg, #d4b96a 0%, #a8863a 55%, #8f7340 100%) !important;
    border: 1px solid #7a6535 !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(168, 134, 58, 0.35) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--learning) button {{
    background: linear-gradient(180deg, #4a6f9a 0%, #2d4a6f 55%, #1e3550 100%) !important;
    border: 1px solid #1a2f48 !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(45, 74, 111, 0.35) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--forest) button {{
    background: linear-gradient(180deg, #52a078 0%, #2d6b4f 55%, #1f4d3a 100%) !important;
    border: 1px solid #1a4030 !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(45, 107, 79, 0.35) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--emotion) button {{
    background: linear-gradient(180deg, #9aadc4 0%, #6b849e 55%, #556b82 100%) !important;
    border: 1px solid #4a5f75 !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(107, 132, 158, 0.35) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--narrative) button:hover {{
    transform: translateY(-2px) !important;
    filter: brightness(1.06) !important;
    box-shadow: 0 8px 20px rgba(168, 134, 58, 0.42) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--learning) button:hover {{
    transform: translateY(-2px) !important;
    filter: brightness(1.06) !important;
    box-shadow: 0 8px 20px rgba(45, 74, 111, 0.42) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--forest) button:hover {{
    transform: translateY(-2px) !important;
    filter: brightness(1.06) !important;
    box-shadow: 0 8px 20px rgba(45, 107, 79, 0.42) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-cta--emotion) button:hover {{
    transform: translateY(-2px) !important;
    filter: brightness(1.06) !important;
    box-shadow: 0 8px 20px rgba(107, 132, 158, 0.42) !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-landing-root-marker)
div[data-testid="column"]:has(.dlinso-salon-card--soon-marker) button {{
    opacity: 0.45 !important;
    background: #f5f5f5 !important;
}}

div[data-testid="stAppViewContainer"]:has(.dlinso-intro-gate-active)
.dlinso-reveal-overlay-marker ~ div button {{
    position: fixed !important; inset: 0 !important;
    width: 100vw !important; height: 100vh !important;
    opacity: 0 !important; z-index: 25 !important;
    border: none !important; background: transparent !important;
    cursor: pointer !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-intro-gate-active)
.dlinso-gate-enter-wrap ~ div button {{
    position: relative !important;
    width: 100% !important;
    height: auto !important;
    opacity: 1 !important;
    z-index: 40 !important;
    cursor: pointer !important;
    min-height: 2.85rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
}}
.dlinso-scroll-cue {{
    text-align: center; font-size: 0.78rem; letter-spacing: 0.12em;
    color: {INTRO_MUTED};
    margin-top: 0.5rem; padding-bottom: 1.5rem; pointer-events: none;
    line-height: 1.5;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-intro-gate-active) .dlinso-brand-domain {{
    color: {TEXT_DARK} !important;
    text-shadow: 0 1px 0 rgba(255,255,255,0.6);
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-intro-gate-active) .dlinso-brand-gate-lead {{
    color: {TEXT_MID} !important;
}}
div[data-testid="stAppViewContainer"]:has(.dlinso-intro-gate-active) .dlinso-brand-soon {{
    color: {INTRO_MUTED} !important;
    font-style: normal;
    letter-spacing: 0.14em;
}}
div[data-testid="stVerticalBlock"]:has(.dlinso-home-mininav-marker) {{
    position: sticky !important;
    top: 0 !important;
    z-index: 200 !important;
    padding: 0.4rem 0 0.5rem !important;
    margin-bottom: 0.25rem !important;
    background: rgba(250, 248, 244, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    border-bottom: 1px solid rgba(80, 70, 60, 0.08) !important;
}}
div[data-testid="stVerticalBlock"]:has(.dlinso-home-mininav-marker)
[data-testid="stSelectbox"] {{
    margin: 0 !important;
}}
div[data-testid="stVerticalBlock"]:has(.dlinso-home-mininav-marker)
[data-testid="stSelectbox"] div[data-baseweb="select"] {{
    font-size: 0.8rem !important;
    min-height: 2.1rem !important;
    border-radius: 999px !important;
    background: #fff !important;
    border: 1px solid rgba(60, 50, 40, 0.16) !important;
    box-shadow: 0 1px 4px rgba(40, 30, 20, 0.06) !important;
}}
.dlinso-home-mininav-wrap {{
    position: relative; z-index: 50;
    padding: 0; max-width: 940px; margin: 0 auto;
}}
.lab-footer-brand {{
    text-align: center; padding: 2rem 1rem 0.85rem;
    color: {TEXT_MID}; font-size: 0.78rem;
    letter-spacing: 0.1em;
    font-family: {FONT_SANS};
    margin: 0;
}}
</style>
"""

REVEAL_INTERACTION_JS = """
<script>
(function () {
  const parentWin = window.parent;
  const doc = parentWin.document;
  function navigateReveal() {
    try {
      const url = new URL(parentWin.location.href);
      if (url.searchParams.get("revealed") === "1") return;
      url.searchParams.set("revealed", "1");
      parentWin.location.assign(url.toString());
    } catch (e) {}
  }
  function clickHiddenReveal() {
    for (const btn of doc.querySelectorAll("button")) {
      const label = (btn.getAttribute("aria-label") || btn.innerText || "").trim();
      if (label === "dlinso-reveal") { btn.click(); return true; }
    }
    return false;
  }
  function isUiControl(ev) {
    const t = ev.target;
    if (!t || !t.closest) return false;
    return Boolean(
      t.closest("[data-testid='stButton'] button") ||
      t.closest("[data-testid='stSelectbox']") ||
      t.closest("[data-baseweb='select']") ||
      t.closest("[data-baseweb='popover']") ||
      t.closest(".dlinso-home-mininav-marker")
    );
  }
  function reveal() {
    if (clickHiddenReveal()) return;
    setTimeout(function () {
      if (!clickHiddenReveal()) navigateReveal();
    }, 150);
  }
  if (!doc.querySelector(".dlinso-intro-gate-active")) return;
  doc.body.addEventListener("click", function (ev) {
    if (isUiControl(ev)) return;
    reveal();
  }, { once: true, capture: true });
  let scrolled = false;
  let scrollReady = false;
  setTimeout(function () { scrollReady = true; }, 900);
  function onScroll() {
    if (!scrollReady || scrolled) return;
    const y = parentWin.scrollY || doc.documentElement.scrollTop || 0;
    if (y > 120) { scrolled = true; reveal(); }
  }
  parentWin.addEventListener("scroll", onScroll, { passive: true });
})();
</script>
"""


def sync_home_intro_revealed() -> bool:
    if st.session_state.get("home_intro_revealed"):
        return True
    if query_param_str("revealed").lower() in ("1", "true", "yes"):
        st.session_state.home_intro_revealed = True
        return True
    return False


def reveal_home_intro() -> None:
    st.session_state.home_intro_revealed = True
    try:
        st.query_params["revealed"] = "1"
    except Exception:  # noqa: BLE001
        pass


def _module_cta_label(module_id: str) -> str:
    base = module_cta_label(module_id, lang=get_lang())
    icon = MODULE_CTA_ICON.get(module_id, "→")
    return f"{icon}  {base}"


def _learning_spotlight_copy() -> dict[str, str]:
    if get_lang() == "ko":
        return {
            "badge": "배움 여정 · 딥링크",
            "title": LEARNING_SPOTLIGHT_TITLE_KO,
            "lead": LEARNING_SPOTLIGHT_LEAD_KO,
            "steps": LEARNING_SPOTLIGHT_STEPS_KO,
            "cta": LEARNING_SPOTLIGHT_CTA_KO,
        }
    return {
        "badge": "Learning journey · deep link",
        "title": LEARNING_SPOTLIGHT_TITLE_EN,
        "lead": LEARNING_SPOTLIGHT_LEAD_EN,
        "steps": LEARNING_SPOTLIGHT_STEPS_EN,
        "cta": LEARNING_SPOTLIGHT_CTA_EN,
    }


def _render_learning_spotlight() -> None:
    """?module=learning — 배움 여정 전용 안내·시작."""
    if active_deep_link_module_id() != MODULE_LEARNING:
        return
    c = _learning_spotlight_copy()
    st.markdown(
        '<section class="dlinso-learning-spotlight" aria-label="learning journey">'
        f'<span class="dlinso-learning-spotlight-badge">{html.escape(c["badge"])}</span>'
        f'<h2 class="dlinso-learning-spotlight-title">{html.escape(c["title"])}</h2>'
        f'<p class="dlinso-learning-spotlight-lead">{html.escape(c["lead"])}</p>'
        f'<p class="dlinso-learning-spotlight-steps">{html.escape(c["steps"])}</p>'
        "</section>",
        unsafe_allow_html=True,
    )
    if st.button(
        c["cta"],
        key="learning_deep_link_start",
        type="primary",
        use_container_width=True,
    ):
        navigate_to_landing_module(MODULE_LEARNING)


def _html_layout_marker(*classes: str) -> None:
    st.markdown(f'<div class="{" ".join(classes)}" aria-hidden="true"></div>', unsafe_allow_html=True)


def _version_pill_html() -> str:
    label = html.escape(APP_VERSION_LABEL)
    return f'<span class="dlinso-version-pill" aria-label="version {label}">{label}</span>'


def _brand_title_row_html(*, include_version: bool = True) -> str:
    version = _version_pill_html() if include_version else ""
    return (
        f'<div class="dlinso-brand-title-row">'
        f'<h1 class="dlinso-brand-domain">dlinso</h1>'
        f"{version}"
        f"</div>"
    )


def render_home_top_bar(*, dark: bool = False) -> None:
    """홈 전용 상단 — 언어 · About dlinso."""
    _html_layout_marker("dlinso-home-mininav-marker")
    st.markdown('<div class="dlinso-home-mininav-wrap">', unsafe_allow_html=True)
    left, mid, right = st.columns([2.2, 1.3, 1.3], gap="small")
    with left:
        color = "#c8c4be" if dark else TEXT_DARK
        st.markdown(
            f'<span style="font-size:0.82rem;letter-spacing:0.2em;color:{color};">dlinso</span>',
            unsafe_allow_html=True,
        )
    with mid:
        render_language_selector(key="home_lang", compact=True)
    with right:
        if st.button(
            t("nav_about"),
            key="home_nav_about",
            use_container_width=True,
            type="secondary",
        ):
            open_dlinso_about()
    st.markdown("</div>", unsafe_allow_html=True)
    render_dlinso_about_expander_if_needed()


def _premium_bg_html() -> str:
    return (
        '<div class="dlinso-premium-bg" aria-hidden="true">'
        '<div class="dlinso-bg-vignette"></div>'
        '<div class="dlinso-bg-linen"></div>'
        '<div class="dlinso-bg-arc"></div>'
        '<div class="dlinso-bg-orb dlinso-bg-orb--1"></div>'
        '<div class="dlinso-bg-orb dlinso-bg-orb--2"></div>'
        '<div class="dlinso-bg-orb dlinso-bg-orb--3"></div>'
        "</div>"
        '<div class="dlinso-premium-grain" aria-hidden="true"></div>'
    )


def _brand_hero_html(*, lifted: bool) -> str:
    hero_cls = "dlinso-brand-hero--lifted" if lifted else "dlinso-brand-hero--gate"
    tagline_text = html.escape(t("brand_tagline"))
    gate_hint = html.escape(t("brand_gate_hint"))
    if lifted:
        plaque_inner = (
            f"{_brand_title_row_html()}"
            f'<p class="dlinso-brand-tagline">{tagline_text}</p>'
        )
    else:
        plaque_inner = (
            f"{_brand_title_row_html()}"
            f'<p class="dlinso-brand-gate-lead">{tagline_text}</p>'
            f'<span class="dlinso-brand-soon">{gate_hint}</span>'
        )
    intro_bg = (
        '<div class="dlinso-intro-atmosphere" aria-hidden="true"></div>'
        '<div class="dlinso-brand-noise" aria-hidden="true"></div>'
    )
    hero_inner = (
        f'<header class="dlinso-brand-hero {hero_cls}">'
        f'<div class="dlinso-brand-plaque">{plaque_inner}</div>'
        f"</header>"
    )
    if lifted:
        return hero_inner
    return intro_bg + hero_inner


def _module_card_title_parts(spec) -> tuple[str, str]:
    lang = get_lang()
    title_src = spec.title if lang == "ko" else (spec.title_en or spec.title)
    parts = title_src.split(" · ", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def _card_html(spec, *, active: bool, spotlight: bool = False) -> str:
    lang = get_lang()
    state = "dlinso-salon-card--live" if active else "dlinso-salon-card--soon"
    marker = "dlinso-salon-card-marker" if active else "dlinso-salon-card--soon-marker"
    spot = " dlinso-salon-card--spotlight" if spotlight else ""
    badge = (
        f'<span class="dlinso-salon-badge">{html.escape(spec.status_badge)}</span>'
        if spec.status_badge
        else ""
    )
    word, sub = _module_card_title_parts(spec)
    word = html.escape(word)
    sub = html.escape(sub)
    sub_html = f'<p class="dlinso-salon-card-sub">{sub}</p>' if sub else ""
    if lang == "ko":
        desc = spec.description
        o1_raw, o2_raw = spec.outcome_line1, spec.outcome_line2
    else:
        desc = spec.description_en or spec.description
        o1_raw = spec.outcome_line1_en or spec.outcome_line1
        o2_raw = spec.outcome_line2_en or spec.outcome_line2
    desc_en = ""
    o1 = html.escape(o1_raw) if o1_raw else ""
    o2 = html.escape(o2_raw) if o2_raw else ""
    outcomes = ""
    if o1 or o2:
        outcomes = (
            '<div class="dlinso-salon-outcomes">'
            + (f'<p class="dlinso-salon-outcome">· {o1}</p>' if o1 else "")
            + (f'<p class="dlinso-salon-outcome">· {o2}</p>' if o2 else "")
            + "</div>"
        )
    col_cls = f"dlinso-salon-col--{html.escape(spec.id)}"
    return (
        f'<article class="dlinso-salon-card {state} {marker}{spot} {col_cls}" '
        f'data-module-id="{html.escape(spec.id)}">'
        f"{badge}"
        f'<h2 class="dlinso-salon-card-word">{word}</h2>{sub_html}'
        f'<p class="dlinso-salon-card-desc">{html.escape(desc)}</p>'
        f"{desc_en}{outcomes}</article>"
    )


def _render_module_card(spec, *, spotlight: bool = False) -> None:
    active = spec.enabled and spec.app_mode
    module_id = spec.id
    if not active:
        st.markdown(_card_html(spec, active=False, spotlight=spotlight), unsafe_allow_html=True)
        st.button(
            t("home_coming_soon"),
            key=f"home_module_disabled_{module_id}",
            disabled=True,
            use_container_width=True,
        )
        return
    with st.form(key=f"home_form_{module_id}", border=False):
        st.markdown(_card_html(spec, active=True, spotlight=spotlight), unsafe_allow_html=True)
        _html_layout_marker(f"dlinso-salon-cta--{module_id}")
        submitted = st.form_submit_button(
            _module_cta_label(module_id),
            use_container_width=True,
        )
    if submitted:
        navigate_to_landing_module(module_id)


def _render_intro_gate() -> None:
    render_home_top_bar(dark=False)
    _html_layout_marker("dlinso-intro-gate-active")
    st.markdown(_brand_hero_html(lifted=False), unsafe_allow_html=True)
    st.markdown('<div class="dlinso-gate-enter-wrap">', unsafe_allow_html=True)
    if st.button(
        t("btn_enter_archive"),
        key="home_reveal_visible",
        type="primary",
        use_container_width=True,
    ):
        reveal_home_intro()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="dlinso-reveal-overlay-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.button("dlinso-reveal", key="home_reveal_fullclick", on_click=reveal_home_intro)
    st.markdown(
        f'<p class="dlinso-scroll-cue">{html.escape(t("home_scroll_cue"))}</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div style="height:18vh" aria-hidden="true"></div>', unsafe_allow_html=True)
    components.html(REVEAL_INTERACTION_JS, height=0)


def _render_salon_section() -> None:
    _html_layout_marker("dlinso-landing-revealed-marker")
    st.markdown(_premium_bg_html(), unsafe_allow_html=True)
    st.markdown('<div class="dlinso-brand-hero-panel">', unsafe_allow_html=True)
    st.markdown(_brand_hero_html(lifted=True), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(about_intro_panel_html(), unsafe_allow_html=True)
    st.markdown(
        f'<div class="dlinso-salon-guide">'
        f'<p class="dlinso-salon-guide-title">{html.escape(t("salon_guide_line"))}</p>'
        f'<p class="dlinso-salon-guide-sub">{html.escape(t("salon_guide_sub"))}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )
    _render_learning_spotlight()
    st.markdown(
        f'<section class="dlinso-salon-section">'
        f'<h2 class="dlinso-salon-heading">{html.escape(t("salon_section_title"))}</h2></section>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="dlinso-salon-grid">', unsafe_allow_html=True)
    learning_focus = active_deep_link_module_id() == MODULE_LEARNING
    narrative = get_landing_module("narrative")
    learning = get_landing_module("learning")
    forest = get_landing_module("forest")
    emotion = get_landing_module("emotion")
    col_narrative, col_learning = st.columns(2, gap="medium")
    with col_narrative:
        if narrative:
            _render_module_card(narrative)
    with col_learning:
        if learning:
            _render_module_card(learning, spotlight=learning_focus)
    st.markdown("<div style='height:0.65rem'></div>", unsafe_allow_html=True)
    col_forest, col_emotion = st.columns(2, gap="medium")
    with col_forest:
        if forest:
            _render_module_card(forest)
    with col_emotion:
        if emotion:
            _render_module_card(emotion)
    st.markdown("</div>", unsafe_allow_html=True)


def render_main_home() -> bool:
    st.markdown(BRAND_LANDING_CSS, unsafe_allow_html=True)
    _html_layout_marker("dlinso-landing-root-marker")
    if "home_intro_revealed" not in st.session_state:
        st.session_state.home_intro_revealed = False
    if sync_home_intro_revealed():
        _render_salon_section()
        return True
    _render_intro_gate()
    return False


def render_home_footer_minimal() -> None:
    st.markdown(
        f'<p class="lab-footer-brand">dlinso · {html.escape(t("brand_tagline"))}</p>',
        unsafe_allow_html=True,
    )
    render_copyright_footer()
