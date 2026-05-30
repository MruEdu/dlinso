"""
배움의 정원사 엔진 샌드박스 — learning_engine 직접 대화.

실행:
  streamlit run learning_sandbox.py
"""

from __future__ import annotations

import json
import os

import streamlit as st

from env_config import APP_DIR, credentials_source_label
from i18n import t
from learning_analysis import render_learning_report_blocks
from learning_engine import (
    FOUR_THEORY_KEYS,
    LEARNING_COMPANION_NAME,
    build_full_learning_system_instruction,
    extract_learning_signals,
    generate_learning_narrative_report_for_messages,
    iter_learning_reply_stream,
)
from llm_client import LLMNotConfiguredError, init_llm_client, is_llm_configured
from modes.learning import (
    AUDIENCE_STUDENT,
    LEARNING_AUDIENCE_IDS,
    MIN_USER_TURNS_FOR_LEARNING_REPORT,
    audience_i18n_key,
    get_learning_display,
    is_student_audience,
)

os.chdir(APP_DIR)

SANDBOX_CSS = """
<style>
  .sandbox-banner {
    background: linear-gradient(135deg, #eef5ea 0%, #e8dfd2 100%);
    border: 1px solid rgba(60, 90, 55, 0.18);
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.92rem;
    color: #333;
  }
  .sandbox-axis {
    font-size: 0.82rem;
    color: #444;
    margin: 0.35rem 0;
    line-height: 1.45;
  }
  .sandbox-theory-title {
    font-weight: 600;
    color: #2d4a28;
    margin-top: 0.5rem;
  }
</style>
"""

FOUR_THEORY_LABELS = {
    "bloom": "Bloom · 인지적 창조 (수직)",
    "todd_rose": "Todd Rose · Jagged (수평)",
    "pattern_seeker": "Pattern Seeker · 체계화",
    "dynamics": "Dynamics · 학습 동역학",
}


