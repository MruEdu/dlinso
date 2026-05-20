"""dlinso 브랜치 레지스트리 — 활성/예정 모드를 한곳에서 관리."""

from __future__ import annotations

from dataclasses import dataclass

MODE_LIFESPAN = "lifespan"
MODE_ASSESSMENT = "assessment"
MODE_COUNSELING = "counseling"
MODE_RESEARCH = "research"


@dataclass(frozen=True, slots=True)
class AppModeSpec:
    """향후 기능 브랜치 메타데이터."""

    id: str
    label_key: str
    desc_key: str
    enabled: bool
    tag_key: str = ""


APP_MODES: tuple[AppModeSpec, ...] = (
    AppModeSpec(
        MODE_LIFESPAN,
        "mode_lifespan_label",
        "mode_lifespan_desc",
        True,
        "mode_tag_active",
    ),
    AppModeSpec(
        MODE_ASSESSMENT,
        "mode_assessment_label",
        "mode_assessment_desc",
        False,
        "mode_tag_soon",
    ),
    AppModeSpec(
        MODE_COUNSELING,
        "mode_counseling_label",
        "mode_counseling_desc",
        False,
        "mode_tag_soon",
    ),
    AppModeSpec(
        MODE_RESEARCH,
        "mode_research_label",
        "mode_research_desc",
        False,
        "mode_tag_soon",
    ),
)

_MODE_BY_ID = {m.id: m for m in APP_MODES}


def default_mode() -> str:
    return MODE_LIFESPAN


def get_mode_spec(mode_id: str) -> AppModeSpec:
    return _MODE_BY_ID.get(mode_id, _MODE_BY_ID[MODE_LIFESPAN])


def list_enabled_modes() -> list[AppModeSpec]:
    return [m for m in APP_MODES if m.enabled]
