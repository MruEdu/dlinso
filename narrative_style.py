"""대화 응답 톤 — 공감·재진술(모듈 공통)."""

from __future__ import annotations

EMPATHETIC_REPHRASE_INSTRUCTION = """
[공감·재진술 — 화면에 보이는 AI 답변]
- 참여자 발화를 **오타·깨진 표기 그대로 복사하거나 「」로 재현하지 마세요**.
- 뜻·감정·장면만 살려 **당신의 따뜻한 말**로 되짚거나 은유·비유로 재진술하세요.
- ㅁ ㅓ, ㅓㄱ당, 맣군 등 명백한 오타는 자연스러운 문장으로 고친 뒤 의미만 전달하세요.
- 같은 문장·같은 표현을 두 번 반복하지 마세요.
"""


def user_turn_context_for_llm(last_user: str, *, max_len: int = 200) -> str:
    """직전 발화 — LLM 맥락용. 답변에 원문 복붙 금지."""
    text = (last_user or "").strip()
    if not text:
        return ""
    return (
        f"\n- [방금 참여자 뜻 — 내부 참고만, 답변에 원문·오타 복붙 금지] "
        f"{text[:max_len]}"
    )
