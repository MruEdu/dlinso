"""학습 서사 검사 리포트 — 통계·프롬프트·후처리."""

from __future__ import annotations

import html
import json
import re
from typing import Any

from hbridge_analysis import (
    compute_midpoint_statistics,
    extract_anchor_phrases,
    format_midpoint_section_body,
    sanitize_midpoint_prose,
)
from modes.learning import (
    AUDIENCE_FATHER,
    AUDIENCE_GRANDPARENT,
    AUDIENCE_MOTHER,
    AUDIENCE_PARENT,
    AUDIENCE_STUDENT,
    AUDIENCE_TEACHER,
    MIN_USER_TURNS_FOR_LEARNING_REPORT,
    audience_label_ko,
    is_adult_learning_proxy,
    is_student_audience,
)

LEARNING_VOYAGE_LOG_TITLE = "서사적 항해 일지"
TITLE_IDENTITY = "나의 학습 정체성"
TITLE_FOUR_LENSES = "네 가지 렌즈로 본 배움 서사"
TITLE_JAGGED = "들쭉날쭉한 배움 지형"
TITLE_PRESCRIPTION = "동역학적 처방 · 폼나는 삶을 향한 학습 전술"

THEORY_BLOOM_KO = "Bloom · 인지적 창조 (수직적 위계)"
THEORY_TODD_ROSE_KO = "Todd Rose · 평균의 종말 (수평적 Jagged)"
THEORY_PATTERN_KO = "Pattern Seeker · 체계화 지능"
THEORY_DYNAMICS_KO = "Dynamics · 변화의 흐름 (동기·마찰·관성·중력)"

# 교육철학 3렌즈 ↔ 내부 도메인(한글 라벨) 매핑
LENS_BEHAVIORISM_KO = "행동주의 (습관·보상)"
LENS_COGNITIVISM_KO = "인지주의 (메타인지·전략)"
LENS_CONSTRUCTIVISM_KO = "구성주의 (관계·맥락)"
LENS_DOMAIN_GROUPS: dict[str, tuple[str, ...]] = {
    "behaviorism": ("자아 주도성", "성취·도전"),
    "cognitivism": ("의미·성찰", "기억·서사"),
    "constructivism": ("관계·연대", "정서 표현"),
}
LENS_LABELS_KO = {
    "behaviorism": LENS_BEHAVIORISM_KO,
    "cognitivism": LENS_COGNITIVISM_KO,
    "constructivism": LENS_CONSTRUCTIVISM_KO,
}

LEARNING_MAP_PREFACE = (
    "지금까지 나눈 이야기를 바탕으로, 당신의 배움 여정을 "
    "한 권의 「서사적 항해 일지」로 정리했습니다."
)

LEARNING_PROSE_KEYS = (
    "learning_preface",
    "section_identity",
    "section_four_lenses",
    "section_jagged",
    "section_prescription",
    "situational_opening",
    "jagged_profile_sentence",
    "learning_tactic",
)


def polish_learning_report(report: dict[str, Any]) -> dict[str, Any]:
    """별표 제거·인용 순화·에세이형 단락."""
    polished = dict(report)
    for key in LEARNING_PROSE_KEYS:
        raw = polished.get(key)
        if not isinstance(raw, str) or not raw.strip():
            continue
        if key.startswith("section_"):
            polished[key] = format_midpoint_section_body(raw)
        else:
            polished[key] = sanitize_midpoint_prose(raw)
    return polished


def compute_learning_statistics(
    messages: list[dict],
    profile: dict[str, float] | None = None,
) -> dict[str, Any]:
    """학습 리포트용 내부 통계 — 화면에는 수치 미노출."""
    stats = compute_midpoint_statistics(messages, profile)
    domain = stats.get("domain_scores") or {}
    ranked = sorted(domain.items(), key=lambda x: -float(x[1])) if domain else []
    stats["learning_peaks"] = [k for k, _ in ranked[:2]]
    stats["learning_troughs"] = [k for k, _ in ranked[-2:]] if len(ranked) > 2 else []
    return stats


def compute_lens_scores(stats: dict[str, Any]) -> dict[str, float]:
    """행동·인지·구성 3렌즈 점수 (0~100, 내부용)."""
    domain = stats.get("domain_scores") or {}
    out: dict[str, float] = {}
    for lens, keys in LENS_DOMAIN_GROUPS.items():
        vals = [float(domain.get(k, 0)) for k in keys if k in domain]
        out[lens] = round(sum(vals) / len(vals), 1) if vals else 50.0
    return out


