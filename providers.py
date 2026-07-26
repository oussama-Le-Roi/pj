#!/usr/bin/env python3
"""
Free AI providers and their selectable models.

Each entry: key = short id used in callback data, value = (label, model id).
Keep ids short — Telegram callback_data is limited to 64 bytes.
"""

PROVIDERS = {
    "groq": {
        "label": "⚡ Groq",
        "env": "GROQ_API_KEY",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "signup": "https://console.groq.com/keys",
        "models": {
            "l70": ("Llama 3.3 70B (ذكي)", "llama-3.3-70b-versatile"),
            "l8": ("Llama 3.1 8B (سريع)", "llama-3.1-8b-instant"),
            "gpt": ("GPT-OSS 20B", "openai/gpt-oss-20b"),
        },
    },
    "openrouter": {
        "label": "🌐 OpenRouter",
        "env": "OPENROUTER_API_KEY",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "signup": "https://openrouter.ai/keys",
        "models": {
            "l70": ("Llama 3.3 70B", "meta-llama/llama-3.3-70b-instruct:free"),
            "ds": ("DeepSeek V3", "deepseek/deepseek-chat-v3.1:free"),
            "qw": ("Qwen 3 Coder", "qwen/qwen3-coder:free"),
            "gem": ("Gemma 2 9B", "google/gemma-2-9b-it:free"),
        },
    },
    "gemini": {
        "label": "✨ Gemini",
        "env": "GEMINI_API_KEY",
        "url": "",  # handled separately (not OpenAI-compatible)
        "signup": "https://aistudio.google.com/apikey",
        "models": {
            "f20": ("Gemini 2.0 Flash", "gemini-2.0-flash"),
            "f25": ("Gemini 2.5 Flash", "gemini-2.5-flash"),
        },
    },
}

DEFAULT_PROVIDER = "groq"
DEFAULT_MODEL = "l70"


def model_id(provider: str, model_key: str) -> str:
    """Resolve a (provider, short key) pair to the real model identifier."""
    models = PROVIDERS[provider]["models"]
    if model_key not in models:
        model_key = next(iter(models))
    return models[model_key][1]


def model_label(provider: str, model_key: str) -> str:
    models = PROVIDERS[provider]["models"]
    if model_key not in models:
        model_key = next(iter(models))
    return models[model_key][0]
