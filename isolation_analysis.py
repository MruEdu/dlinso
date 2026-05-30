"""숲 · 연결의 서사 — 자아성/사회성 자산·최종 서사 리포트 (점수 없음)."""

from __future__ import annotations

import html
import json
from typing import Any

from hbridge_analysis import (
    compute_midpoint_statistics,
    extract_anchor_phrases,
    extract_situational_context,
    format_midpoint_section_body,
    format_sheet_stats_summary,
    sanitize_midpoint_prose,
)
from modes.isolation import MIN_USER_TURNS_FOR_ASSET, MIN_USER_TURNS_FOR_REPORT

TITLE_INNER_STRENGTH = "내면의 힘"
TITLE_LIFE_TEXTURE = "고유한 삶의 무늬"
TITLE_IDENTITY_ASSET = "자아성 자산"
TITLE_SOCIAL_ASSET = "사회성 자산"
TITLE_FOUR_LENSES = "네 가지 렌즈로 본 고립의 서사"
REPORT_PREFACE = (
    "지금까지 나눈 이야기를 바탕으로, 점수 대신 "
    "당신만의 내면의 힘과 삶의 무늬를 서사로 정리했습니다."
)
ASSET_PREFACE = (
    "지금까지의 대화를 바탕으로, 자아성과 사회성의 자산을 "
    "짧게 돌아봅니다. 검사가 아닙니다."
)


def polish_isolation_prose(report: dict[str, Any]) -> dict[str, Any]:
    out = dict(report)
    for key in (
        "asset_preface",
        "section_identity_asset",
        "section_social_asset",
        "isolation_preface",
        "section_inner_strength",
        "section_life_texture",
        "section_four_lenses",
    ):
        raw = out.get(key)
        if isinstance(raw, str) and raw.strip():
            if key.startswith("section_"):
                out[key] = format_midpoint_section_body(raw)
            else:
                out[key] = sanitize_midpoint_prose(raw)
    return out


def compute_isolation_statistics(
    messages: list[dict],
    profile: dict[str, float] | None = None,
) -> dict[str, Any]:
    return compute_midpoint_statistics(messages, profile)


def _signal_line(block: Any) -> str:
    if isinstance(block, dict):
        parts = [str(v) for v in block.values() if v and isinstance(v, str)]
        if block.get("summary"):
            parts.insert(0, str(block["summary"]))
        return " ".join(parts)[:400]
    return str(block or "")[:400]


def compose_asset_fallback(
    signals: dict[str, Any],
    *,
    user_texts: list[str],
    situational: dict[str, str],
) -> dict[str, str]:
    scene = situational.get("scene_phrase", "지금까지의 고립과 연결 이야기")
    quote = ""
    for line in user_texts:
        if len(line) >= 8:
            quote = f"「{line[:36]}」"
            break
    id_block = signals.get("identity") or {}
    soc_block = signals.get("social") or {}
    identity = (
        f"[{scene}] {quote} "
        f"{_signal_line(id_block) or '고립 속에서 자신을 정의하려는 시선이 보입니다.'}"
    ).strip()
    social = (
        f"{_signal_line(soc_block) or '타인·세상과의 관계에 대한 말이 조심스럽게 스며 있습니다.'} "
        "연결에 대한 갈망과 두려움이 함께 있을 수 있습니다."
    ).strip()
    return {
        "asset_preface": ASSET_PREFACE,
        "title_identity_asset": TITLE_IDENTITY_ASSET,
        "title_social_asset": TITLE_SOCIAL_ASSET,
        "section_identity_asset": identity,
        "section_social_asset": social,
    }


def compose_report_fallback(
    signals: dict[str, Any],
    *,
    user_texts: list[str],
    situational: dict[str, str],
) -> dict[str, str]:
    scene = situational.get("scene_phrase", "지금까지의 이야기")
    quote = ""
    for line in user_texts:
        if len(line) >= 6:
            quote = f"「{line[:40]}」"
            break
    dyn = signals.get("dynamics") or {}
    friction = str(dyn.get("friction") or "세상과의 마찰")
    motivation = str(dyn.get("motivation") or "작은 추진")
    inner = (
        f"{quote} 당신의 이야기 속에는 고립을 지키면서도 "
        f"조금씩 움직이려는 {motivation}이 스며 있습니다. "
        "그것이 당신만의 내면의 힘입니다."
    )
    texture = (
        f"평균이 아닌, 당신만의 삶의 무늬가 있습니다. "
        f"{friction}와 맞선 경험이 패턴을 만들었고, "
        "그 무늬는 앞으로의 서사를 쓸 재료가 됩니다."
    )
    lenses = (
        "고립을 스스로 바라보는 시선이 자라고 있습니다.\n\n"
        "가장 안전하다고 느끼는 맥락이 당신만의 지형입니다.\n\n"
        "세상에 대한 생각을 질서로 엮으려는 기질이 보입니다.\n\n"
        f"두려움과 작은 용기 사이에서 {motivation}이 움직이고 있습니다."
    )
    return {
        "isolation_preface": REPORT_PREFACE,
        "title_inner_strength": TITLE_INNER_STRENGTH,
        "title_life_texture": TITLE_LIFE_TEXTURE,
        "title_four_lenses": TITLE_FOUR_LENSES,
        "section_inner_strength": inner,
        "section_life_texture": texture,
        "section_four_lenses": lenses,
        "situational_opening": f"[{scene}]",
    }


