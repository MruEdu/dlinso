"""숨결 · 마음챙김 — 현존·신체 이완 가이드."""

from __future__ import annotations

MODE_ID = "mindfulness"

MINDFULNESS_COMPANION = {
    "label": "마음챙김 가이드",
    "short": "마음챙김",
    "emoji": "🌬️",
}


def get_mindfulness_display() -> dict[str, str]:
    return dict(MINDFULNESS_COMPANION)
