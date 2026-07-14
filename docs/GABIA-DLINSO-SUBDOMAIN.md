# dlniso.com → Streamlit 앱 (가비아 URL 포워딩)

Streamlit Community Cloud는 커스텀 도메인 CNAME을 지원하지 않습니다.  
**가비아 URL 포워딩(301)**으로 `dlniso.com` → 앱만 연결하면 됩니다.

브랜드 표기: **들니소** (한글) / **dlniso** (영문) · `core/brand.py`  
운영사: **바이브스타틱스(VibeStatics)** — 별도 홈 https://vibestatics.com/  
(가비아 키워드에는 들니소만: `dlniso, 들니소, 서사`)

| 주소 | 역할 |
|------|------|
| **https://dlniso.com** | 들니소 입구 (가비아 → Streamlit) |
| **https://vibestatics.com** | 바이브스타틱스 회사 홈 (별도) |
| **Streamlit 앱** | 실제 대화 (`?gate=1`) |

---

## 가비아에서 할 일

1. [가비아](https://www.gabia.com) 로그인 → **My가비아** → **dlniso.com** 관리
2. **DNS 관리** 또는 **URL 포워딩** 메뉴
3. 포워딩 추가 (루트 `@` / 또는 도메인 자체):
   - **유형**: URL 포워딩 · **301 리다이렉트** (가능하면)
   - **대상 URL**:  
     `https://dlinso-2fafhxhzevtw5oeelwinsf.streamlit.app/?gate=1`
4. **www**도 같은 대상으로 포워딩 (또는 www → dlniso.com)
5. 저장 → 10분~24시간 전파 대기
6. 브라우저에서 `https://dlniso.com` 접속 → 앱으로 이동하는지 확인

> CNAME을 `*.streamlit.app`으로 직접 걸지 마세요. HTTPS가 깨집니다.

---

## (선택) 앱 주소 짧게

1. [share.streamlit.io](https://share.streamlit.io) → 앱 → **Settings → App URL**
2. `dlniso`로 변경 → `https://dlniso.streamlit.app`
3. 가비아 포워딩 대상을 새 URL로 바꾸고, `core/public_urls.py`의 `DLINSO_APP`도 갱신

---

## 확인

- [ ] `https://dlniso.com` → Streamlit 앱 (`?gate=1`)
- [ ] `https://www.dlniso.com` → 동일
- [ ] 앱 UI에 **들니소** / **dlniso** 표기 (구 dlinso·DeulniSo 없음)