def build_jagged_profile_bundle(
    stats: dict[str, Any],
    *,
    user_texts: list[str] | None = None,
) -> dict[str, Any]:
    """
    비대칭 Jagged Profile — 한 문장 요약 + 렌즈별 점수 + HTML 막대.
    """
    lens = compute_lens_scores(stats)
    ranked = sorted(lens.items(), key=lambda x: -x[1])
    peak_key, peak_val = ranked[0]
    trough_key, trough_val = ranked[-1]
    gap = peak_val - trough_val

    peak_trait = {
        "behaviorism": "행동적 루틴·실행력",
        "cognitivism": "인지적 탐구심·메타인지",
        "constructivism": "관계·맥락 속 배움",
    }
    trough_need = {
        "behaviorism": "행동적 루틴 형성",
        "cognitivism": "학습 전략·메타인지 정교화",
        "constructivism": "관계·환경 맥락 설계",
    }

    if gap < 8:
        sentence = (
            "당신의 배움 지형은 세 렌즈가 고르게 펼쳐져 있으며, "
            "특정 한 축에만 치우치지 않은 균형에 가깝습니다. "
            "다만 작은 루틴 하나를 정해 깊이를 더하면 봉우리가 더 선명해질 수 있습니다."
        )
    else:
        sentence = (
            f"당신은 {peak_trait.get(peak_key, '강점')}은(는) 높지만 "
            f"{trough_need.get(trough_key, '보완 영역')}이(가) 더 필요한 상태입니다. "
            "평균형 학습자라기보다, 들쭉날쭉한(Jagged) 강점 지형을 가진 배움자에 가깝습니다."
        )

    quote = ""
    for line in user_texts or []:
        if len(line) >= 8:
            quote = line[:36]
            break
    if quote:
        sentence += f" 대화 속 「{quote}」가 이 지형을 잘 보여 줍니다."

    bars_html = _jagged_profile_bars_html(lens)
    return {
        "lens_scores": lens,
        "peak_lens": peak_key,
        "trough_lens": trough_key,
        "jagged_profile_sentence": sentence,
        "jagged_bars_html": bars_html,
        "peak_label": LENS_LABELS_KO.get(peak_key, peak_key),
        "trough_label": LENS_LABELS_KO.get(trough_key, trough_key),
    }


def _jagged_profile_bars_html(lens_scores: dict[str, float]) -> str:
    rows = []
    for key in ("behaviorism", "cognitivism", "constructivism"):
        val = float(lens_scores.get(key, 50))
        label = LENS_LABELS_KO.get(key, key)
        rows.append(
            f'<div class="jagged-row">'
            f'<span class="jagged-label">{label}</span>'
            f'<div class="jagged-track"><div class="jagged-fill" style="width:{min(100, val):.0f}%"></div></div>'
            f'<span class="jagged-val">{val:.0f}</span></div>'
        )
    return (
        '<div class="jagged-profile-viz" aria-label="Jagged Profile">'
        + "".join(rows)
        + "</div>"
    )


def _jagged_learning_hint(stats: dict[str, Any]) -> str:
    bundle = build_jagged_profile_bundle(stats)
    return str(bundle.get("jagged_profile_sentence", ""))


def _theoretical_lens_hints(
    stats: dict[str, Any],
    user_lines: list[str],
) -> str:
    """프롬프트용 — 이론 키워드 + 사례 결합 지시."""
    lens = compute_lens_scores(stats)
    anchors = extract_anchor_phrases(user_lines)[:3]
    anchor_txt = " · ".join(f"「{a}」" for a in anchors) if anchors else "(발화에서 직접 인용)"
    return (
        f"- {LENS_BEHAVIORISM_KO} 점수(내부): {lens.get('behaviorism', 50):.0f} — "
        "습관·보상·루틴·실행을 참여자 사례와 결합\n"
        f"- {LENS_COGNITIVISM_KO} 점수(내부): {lens.get('cognitivism', 50):.0f} — "
        "메타인지·이해·정리·전략을 참여자 사례와 결합\n"
        f"- {LENS_CONSTRUCTIVISM_KO} 점수(내부): {lens.get('constructivism', 50):.0f} — "
        "관계·장소·맥락·상호작용을 참여자 사례와 결합\n"
        f"- 인용 후보: {anchor_txt}"
    )


