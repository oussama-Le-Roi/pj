#!/usr/bin/env python3
"""
🤖 Telegram AI Bot — Powered by Google Gemini (Free Tier)
Runs automatically via GitHub Actions every 5 minutes.
"""

import os
import sys
import requests
import google.generativeai as genai

# ──────────────────────────────────────────────
#  Configuration (loaded from GitHub Secrets)
# ──────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

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
    except requests.RequestException as exc:
        print(f"[Telegram API Error] {method}: {exc}", file=sys.stderr)
        return {"ok": False}


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

def ask_gemini(question: str) -> str:
    """Send a question to Google Gemini and return the answer."""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )
    response = model.generate_content(question)
    return response.text


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
        answer = ask_gemini(text)
        send_message(chat_id, answer)
        print(f"  ✅ Replied to {first_name} (chat {chat_id})")
    except Exception as exc:
        error_msg = "⚠️ عذراً، حدث خطأ أثناء معالجة سؤالك.\nحاول مرة أخرى لاحقاً."
        send_message(chat_id, error_msg)
        print(f"  ❌ Error for {first_name}: {exc}", file=sys.stderr)


# ──────────────────────────────────────────────
#  Main Entry Point
# ──────────────────────────────────────────────

def main():
    """Fetch new Telegram updates, reply with AI, then exit."""

    # Validate configuration
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN is not set!", file=sys.stderr)
        sys.exit(1)
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY is not set!", file=sys.stderr)
        sys.exit(1)

    print("🤖 Bot started — checking for new messages...")

    # 1) Fetch updates
    result = get_updates()
    if not result.get("ok"):
        print(f"❌ Failed to fetch updates: {result}", file=sys.stderr)
        sys.exit(1)

    updates = result.get("result", [])
    if not updates:
        print("📭 No new messages.")
        return

    print(f"📩 Processing {len(updates)} update(s)...")

    # 2) Handle each message
    for update in updates:
        if "message" in update:
            handle_message(update["message"])

    # 3) Acknowledge processed updates so they are not returned again
    last_id = updates[-1]["update_id"]
    get_updates(offset=last_id + 1)

    print("✅ Done — all messages processed!")


if __name__ == "__main__":
    main()