def _init_sandbox_state() -> None:
    defaults = {
        "sandbox_messages": [],
        "sandbox_audience": AUDIENCE_STUDENT,
        "sandbox_age": "20대",
        "sandbox_stage": "대학·전문대 재학",
        "sandbox_nick": "테스트",
        "sandbox_lang": "ko",
        "sandbox_report_done": False,
        "sandbox_signals": None,
        "sandbox_last_report": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _user_turn_count() -> int:
    return sum(
        1
        for m in st.session_state.sandbox_messages
        if m.get("role") == "user"
        and str(m.get("content") or "").strip()
    )


def _render_four_theory_signals(signals: dict) -> None:
    st.markdown("#### 인출된 4대 이론 신호")
    thin = signals.get("thin_axis", "")
    if thin:
        st.caption(f"다음에 보강할 축: **{FOUR_THEORY_LABELS.get(thin, thin)}** · 출처: {signals.get('source', '—')}")

    for key in FOUR_THEORY_KEYS:
        block = signals.get(key)
        label = FOUR_THEORY_LABELS.get(key, key)
        st.markdown(f'<p class="sandbox-theory-title">{label}</p>', unsafe_allow_html=True)
        if isinstance(block, dict):
            if key == "bloom":
                level = block.get("level", "")
                parts = [f"수준: {level}"] if level else []
                if block.get("summary"):
                    parts.append(str(block["summary"]))
                if block.get("create_aspiration"):
                    parts.append(f"창조 열망: {block['create_aspiration']}")
                text = " · ".join(parts)
            elif key == "todd_rose":
                parts = []
                if block.get("summary"):
                    parts.append(str(block["summary"]))
                peaks = block.get("peak_strengths") or []
                if peaks:
                    parts.append("강점: " + ", ".join(str(p) for p in peaks))
                troughs = block.get("trough_areas") or []
                if troughs:
                    parts.append("보완: " + ", ".join(str(p) for p in troughs))
                if block.get("peak_contexts"):
                    parts.append(f"맥락: {block['peak_contexts']}")
                text = " ".join(parts)
            elif key == "pattern_seeker":
                text = " ".join(
                    str(block.get(k, ""))
                    for k in ("summary", "writing_connection")
                    if block.get(k)
                )
            else:  # dynamics
                text = " | ".join(
                    f"{k}: {block[k]}"
                    for k in ("motivation", "friction", "inertia", "gravity", "synthesis")
                    if block.get(k)
                )
            if text.strip():
                st.markdown(f'<p class="sandbox-axis">{text}</p>', unsafe_allow_html=True)
        elif block:
            st.markdown(f'<p class="sandbox-axis">{block}</p>', unsafe_allow_html=True)

    for legacy_key, legacy_label in (
        ("motivation", "학습 동기 (요약)"),
        ("metacognition", "메타인지 (요약)"),
        ("career_values", "폼나는 삶 (요약)"),
    ):
        val = signals.get(legacy_key, "")
        if val and isinstance(val, str):
            st.markdown(f'<p class="sandbox-axis"><b>{legacy_label}</b>: {val}</p>', unsafe_allow_html=True)

    if signals.get("anchor_quote"):
        st.caption(f"핵심 인용: 「{signals['anchor_quote']}」")

    with st.expander("JSON 원본"):
        st.code(json.dumps(signals, ensure_ascii=False, indent=2), language="json")


def main() -> None:
    st.set_page_config(
        page_title="배움의 정원사 샌드박스",
        page_icon="🌱",
        layout="wide",
    )
    st.markdown(SANDBOX_CSS, unsafe_allow_html=True)
    _init_sandbox_state()

    try:
        init_llm_client()
        api_ok = is_llm_configured()
        api_note = credentials_source_label()
    except LLMNotConfiguredError as exc:
        api_ok = False
        api_note = str(exc)

    aud = st.session_state.sandbox_audience
    report_tone = (
        "성장 가이드 (학생)"
        if is_student_audience(aud)
        else "환경 설계 가이드 (보호자·교사)"
    )

    with st.sidebar:
        st.markdown(f"### 🌱 {LEARNING_COMPANION_NAME}")
        st.caption("소크라테스적 산파술 · learning_engine.py")

        st.markdown("**① 상담 당사자**")
        st.session_state.sandbox_audience = st.selectbox(
            "당신은 누구인가요?",
            list(LEARNING_AUDIENCE_IDS),
            format_func=lambda aid: t(audience_i18n_key(aid)),
            key="sb_audience_radio",
            label_visibility="collapsed",
        )
        st.caption(f"리포트 톤: {report_tone}")

        st.markdown("**② 맥락**")
        st.session_state.sandbox_age = st.selectbox(
            "연령",
            [
                "초등 연령(약 7–12세)",
                "중등 연령(약 13–15세)",
                "고등 연령(약 16–18세)",
                "20대",
                "30대",
                "40대",
            ],
            index=3,
        )
        st.session_state.sandbox_stage = st.text_input("생활·재학 단계", st.session_state.sandbox_stage)
        st.session_state.sandbox_nick = st.text_input("닉네임", st.session_state.sandbox_nick)
        st.session_state.sandbox_lang = st.selectbox("응답 언어", ["ko", "en"], index=0)

        if st.button("대화 초기화", use_container_width=True):
            st.session_state.sandbox_messages = []
            st.session_state.sandbox_report_done = False
            st.session_state.sandbox_signals = None
            st.session_state.sandbox_last_report = None
            st.rerun()

        turns = _user_turn_count()
        st.caption(f"사용자 발화 {turns}회 · 리포트 권장 {MIN_USER_TURNS_FOR_LEARNING_REPORT}회+")

        if st.button("최종 서사 리포트 생성", use_container_width=True, type="primary"):
            if not api_ok:
                st.error(api_note)
            elif turns < 3:
                st.warning("리포트 테스트는 최소 3회 이상 대화 후 생성해 주세요.")
            else:
                with st.spinner("4대 이론·서사 리포트 작성 중…"):
                    st.session_state.sandbox_last_report = (
                        generate_learning_narrative_report_for_messages(
                            st.session_state.sandbox_messages,
                            learning_audience=st.session_state.sandbox_audience,
                            age_group=st.session_state.sandbox_age,
                            life_stage=st.session_state.sandbox_stage,
                            participant_id=st.session_state.sandbox_nick,
                            lang=st.session_state.sandbox_lang,
                        )
                    )
                    st.session_state.sandbox_report_done = True
                st.rerun()

        if st.button("4대 이론 신호 인출 (JSON)", use_container_width=True):
            if not api_ok:
                st.error(api_note)
            elif turns < 1:
                st.warning("한 번 이상 대화한 뒤 인출해 주세요.")
            else:
                with st.spinner("Bloom · Todd Rose · Pattern · Dynamics 인출 중…"):
                    st.session_state.sandbox_signals = extract_learning_signals(
                        st.session_state.sandbox_messages,
                        lang=st.session_state.sandbox_lang,
                    )
                st.rerun()

        st.divider()
        if api_ok:
            st.success(f"LLM 연결됨 · {api_note}")
        else:
            st.error(api_note)

        with st.expander("System Instruction 미리보기"):
            preview = build_full_learning_system_instruction(
                lang=st.session_state.sandbox_lang,
                learning_audience=st.session_state.sandbox_audience,
                age_group=st.session_state.sandbox_age,
                life_stage=st.session_state.sandbox_stage,
                nickname=st.session_state.sandbox_nick,
                user_turns=_user_turn_count(),
                report_completed=st.session_state.sandbox_report_done,
            )
            st.text_area("system", preview, height=360, label_visibility="collapsed")

    display = get_learning_display(st.session_state.sandbox_audience)
    st.markdown(
        f'<div class="sandbox-banner">'
        f"<strong>🌱 {LEARNING_COMPANION_NAME}</strong> · {display['label']} · 샌드박스<br>"
        f"미션: 학습 <b>동역학</b> 인출 · 서사적 통찰 · <b>{report_tone}</b><br>"
        f"4대 렌즈: <b>Bloom</b> · <b>Todd Rose</b> · <b>Pattern Seeker</b> · <b>Dynamics</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

    report = st.session_state.sandbox_last_report
    if isinstance(report, dict) and report.get("section_identity"):
        st.markdown("---")
        render_learning_report_blocks(report)
        sig_in_report = report.get("learning_signals")
        if isinstance(sig_in_report, dict) and sig_in_report:
            with st.expander("리포트 생성 시 인출된 신호"):
                _render_four_theory_signals(sig_in_report)

    signals = st.session_state.sandbox_signals
    if isinstance(signals, dict) and signals:
        st.markdown("---")
        _render_four_theory_signals(signals)

    for msg in st.session_state.sandbox_messages:
        avatar = "🧑" if msg["role"] == "user" else display["emoji"]
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(str(msg.get("display") or msg.get("content") or ""))

    if not api_ok:
        st.warning("API 키를 설정한 뒤 대화를 시작하세요.")
        return

    prompt = st.chat_input("배움 이야기를 적어 보세요…")
    if not prompt:
        return

    st.session_state.sandbox_messages.append(
        {"role": "user", "content": prompt, "display": prompt}
    )
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=display["emoji"]):
        try:
            stream = iter_learning_reply_stream(
                st.session_state.sandbox_messages,
                prompt,
                lang=st.session_state.sandbox_lang,
                learning_audience=st.session_state.sandbox_audience,
                age_group=st.session_state.sandbox_age,
                life_stage=st.session_state.sandbox_stage,
                nickname=st.session_state.sandbox_nick,
                report_completed=st.session_state.sandbox_report_done,
            )
            reply = st.write_stream(stream)
        except LLMNotConfiguredError as exc:
            st.error(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            st.error(f"응답 생성 오류: {exc}")
            return

    reply = (reply or "").strip()
    if reply:
        st.session_state.sandbox_messages.append(
            {"role": "assistant", "content": reply, "display": reply}
        )


if __name__ == "__main__":
    main()