def _format_learning_signals_for_prompt(signals: dict[str, Any] | None) -> str:
    if not signals:
        return ""
    slim = {
        k: signals.get(k)
        for k in (
            "bloom",
            "todd_rose",
            "pattern_seeker",
            "dynamics",
            "motivation",
            "metacognition",
            "career_values",
            "anchor_quote",
        )
        if signals.get(k)
    }
    if not slim:
        return ""
    return (
        "\n[실시간 인출 신호 — 해석 재료, 출력에 JSON·점수·별표 금지]\n"
        + json.dumps(slim, ensure_ascii=False, indent=0)
        + "\n"
    )


def build_learning_report_prompt(
    *,
    user_lines: list[str],
    stats: dict[str, Any],
    voice_guide: str,
    scene: str,
    learning_audience: str,
    age_group: str,
    life_stage: str,
    lang_name: str,
    learning_signals: dict[str, Any] | None = None,
) -> str:
    anchors = extract_anchor_phrases(user_lines)
    anchor_block = (
        "\n".join(
            f"- 인용 후보: {a}\n  → 「」로 감싸고 명백한 오타만 순화"
            for a in anchors
        )
        if anchors
        else "- 발화에서 2~3개 핵심 구절을 「」로 직접 인용 (6~40자)."
    )
    audience_ko = audience_label_ko(learning_audience) or "참여자"
    jagged_bundle = build_jagged_profile_bundle(stats, user_texts=user_lines)
    stats_for_model = {
        "strength_categories": stats.get("strength_categories"),
        "domain_scores": stats.get("domain_scores"),
        "lens_scores": jagged_bundle.get("lens_scores"),
        "jaggedness_index": stats.get("jaggedness_index"),
        "learning_peaks": stats.get("learning_peaks"),
        "learning_troughs": stats.get("learning_troughs"),
    }
    lens_hints = _theoretical_lens_hints(stats, user_lines)
    jagged_sentence = str(jagged_bundle.get("jagged_profile_sentence", ""))
    signals_block = _format_learning_signals_for_prompt(learning_signals)
    if is_student_audience(learning_audience):
        report_mode = "성장 가이드 (학생 당사자용 — 자기 성장·If-Then·패턴 중심)"
    else:
        report_mode = "환경 설계 가이드 (보호자·교사용 — 가정·교실·관계·마찰 조정)"

    return (
        "당신은 dlinso **배움의 정원사**의 최종 **서사적 항해 일지** 작성자입니다.\n"
        f"대화 상대: {audience_ko}. 리포트 유형: **{report_mode}**.\n"
        "내부 통계·점수는 해석 재료일 뿐, 출력에 숫자·OR·%·영문 지표명·별표(*)를 넣지 마세요.\n"
        "금지 단어: 평균, 우수, 미달, 정상, 하위, 상위 등 정형화 평가 표현.\n\n"
        "[리포트 정체성]\n"
        f"서두(learning_preface): 「{LEARNING_MAP_PREFACE}」에 가깝게 1~2문장.\n\n"
        f"■ {TITLE_IDENTITY}\n"
        "- 은유적 학습 정체성 한 이름 (예: 지식의 나침반을 든 탐험가).\n"
        "- 참여자 말에서 뽑은 이미지·동사를 녹일 것.\n\n"
        f"■ {TITLE_FOUR_LENSES}\n"
        "- 반드시 **네 단락**으로 작성(단락 사이 빈 줄):\n"
        f"  1) {THEORY_BLOOM_KO}: 암기·이해를 넘어 분석·평가·창조(체계화·저술) — 인용 1회 이상\n"
        f"  2) {THEORY_TODD_ROSE_KO}: Jagged 강점·취약, 장소·사람 맥락 — 인용 1회 이상\n"
        f"  3) {THEORY_PATTERN_KO}: 패턴·시스템화·저술 연결 — 인용 1회 이상\n"
        f"  4) {THEORY_DYNAMICS_KO}: 동기·마찰·관성·중력(목표) 역학 — 인용 1회 이상\n"
        "- 각 단락 2~3문장. 이론명만 나열하지 말고 **그 사람의 장면**과 붙일 것.\n\n"
        f"■ {TITLE_JAGGED}\n"
        "- section_jagged **첫 문장**은 아래 jagged_profile_sentence와 **의미가 같거나** "
        "더 풍부하게(예: 「암기는 보통이지만, 연결·창조에서 봉우리가 있습니다」 형태):\n"
        f'  참고: 「{jagged_sentence}」\n'
        "- 강점 봉우리 vs 보완 골짜기 대비(2~3문장). 영문 Jagged Profile 금지.\n\n"
        f"■ {TITLE_PRESCRIPTION}\n"
        "- **동역학적 처방**: 현재 마찰력을 줄이기 위해 환경(장소·사람)을 어떻게 조정할지 1~2문장.\n"
        "- 참여자가 말한 「폼나는 삶」「의미 있는 삶」을 인용·반영.\n"
        "- learning_tactic: 폼나는 삶을 향한 **학습 전술 딱 1가지** "
        "(언제·어디서·무엇을·몇 분 — 실행 가능).\n"
        "- section_prescription: 환경 설계(보호자·교사) 또는 성장 루틴(학생)에 맞게 전술을 풀고 격려 1문장.\n\n"
        "[내부 통계 힌트 — 출력에 점수 금지]\n"
        f"{lens_hints}\n"
        f"{signals_block}\n"
        "[인용·형식]\n"
        f"{anchor_block}\n"
        "- 전 섹션 합쳐 「」 인용 최소 3회.\n"
        "- JSON 값에 마크다운 별표(*, **) 금지. 단락은 \\n\\n.\n"
        "- 명백한 오타만 표준어로 순화.\n\n"
        "[말투]\n"
        f"{voice_guide}\n"
        f"응답 언어: {lang_name}\n\n"
        f"[상황] {scene}\n\n"
        f"[내부 통계 — 출력 금지]\n{json.dumps(stats_for_model, ensure_ascii=False)}\n\n"
        "[참여자 발화]\n"
        + "\n".join(f"- {line}" for line in user_lines[-16:])
        + "\n\n"
        "JSON만 출력:\n"
        "{\n"
        '  "learning_preface": "서두",\n'
        f'  "title_identity": "{TITLE_IDENTITY}",\n'
        f'  "title_four_lenses": "{TITLE_FOUR_LENSES}",\n'
        f'  "title_jagged": "{TITLE_JAGGED}",\n'
        f'  "title_prescription": "{TITLE_PRESCRIPTION}",\n'
        f'  "section_identity": "본문",\n'
        f'  "section_four_lenses": "본문(Bloom·Todd Rose·Pattern·Dynamics 네 단락)",\n'
        f'  "section_jagged": "본문",\n'
        f'  "section_prescription": "본문",\n'
        f'  "jagged_profile_sentence": "{jagged_sentence[:200]}",\n'
        '  "learning_tactic": "전술 한 가지(실행 가능)",\n'
        '  "situational_opening": "[상황] 짧게"\n'
        "}\n"
    )


