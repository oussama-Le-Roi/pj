#!/usr/bin/env python3
"""
🤖 Telegram AI Bot — Powered by Google Gemini (Free Tier)
Runs automatically via GitHub Actions every 5 minutes.
"""

import os
import sys
import requests

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
            timeout=30,
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


def get_updates(offset=None):
    """Fetch new messages from Telegram."""
    params = {"timeout": 5, "allowed_updates": ["message"]}
    if offset is not None:
        params["offset"] = offset
    return tg_request("getUpdates", **params)


def send_message(chat_id, text):
    """Send a text message, splitting if it exceeds Telegram's limit."""
    if not text or not text.strip():
        text = "⚠️ لم أتمكن من إنشاء رد. حاول مرة أخرى."
    chunks = [text[i : i + MAX_MSG_LENGTH] for i in range(0, len(text), MAX_MSG_LENGTH)]
    for chunk in chunks:
        tg_request("sendMessage", chat_id=chat_id, text=chunk)


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
            last_error = RuntimeError(f"{resp.status_code}: {resp.text[:200]}")
            continue

        choices = resp.json().get("choices") or []
        text = (choices[0].get("message", {}).get("content") or "").strip() if choices else ""
        if text:
            return text
        last_error = RuntimeError("empty response")

    raise RuntimeError(str(last_error))


def ask_gemini(question: str) -> str:
    """Send a question to Google Gemini (REST API) and return the answer."""
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": question}]}],
    }
    last_error = None

    for model in GEMINI_MODELS:
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

        # 404 = model unavailable, 429 = quota exhausted -> try the next model
        if resp.status_code in (404, 429):
            last_error = RuntimeError(f"{model}: HTTP {resp.status_code}")
            continue
        if resp.status_code in (400, 401, 403):
            raise RuntimeError(
                f"Gemini rejected the API key (HTTP {resp.status_code}). "
                "Create a new one at https://aistudio.google.com/apikey and update "
                "the GEMINI_API_KEY secret."
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


def ask_openrouter(question: str) -> str:
    return _chat_completions(
        "https://openrouter.ai/api/v1/chat/completions",
        OPENROUTER_API_KEY,
        OPENROUTER_MODELS,
        question,
    )


def ask_groq(question: str) -> str:
    return _chat_completions(
        "https://api.groq.com/openai/v1/chat/completions",
        GROQ_API_KEY,
        GROQ_MODELS,
        question,
    )


def ask_ai(question: str) -> str:
    """Try every configured AI provider in order until one answers."""
    providers = []
    if GEMINI_API_KEY:
        providers.append(("Gemini", ask_gemini))
    if OPENROUTER_API_KEY:
        providers.append(("OpenRouter", ask_openrouter))
    if GROQ_API_KEY:
        providers.append(("Groq", ask_groq))

    if not providers:
        raise RuntimeError("No AI provider configured (set GEMINI_API_KEY, OPENROUTER_API_KEY or GROQ_API_KEY)")

    errors = []
    for name, fn in providers:
        try:
            answer = fn(question)
            print(f"  🧠 answered by {name}")
            return answer
        except Exception as exc:
            errors.append(f"{name} -> {exc}")
            print(f"  ⚠️ {name} failed: {exc}", file=sys.stderr)

    raise RuntimeError(" | ".join(errors))


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
            "  /help  — عرض هذه المساعدة\n\n"
            "⏱️ ملاحظة: قد يكون هناك تأخير بسيط في الرد (حتى 5 دقائق)\n"
            "لأن البوت يعمل عبر GitHub Actions.\n\n"
            "🌐 مدعوم بـ Google Gemini AI"
        )
        send_message(chat_id, help_text)
        return

    # ── Unknown command ──
    if text.startswith("/"):
        send_message(chat_id, "❓ أمر غير معروف. اكتب /help للمساعدة.")
        return

    # ── AI Response ──
    send_typing(chat_id)
    try:
        answer = ask_ai(text)
        send_message(chat_id, answer)
        print(f"  ✅ Replied to {first_name} (chat {chat_id})")
    except Exception as exc:
        error_msg = (
            "⚠️ عذراً، حدث خطأ أثناء معالجة سؤالك.\n"
            f"التفاصيل: {str(exc)[:300]}"
        )
        send_message(chat_id, error_msg)
        print(f"  ❌ Error for {first_name}: {exc}", file=sys.stderr)


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

    print("🤖 Bot started — checking for new messages...", flush=True)

    check_token()

    # 1) Fetch updates
    result = get_updates()
    if not result.get("ok"):
        print(f"❌ Failed to fetch updates: {result.get('description')}", file=sys.stderr)
        sys.exit(1)

    updates = result.get("result", [])
    if not updates:
        print("📭 No new messages.")
        return

    print(f"📩 Processing {len(updates)} update(s)...")

    # 2) Acknowledge updates first so a crash cannot cause an endless retry loop
    last_id = updates[-1]["update_id"]
    get_updates(offset=last_id + 1)

    # 3) Handle each message
    for update in updates:
        if "message" in update:
            handle_message(update["message"])

    print("✅ Done — all messages processed!")


if __name__ == "__main__":
    main()
