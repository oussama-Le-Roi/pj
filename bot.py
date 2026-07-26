#!/usr/bin/env python3
"""
🤖 Telegram AI Bot — Powered by Google Gemini (Free Tier)
Runs automatically via GitHub Actions every 5 minutes.
"""

import os
import sys
import json
import time
import requests

from providers import (
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    PROVIDERS,
    model_id,
    model_label,
)

# Optional: load keys from a local .env file (never committed) for local runs.
if os.path.exists(".env"):
    with open(".env", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"\''))

# ──────────────────────────────────────────────
#  Configuration (loaded from GitHub Secrets)
# ──────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip().strip('"\'')
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip().strip('"\'')

# Users sometimes paste the token with the "bot" prefix already attached.
if TELEGRAM_TOKEN.startswith("bot"):
    TELEGRAM_TOKEN = TELEGRAM_TOKEN[3:]
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Gemini REST endpoint (the old google-generativeai SDK is end-of-life).
GEMINI_API = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_MODELS = ("gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest")

# Optional free fallback providers (used only if their key is present).
# OpenRouter  -> https://openrouter.ai/keys        (free :free models)
# Groq        -> https://console.groq.com/keys     (generous free tier)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

OPENROUTER_MODELS = (
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-chat-v3.1:free",
    "google/gemma-2-9b-it:free",
)
GROQ_MODELS = ("llama-3.3-70b-versatile", "llama-3.1-8b-instant")

# Long-polling: how long a single run keeps listening (seconds).
# 0 = process the current backlog once and exit (old behaviour).
RUN_DURATION = int(os.environ.get("RUN_DURATION", "0"))
POLL_TIMEOUT = 25  # seconds Telegram holds the connection open per poll

# Per-chat provider/model choice, persisted between runs.
SETTINGS_FILE = os.environ.get("SETTINGS_FILE", "settings.json")

# Telegram message length limit
MAX_MSG_LENGTH = 4000

# AI System Prompt
SYSTEM_PROMPT = (
    "أنت مساعد ذكي ودود على تلقرام اسمك 'بوت الذكاء'. "
    "أجب بوضوح واختصار مع استخدام الإيموجي لجعل الردود ممتعة. "
    "إذا سُئلت بالعربية أجب بالعربية، وإذا سُئلت بالإنجليزية أجب بالإنجليزية. "
    "كن مفيداً ودقيقاً ومحترفاً في إجاباتك. "
    "لا ترد على أي رسالة بأكثر من 3000 حرف."
)


# ──────────────────────────────────────────────
#  Telegram API Helpers
# ──────────────────────────────────────────────

def tg_request(method, **kwargs):
    """Send a request to the Telegram Bot API."""
    try:
        resp = requests.post(
            f"{TELEGRAM_API}/{method}",
            json=kwargs,
            # Must outlive Telegram's long-poll window.
            timeout=kwargs.get("timeout", 30) + 20,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as exc:
        body = {}
        try:
            body = exc.response.json()
        except Exception:
            pass
        desc = body.get("description", str(exc))
        print(f"[Telegram API Error] {method}: {desc}", file=sys.stderr)
        return {"ok": False, "error_code": body.get("error_code"), "description": desc}
    except requests.RequestException as exc:
        print(f"[Telegram API Error] {method}: {exc}", file=sys.stderr)
        return {"ok": False, "description": str(exc)}


def load_settings() -> dict:
    """Load per-chat provider/model preferences."""
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_settings(settings: dict) -> None:
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
            json.dump(settings, fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"[settings] could not save: {exc}", file=sys.stderr)


SETTINGS = {}


def get_choice(chat_id) -> tuple:
    """Return (provider, model_key) for a chat, falling back to defaults."""
    entry = SETTINGS.get(str(chat_id), {})
    provider = entry.get("provider", DEFAULT_PROVIDER)
    if provider not in PROVIDERS or not os.environ.get(PROVIDERS[provider]["env"], "").strip():
        provider = next(
            (p for p in PROVIDERS if os.environ.get(PROVIDERS[p]["env"], "").strip()),
            DEFAULT_PROVIDER,
        )
    model_key = entry.get("model", DEFAULT_MODEL)
    if model_key not in PROVIDERS[provider]["models"]:
        model_key = next(iter(PROVIDERS[provider]["models"]))
    return provider, model_key


def set_choice(chat_id, provider=None, model_key=None) -> None:
    entry = SETTINGS.setdefault(str(chat_id), {})
    if provider:
        entry["provider"] = provider
        entry.pop("model", None)
    if model_key:
        entry["model"] = model_key
    save_settings(SETTINGS)


def get_updates(offset=None, timeout=5):
    """Fetch new messages from Telegram (long-polling when timeout > 0)."""
    params = {"timeout": timeout, "allowed_updates": ["message", "callback_query"]}
    if offset is not None:
        params["offset"] = offset
    return tg_request("getUpdates", **params)


def send_message(chat_id, text, keyboard=None):
    """Send a text message, splitting if it exceeds Telegram's limit."""
    if not text or not text.strip():
        text = "⚠️ لم أتمكن من إنشاء رد. حاول مرة أخرى."
    chunks = [text[i : i + MAX_MSG_LENGTH] for i in range(0, len(text), MAX_MSG_LENGTH)]
    for index, chunk in enumerate(chunks):
        payload = {"chat_id": chat_id, "text": chunk}
        # Attach the keyboard only to the last chunk.
        if keyboard and index == len(chunks) - 1:
            payload["reply_markup"] = {"inline_keyboard": keyboard}
        tg_request("sendMessage", **payload)


def edit_message(chat_id, message_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if keyboard:
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    tg_request("editMessageText", **payload)


def answer_callback(callback_id, text=""):
    tg_request("answerCallbackQuery", callback_query_id=callback_id, text=text)


# ──────────────────────────────────────────────
#  Inline keyboards
# ──────────────────────────────────────────────

def provider_keyboard(current_provider):
    """Buttons listing every provider that has an API key configured."""
    rows = []
    for pid, info in PROVIDERS.items():
        if not os.environ.get(info["env"], "").strip():
            continue
        mark = "✅ " if pid == current_provider else ""
        rows.append([{"text": f"{mark}{info['label']}", "callback_data": f"p:{pid}"}])
    return rows


def model_keyboard(provider, current_model):
    """Buttons listing the free models of one provider."""
    rows = []
    for key, (label, _) in PROVIDERS[provider]["models"].items():
        mark = "✅ " if key == current_model else ""
        rows.append([{"text": f"{mark}{label}", "callback_data": f"m:{provider}:{key}"}])
    rows.append([{"text": "⬅️ رجوع للمزودين", "callback_data": "back"}])
    return rows


def send_typing(chat_id):
    """Show 'typing…' indicator in chat."""
    tg_request("sendChatAction", chat_id=chat_id, action="typing")


# ──────────────────────────────────────────────
#  Gemini AI
# ──────────────────────────────────────────────

def _chat_completions(url: str, api_key: str, models, question: str) -> str:
    """Call any OpenAI-compatible /chat/completions endpoint."""
    last_error = None
    for model in models:
        try:
            resp = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    # Recommended by OpenRouter, ignored by other providers.
                    "HTTP-Referer": "https://github.com/oussama-Le-Roi/pj",
                    "X-Title": "Telegram AI Bot",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": question},
                    ],
                },
                timeout=60,
            )
        except requests.RequestException as exc:
            last_error = exc
            continue

        if resp.status_code >= 400:
            last_error = RuntimeError(f"{model}: HTTP {resp.status_code} {resp.text[:200]}")
            continue

        choices = resp.json().get("choices") or []
        text = (choices[0].get("message", {}).get("content") or "").strip() if choices else ""
        if text:
            return text
        last_error = RuntimeError(f"{model}: empty response")

    raise RuntimeError(str(last_error))