def resolve_learning_voice(
    learning_audience: str,
    life_stage: str,
    age_group: str,
) -> str:
    a = (learning_audience or "").strip()
    if a == AUDIENCE_TEACHER:
        return "teacher"
    if is_adult_learning_proxy(a):
        return "parent"
    stage = (life_stage or "").strip()
    if "초등" in stage or "초등 연령" in (age_group or ""):
        return "elementary"
    if "중·고" in stage or "청소년" in stage or "중등" in (age_group or ""):
        return "secondary"
    return "adult"


def build_learning_voice_guide(
    learning_audience: str,
    *,
    voice: str,
    nick: str,
) -> str:
    """리포트 LLM용 말투·역할 가이드."""
    a = (learning_audience or "").strip()
    name = (nick or "").strip()[:12] or "참여자"
    if a == AUDIENCE_MOTHER:
        return (
            "엄마 맞춤 · 환경 설계 가이드: 배움의 정원사. 따뜻한 존댓말. "
            "자녀 진단·비교·평균·우수·미달 금지. 「」 인용."
        )
    if a == AUDIENCE_FATHER:
        return (
            "아빠 맞춤 · 환경 설계 가이드: 배움의 정원사. 따뜻한 존댓말. "
            "판단·비교·평균 라벨 금지. 「」 인용."
        )
    if a == AUDIENCE_GRANDPARENT:
        return (
            "조부모·조모 · 환경 설계 가이드: 배움의 정원사. 정중·따뜻. "
            "손주 과잉 평가 금지. 「」 인용."
        )
    if a == AUDIENCE_TEACHER:
        return (
            "교사 · 환경 설계 가이드: 배움의 정원사. 교실 맥락. "
            "학생 라벨링·순위·평균 금지. 「」 인용."
        )
    if a == AUDIENCE_PARENT or is_adult_learning_proxy(a):
        return (
            "보호자 · 환경 설계 가이드: 배움의 정원사. 존댓말. "
            "가정·학교·마찰 조정. 「」 인용. 별표·수치·평균·우수·미달 금지."
        )
    if is_student_audience(a) and voice == "elementary":
        return (
            f'초등 · 성장 가이드: "{name}아/야" 다정한 입말. 배움의 정원사. '
            "「」 인용. 쉬운 은유."
        )
    if is_student_audience(a) and voice == "secondary":
        return (
            "중·고 · 성장 가이드: 친근한 존댓말. 배움의 정원사. "
            "폼나는 삶·If-Then. 「」 인용."
        )
    if is_student_audience(a):
        return (
            "성인·대학 · 성장 가이드: 격조 있는 존댓말. 배움의 정원사. "
            "의미 있는 삶·학습 전술. 「」 인용."
        )
    return "배움의 정원사. 「」 인용. 별표·평균·우수·미달 금지."


