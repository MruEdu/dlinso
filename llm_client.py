"""
LLM 호출 추상화 — Upstage Solar (OpenAI 호환) / Gemini.

마이그레이션: narrative_engine · maieutic_engine · app.py 의
`genai.GenerativeModel` / `generate_content` 호출을 이 모듈로 옮깁니다.

환경 변수 (.env / Streamlit Secrets):
  LLM_PROVIDER=upstage | gemini
  UPSTAGE_API_KEY, UPSTAGE_MODEL=solar-pro3
  GEMINI_API_KEY, GEMINI_MODEL (폴백)
"""

from __future__ import annotations

import base64
import json
import re
from collections.abc import Iterator
from typing import Any

from env_config import (
    ENV_PATH,
    UPSTAGE_API_BASE,
    get_gemini_api_key,
    get_gemini_model_name,
    get_llm_provider,
    get_upstage_api_key,
    get_upstage_model_name,
)

_openai_client: Any | None = None
_gemini_configured = False


class LLMNotConfiguredError(RuntimeError):
    """API 키·provider 미설정."""


def extract_json(text: str) -> dict | None:
    text = (text or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None


def _require_upstage_key() -> str:
    key = get_upstage_api_key()
    if not key:
        raise LLMNotConfiguredError(
            f"UPSTAGE_API_KEY가 설정되지 않았습니다. {ENV_PATH} 또는 Streamlit Secrets를 확인하세요."
        )
    return key


def _ensure_gemini() -> None:
    global _gemini_configured
    if _gemini_configured:
        return
    import google.generativeai as genai

    api_key = get_gemini_api_key()
    if not api_key:
        raise LLMNotConfiguredError(
            f"GEMINI_API_KEY가 설정되지 않았습니다. {ENV_PATH} 파일을 확인하세요."
        )
    genai.configure(api_key=api_key)
    _gemini_configured = True


def get_openai_client() -> Any:
    """Upstage Solar — OpenAI SDK + base_url."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "openai 패키지가 필요합니다: pip install 'openai>=1.52.0'"
        ) from exc
    _openai_client = OpenAI(api_key=_require_upstage_key(), base_url=UPSTAGE_API_BASE)
    return _openai_client


def effective_llm_provider() -> str:
    """설정 provider + 실제 키 존재 여부 — Upstage 없으면 Gemini 자동 폴백."""
    pref = get_llm_provider()
    if pref == "upstage" and get_upstage_api_key():
        return "upstage"
    if get_gemini_api_key():
        return "gemini"
    return pref


def is_llm_configured() -> bool:
    provider = effective_llm_provider()
    if provider == "upstage":
        return bool(get_upstage_api_key())
    return bool(get_gemini_api_key())


def messages_from_gemini_history(history: list[dict]) -> list[dict[str, Any]]:
    """app.build_gemini_history 형식 → OpenAI messages."""
    out: list[dict[str, Any]] = []
    for item in history:
        role = item.get("role", "user")
        if role == "model":
            role = "assistant"
        parts = item.get("parts") or []
        text = ""
        if parts:
            first = parts[0]
            text = first if isinstance(first, str) else str(first)
        if text:
            out.append({"role": role, "content": text})
    return out


def init_llm_client() -> None:
    """provider에 맞게 클라이언트 초기화 — 실패 시 LLMNotConfiguredError."""
    if effective_llm_provider() == "upstage":
        get_openai_client()
    else:
        _ensure_gemini()


def _upstage_user_content(
    text: str,
    *,
    image_bytes: bytes | None = None,
    image_mime: str = "image/jpeg",
) -> str | list[dict[str, Any]]:
    if not image_bytes:
        return text
    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    mime = image_mime or "image/jpeg"
    parts: list[dict[str, Any]] = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"},
        },
    ]
    if text.strip():
        parts.append({"type": "text", "text": text})
    else:
        parts.append({"type": "text", "text": "(사진을 보냈습니다)"})
    return parts


def _upstage_chat_create(
    *,
    messages: list[dict[str, Any]],
    system: str | None = None,
    temperature: float = 0.7,
    top_p: float | None = None,
    max_tokens: int = 2048,
    stream: bool = False,
) -> Any:
    client = get_openai_client()
    payload: list[dict[str, Any]] = []
    if system and system.strip():
        payload.append({"role": "system", "content": system.strip()})
    payload.extend(messages)
    kwargs: dict[str, Any] = {
        "model": get_upstage_model_name(),
        "messages": payload,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
    }
    if top_p is not None:
        kwargs["top_p"] = top_p
    return client.chat.completions.create(**kwargs)


def _gemini_generate_text(
    prompt: str,
    *,
    system: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    image_bytes: bytes | None = None,
    image_mime: str = "image/jpeg",
) -> str:
    import google.generativeai as genai

    _ensure_gemini()
    model = genai.GenerativeModel(
        get_gemini_model_name(),
        system_instruction=system or None,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
    )
    if image_bytes:
        content: list[Any] = [
            {"mime_type": image_mime or "image/jpeg", "data": image_bytes},
            prompt,
        ]
    else:
        content = prompt
    response = model.generate_content(content)
    return (response.text or "").strip()


def generate_text(
    prompt: str,
    *,
    system: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    image_bytes: bytes | None = None,
    image_mime: str = "image/jpeg",
) -> str:
    """단일 프롬프트 완성 — narrative_engine · maieutic 분석용."""
    if effective_llm_provider() == "upstage":
        messages: list[dict[str, Any]] = []
        if image_bytes:
            b64 = base64.standard_b64encode(image_bytes).decode("ascii")
            mime = image_mime or "image/jpeg"
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            )
        else:
            messages.append({"role": "user", "content": prompt})
        response = _upstage_chat_create(
            messages=messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )
        return (response.choices[0].message.content or "").strip()
    return _gemini_generate_text(
        prompt,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        image_bytes=image_bytes,
        image_mime=image_mime,
    )


def generate_json(
    prompt: str,
    *,
    system: str | None = None,
    temperature: float = 0.45,
    max_tokens: int = 600,
    image_bytes: bytes | None = None,
    image_mime: str = "image/jpeg",
) -> dict | None:
    raw = generate_text(
        prompt,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        image_bytes=image_bytes,
        image_mime=image_mime,
    )
    return extract_json(raw)


def _gemini_stream_chunks(response: Any) -> Iterator[str]:
    accumulated: list[str] = []
    for chunk in response:
        piece = ""
        try:
            text = chunk.text
            if text:
                piece = str(text)
        except Exception:  # noqa: BLE001
            pass
        if not piece:
            for cand in getattr(chunk, "candidates", None) or []:
                content = getattr(cand, "content", None)
                for part in getattr(content, "parts", None) or []:
                    t = getattr(part, "text", None)
                    if t:
                        piece += str(t)
        if piece:
            accumulated.append(piece)
            yield piece
    streamed = "".join(accumulated)
    try:
        final = (response.text or "").strip()
    except Exception:  # noqa: BLE001
        final = ""
    if not final:
        parts: list[str] = []
        for cand in getattr(response, "candidates", None) or []:
            content = getattr(cand, "content", None)
            for part in getattr(content, "parts", None) or []:
                t = getattr(part, "text", None)
                if t:
                    parts.append(str(t))
        final = "".join(parts).strip()
    if final and len(final) > len(streamed):
        remainder = final[len(streamed) :]
        if remainder:
            yield remainder


def _gemini_message_parts(
    user_prompt: str,
    *,
    image_bytes: bytes | None = None,
) -> list[Any]:
    parts: list[Any] = []
    if image_bytes:
        try:
            from PIL import Image
            import io

            parts.append(Image.open(io.BytesIO(image_bytes)))
        except Exception:  # noqa: BLE001
            pass
    parts.append(user_prompt or "(사진을 보냈습니다)")
    return parts


def iter_chat_stream(
    messages: list[dict],
    user_prompt: str,
    *,
    system: str | None = None,
    temperature: float = 0.82,
    top_p: float = 0.92,
    max_tokens: int = 2048,
    gemini_history: list[dict] | None = None,
    image_bytes: bytes | None = None,
    image_mime: str | None = None,
) -> Iterator[str]:
    """
    채팅 스트리밍 — app.py 대화 UI용.
    system: build_system_instruction() 등 서사 동행자·마이에우틱 지시문.
    gemini_history: build_chat_history(messages) 결과(마지막 user 턴 제외).
    """
    del messages  # history는 gemini_history로 전달
    if effective_llm_provider() == "upstage":
        history = gemini_history if gemini_history is not None else []
        api_messages = messages_from_gemini_history(history)
        user_content = _upstage_user_content(
            user_prompt.strip() or "(메시지)",
            image_bytes=image_bytes,
            image_mime=image_mime or "image/jpeg",
        )
        api_messages.append({"role": "user", "content": user_content})
        stream = _upstage_chat_create(
            messages=api_messages,
            system=system,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=True,
        )
        accumulated: list[str] = []
        for chunk in stream:
            if not getattr(chunk, "choices", None):
                continue
            delta = chunk.choices[0].delta
            piece = getattr(delta, "content", None)
            if piece:
                accumulated.append(str(piece))
                yield str(piece)
        if not accumulated:
            # 스트림이 비었을 때 비스트림 1회로 본문 확보
            fallback = _upstage_chat_create(
                messages=api_messages,
                system=system,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stream=False,
            )
            text = (fallback.choices[0].message.content or "").strip()
            if text:
                yield text
        return

    # Gemini 폴백
    import google.generativeai as genai

    _ensure_gemini()
    history = gemini_history or []
    model = genai.GenerativeModel(
        get_gemini_model_name(),
        system_instruction=system or None,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_tokens,
        ),
    )
    chat = model.start_chat(history=history)
    parts = _gemini_message_parts(
        user_prompt,
        image_bytes=image_bytes,
    )
    response = chat.send_message(parts, stream=True)
    yield from _gemini_stream_chunks(response)


def collect_chat_stream(**kwargs: Any) -> str:
    return "".join(iter_chat_stream(**kwargs)).strip()