def ask_gemini(question: str, models=None) -> str:
    """Send a question to Google Gemini (REST API) and return the answer."""
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": question}]}],
    }
    last_error = None

    for model in models or GEMINI_MODELS:
        try:
            resp = requests.post(
                f"{GEMINI_API}/{model}:generateContent",
                headers={"x-goog-api-key": GEMINI_API_KEY},
                json=payload,
                timeout=60,
            )
        except requests.RequestException as exc:
            last_error = exc
            continue

        if resp.status_code == 404:
            last_error = RuntimeError(f"{model}: not available")
            continue
        if resp.status_code == 429:
            raise RuntimeError(
                "Gemini free-tier quota exhausted (HTTP 429). Use /model to switch "
                "to Groq or OpenRouter."
            )
        if resp.status_code in (400, 401, 403):
            raise RuntimeError(
                f"Gemini rejected the API key (HTTP {resp.status_code}). "
                "Create a new one at https://aistudio.google.com/apikey."
            )
        if resp.status_code >= 400:
            last_error = RuntimeError(f"{model}: HTTP {resp.status_code} {resp.text[:200]}")
            continue

        data = resp.json()
        candidates = data.get("candidates") or []
        if not candidates:
            reason = (data.get("promptFeedback") or {}).get("blockReason", "empty response")
            last_error = RuntimeError(f"{model}: {reason}")
            continue

        parts = (candidates[0].get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts).strip()
        if text:
            return text
        last_error = RuntimeError(f"{model}: empty text")

    raise RuntimeError(str(last_error))