def compose_learning_report_fallback(
    *,
    stats: dict[str, Any],
    situational: dict[str, str],
    voice: str,
    learning_audience: str,
    user_texts: list[str],
) -> dict[str, str]:
    scene = situational.get("scene_phrase", "지금까지의 배움 이야기")
    bracket = f"[{scene}]"
    q = ""
    for line in user_texts:
        if len(line) >= 8:
            q = line[:36]
            break
    quote = f"「{q}」" if q else "「잘 되던 그때의 장면」"
    jagged = _jagged_learning_hint(stats)

    jagged_bundle = build_jagged_profile_bundle(stats, user_texts=user_texts)
    jagged_sentence = str(jagged_bundle.get("jagged_profile_sentence", jagged))
    lens = compute_lens_scores(stats)

    proxy_identity = {
        AUDIENCE_PARENT: (
            f"{bracket} 학부모님의 말 속에서, 아이의 배움을 지켜보는 "
            "「따뜻한 나침반」 같은 정체성이 보입니다."
        ),
        AUDIENCE_MOTHER: (
            f"{bracket} 엄마의 말 속에서, 아이의 배움을 지켜보는 "
            "「따뜻한 나침반」 같은 정체성이 보입니다."
        ),
        AUDIENCE_FATHER: (
            f"{bracket} 아빠의 말 속에서, 아이의 배움을 바라보는 "
            "「든든한 나침반」 같은 정체성이 보입니다."
        ),
        AUDIENCE_GRANDPARENT: (
            f"{bracket} 조부모·조모님의 말 속에서, 손주의 배움을 품는 "
            "「따뜻한 지킴이」 같은 정체성이 보입니다."
        ),
        AUDIENCE_TEACHER: (
            f"{bracket} 교실 이야기 속에서, 학생의 배움을 돕는 "
            "「배움의 나침반」 같은 정체성이 보입니다."
        ),
    }
    aud = (learning_audience or "").strip()
    if aud in proxy_identity:
        identity = proxy_identity[aud]
    elif voice == "elementary" and is_student_audience(aud):
        identity = (
            f"{bracket} 네 이야기 속에는 {quote}를 품은 "
            "「호기심 탐험가」 같은 배움 정체성이 있어."
        )
    else:
        identity = (
            f"{bracket} 당신의 배움 서사에는 {quote}가 담긴 "
            "「지식의 나침반을 든 탐험가」에 가까운 정체성이 있습니다."
        )

    lenses = (
        f"{THEORY_BLOOM_KO}: {quote}와 연결해 보면, "
        "이해를 넘어 정리·표현·창조로 가고 싶은 열망이 보입니다.\n\n"
        f"{THEORY_TODD_ROSE_KO}: 영역마다 강약이 다릅니다. "
        "특정 장소·관계에서 역량이 커지는 Jagged 지형이 드러납니다.\n\n"
        f"{THEORY_PATTERN_KO}: 흩어진 경험 속에서 패턴을 찾아 "
        "연결·체계화하려는 기질이 있습니다.\n\n"
        f"{THEORY_DYNAMICS_KO}: 동기·환경 마찰·습관·목표가 "
        "서로 맞물려 배움의 속도를 만들고 있습니다."
    )

    jagged_section = (
        f"{jagged_sentence}\n\n"
        f"상대적으로 높은 렌즈는 {jagged_bundle.get('peak_label', '강점')}이고, "
        f"지금 돌보면 좋은 축은 {jagged_bundle.get('trough_label', '보완')}입니다. "
        "솟은 봉우리는 지금의 강점으로 삼고, 완만한 축은 부담 없이 키워 가면 됩니다."
    )

    tactic = (
        "폼나는 삶을 한 뼘 가까이: 이번 주 3회, "
        "잘 되던 시간·장소를 15분만 고정해 같은 자리에서 시작하기. "
        f"{quote}가 떠오른 그 장면을 첫날 메모 한 줄로 남기세요."
    )
    env_note = (
        "마찰을 줄이려면, 잘 되던 장소·사람 맥락을 한 가지만 이번 주에 고정해 보세요."
        if is_adult_learning_proxy(aud)
        else "가속도가 붙던 If-Then 맥락(시간·장소)을 한 가지만 이번 주에 반복해 보세요."
    )
    prescription = (
        f"{env_note}\n\n"
        f"당신이 말한 폼나는 삶의 방향을 잃지 않으려면, 지금은 크게 바꾸기보다 "
        "작은 루틴 하나를 지키는 것이 유리합니다.\n\n"
        f"【학습 전술】\n{tactic}"
    )

    return polish_learning_report(
        {
            "learning_preface": LEARNING_MAP_PREFACE,
            "title_identity": TITLE_IDENTITY,
            "title_four_lenses": TITLE_FOUR_LENSES,
            "title_jagged": TITLE_JAGGED,
            "title_prescription": TITLE_PRESCRIPTION,
            "section_identity": identity.strip(),
            "section_four_lenses": lenses.strip(),
            "section_jagged": jagged_section.strip(),
            "section_prescription": prescription.strip(),
            "jagged_profile_sentence": jagged_sentence.strip(),
            "learning_tactic": tactic.strip(),
            "situational_opening": bracket,
            "jagged_bars_html": str(jagged_bundle.get("jagged_bars_html", "")),
            "lens_scores": lens,
        }
    )


