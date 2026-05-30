# Streamlit Cloud 배포 가이드 (dlinso v2)

## 1. 저장소 연결

1. [share.streamlit.io](https://share.streamlit.io) → **New app**
2. GitHub 저장소 `MruEdu/dlinso` (또는 본 프로젝트) 선택
3. **Main file path**: `app.py`
4. **Branch**: `main` (또는 배포 브랜치)

## 2. requirements.txt

루트의 `requirements.txt`가 자동 설치됩니다. 별도 `packages.txt`는 없습니다.

## 3. Secrets (필수)

앱 → **Settings → Secrets** 에 아래 TOML을 **통째로** 붙여넣고 값을 채운 뒤 **Save** → **Reboot app**.

```toml
# --- LLM (Upstage 권장) ---
UPSTAGE_API_KEY = "up_xxxxxxxx"
UPSTAGE_MODEL = "solar-pro3"
LLM_PROVIDER = "upstage"

# --- Gemini 폴백 (Upstage 미사용 시) ---
# GEMINI_API_KEY = "AIza..."
# GEMINI_MODEL = "gemini-2.5-flash"
# LLM_PROVIDER = "gemini"

# --- Supabase (숲 · 여정 · 학습 — Cloud 영속 저장) ---
[supabase]
url = "https://xxxx.supabase.co"
key = "sb_publishable_..." 

# 또는 평면 키:
# SUPABASE_URL = "https://xxxx.supabase.co"
# SUPABASE_KEY = "sb_publishable_..."

# --- SQLite 경로 (Cloud: 상대 경로 권장, 생략 가능) ---
# DATABASE_PATH = "data/dlinso.db"
# ISOLATION_DATABASE_PATH = "data/isolation.db"

# --- 선택 ---
# INQUIRY_EMAIL = "lab@example.com"
```

### 키 위치

| 항목 | 어디서 |
|------|--------|
| `UPSTAGE_API_KEY` | [Upstage Console](https://console.upstage.ai/api-keys) |
| `[supabase] url` / `key` | Supabase → Project Settings → API |
| `GEMINI_API_KEY` | Google AI Studio |

**주의:** Secrets에 넣은 값은 Git에 커밋하지 마세요. `.env`는 Cloud에서 읽히지 않습니다 (`st.secrets`만 사용).

## 4. Supabase 테이블

배포 전 Supabase SQL Editor에서 **두 스크립트**를 실행하세요.

1. `scripts/supabase_isolation_narratives.sql` — 숲 모듈
2. `scripts/supabase_dlinso_cloud.sql` — **여정 · 학습** (재로그인·대화 복원)
3. `scripts/supabase_narrative_archive.sql` — **user_sessions · narrative_assets** (기록실 Memory)

동일한 `[supabase] url` / `key` Secrets 를 사용합니다.

## 5. 로컬 경로 / SQLite on Cloud

- 코드는 `APP_DIR/data/*.db` 를 기본으로 사용합니다.
- `.env`에 `E:\work\...` 같은 Windows 절대 경로가 있어도 Cloud(Linux)에서는 **자동으로** `data/isolation.db` 등으로 폴백합니다.
- Streamlit Cloud의 디스크는 **재시작 시 초기화**될 수 있습니다.
- **숲** → `isolation_narratives` · **여정·학습** → `dlinso_users` + `dlinso_conversation_turns` (Supabase)

## 6. 배포 후 확인

1. 홈 → **학습 · 성장의 서사** 또는 **숲 · 연결의 서사** 진입
2. 대화 1턴 전송
3. Supabase Table Editor 확인:
   - 학습/여정: `dlinso_conversation_turns`
   - 숲: `isolation_narratives`
4. LLM 오류 시 Secrets의 `UPSTAGE_API_KEY` / `LLM_PROVIDER` 재확인 후 Reboot

## 7. 로컬 vs Cloud

| | 로컬 | Streamlit Cloud |
|---|------|-----------------|
| API 키 | `.streamlit/secrets.toml` 또는 `.env` | **Settings → Secrets** |
| DB | `data/*.db` | `data/*.db` (임시) + Supabase (전 모듈) |
| 진입 | `run_app.bat` | 배포 URL |

템플릿 파일: `.streamlit/secrets.toml.example`