def ask_provider(provider: str, question: str, models=None) -> str:
    """Ask one specific provider, optionally forcing a model list."""
    info = PROVIDERS[provider]
    api_key = os.environ.get(info["env"], "").strip()
    if not api_key:
        raise RuntimeError(f"{info['label']}: no API key configured")

    if provider == "gemini":
        return ask_gemini(question, models)

    if models is None:
        models = [m[1] for m in info["models"].values()]
    return _chat_completions(info["url"], api_key, models, question)


def ask_ai(question: str, chat_id=None) -> str:
    """Answer using the chat's chosen model, then fall back to other providers."""
    if chat_id is not None:
        provider, model_key = get_choice(chat_id)
    else:
        provider, model_key = DEFAULT_PROVIDER, DEFAULT_MODEL

    attempts = [(provider, [model_id(provider, model_key)])]
    # Fallbacks: the rest of the chosen provider's models, then other providers.
    attempts.append((provider, None))
    for pid in PROVIDERS:
        if pid != provider and os.environ.get(PROVIDERS[pid]["env"], "").strip():
            attempts.append((pid, None))

    errors = []
    for pid, models in attempts:
        try:
            answer = ask_provider(pid, question, models)
            print(f"  🧠 answered by {PROVIDERS[pid]['label']}")
            return answer
        except Exception as exc:
            errors.append(f"{pid} -> {exc}")
            print(f"  ⚠️ {pid} failed: {exc}", file=sys.stderr)

    raise RuntimeError(" | ".join(errors[-3:]))


# ──────────────────────────────────────────────
#  Message Handler
# ──────────────────────────────────────────────