def format_learning_followup() -> str:
    return (
        "이 지도가 지금의 배움 이야기와 닮았나요? "
        "더 들려주고 싶은 장면이 있다면 이어서 말씀해 주세요."
    )


LEARNING_REPORT_VIZ_CSS = """
<style>
.jagged-profile-viz { margin: 0.65rem 0 0.85rem; }
.jagged-row { display: flex; align-items: center; gap: 0.5rem; margin: 0.35rem 0; font-size: 0.82rem; }
.jagged-label { flex: 0 0 11.5rem; color: #444; }
.jagged-track { flex: 1; height: 0.55rem; background: #e8e4dc; border-radius: 4px; overflow: hidden; }
.jagged-fill { height: 100%; background: linear-gradient(90deg, #c4b5a5, #8a7a68); border-radius: 4px; }
.jagged-val { flex: 0 0 2rem; text-align: right; color: #555; font-weight: 600; }
.jagged-sentence-box {
  background: #f7f3ec; border-left: 3px solid #8a7a68;
  padding: 0.65rem 0.85rem; margin: 0.5rem 0 0.75rem;
  font-weight: 600; color: #333; line-height: 1.55;
}
.learning-tactic-box {
  background: #fff; border: 1px solid rgba(80,70,55,0.18);
  border-radius: 8px; padding: 0.75rem 0.9rem; margin-top: 0.5rem;
}
</style>
"""