def run_isolation_asset_pipeline(
    messages: list[dict],
    profile: dict[str, float] | None,
    *,
    signals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    user_texts = [
        str(m.get("content") or m.get("display") or "").strip()
        for m in messages
        if m.get("role") == "user"
        and str(m.get("content") or m.get("display") or "").strip()
    ]
    stats = compute_isolation_statistics(messages, profile)
    situational = extract_situational_context(user_texts)
    sig = signals or {}
    body = compose_asset_fallback(sig, user_texts=user_texts, situational=situational)
    merged = polish_isolation_prose(
        {
            **body,
            "stats": stats,
            "signals": sig,
            "stats_json": json.dumps(stats, ensure_ascii=False)[:2000],
            "situational_context": situational,
        }
    )
    merged["hbridge_summary"] = format_sheet_stats_summary(merged)
    return merged


def run_isolation_report_pipeline(
    messages: list[dict],
    profile: dict[str, float] | None,
    *,
    signals: dict[str, Any] | None = None,
    age_group: str = "",
    life_stage: str = "",
    participant_id: str = "",
    lang: str = "ko",
) -> dict[str, Any]:
    user_texts = [
        str(m.get("content") or "").strip()
        for m in messages
        if m.get("role") == "user"
        and str(m.get("content") or "").strip()
    ]
    stats = compute_isolation_statistics(messages, profile)
    situational = extract_situational_context(user_texts)
    sig = signals or {}
    body = compose_report_fallback(sig, user_texts=user_texts, situational=situational)
    merged = polish_isolation_prose(
        {
            **body,
            "report_title": "연결의 서사 · 내면 항해 일지",
            "signals": sig,
            "stats": stats,
            "stats_json": json.dumps(stats, ensure_ascii=False)[:2000],
            "jaggedness_index": stats.get("jaggedness_index", 0),
            "narrative_precision": stats.get("narrative_precision", 50),
            "learning_signals": sig,
        }
    )
    merged["hbridge_summary"] = format_sheet_stats_summary(merged)
    return merged


def format_full_asset_message(report: dict[str, Any]) -> str:
    r = polish_isolation_prose(report)
    parts = [
        "### 자아성·사회성 자산",
        str(r.get("asset_preface", "")),
        f"#### {r.get('title_identity_asset', TITLE_IDENTITY_ASSET)}",
        str(r.get("section_identity_asset", "")),
        f"#### {r.get('title_social_asset', TITLE_SOCIAL_ASSET)}",
        str(r.get("section_social_asset", "")),
    ]
    return "\n\n".join(p for p in parts if p.strip())


def format_full_isolation_report_message(report: dict[str, Any]) -> str:
    r = polish_isolation_prose(report)
    title = str(r.get("report_title", "연결의 서사 · 내면 항해 일지"))
    parts = [
        f"### {title}",
        str(r.get("isolation_preface", "")),
        f"#### {r.get('title_inner_strength', TITLE_INNER_STRENGTH)}",
        str(r.get("section_inner_strength", "")),
        f"#### {r.get('title_life_texture', TITLE_LIFE_TEXTURE)}",
        str(r.get("section_life_texture", "")),
        f"#### {r.get('title_four_lenses', TITLE_FOUR_LENSES)}",
        str(r.get("section_four_lenses", "")),
    ]
    return "\n\n".join(p for p in parts if p.strip())


def render_isolation_asset_blocks(report: dict[str, Any]) -> None:
    import streamlit as st

    r = polish_isolation_prose(report)
    st.markdown("### 자아성·사회성 자산")
    pre = str(r.get("asset_preface", "")).strip()
    if pre:
        st.markdown(pre)
    st.markdown(f"#### {r.get('title_identity_asset', TITLE_IDENTITY_ASSET)}")
    st.markdown(str(r.get("section_identity_asset", "")).strip())
    st.markdown(f"#### {r.get('title_social_asset', TITLE_SOCIAL_ASSET)}")
    st.markdown(str(r.get("section_social_asset", "")).strip())


def render_isolation_report_blocks(report: dict[str, Any]) -> None:
    import streamlit as st

    r = polish_isolation_prose(report)
    title = str(r.get("report_title", "연결의 서사 · 내면 항해 일지"))
    st.markdown(f"### {html.escape(title)}")
    pre = str(r.get("isolation_preface", "")).strip()
    if pre:
        st.markdown(pre)
    for tkey, skey in (
        ("title_inner_strength", "section_inner_strength"),
        ("title_life_texture", "section_life_texture"),
        ("title_four_lenses", "section_four_lenses"),
    ):
        st.markdown(f"#### {r.get(tkey, '')}")
        st.markdown(str(r.get(skey, "")).strip())


def render_isolation_recovery_signals(signals: dict[str, Any] | None) -> None:
    """대화 중 H-Bridge — 자아성/사회성 회복 신호 패널 (점수·진단 없음)."""
    import streamlit as st

    from isolation_engine import summarize_recovery_signals

    if not isinstance(signals, dict):
        return
    recap = summarize_recovery_signals(signals)
    quote = recap.get("anchor_quote") or ""
    quote_html = f'<p class="isolation-signal-quote">「{html.escape(quote)}」</p>' if quote else ""
    st.markdown(
        f'<div class="isolation-recovery-panel">'
        f'<p class="isolation-recovery-title">🌲 자아성 · 사회성 회복 신호</p>'
        f'<p class="isolation-recovery-meta">'
        f'어휘 단계: {html.escape(recap.get("lexicon_phase") or "—")} · '
        f'열리는 축: {html.escape(recap.get("thin_axis_label", ""))} · '
        f'신호: {html.escape(recap.get("recovery_strength", ""))}'
        f"</p>"
        f"{quote_html}"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"**자아성** — {recap.get('identity', '')}")
    st.markdown(f"**사회성** — {recap.get('social', '')}")
    fw = str(recap.get("framework_block") or "").strip()
    if fw:
        st.markdown("**네 가지 렌즈**")
        st.markdown(fw)