def handle_message(message: dict):
    """Process a single incoming Telegram message."""
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    user = message.get("from", {})
    first_name = user.get("first_name", "صديقي")

    if not text:
        return

    # ── /start command ──
    if text.strip() == "/start":
        welcome = (
            f"مرحباً {first_name}! 👋\n\n"
            "🤖 أنا *بوت الذكاء* — مساعدك الشخصي بالذكاء الاصطناعي!\n\n"
            "💬 اسألني أي سؤال وسأجيبك فوراً.\n\n"
            "📚 أقدر أساعدك في:\n"
            "  • الإجابة على أي سؤال عام\n"
            "  • الشرح والتعليم والتلخيص\n"
            "  • الترجمة بين اللغات\n"
            "  • البرمجة وحل المشاكل التقنية\n"
            "  • كتابة النصوص والمقالات\n"
            "  • وأشياء كثيرة!\n\n"
            "🧠 استخدم /model لاختيار المزوّد والموديل المجاني.\n\n"
            "⌨️ اكتب سؤالك الآن وجرّب..."
        )
        send_message(chat_id, welcome)
        return

    # ── /help command ──
    if text.strip() == "/help":
        help_text = (
            "📖 *كيفية الاستخدام:*\n\n"
            "ببساطة اكتب أي سؤال وسأجيبك بالذكاء الاصطناعي!\n\n"
            "🔹 الأوامر المتاحة:\n"
            "  /start — بدء المحادثة\n"
            "  /help  — عرض هذه المساعدة\n"
            "  /model — اختيار المزوّد والموديل 🧠\n\n"
            "⏱️ ملاحظة: قد يكون هناك تأخير بسيط في الرد (حتى 5 دقائق)\n"
            "لأن البوت يعمل عبر GitHub Actions.\n\n"
            "🌐 مدعوم بـ Google Gemini AI"
        )
        send_message(chat_id, help_text)
        return

    # ── /model command: choose provider & model ──
    if text.strip() in ("/model", "/models", "/ai"):
        provider, model_key = get_choice(chat_id)
        rows = provider_keyboard(provider)
        if not rows:
            send_message(chat_id, "⚠️ لا يوجد أي مزود مفعّل. أضف GROQ_API_KEY أو OPENROUTER_API_KEY.")
            return
        send_message(
            chat_id,
            "🧠 *اختر مزوّد الذكاء الاصطناعي:*\n\n"
            f"الحالي: {PROVIDERS[provider]['label']} — {model_label(provider, model_key)}",
            keyboard=rows,
        )
        return

    # ── Unknown command ──
    if text.startswith("/"):
        send_message(chat_id, "❓ أمر غير معروف. اكتب /help للمساعدة.")
        return

    # ── AI Response ──
    send_typing(chat_id)
    try:
        answer = ask_ai(text, chat_id)
        send_message(chat_id, answer)
        print(f"  ✅ Replied to {first_name} (chat {chat_id})")
    except Exception as exc:
        error_msg = (
            "⚠️ عذراً، حدث خطأ أثناء معالجة سؤالك.\n"
            f"التفاصيل: {str(exc)[:300]}"
        )
        send_message(chat_id, error_msg)
        print(f"  ❌ Error for {first_name}: {exc}", file=sys.stderr)


def handle_callback(callback: dict):
    """Handle inline-keyboard button presses."""
    data = callback.get("data", "")
    message = callback.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    callback_id = callback.get("id")

    if chat_id is None:
        return

    if data == "back":
        provider, model_key = get_choice(chat_id)
        edit_message(
            chat_id,
            message_id,
            "🧠 اختر مزوّد الذكاء الاصطناعي:",
            keyboard=provider_keyboard(provider),
        )
        answer_callback(callback_id)
        return

    if data.startswith("p:"):
        provider = data[2:]
        if provider not in PROVIDERS:
            answer_callback(callback_id, "مزود غير معروف")
            return
        set_choice(chat_id, provider=provider)
        _, model_key = get_choice(chat_id)
        edit_message(
            chat_id,
            message_id,
            f"{PROVIDERS[provider]['label']}\n\n📦 اختر الموديل المجاني:",
            keyboard=model_keyboard(provider, model_key),
        )
        answer_callback(callback_id, f"تم اختيار {PROVIDERS[provider]['label']}")
        return

    if data.startswith("m:"):
        _, provider, model_key = data.split(":", 2)
        if provider not in PROVIDERS or model_key not in PROVIDERS[provider]["models"]:
            answer_callback(callback_id, "موديل غير معروف")
            return
        set_choice(chat_id, provider=provider, model_key=model_key)
        label = model_label(provider, model_key)
        edit_message(
            chat_id,
            message_id,
            f"✅ تم التفعيل!\n\n"
            f"المزوّد: {PROVIDERS[provider]['label']}\n"
            f"الموديل: {label}\n\n"
            "اكتب سؤالك الآن 💬",
            keyboard=model_keyboard(provider, model_key),
        )
        answer_callback(callback_id, f"✅ {label}")
        return

    answer_callback(callback_id)


