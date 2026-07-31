"""Local model layer for the cross model-family probe.

Self-contained on purpose: the two new models are registered HERE, not in the
shared config.py / api_clients.py (which stay untouched). Each class exposes the
same duck-typed interface run_sweep expects from a model object:
  .name, .reset(), .__call__(system, user) -> str, .calls, .pt, .ct

Model families (deliberately NOT Qwen or DeepSeek, so this is a genuine
third-family probe):
  - weak   = Llama 3.1 8B (Meta), local via Ollama. A plain instruct model:
    clean `content`, standard `max_tokens` + `temperature`, so it uses the
    OpenAI-compatible /v1 endpoint directly. (Note: an earlier candidate,
    deepseek-r1:32b, was dropped because it is distilled from Qwen2.5, which
    would defeat the cross-family purpose, and it was slow.)
  - strong = gpt-5.6-luna (OpenAI), a reasoning model: it needs
    `max_completion_tokens` (NOT `max_tokens`) and only supports the default
    temperature (1). So it is usable as an ACTOR (actor temperature is 1.0) but
    never as a critic.

Keys come from the standard loader (env vars or a keys file); point
SBLFR_API_KEYS_PATH at your key file, e.g. path/to/API-keys.txt.
Local Ollama needs no key.
"""
from __future__ import annotations
import asyncio
import random
import sys
from pathlib import Path

from openai import AsyncOpenAI

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from config import load_keys, TIMEOUT_S, MAX_RETRIES   # noqa: E402  (read-only reuse)

OPENAI_BASE = "https://api.openai.com/v1"
OLLAMA_V1 = "http://localhost:11434/v1"

WEAK_MODEL_ID = "llama3.1:8b"


class _RetryMixin:
    def reset(self):
        self.calls = self.pt = self.ct = 0

    def __call__(self, system, user):
        text, pt, ct = asyncio.run(self._chat(system, user))
        self.calls += 1
        self.pt += pt
        self.ct += ct
        return text or ""


class OllamaChatModel(_RetryMixin):
    """Local Ollama instruct model (e.g. Llama 3.1 8B, Mistral) via the
    OpenAI-compatible /v1 endpoint. For non-reasoning models whose `content`
    is already clean, so standard max_tokens + temperature apply."""

    def __init__(self, model_id: str, temperature: float = 1.0,
                 max_tokens: int = 1500, base_url: str = OLLAMA_V1):
        self.name = model_id
        self._client = AsyncOpenAI(api_key="ollama", base_url=base_url, timeout=TIMEOUT_S)
        self._temp = temperature
        self._maxtok = max_tokens
        self.calls = self.pt = self.ct = 0

    async def _chat(self, system, user):
        msgs = ([{"role": "system", "content": system}] if system else [])
        msgs.append({"role": "user", "content": user})
        last = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = await self._client.chat.completions.create(
                    model=self.name, messages=msgs,
                    temperature=self._temp, max_tokens=self._maxtok)
                m = resp.choices[0].message
                u = resp.usage
                return (m.content or "",
                        u.prompt_tokens if u else 0,
                        u.completion_tokens if u else 0)
            except Exception as e:  # noqa: BLE001
                last = e
                base = 2 ** attempt
                await asyncio.sleep(base + random.uniform(0, base))
        raise RuntimeError(f"{self.name} chat failed after {MAX_RETRIES} tries: {last}")


class LunaModel(_RetryMixin):
    """OpenAI reasoning model (gpt-5.6-luna). Actor-only: temperature is left at
    the model default (1). Budget is max_completion_tokens (covers reasoning)."""
    name = "gpt-5.6-luna"

    def __init__(self, max_completion_tokens: int = 4000):
        keys = load_keys()
        key = keys.get("gpt")
        if not key:
            raise RuntimeError(
                "missing 'gpt' key. Set SBLFR_API_KEYS_PATH to your key file "
                "(a line 'GPT: sk-...') or export the key.")
        self._client = AsyncOpenAI(api_key=key, base_url=OPENAI_BASE, timeout=TIMEOUT_S)
        self._maxct = max_completion_tokens
        self.calls = self.pt = self.ct = 0

    async def _chat(self, system, user):
        msgs = ([{"role": "system", "content": system}] if system else [])
        msgs.append({"role": "user", "content": user})
        last = None
        for attempt in range(MAX_RETRIES):
            try:
                # No temperature: this model only supports the default (1), which
                # is exactly the actor temperature convention.
                resp = await self._client.chat.completions.create(
                    model=self.name, messages=msgs,
                    max_completion_tokens=self._maxct)
                m = resp.choices[0].message
                u = resp.usage
                return (m.content or "",
                        u.prompt_tokens if u else 0,
                        u.completion_tokens if u else 0)
            except Exception as e:  # noqa: BLE001
                last = e
                base = 2 ** attempt
                await asyncio.sleep(base + random.uniform(0, base))
        raise RuntimeError(f"luna chat failed after {MAX_RETRIES} tries: {last}")


def make_actor(which: str):
    """which='weak' -> Llama 3.1 8B (local Ollama); 'strong' -> gpt-5.6-luna (OpenAI)."""
    if which == "weak":
        return OllamaChatModel(WEAK_MODEL_ID, temperature=1.0)
    if which == "strong":
        return LunaModel()
    raise ValueError(f"unknown actor spec {which!r} (use 'weak' or 'strong')")
