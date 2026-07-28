"""SBLFR-Chem v1 — LLM client configuration.

API keys are read from environment variables. A local ``API-keys.txt`` file
(gitignored, optional) is read as a fallback so individual contributors can
keep a private key file without leaking it. Format of that file is one
``provider: key`` line per provider, e.g.::

    deepseek: sk-...
    kimi: sk-...

For local Ollama models (qwen7b / qwen32b) no key is needed.
"""
from __future__ import annotations
import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
_LOCAL_KEYS_FILE = Path(
    os.environ.get("SBLFR_API_KEYS_PATH", str(_REPO_ROOT / "API-keys.txt"))
)

_ENV_VAR_BY_PROVIDER = {
    "deepseek": "DEEPSEEK_API_KEY",
    "kimi": "KIMI_API_KEY",
    "qwen": "DASHSCOPE_API_KEY",
}


def load_keys() -> dict[str, str]:
    keys: dict[str, str] = {}
    for provider, env_var in _ENV_VAR_BY_PROVIDER.items():
        v = os.environ.get(env_var)
        if v:
            keys[provider] = v
    if _LOCAL_KEYS_FILE.exists():
        for line in _LOCAL_KEYS_FILE.read_text().splitlines():
            line = line.strip()
            if not line or ":" not in line or line.startswith("#"):
                continue
            provider, key = line.split(":", 1)
            keys.setdefault(provider.strip().lower(), key.strip())
    return keys


MODELS = {
    "deepseek": {
        "model_id": "deepseek-v4-pro",
        "base_url": "https://api.deepseek.com/v1",
        "key_name": "deepseek",
    },
    # Same model with thinking mode disabled per DeepSeek docs. With the
    # default thinking on, V4 Pro routes its final answer into
    # message.reasoning_content and leaves message.content empty for most
    # reasoning-heavy prompts. Default is content-only (CoT fallback off) to
    # keep parsing fair across models, so under that setting thinking-on DS
    # appears to "parse fail" on 25-35% of attempts (~80% on multi-agent
    # Diagnosis prompts). Disabling thinking forces V4 Pro into final-answer
    # mode in `content`, matching the channel every other model in the
    # benchmark already uses.
    "deepseek_nothink": {
        "model_id": "deepseek-v4-pro",
        "base_url": "https://api.deepseek.com/v1",
        "key_name": "deepseek",
        "extra_body": {"thinking": {"type": "disabled"}},
    },
    "kimi": {
        "model_id": "kimi-k2.6",
        "base_url": "https://api.moonshot.cn/v1",
        "key_name": "kimi",
    },
    # Alibaba DashScope OpenAI-compat endpoint for Qwen3.7-Max.
    "qwen_max": {
        "model_id": "qwen3.7-max",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key_name": "qwen",
    },
    "qwen_plus": {                       # qwen3.7-plus: multimodal (vision) on DashScope
        "model_id": "qwen3.7-plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key_name": "qwen",
    },
    "qwen7b": {
        "model_id": "qwen2.5:7b-instruct",
        "base_url": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "key_name": "_local_ollama",
    },
    "qwen32b": {
        "model_id": "qwen2.5:32b",
        "base_url": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "key_name": "_local_ollama",
    },
    "qwen3moe": {
        "model_id": "qwen3:30b-a3b",
        "base_url": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "key_name": "_local_ollama",
    },
    # Sidecar Ollama on 127.0.0.1:11435 (0.23.1, D-drive model storage).
    # These models need the native `/api/chat` path so we can pass
    # `think: False` (Ollama's OpenAI-compat /v1 endpoint silently
    # ignores that field, leaving the model in thinking mode which
    # times out our recovery loops).
    "qwen36": {
        "model_id": "qwen3.6:27b",
        "base_url": "http://127.0.0.1:11435",
        "key_name": "_local_ollama",
        "client": "ollama_native",
        "think": False,
    },
    "qwen25vl": {                        # qwen2.5-vl:7b local multimodal (sprhq :11435, /mnt/d)
        "model_id": "qwen2.5vl:7b",
        "base_url": "http://127.0.0.1:11435",
        "key_name": "_local_ollama",
        "client": "ollama_native",
    },
    "gemma26": {
        "model_id": "gemma4:26b",
        "base_url": "http://127.0.0.1:11435",
        "key_name": "_local_ollama",
        "client": "ollama_native",
        "think": False,
    },
    "gemma4b": {
        "model_id": "gemma4:e4b",
        "base_url": "http://127.0.0.1:11435",
        "key_name": "_local_ollama",
        "client": "ollama_native",
        "think": False,
    },
}

TIMEOUT_S = 600
MAX_RETRIES = 6