# ──────────────────────────────────────────────
#  Main Entry Point
# ──────────────────────────────────────────────

def check_token():
    """Verify the Telegram token before doing anything else."""
    result = tg_request("getMe")
    if not result.get("ok"):
        print(
            "❌ Invalid TELEGRAM_BOT_TOKEN — Telegram rejected it "
            f"({result.get('description')}).\n"
            "   • Token format must be like 123456789:AAE... (no 'bot' prefix, no quotes/spaces)\n"
            "   • Get a fresh one from @BotFather → /mybots → API Token\n"
            "   • Update it in GitHub → Settings → Secrets and variables → Actions → TELEGRAM_BOT_TOKEN",
            file=sys.stderr,
        )
        sys.exit(1)
    bot = result.get("result", {})
    print(f"🔑 Authenticated as @{bot.get('username')} (id {bot.get('id')})")


def main():
    """Fetch new Telegram updates, reply with AI, then exit."""

    # Validate configuration
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN is not set!", file=sys.stderr)
        sys.exit(1)
    configured = [
        name
        for name, key in (
            ("Gemini", GEMINI_API_KEY),
            ("OpenRouter", OPENROUTER_API_KEY),
            ("Groq", GROQ_API_KEY),
        )
        if key
    ]
    print(f"🧩 AI providers configured: {', '.join(configured) or 'none'}")

    if not configured:
        print(
            "❌ No AI key set! Add at least one of: GEMINI_API_KEY, "
            "OPENROUTER_API_KEY, GROQ_API_KEY",
            file=sys.stderr,
        )
        sys.exit(1)

    mode = f"live for {RUN_DURATION}s" if RUN_DURATION > 0 else "single pass"
    print(f"🤖 Bot started — {mode}...", flush=True)

    check_token()

    global SETTINGS
    SETTINGS = load_settings()

    offset = None
    deadline = time.time() + RUN_DURATION
    total = 0

    while True:
        # Long-poll while in live mode, quick check otherwise.
        remaining = deadline - time.time()
        if RUN_DURATION > 0:
            wait = max(1, min(POLL_TIMEOUT, int(remaining)))
        else:
            wait = 0

        result = get_updates(offset=offset, timeout=wait)
        if not result.get("ok"):
            print(f"❌ Failed to fetch updates: {result.get('description')}", file=sys.stderr)
            if result.get("error_code") in (401, 404):
                sys.exit(1)
            time.sleep(3)
            if RUN_DURATION == 0 or time.time() >= deadline:
                sys.exit(1)
            continue

        updates = result.get("result", [])
        if updates:
            print(f"📩 Processing {len(updates)} update(s)...", flush=True)
            # Acknowledge first so a crash cannot replay the same update forever.
            offset = updates[-1]["update_id"] + 1
            for update in updates:
                if "message" in update:
                    handle_message(update["message"])
                    total += 1
                elif "callback_query" in update:
                    handle_callback(update["callback_query"])

        if RUN_DURATION == 0:
            if not updates:
                print("📭 No new messages.")
            break
        if time.time() >= deadline:
            break

    # Flush the offset so the next run does not reprocess these updates.
    if offset is not None:
        get_updates(offset=offset, timeout=0)

    print(f"✅ Done — {total} message(s) processed!")


if __name__ == "__main__":
    main()
