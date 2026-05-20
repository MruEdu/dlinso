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
    "primary": (
        "🌿 dlinso: 개개인성 기반 내러티브 연구 허브 (Beta 1.0)"
    ),
    "secondary": "Dlinso Lab",
    "copyright": "© 2026 Dlinso Lab by sinihyun. All Rights Reserved.",
    "powered": "Powered by Gemini 2.5 Flash · Google Sheets",
}

# 공통 옵션 (연령·학력은 연구 표준 한국어 라벨 유지, UI만 번역)
TEXTS: dict[str, dict[str, str]] = {
    "ko": {
        "app_title": "dlinso",
        "beta_badge": "Beta 1.0",
        "hub_eyebrow": "Narrative Research · dlinso",
        "hub_tagline": "",
        "hub_slogan": (
            "마음의 정원사와 나누는 들쭉날쭉한 일상 서사 — "
            "당신만의 고유한 가치를 열매로 맺는 **익명 베타 테스트**에 함께해 주세요."
        ),
        "hub_slogan_beta_note": (
            "지금은 **Beta 1.0** 익명 베타 기간입니다. "
            "닉네임과 비밀번호만으로 안전하게 이어갈 수 있어요."
        ),
        "err_gemini_reply": "응답 생성 중 오류가 발생했습니다",
        "err_gemini_leaked": (
            "Gemini API 키가 유출로 차단되었습니다. "
            "[Google AI Studio](https://aistudio.google.com/apikey)에서 **새 API 키**를 만든 뒤 "
            "Streamlit Cloud **Settings → Secrets**와 로컬 `.env`의 `GEMINI_API_KEY`를 "
            "교체하고 앱을 **Reboot**하세요."
        ),
        "lang_label": "언어",
        "tab_new": "처음 오신 분",
        "tab_return": "다시 오신 분",
        "onboarding_banner": (
            "👇 아래에서 **개인정보 동의** 후, "
            "「처음 오신 분」또는 「다시 오신 분」탭을 선택해 주세요."
        ),
        "nav_home": "🏠 dlinso 안내",
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
        "intro_hint": "가입·동의·로그인은 상단 **📖 나의 이야기** 메뉴에서 진행합니다.",
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
        "chat_photo_hint": "📷 사진의 색·구도·사물을 읽고, 마음의 정원사가 씨앗이 될 질문으로 이어갑니다.",
        "chat_alt_send": "보내기",
        "midpoint_analysis_btn": (
            "지금까지의 대화 중간 정리 및 나만의 마음 지도 확인"
        ),
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
        "chat_ph_collect": "지금 마음이나 기억을 적어 보세요…",
        "chat_ph_giant": "이어서 적어 보세요…",
        "opening": (
            "저는 **마음의 정원사**입니다. 답을 대신 드리지 않고, "
            "당신의 말씀을 **열매를 맺을 씨앗**으로 받아 질문으로 돌봅니다.\n\n"
            "따뜻한 기억, 사진, 또는 지금 마음 — 무엇이든 괜찮아요."
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
        "hub_eyebrow": "Narrative Research · dlinso",
        "err_gemini_reply": "Error while generating a reply",
        "err_gemini_leaked": (
            "Your Gemini API key was reported as leaked and blocked. "
            "Create a **new key** at [Google AI Studio](https://aistudio.google.com/apikey), "
            "update `GEMINI_API_KEY` in Streamlit **Settings → Secrets** (and local `.env`), "
            "then **Reboot** the app."
        ),
        "hub_tagline": (
            "Everyday bumpy stories with the Mind Gardener — "
            "join our anonymous beta to grow your unique values into fruit."
        ),
        "hub_slogan": (
            "Everyday jagged stories with the **Mind Gardener** — "
            "grow your unique values into fruit. Join our **anonymous beta test**."
        ),
        "hub_slogan_beta_note": (
            "Now in **Beta 1.0** — participate anonymously with only a nickname and password."
        ),
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
        "education": "Education / life stage",
        "nav_home": "🏠 dlinso guide",
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
        "chat_photo_hint": "📷 We read color, composition, and objects — then ask a maieutic question.",
        "chat_alt_send": "Send",
        "midpoint_analysis_btn": (
            "Mid-conversation summary & your mind map"
        ),
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
        "chat_ph_collect": "Write what's on your mind…",
        "chat_ph_giant": "Continue your story…",
        "opening": (
            "Shall we begin with a **memory that warms your heart**?\n\n"
            "A joyful moment, a small achievement, or a memory you wish to keep."
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


def get_lang() -> str:
    code = st.session_state.get("lang", "ko")
    return code if code in LANG_CODES else "ko"


def t(key: str, lang: str | None = None) -> str:
    code = lang or get_lang()
    return TEXTS.get(code, TEXTS["ko"]).get(key, TEXTS["ko"].get(key, key))


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