def render_learning_report_blocks(report: dict[str, Any]) -> None:
    """Streamlit — 학습 서사 리포트 렌더 (샌드박스·앱 공용)."""
    import streamlit as st

    r = polish_learning_report(report)
    st.markdown(LEARNING_REPORT_VIZ_CSS, unsafe_allow_html=True)
    title = str(r.get("report_title", LEARNING_VOYAGE_LOG_TITLE)).strip()
    st.markdown(f"### {html.escape(title)}")
    preface = str(r.get("learning_preface", "")).strip()
    if preface:
        st.markdown(preface)

    st.markdown(f"#### {r.get('title_identity', TITLE_IDENTITY)}")
    st.markdown(str(r.get("section_identity", "")).strip())

    st.markdown(f"#### {r.get('title_four_lenses', TITLE_FOUR_LENSES)}")
    st.markdown(str(r.get("section_four_lenses", "")).strip())

    st.markdown(f"#### {r.get('title_jagged', TITLE_JAGGED)}")
    jagged_one = str(r.get("jagged_profile_sentence", "")).strip()
    if jagged_one:
        st.markdown(
            f'<div class="jagged-sentence-box">{html.escape(jagged_one)}</div>',
            unsafe_allow_html=True,
        )
    bars = str(r.get("jagged_bars_html", "")).strip()
    if bars:
        st.markdown(bars, unsafe_allow_html=True)
    body_jagged = str(r.get("section_jagged", "")).strip()
    if body_jagged and body_jagged != jagged_one:
        st.markdown(body_jagged)

    st.markdown(f"#### {r.get('title_prescription', TITLE_PRESCRIPTION)}")
    tactic = str(r.get("learning_tactic", "")).strip()
    if tactic:
        st.markdown(
            f'<div class="learning-tactic-box"><b>학습 전술 (Learning Tactic)</b><br>'
            f"{html.escape(tactic)}</div>",
            unsafe_allow_html=True,
        )
    st.markdown(str(r.get("section_prescription", "")).strip())
    st.caption(format_learning_followup())


def format_full_learning_message(report: dict[str, Any]) -> str:
    r = polish_learning_report(report)
    title = str(r.get("report_title", LEARNING_VOYAGE_LOG_TITLE)).strip()
    parts = [
        f"### {title}",
        str(r.get("learning_preface", "")).strip(),
        f"#### [{r.get('title_identity', TITLE_IDENTITY)}]",
        str(r.get("section_identity", "")).strip(),
        f"#### [{r.get('title_four_lenses', TITLE_FOUR_LENSES)}]",
        str(r.get("section_four_lenses", "")).strip(),
        f"#### [{r.get('title_jagged', TITLE_JAGGED)}]",
        str(r.get("jagged_profile_sentence", "")).strip()
        or str(r.get("section_jagged", "")).strip(),
        f"#### [{r.get('title_prescription', TITLE_PRESCRIPTION)}]",
        str(r.get("learning_tactic", "")).strip(),
        str(r.get("section_prescription", "")).strip(),
        format_learning_followup(),
    ]
    return "\n\n".join(p for p in parts if p.strip())


def run_learning_report_pipeline(
    messages: list[dict],
    profile: dict[str, float] | None = None,
    *,
    learning_audience: str = "",
    life_stage: str = "",
    age_group: str = "",
    humanistic: dict[str, str] | None = None,
    situational: dict[str, str] | None = None,
    user_texts: list[str] | None = None,
    learning_signals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    user_texts = user_texts or [
        str(m.get("content") or "").strip()
        for m in messages
        if m.get("role") == "user" and str(m.get("content") or "").strip()
    ]
    stats = compute_learning_statistics(messages, profile)
    situational = situational or {"scene_phrase": "지금까지의 배움 이야기"}
    jagged_bundle = build_jagged_profile_bundle(stats, user_texts=user_texts)
    narrative = humanistic or compose_learning_report_fallback(
        stats=stats,
        situational=situational,
        voice=resolve_learning_voice(learning_audience, life_stage, age_group),
        learning_audience=learning_audience,
        user_texts=user_texts,
    )
    if humanistic and not narrative.get("jagged_bars_html"):
        narrative = {
            **narrative,
            "jagged_profile_sentence": narrative.get("jagged_profile_sentence")
            or jagged_bundle.get("jagged_profile_sentence"),
            "jagged_bars_html": jagged_bundle.get("jagged_bars_html", ""),
            "lens_scores": jagged_bundle.get("lens_scores"),
        }
    from hbridge_analysis import format_sheet_stats_summary

    merged = polish_learning_report(
        {
            **narrative,
            "report_title": LEARNING_VOYAGE_LOG_TITLE,
            "jaggedness_index": stats.get("jaggedness_index", 0),
            "narrative_precision": stats.get("narrative_precision", 50),
            "stats": stats,
            "stats_json": json.dumps(stats, ensure_ascii=False)[:2000],
            "learning_audience": learning_audience,
            "learning_signals": learning_signals or {},
            "lens_scores": narrative.get("lens_scores") or jagged_bundle.get("lens_scores"),
            "jagged_bars_html": narrative.get("jagged_bars_html")
            or jagged_bundle.get("jagged_bars_html", ""),
        }
    )
    merged["hbridge_summary"] = format_sheet_stats_summary(merged)
    return merged
