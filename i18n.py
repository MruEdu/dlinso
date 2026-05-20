"""UI 다국어 사전 — ko / en / mn / ja / zh / vi."""

from __future__ import annotations

import streamlit as st

LANG_CODES = ("ko", "en", "mn", "ja", "zh", "vi")

LANG_LABELS: dict[str, str] = {
    "ko": "한국어",
    "en": "English",
    "mn": "Монгол",
    "ja": "日本語",
    "zh": "中文",
    "vi": "Tiếng Việt",
}

LANG_FULL: dict[str, str] = {
    "ko": "Korean",
    "en": "English",
    "mn": "Mongolian",
    "ja": "Japanese",
    "zh": "Chinese",
    "vi": "Vietnamese",
}

# 하단 배너 — 언어 선택과 무관하게 한/영 병기 (글로벌 공통)
FOOTER_BANNER: dict[str, str] = {
    "primary": "🌿 dlinso",
    "secondary": "Dlinso Lab",
    "copyright": "© 2026 Dlinso Lab by sinihyun. All Rights Reserved.",
    "powered": "대화 · 서사 구조화 · Google Sheets",
}

# 공통 옵션 (연령·학력은 연구 표준 한국어 라벨 유지, UI만 번역)
TEXTS: dict[str, dict[str, str]] = {
    "ko": {
        "app_title": "dlinso",
        "beta_badge": "베타 1.0",
        "hub_eyebrow": "",
        "hub_tagline": "",
        "hub_slogan": (
            "대화로 발견하는 나의 보물, 예술이 되는 나의 삶. **dlinso**"
        ),
        "hub_slogan_beta_note": "베타 버전입니다. 기능과 문구가 계속 다듬어지고 있어요.",
        "intro_headline": (
            "대화로 발견하는 나의 보물, 예술이 되는 나의 삶. dlinso"
        ),
        "intro_sub": (
            "당신의 일상이 작품이 되고, 당신의 강점이 빛나는 기록이 되는 곳. "
            "dlinso는 당신만의 이야기를 완성하는 대화형 성찰 플랫폼입니다."
        ),
        "intro_guide_label": "안내",
        "intro_guide_body": (
            "**서사 구조화** — 나눈 대화를 바탕으로 당신만의 이야기 결을 세웁니다. "
            "대화 기록은 안전하게 보관됩니다."
        ),
        "err_gemini_reply": "대화 응답을 준비하지 못했습니다",
        "err_gemini_leaked": (
            "대화 연결이 일시적으로 차단되었습니다. "
            "관리자 설정(Streamlit **Secrets**·로컬 `.env`)의 연결 키를 "
            "교체한 뒤 앱을 **Reboot**하세요."
        ),
        "err_dialogue_unavailable": (
            "지금은 대화를 이어갈 수 없습니다. 연결 설정을 확인해 주세요."
        ),
        "err_dialogue_not_connected": "대화에 연결되지 않았습니다.",
        "status_dialogue": "대화",
        "status_record": "기록",
        "lang_label": "언어",
        "tab_new": "처음 오신 분",
        "tab_return": "다시 오신 분",
        "onboarding_banner": (
            "👇 아래에서 **개인정보 동의** 후, "
            "「처음 오신 분」또는 「다시 오신 분」탭을 선택해 주세요."
        ),
        "nav_home": "🏠 dlinso",
        "nav_consult": "📖 나의 이야기",
        "nav_inquiry": "✉️ 문의하기",
        "nav_inquiry_short": "✉️",
        "inquiry_page_title": "✉️ 연구소에 문의하기",
        "inquiry_page_intro": (
            "아래 양식을 작성해 **보내기**를 누르면 문의가 Google Sheets에 "
            "안전하게 기록됩니다. (이메일 앱은 사용하지 않습니다.)"
        ),
        "inquiry_guest_nick": "닉네임 (가입 전 문의 시)",
        "inquiry_empty": "문의 내용을 입력해 주세요.",
        "inquiry_back": "← 이전 화면으로",
        "inquiry_fab_label": "✉️ 연구 협업 등 문의",
        "go_life_story": "📖 나의 이야기 · 가입/로그인",
        "mode_roadmap_title": "dlinso 여정",
        "mode_lifespan_label": "생애사적 대화",
        "mode_lifespan_desc": "지금의 말투로 대화하며, 이어지는 이야기 속에서 삶의 서사를 함께 만듭니다.",
        "mode_assessment_label": "심리·강점",
        "mode_assessment_desc": "대화 속에서 마음 상태와 강점을 살펴봅니다.",
        "mode_counseling_label": "나러티브 상담",
        "mode_counseling_desc": "전문 상담 기법이 담긴 심화 대화입니다.",
        "mode_research_label": "연구용",
        "mode_research_desc": "질적 연구를 위한 데이터 수집·구조화입니다.",
        "mode_tag_active": "지금",
        "mode_tag_soon": "준비 중",
        "age_current": "현재 연령대",
        "age_field_help": (
            "가입 정보로 저장되며, 대화의 말투와 맥락에만 사용됩니다. "
            "어느 시기의 이야기를 할지 정하는 항목이 아닙니다."
        ),
        "education_field_help": (
            "현재의 생활 단계를 알려 주시면, 맞는 말투로 동행합니다."
        ),
        "profile_save_hint": (
            "아래에 **현재** 연령·생애 단계를 입력해 주세요. "
            "첫 대화는 지금이든 과거든 자유롭게 시작하시면 됩니다."
        ),
        "chat_age_context_caption": (
            "현재 연령 {age} · 생애 단계 {stage} — 이 맞춤 말투로 대화합니다. "
            "오늘의 일상이든 과거의 기억이든, 떠오르는 대로 편하게 적어 주세요."
        ),
        "intro_whisper": "📖 나의 이야기 — 그곳에서 열립니다.",
        "intro_hint": "이야기는 **📖 나의 이야기**에서 열립니다.",
        "reset_session": "🔄 처음부터 (세션 초기화)",
        "consent_title": "개인정보처리방침 및 연구 동의",
        "consent_check": "연구 목적·익명 처리에 동의합니다. (필수)",
        "key_hint": (
            "🔑 **닉네임**과 **비밀번호**가 당신만의 열쇠입니다. "
            "「이어 가기」에서 지난 대화를 이어갈 수 있어요."
        ),
        "return_hint": "🔑 가입 시 만든 **닉네임**과 **비밀번호**로 지난 이야기를 불러옵니다.",
        "nickname": "닉네임",
        "password": "비밀번호",
        "password_confirm": "비밀번호 확인",
        "gender": "성별",
        "age": "연령대",
        "education": "현재 학력 및 생애주기",
        "btn_start": "✅ 동의하고 나의 이야기 시작하기",
        "btn_continue": "✅ 이어서 이야기하기",
        "gentle_record": "마음의 기록이 차곡차곡 쌓이고 있어요 🌿",
        "input_hint": (
            "여기를 탭하여 대화해 보세요. 추억 사진을 올리면 사진 이야기도 할 수 있어요. "
            "문의는 상단 ✉️ 문의하기."
        ),
        "chat_composer_guide": (
            "여기를 탭하여 대화해 보세요. 추억 사진을 올리면 사진 이야기도 할 수 있어요. "
            "문의는 상단 ✉️ 문의하기."
        ),
        "chat_photo_row_caption": "📷 사진 (선택)",
        "chat_photo_label": "사진 업로드",
        "chat_photo_hint": "📷 사진의 색·구도·분위기를 읽고, 대화를 이어갑니다.",
        "chat_alt_send": "보내기",
        "midpoint_analysis_btn": (
            "지금까지의 대화 중간 정리 및 나만의 마음 지도 확인"
        ),
        "midpoint_analysis_btn_rerun": "중간 정리 · 마음 지도 다시 받기",
        "midpoint_view_expand": "🗺️ 나만의 마음 지도 다시 보기",
        "reflection_depth_gauge_label": "성찰의 깊이",
        "midpoint_encourage_before_unlock": (
            "당신의 서사가 훌륭하게 쌓이고 있습니다. "
            "조금만 더 이야기를 나누면 '중간 정리'를 도와드릴 수 있어요."
        ),
        "narrative_asset_progress_label": "나만의 서사 자산화 진행률",
        "narrative_asset_progress_turns": (
            "{current}/{need}회 대화 · 진행 {percent}% — "
            "이야기가 쌓이면 마음 지도를 그릴 수 있어요"
        ),
        "narrative_asset_progress_ready": (
            "이야기가 충분히 쌓였어요. 아래 버튼으로 마음 지도를 받아 보세요."
        ),
        "narrative_asset_progress_need_detail": (
            "10회는 채웠어요. 조금 더 구체적인 장면을 나누면 더 선명한 지도가 그려져요."
        ),
        "midpoint_need_turns": (
            "중간 정리는 참여자 답변 {need}회 이후에 가능합니다. (현재 {current}회)"
        ),
        "midpoint_scaffold_default": (
            "조금 더 구체적인 상황을 들려주시면 더 선명한 지도를 그릴 수 있어요."
        ),
        "midpoint_char_mobile_hint": "모바일 환경에서는 1,000자 내외도 충분합니다.",
        "midpoint_char_over": "입력은 최대 {limit:,}자까지 가능합니다.",
        "chat_ph_collect": "오늘 마음속 이야기를 적어 보세요…",
        "chat_ph_giant": "이어서 적어 보세요…",
        "chat_opening_placeholder": (
            "지금 떠오르는 말을 자유롭게 적어 보세요…"
        ),
        "opening": (
            "반가워요! 당신의 **마음의 정원사** dlinso입니다.\n\n"
            "오늘의 하루, 지금 마음, 혹은 떠오르는 옛날 이야기—무엇이든 괜찮아요. "
            "정해진 주제 없이, 편한 속도로 시작해 주세요.\n\n"
            "먼저 떠오르는 한 가지를 들려주시면, 대화가 이어집니다."
        ),
        "opening_stage_초등학생": (
            "반가워요! **마음의 정원사** dlinso예요.\n\n"
            "우리는 대화로 네 마음속 보물을 함께 찾아볼 거야. "
            "학교·친구·집 이야기, 요즘 제일 신나거나 속상한 일도 좋아.\n\n"
            "오늘 가장 먼저 떠오르는 이야기를 들려줄래?"
        ),
        "opening_stage_중학생": (
            "반가워요! **마음의 정원사** dlinso입니다.\n\n"
            "대화를 통해 네 삶 속 이야기를 함께 살펴볼 거예요. "
            "친구, 학교, 꿈, 작은 일상도 모두 소중한 조각이에요.\n\n"
            "지금 마음에 가장 남는 이야기를 편하게 적어 주세요."
        ),
        "opening_stage_고등학생": (
            "반가워요! **마음의 정원사** dlinso입니다.\n\n"
            "우리는 대화로 네가 소중히 여기는 이야기를 함께 이어 갈 거예요. "
            "진로, 관계, 지금의 고민이나 작은 기쁨도 괜찮아요.\n\n"
            "오늘 가장 크게 자리한 이야기를 들려주세요."
        ),
        "opening_stage_대학생": (
            "반가워요! **마음의 정원사** dlinso입니다.\n\n"
            "대화를 통해 네 삶의 조각들을 함께 이어 볼 거예요. "
            "전공, 관계, 앞으로의 선택—부담 없이 적어 주세요.\n\n"
            "지금 마음속 이야기를 들려주세요."
        ),
        "opening_stage_성인일반": (
            "반가워요! 당신의 **마음의 정원사** dlinso입니다.\n\n"
            "우리는 대화를 통해 당신의 삶 속 보물을 함께 찾아볼 거예요.\n\n"
            "오늘 마음속에 가장 크게 자리한 이야기는 무엇인가요? "
            "작은 일상의 조각도 괜찮아요.\n\n"
            "당신의 이야기를 들려주세요."
        ),
        "opening_stage_은퇴_후_삶": (
            "반가워요! **마음의 정원사** dlinso입니다.\n\n"
            "천천히 대화하며 지나온 이야기와 앞으로의 마음을 함께 짚어 볼 거예요. "
            "기억, 관계, 지금 느끼는 감정—무엇이든 괜찮습니다.\n\n"
            "편한 마음으로 이야기를 들려주세요."
        ),
        "opening_age_10대": (
            "반가워요! **마음의 정원사** dlinso예요.\n\n"
            "대화로 네 하루와 마음속 이야기를 함께 살펴볼 거야. "
            "친구, 학교, 작은 기쁨이나 속상함도 좋아.\n\n"
            "지금 가장 먼저 떠오르는 이야기를 들려줄래?"
        ),
        "opening_age_20대": (
            "반가워요! **마음의 정원사** dlinso입니다.\n\n"
            "우리는 대화로 네가 걸어온 길과 지금의 마음을 함께 이어 볼 거예요. "
            "선택, 관계, 작은 일상도 모두 소중해요.\n\n"
            "오늘 가장 크게 자리한 이야기를 들려주세요."
        ),
        "opening_age_30대": (
            "반가워요! **마음의 정원사** dlinso입니다.\n\n"
            "대화를 통해 일과 관계 속에 숨은 보물을 함께 찾아볼 거예요. "
            "바쁜 하루 속 작은 장면도 괜찮아요.\n\n"
            "지금 마음속 이야기를 들려주세요."
        ),
        "opening_age_40대": (
            "반가워요! **마음의 정원사** dlinso입니다.\n\n"
            "우리는 대화로 삶의 무게와 빛나는 순간을 함께 짚어 볼 거예요. "
            "책임, 전환, 작은 기쁨—무엇이든 괜찮아요.\n\n"
            "당신의 이야기를 들려주세요."
        ),
        "opening_age_50대": (
            "반가워요! **마음의 정원사** dlinso입니다.\n\n"
            "대화를 통해 쌓아 온 이야기와 지금의 마음을 함께 살펴볼 거예요.\n\n"
            "오늘 가장 전하고 싶은 이야기를 편하게 적어 주세요."
        ),
        "opening_age_60대_이상": (
            "반가워요! **마음의 정원사** dlinso입니다.\n\n"
            "천천히 대화하며 삶의 기억과 지금의 마음을 함께 이어 가요. "
            "작은 일상의 한 조각도 소중합니다.\n\n"
            "편안한 마음으로 이야기를 들려주세요."
        ),
        "opening_gender_note_여": "편한 말투로, 마음 가는 대로 천천히 적어 주셔도 좋아요.",
        "opening_gender_note_남": "부담 없이, 오늘 떠오르는 장면부터 적어 주셔도 좋아요.",
        "opening_gender_note_기타": "어떤 표현이든 괜찮아요. 당신의 속도로 이야기해 주세요.",
        "chat_opening_placeholder_stage_초등학생": (
            "오늘 제일 떠오르는 이야기를 적어 볼래?"
        ),
        "chat_opening_placeholder_stage_중학생": (
            "지금 마음에 남는 이야기를 적어 보세요…"
        ),
        "chat_opening_placeholder_stage_고등학생": (
            "오늘 가장 크게 자리한 이야기를 적어 보세요…"
        ),
        "chat_opening_placeholder_stage_대학생": (
            "지금 마음속 이야기를 적어 보세요…"
        ),
        "chat_opening_placeholder_age_10대": "지금 떠오르는 이야기를 적어 볼래?",
        "chat_opening_placeholder_age_20대": "오늘 마음속 이야기를 적어 보세요…",
        "chat_opening_placeholder_age_30대": "지금 마음속 이야기를 적어 보세요…",
        "chat_opening_placeholder_age_40대": "오늘 전하고 싶은 이야기를 적어 보세요…",
        "chat_opening_placeholder_age_50대": "편하게 이야기를 적어 보세요…",
        "chat_opening_placeholder_age_60대_이상": "천천히, 오늘의 이야기를 적어 보세요…",
        "err_sheets_busy": (
            "잠시 접속이 많아 기록이 지연되었습니다. "
            "잠시 후 다시 보내 주시거나, 같은 내용이 중복되지 않았는지 확인해 주세요."
        ),
        "sidebar_inquiry": "연구소에 문의하기",
        "inquiry_type_label": "문의 유형",
        "inquiry_type_general": "일반 상담",
        "inquiry_type_research": "네러티브 연구 협업",
        "inquiry_type_interview": "인터뷰 문의",
        "researcher_affiliation": "소속 (기관·학과)",
        "researcher_contact": "연락처 (이메일·전화)",
        "inquiry_placeholder": "궁금한 점이나 전하고 싶은 말을 적어 주세요…",
        "inquiry_send": "문의 보내기",
        "inquiry_ok": "문의가 Google Sheets에 기록되었습니다. 🌿",
        "admin_reply_title": "🌿 dlinso sinihyun님의 답변이 도착했습니다",
        "admin_reply_title_research": (
            "🌿 dlinso · 네러티브 연구 협업 회신"
        ),
        "admin_reply_title_interview": "🌿 dlinso · 인터뷰 관련 회신",
        "connection": "연결 상태",
        "connected": "연결됨",
        "disconnected": "연결 안 됨",
        "reset_chat": "대화 기록 초기화",
        "finish_chat": "오늘 이야기 마무리 · 요약본 받기",
        "new_story": "새 이야기 시작하기",
        "err_consent": "연구 동의에 체크해 주세요.",
        "err_nick": "닉네임을 입력해 주세요.",
        "err_pw": "비밀번호를 입력해 주세요.",
        "err_pw_match": "비밀번호가 일치하지 않습니다.",
        "err_nick_taken": "이미 사용 중인 닉네임입니다. 「이어 가기」에서 로그인하세요.",
        "err_login": "닉네임 또는 비밀번호가 맞지 않습니다.",
        "err_login_both": "닉네임과 비밀번호를 모두 입력해 주세요.",
        "err_sheets": "Google Sheets 연결이 필요합니다.",
        "err_sheets_setup": (
            "**배포(Streamlit Cloud):** 앱 **Settings → Secrets**에 "
            "`GOOGLE_SHEET_ID`와 `[gcp_service_account]`(JSON 키 전체)를 넣어 주세요.\n\n"
            "**로컬:** 프로젝트 폴더에 `service_account.json` + `.env`의 "
            "`GOOGLE_SHEET_ID`.\n\n"
            "Google 시트 **공유**에 서비스 계정 이메일(예: `...@...iam.gserviceaccount.com`)을 "
            "**편집자**로 추가해야 합니다.\n\n"
            "`Invalid JWT Signature`가 보이면 GCP에서 **새 JSON 키**를 발급해 "
            "Secrets/`service_account.json`을 교체하세요.\n\n"
            "**`Unable to load PEM file` / `InvalidByte`:** Secrets의 `private_key`가 "
            "깨진 경우입니다. `[gcp_service_account]` 대신 "
            "`GOOGLE_SERVICE_ACCOUNT_JSON`에 **JSON 파일 전체 한 줄**을 넣는 것이 "
            "가장 안전합니다."
        ),
        "phase_collect": "서사 자원을 모으는 중",
        "profile_nick": "닉네임",
        "profile_age": "연령",
        "profile_stage": "생애 단계",
        "profile_companion": "동반",
        "returning_badge": "🔄 재방문",
    },
    "en": {
        "app_title": "dlinso",
        "beta_badge": "Beta 1.0",
        "hub_eyebrow": "",
        "intro_headline": (
            "Discover your treasure through dialogue — your life as art. dlinso"
        ),
        "intro_sub": (
            "Where daily life becomes a work and your strengths shine in what you record. "
            "dlinso is a conversational reflection space to complete your own story."
        ),
        "intro_guide_label": "Guide",
        "intro_guide_body": (
            "**Narrative structuring** — we shape the flow of your story from dialogue. "
            "Your words are kept safe."
        ),
        "err_gemini_reply": "Could not prepare a dialogue response",
        "err_gemini_leaked": (
            "The dialogue connection was blocked. "
            "Update the connection key in Streamlit **Secrets** (and local `.env`), "
            "then **Reboot** the app."
        ),
        "err_dialogue_unavailable": (
            "Dialogue is unavailable right now. Please check the connection settings."
        ),
        "err_dialogue_not_connected": "Not connected to dialogue.",
        "status_dialogue": "Dialogue",
        "status_record": "Record",
        "hub_tagline": "",
        "hub_slogan": (
            "Discover your treasure through dialogue — your life as art. **dlinso**"
        ),
        "hub_slogan_beta_note": "Beta release — features and copy are still evolving.",
        "lang_label": "Language",
        "tab_new": "First visit",
        "tab_return": "Continue",
        "consent_title": "Privacy & Research Consent",
        "consent_check": "I agree to anonymous research use. (Required)",
        "key_hint": (
            "🔑 Your **nickname** and **password** are your unique key. "
            "Use the same pair under **Continue** to resume your story."
        ),
        "return_hint": "🔑 Enter the **nickname** and **password** you created to restore your story.",
        "nickname": "Nickname",
        "password": "Password",
        "password_confirm": "Confirm password",
        "gender": "Gender",
        "age": "Age group",
        "age_current": "Current age group",
        "age_field_help": (
            "Saved in your profile for tone and context only—not to pick which era to discuss."
        ),
        "education_field_help": (
            "Your current life stage helps us match tone as we walk alongside you."
        ),
        "profile_save_hint": (
            "Enter your **current** age and life stage below. "
            "Your first message can be about today or long ago—whatever comes to mind."
        ),
        "chat_age_context_caption": (
            "Current age {age} · life stage {stage} — we match this tone. "
            "Write freely about today or the past."
        ),
        "mode_lifespan_label": "Life-narrative dialogue",
        "mode_lifespan_desc": (
            "Dialogue in a tone that fits you now; your story unfolds as we talk."
        ),
        "education": "Education / life stage",
        "nav_home": "🏠 dlinso",
        "nav_consult": "📖 My story",
        "nav_inquiry": "✉️ Contact",
        "nav_inquiry_short": "✉️",
        "inquiry_page_title": "✉️ Contact the lab",
        "inquiry_page_intro": (
            "Fill out the form below and tap **Send** — your message is saved "
            "to Google Sheets (no email app required)."
        ),
        "inquiry_guest_nick": "Nickname (if not signed in yet)",
        "inquiry_empty": "Please enter your message.",
        "inquiry_back": "← Back",
        "inquiry_fab_label": "✉️ Research collaboration & inquiries",
        "btn_start": "✅ Agree and start my story",
        "btn_continue": "✅ Continue my story",
        "gentle_record": "Your story is gently being recorded 🌿",
        "input_hint": (
            "Tap here to chat. Add a memory photo to talk about it. "
            "Inquiries: ✉️ Contact (top menu)."
        ),
        "chat_composer_guide": (
            "Tap here to chat. Add a memory photo to talk about it. "
            "Inquiries: ✉️ Contact (top menu)."
        ),
        "chat_photo_row_caption": "📷 Photo (optional)",
        "chat_photo_label": "Upload photo",
        "chat_photo_hint": "📷 We read color, composition, and mood — then continue the dialogue.",
        "chat_alt_send": "Send",
        "midpoint_analysis_btn": (
            "Mid-conversation summary & your mind map"
        ),
        "midpoint_analysis_btn_rerun": "Mid-summary · mind map again",
        "midpoint_view_expand": "🗺️ View your mind map again",
        "reflection_depth_gauge_label": "Depth of reflection",
        "midpoint_encourage_before_unlock": (
            "Your story is growing beautifully. "
            "A few more exchanges, and we can offer a mid-conversation summary."
        ),
        "narrative_asset_progress_label": "Narrative assetization progress",
        "narrative_asset_progress_turns": (
            "{current}/{need} turns · {percent}% — keep sharing your story"
        ),
        "narrative_asset_progress_ready": (
            "You're ready. Use the button below for your mind map."
        ),
        "narrative_asset_progress_need_detail": (
            "10 turns reached. Add a more concrete scene for a clearer map."
        ),
        "midpoint_need_turns": (
            "Summary unlocks after {need} replies. (now {current})"
        ),
        "midpoint_scaffold_default": (
            "Share a bit more context so we can draw a clearer map."
        ),
        "midpoint_char_mobile_hint": "On mobile, about 1,000 characters is often enough.",
        "midpoint_char_over": "You can enter up to {limit:,} characters.",
        "chat_ph_collect": "Share what's on your heart today…",
        "chat_ph_giant": "Continue your story…",
        "chat_opening_placeholder": (
            "What story is sitting largest in your heart today?"
        ),
        "err_sheets_busy": (
            "Many people are connected right now; saving was delayed. "
            "Please try again shortly, or check that the same message was not sent twice."
        ),
        "sidebar_inquiry": "Contact the lab",
        "inquiry_type_label": "Inquiry type",
        "inquiry_type_general": "General counseling",
        "inquiry_type_research": "Narrative research collaboration",
        "inquiry_type_interview": "Interview request",
        "researcher_affiliation": "Affiliation (institution / department)",
        "researcher_contact": "Contact (email / phone)",
        "inquiry_placeholder": "Questions or messages for the research team…",
        "inquiry_send": "Send inquiry",
        "inquiry_ok": "Your message was saved to Google Sheets. 🌿",
        "admin_reply_title": "🌿 A reply from Director sinihyun has arrived",
        "admin_reply_title_research": "🌿 Jjokjjok Lab · Narrative research collaboration reply",
        "admin_reply_title_interview": "🌿 Jjokjjok Lab · Interview-related reply",
        "connection": "Connection",
        "connected": "Connected",
        "disconnected": "Not connected",
        "reset_chat": "Reset conversation",
        "finish_chat": "Finish today · receive summary",
        "new_story": "Start a new story",
        "err_login_both": "Enter both nickname and password.",
        "err_consent": "Please check the consent box.",
        "err_nick": "Please enter a nickname.",
        "err_pw": "Please enter a password.",
        "err_pw_match": "Passwords do not match.",
        "err_nick_taken": "Nickname taken. Use **Continue** to log in.",
        "err_login": "Invalid nickname or password.",
        "err_sheets": "Google Sheets connection required.",
        "err_sheets_setup": (
            "**Streamlit Cloud:** add `GOOGLE_SHEET_ID` and `[gcp_service_account]` "
            "under **Settings → Secrets**. Share the spreadsheet with the service "
            "account email as **Editor**. Regenerate the JSON key if you see "
            "`Invalid JWT Signature`."
        ),
        "phase_collect": "Collecting narrative resources",
        "profile_nick": "Nickname",
        "profile_age": "Age",
        "profile_stage": "Life stage",
        "profile_companion": "Companion",
        "returning_badge": "🔄 Return visit",
    },
    "mn": {
        "app_title": "dlinso",
        "beta_badge": "Beta 1.0",
        "hub_eyebrow": "Narrative Research Hub",
        "hub_tagline": "Дэлхийн түүхийн судалгаа, хувийн түүхийн дэмжлэг нэг төвд.",
        "lang_label": "Хэл",
        "tab_new": "Анх удаа",
        "tab_return": "Үргэлжлүүлэх",
        "consent_title": "Нууцлал ба судалгааны зөвшөөрөл",
        "consent_check": "Судалгаанд зөвшөөрч байна. (Заавал)",
        "key_hint": "🔑 **Хоч нэр** болон **нууц үг** таны түлхүүр.",
        "return_hint": "🔑 Бүртгэсэн **хоч нэр**, **нууц үг**-ээр үргэлжлүүлнэ.",
        "nickname": "Хоч нэр",
        "password": "Нууц үг",
        "password_confirm": "Нууц үг баталгаажуулах",
        "gender": "Хүйс",
        "age": "Насны бүлэг",
        "education": "Боловсрол / амьдралын үе",
        "btn_start": "Зөвшөөрч эхлэх",
        "btn_continue": "Түүхээ үргэлжлүүлэх",
        "gentle_record": "Таны түүх аажмаар бичигдэж байна 🌿",
        "input_hint": "💬 Дэлгэцийн **доод** хэсэгт бичнэ үү.",
        "chat_ph_collect": "Дулаан дурсамжаа хуваалцаарай…",
        "chat_ph_giant": "Үргэлжлүүлээрэй…",
        "opening": "Эхлээд **дурсамж**-аасаа ярьцгаая…",
        "sidebar_inquiry": "Судалгааны газарт асуух",
        "inquiry_type_label": "Асуултын төрөл",
        "inquiry_type_general": "Ерөнхий зөвлөгөө",
        "inquiry_type_research": "Түүхийн судалгааны хамтын ажиллагаа",
        "inquiry_type_interview": "Ярилцлагын асуулт",
        "researcher_affiliation": "Харьяалал (байгууллага)",
        "researcher_contact": "Холбоо барих",
        "inquiry_placeholder": "Асуулт, зурвас…",
        "inquiry_send": "Илгээх",
        "inquiry_ok": "Илгээгдлээ. 🌿",
        "admin_reply_title": "🌿 sinihyun захирлын хариу ирлээ",
        "admin_reply_title_research": "🌿 Түүхийн судалгааны хамтын ажиллагааны хариу",
        "admin_reply_title_interview": "🌿 Ярилцлагын хариу",
        "connection": "Холболт",
        "connected": "Холбогдсон",
        "disconnected": "Холбогдоогүй",
        "reset_chat": "Яриаг цэвэрлэх",
        "finish_chat": "Дуусгах · хураангуй",
        "err_consent": "Зөвшөөрөл өгнө үү.",
        "err_nick": "Хоч нэр оруулна уу.",
        "err_pw": "Нууц үг оруулна уу.",
        "err_pw_match": "Нууц үг таарахгүй байна.",
        "err_nick_taken": "Хоч нэр бүртгэгдсэн.",
        "err_login": "Буруу хоч нэр эсвэл нууц үг.",
        "err_sheets": "Sheets холболт шаардлагатай.",
        "phase_collect": "Түүх цуглуулж байна",
        "returning_badge": "🔄 Буцах",
    },
    "ja": {
        "app_title": "dlinso",
        "beta_badge": "Beta 1.0",
        "hub_eyebrow": "Narrative Research Hub",
        "hub_tagline": "グローバルな物語研究と個人の物語伴走を一つのハブで。",
        "lang_label": "言語",
        "tab_new": "初めての方",
        "tab_return": "続きから",
        "consent_title": "プライバシーと研究同意",
        "consent_check": "研究目的・匿名処理に同意します（必須）",
        "key_hint": "🔑 **ニックネーム**と**パスワード**があなたの鍵です。",
        "return_hint": "🔑 登録した**ニックネーム**と**パスワード**で再開します。",
        "nickname": "ニックネーム",
        "password": "パスワード",
        "password_confirm": "パスワード確認",
        "gender": "性別",
        "age": "年代",
        "education": "学歴・ライフステージ",
        "btn_start": "同意して始める",
        "btn_continue": "物語を続ける",
        "gentle_record": "心の記録が少しずつ積み重なっています 🌿",
        "input_hint": "💬 画面**下**の入力欄に入力してください。",
        "chat_ph_collect": "温かい記憶を聞かせてください…",
        "chat_ph_giant": "続きをどうぞ…",
        "opening": "まず**心が温まる記憶**から話しませんか？",
        "sidebar_inquiry": "研究所へ問い合わせ",
        "inquiry_type_label": "お問い合わせ種別",
        "inquiry_type_general": "一般相談",
        "inquiry_type_research": "ナラティブ研究協働",
        "inquiry_type_interview": "インタビュー問い合わせ",
        "researcher_affiliation": "所属（機関・学部）",
        "researcher_contact": "連絡先（メール・電話）",
        "inquiry_placeholder": "ご質問・メッセージ…",
        "inquiry_send": "送信",
        "inquiry_ok": "送信しました。🌿",
        "admin_reply_title": "🌿 じょっきょっ研究所 sinihyun 所長からの返信が届きました",
        "admin_reply_title_research": "🌿 ナラティブ研究協働に関する返信",
        "admin_reply_title_interview": "🌿 インタビューに関する返信",
        "connection": "接続",
        "connected": "接続済み",
        "disconnected": "未接続",
        "reset_chat": "会話をリセット",
        "finish_chat": "今日の物語を終える",
        "err_consent": "同意にチェックしてください。",
        "err_nick": "ニックネームを入力してください。",
        "err_pw": "パスワードを入力してください。",
        "err_pw_match": "パスワードが一致しません。",
        "err_nick_taken": "使用中のニックネームです。",
        "err_login": "ニックネームまたはパスワードが違います。",
        "err_sheets": "Sheets接続が必要です。",
        "phase_collect": "物語の資源を集めています",
        "returning_badge": "🔄 再訪",
    },
    "zh": {
        "app_title": "dlinso",
        "beta_badge": "Beta 1.0",
        "hub_eyebrow": "Narrative Research Hub",
        "hub_tagline": "全球叙事研究与个人叙事陪伴，汇聚于一站。",
        "lang_label": "语言",
        "tab_new": "首次访问",
        "tab_return": "继续",
        "consent_title": "隐私与研究同意",
        "consent_check": "我同意匿名研究使用（必填）",
        "key_hint": "🔑 **昵称**和**密码**是您的专属钥匙。",
        "return_hint": "🔑 输入注册时的**昵称**和**密码**以恢复故事。",
        "nickname": "昵称",
        "password": "密码",
        "password_confirm": "确认密码",
        "gender": "性别",
        "age": "年龄段",
        "education": "学历/生命阶段",
        "btn_start": "同意并开始",
        "btn_continue": "继续我的故事",
        "gentle_record": "心灵的记录正在慢慢积累 🌿",
        "input_hint": "💬 请在屏幕**底部**输入框中对话。",
        "chat_ph_collect": "分享一段温暖的记忆…",
        "chat_ph_giant": "继续诉说…",
        "opening": "我们先从**温暖心底的记忆**开始好吗？",
        "sidebar_inquiry": "联系研究所",
        "inquiry_type_label": "咨询类型",
        "inquiry_type_general": "一般咨询",
        "inquiry_type_research": "叙事研究合作",
        "inquiry_type_interview": "访谈咨询",
        "researcher_affiliation": "所属（机构·院系）",
        "researcher_contact": "联系方式（邮箱·电话）",
        "inquiry_placeholder": "问题或留言…",
        "inquiry_send": "发送",
        "inquiry_ok": "已发送。🌿",
        "admin_reply_title": "🌿 凹凸研究所 sinihyun 所长的回复已到达",
        "admin_reply_title_research": "🌿 叙事研究合作回复",
        "admin_reply_title_interview": "🌿 访谈相关回复",
        "connection": "连接",
        "connected": "已连接",
        "disconnected": "未连接",
        "reset_chat": "重置对话",
        "finish_chat": "结束今天 · 领取摘要",
        "err_consent": "请勾选同意。",
        "err_nick": "请输入昵称。",
        "err_pw": "请输入密码。",
        "err_pw_match": "密码不一致。",
        "err_nick_taken": "昵称已被使用。",
        "err_login": "昵称或密码错误。",
        "err_sheets": "需要连接 Google Sheets。",
        "phase_collect": "正在收集叙事资源",
        "returning_badge": "🔄 回访",
    },
    "vi": {
        "app_title": "dlinso",
        "beta_badge": "Beta 1.0",
        "hub_eyebrow": "Narrative Research Hub",
        "hub_tagline": "Nghiên cứu tự sự toàn cầu và đồng hành câu chuyện cá nhân.",
        "lang_label": "Ngôn ngữ",
        "tab_new": "Lần đầu",
        "tab_return": "Tiếp tục",
        "consent_title": "Đồng ý nghiên cứu & quyền riêng tư",
        "consent_check": "Tôi đồng ý (bắt buộc)",
        "key_hint": "🔑 **Biệt danh** và **mật khẩu** là chìa khóa của bạn.",
        "return_hint": "🔑 Nhập **biệt danh** và **mật khẩu** đã đăng ký.",
        "nickname": "Biệt danh",
        "password": "Mật khẩu",
        "password_confirm": "Xác nhận mật khẩu",
        "gender": "Giới tính",
        "age": "Nhóm tuổi",
        "education": "Học vấn / giai đoạn đời",
        "btn_start": "Đồng ý và bắt đầu",
        "btn_continue": "Tiếp tục câu chuyện",
        "gentle_record": "Ký ức đang được ghi lại nhẹ nhàng 🌿",
        "input_hint": "💬 Nhập vào ô chat **phía dưới** màn hình.",
        "chat_ph_collect": "Kể một kỷ niệm ấm áp…",
        "chat_ph_giant": "Tiếp tục kể…",
        "opening": "Chúng ta bắt đầu với **kỷ niệm ấm áp** nhé?",
        "sidebar_inquiry": "Liên hệ phòng nghiên cứu",
        "inquiry_type_label": "Loại yêu cầu",
        "inquiry_type_general": "Tư vấn chung",
        "inquiry_type_research": "Hợp tác nghiên cứu tự sự",
        "inquiry_type_interview": "Phỏng vấn",
        "researcher_affiliation": "Đơn vị (cơ quan / khoa)",
        "researcher_contact": "Liên hệ (email / điện thoại)",
        "inquiry_placeholder": "Câu hỏi hoặc lời nhắn…",
        "inquiry_send": "Gửi",
        "inquiry_ok": "Đã gửi. 🌿",
        "admin_reply_title": "🌿 Phản hồi từ Giám đốc sinihyun đã đến",
        "admin_reply_title_research": "🌿 Hợp tác nghiên cứu tự sự — phản hồi",
        "admin_reply_title_interview": "🌿 Phỏng vấn — phản hồi",
        "connection": "Kết nối",
        "connected": "Đã kết nối",
        "disconnected": "Chưa kết nối",
        "reset_chat": "Xóa hội thoại",
        "finish_chat": "Kết thúc hôm nay",
        "err_consent": "Vui lòng đồng ý.",
        "err_nick": "Nhập biệt danh.",
        "err_pw": "Nhập mật khẩu.",
        "err_pw_match": "Mật khẩu không khớp.",
        "err_nick_taken": "Biệt danh đã dùng.",
        "err_login": "Sai biệt danh hoặc mật khẩu.",
        "err_sheets": "Cần kết nối Sheets.",
        "phase_collect": "Đang thu thập câu chuyện",
        "returning_badge": "🔄 Quay lại",
    },
}

from i18n_opening import merge_opening_i18n

merge_opening_i18n(TEXTS)


def get_lang() -> str:
    code = st.session_state.get("lang", "ko")
    return code if code in LANG_CODES else "ko"


def t(key: str, lang: str | None = None) -> str:
    code = lang or get_lang()
    bucket = TEXTS.get(code, TEXTS["ko"])
    if key in bucket:
        return bucket[key]
    if code not in ("ko", "en") and key in TEXTS.get("en", {}):
        return TEXTS["en"][key]
    return TEXTS["ko"].get(key, key)


def render_language_selector(
    *,
    key: str = "lang_selector",
    compact: bool = False,
) -> None:
    """언어 선택 — 각 언어의 고유 이름(한국어, English, 日本語 …)으로 표시."""
    current = get_lang()
    idx = LANG_CODES.index(current) if current in LANG_CODES else 0
    choice = st.selectbox(
        t("lang_label"),
        options=list(LANG_CODES),
        format_func=lambda c: LANG_LABELS[c],
        index=idx,
        key=key,
        label_visibility="collapsed" if compact else "visible",
    )
    if choice != st.session_state.get("lang"):
        st.session_state.lang = choice
        st.rerun()
