"""Async OpenAI-compatible client factory for DeepSeek + Kimi + Ollama.

Note: Kimi (api.moonshot.cn) intermittently returns DNS / network errors;
retries here are deliberately broad (httpx + socket + generic) and use
exponential backoff with jitter.

The sidecar Ollama models (qwen36 / gemma26 / gemma4b) use the native
/api/chat endpoint instead of /v1/chat/completions because the OpenAI
compat layer silently drops the `think: false` flag.
"""
from __future__ import annotations
import asyncio
import random
import socket
import time
from dataclasses import dataclass

import httpx
from openai import (
    AsyncOpenAI, APIError, APIConnectionError, APITimeoutError, RateLimitError,
)

from config import MODELS, load_keys, TIMEOUT_S, MAX_RETRIES

# Errors that warrant a retry — broad on purpose for Kimi DNS / network flakiness.
_RETRYABLE = (
    APITimeoutError,
    RateLimitError,
    APIConnectionError,
    APIError,
    httpx.ConnectError,
    httpx.ReadError,
    httpx.WriteError,
    httpx.RemoteProtocolError,
    httpx.PoolTimeout,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    socket.gaierror,
    OSError,
    asyncio.TimeoutError,
)


@dataclass
class CallResult:
    text: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    error: str | None = None
    reasoning: str | None = None       # DeepSeek / R1-style CoT, if exposed


@dataclass
class OllamaNativeClient:
    """Tiny async wrapper around Ollama's /api/chat endpoint.

    We need this (rather than the OpenAI compat shim) because
    /v1/chat/completions silently ignores the `think` field, which leaves
    qwen3.6 / qwen3-moe in thinking mode and blows the recovery loop's
    timeout. The native endpoint honours `think: False`."""
    base_url: str   # e.g. http://127.0.0.1:11435 (no /v1 suffix)
    timeout: float


def make_clients() -> dict[str, "AsyncOpenAI | OllamaNativeClient"]:
    keys = load_keys()
    clients = {}
    for name, cfg in MODELS.items():
        if cfg.get("client") == "ollama_native":
            clients[name] = OllamaNativeClient(
                base_url=cfg["base_url"].rstrip("/"), timeout=TIMEOUT_S,
            )
            continue
        key_name = cfg["key_name"]
        if key_name == "_local_ollama":
            key = "ollama"  # ollama doesn't auth; any non-empty string works
        else:
            key = keys.get(key_name)
            if not key:
                raise RuntimeError(f"missing API key for {name}")
        clients[name] = AsyncOpenAI(
            api_key=key, base_url=cfg["base_url"], timeout=TIMEOUT_S
        )
    return clients


def _img_b64(path: str) -> str:
    import base64
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def _data_url(path: str) -> str:
    import mimetypes
    mt = mimetypes.guess_type(path)[0] or "image/jpeg"
    return f"data:{mt};base64,{_img_b64(path)}"


async def chat(
    client: "AsyncOpenAI | OllamaNativeClient",
    model_name: str,
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
    response_format_json: bool = False,
    images: list[str] | None = None,
) -> CallResult:
    """Single chat call with retry on transient errors (incl. Kimi DNS / network).
    images: optional list of local image file paths; when given the user turn becomes
    multimodal (OpenAI image_url data-url / Ollama images base64). Default None = text only."""
    if isinstance(client, OllamaNativeClient):
        return await _chat_ollama_native(
            client, model_name, system, user, temperature, max_tokens,
            response_format_json, images,
        )
    model_id = MODELS[model_name]["model_id"]
    last_err: str | None = None
    for attempt in range(MAX_RETRIES):
        t0 = time.perf_counter()
        try:
            messages = []
            if system:  # Kimi rejects empty-string system messages; skip if blank
                messages.append({"role": "system", "content": system})
            if images:
                content = [{"type": "text", "text": user}]
                for p in images:
                    content.append({"type": "image_url", "image_url": {"url": _data_url(p)}})
                messages.append({"role": "user", "content": content})
            else:
                messages.append({"role": "user", "content": user})
            kwargs = {
                "model": model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format_json:
                kwargs["response_format"] = {"type": "json_object"}
            # Provider-specific knobs (e.g. DeepSeek thinking disable) live
            # in MODELS[name]["extra_body"] and are forwarded by the OpenAI
            # SDK as a top-level extension to the request body.
            extra_body = MODELS[model_name].get("extra_body")
            if extra_body:
                kwargs["extra_body"] = extra_body
            resp = await client.chat.completions.create(**kwargs)
            latency_ms = int((time.perf_counter() - t0) * 1000)
            message = resp.choices[0].message
            text = message.content or ""
            # DeepSeek-V4-Pro and R1 expose chain-of-thought as a separate
            # `reasoning_content` field on the message. The OpenAI Python SDK
            # surfaces it via the model_extra dict when not on the typed
            # attribute. We fall back through both for robustness.
            reasoning = (
                getattr(message, "reasoning_content", None)
                or (message.model_extra or {}).get("reasoning_content")
            )
            usage = resp.usage
            return CallResult(
                text=text,
                reasoning=reasoning,
                latency_ms=latency_ms,
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
            )
        except _RETRYABLE as e:
            last_err = f"{type(e).__name__}: {e}"
            # exponential backoff with jitter; longer for network/DNS errors
            base = 2 ** attempt
            await asyncio.sleep(base + random.uniform(0, base))
        except Exception as e:  # noqa: BLE001 — last-resort capture, do not retry
            last_err = f"{type(e).__name__}: {e}"
            break
    return CallResult(
        text="", latency_ms=0, prompt_tokens=0, completion_tokens=0, error=last_err
    )


async def _chat_ollama_native(
    client: OllamaNativeClient,
    model_name: str,
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
    response_format_json: bool,
    images: list[str] | None = None,
) -> CallResult:
    """POST to <base>/api/chat. Honours `think: false` for thinking models."""
    cfg = MODELS[model_name]
    model_id = cfg["model_id"]
    think_flag = cfg.get("think", None)
    url = f"{client.base_url}/api/chat"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    user_msg = {"role": "user", "content": user}
    if images:
        user_msg["images"] = [_img_b64(p) for p in images]
    messages.append(user_msg)

    body: dict = {
        "model": model_id,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }
    if think_flag is not None:
        body["think"] = think_flag
    if response_format_json:
        body["format"] = "json"

    last_err: str | None = None
    for attempt in range(MAX_RETRIES):
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=client.timeout) as http:
                resp = await http.post(url, json=body)
                resp.raise_for_status()
                data = resp.json()
            latency_ms = int((time.perf_counter() - t0) * 1000)
            msg = data.get("message", {}) or {}
            text = msg.get("content") or ""
            reasoning = msg.get("thinking") or None
            return CallResult(
                text=text,
                reasoning=reasoning,
                latency_ms=latency_ms,
                prompt_tokens=data.get("prompt_eval_count", 0) or 0,
                completion_tokens=data.get("eval_count", 0) or 0,
            )
        except (httpx.HTTPError, OSError, asyncio.TimeoutError) as e:
            last_err = f"{type(e).__name__}: {e}"
            base = 2 ** attempt
            await asyncio.sleep(base + random.uniform(0, base))
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            break
    return CallResult(
        text="", latency_ms=0, prompt_tokens=0, completion_tokens=0, error=last_err
    )
