#!/usr/bin/env python3
"""Quick check: is the Telegram token valid and does any AI provider answer?"""
import sys
import bot

print("── Telegram ──")
me = bot.tg_request("getMe")
print("✅ @" + me["result"]["username"] if me.get("ok") else "❌ " + str(me.get("description")))

print("\n── AI providers ──")
for name, key, fn in (
    ("Gemini", bot.GEMINI_API_KEY, bot.ask_gemini),
    ("OpenRouter", bot.OPENROUTER_API_KEY, bot.ask_openrouter),
    ("Groq", bot.GROQ_API_KEY, bot.ask_groq),
):
    if not key:
        print(f"⏭️  {name}: no key set")
        continue
    try:
        print(f"✅ {name}: {fn('Say OK')[:80]}")
    except Exception as exc:
        print(f"❌ {name}: {exc}", file=sys.stderr)
