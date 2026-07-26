# 🤖 بوت الذكاء — Telegram AI Bot

بوت تلقرام ذكي يعمل بالذكاء الاصطناعي (Google Gemini) مجاناً بالكامل!

يتم استضافته على **GitHub Actions** بدون أي تكلفة.

---

## ✨ المميزات

- 🧠 يجيب على أي سؤال باستخدام Google Gemini AI
- 🌍 يدعم العربية والإنجليزية وأي لغة
- 🆓 مجاني بالكامل (GitHub Actions + Gemini Free Tier)
- 🔒 آمن — التوكنات محفوظة في GitHub Secrets
- ⚡ يعمل تلقائياً كل 5 دقائق

---

## 🚀 طريقة التشغيل

### الخطوة 1: إنشاء بوت تلقرام

1. افتح **@BotFather** على تلقرام
2. أرسل `/newbot`
3. اختر اسماً للبوت
4. احفظ **التوكن** الذي يعطيك إياه

### الخطوة 2: الحصول على مفتاح Gemini API

1. اذهب إلى [Google AI Studio](https://aistudio.google.com/apikey)
2. سجّل الدخول بحساب Google
3. اضغط **Create API Key**
4. احفظ المفتاح

### الخطوة 3: رفع الكود على GitHub

```bash
cd telegram-ai-bot
git init
git add .
git commit -m "🤖 Initial commit - Telegram AI Bot"
git remote add origin https://github.com/USERNAME/telegram-ai-bot.git
git push -u origin main
```

### الخطوة 4: إضافة الأسرار (Secrets)

1. اذهب إلى صفحة المستودع على GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. اضغط **New repository secret** وأضف:

| الاسم | القيمة |
|-------|--------|
| `TELEGRAM_BOT_TOKEN` | توكن البوت من BotFather |
| `GEMINI_API_KEY` | مفتاح API من Google AI Studio |

### الخطوة 5: تشغيل البوت

1. اذهب إلى تبويب **Actions** في المستودع
2. اختر **🤖 Telegram AI Bot**
3. اضغط **Run workflow** لتشغيله أول مرة
4. بعد ذلك سيعمل تلقائياً كل 5 دقائق!

---

## 📁 هيكل المشروع

```
telegram-ai-bot/
├── bot.py                      # كود البوت الرئيسي
├── requirements.txt            # المكتبات المطلوبة
├── .github/workflows/bot.yml   # GitHub Actions workflow
├── .gitignore                  # تجاهل الملفات الحساسة
└── README.md                   # هذا الملف
```

---

## ⚠️ ملاحظات مهمة

- **لا تشارك التوكن أبداً** في الكود أو في أي مكان عام
- **التأخير**: البوت يتحقق من الرسائل كل 5 دقائق
- **الحدود المجانية**:
  - Gemini: 1500 طلب/يوم
  - GitHub Actions: 2000 دقيقة/شهر

---

## 🛠️ تخصيص البوت

يمكنك تعديل `SYSTEM_PROMPT` في ملف `bot.py` لتغيير شخصية البوت:

```python
SYSTEM_PROMPT = "أنت مساعد متخصص في البرمجة..."
```

---

**صنع بـ ❤️ باستخدام Python + Google Gemini + GitHub Actions**


## 🧠 Choosing the AI provider & model

Send **/model** in the chat and the bot shows inline buttons:

1. First screen — providers that have an API key set (⚡ Groq, 🌐 OpenRouter, ✨ Gemini).
2. Second screen — the free models of that provider.

The choice is saved per chat in `settings.json` and used for every later question.
If the chosen model fails (quota, outage), the bot silently falls back to the
provider's other models, then to the remaining providers.

> ⚠️ On GitHub Actions the runner filesystem is wiped after each run, so the
> selection resets to the default (Groq / Llama 3.3 70B) unless you host the bot
> somewhere persistent or commit `settings.json`.

### Available free models

| Provider | Models |
| --- | --- |
| ⚡ Groq | Llama 3.3 70B, Llama 3.1 8B, GPT-OSS 20B |
| 🌐 OpenRouter | Llama 3.3 70B, DeepSeek V3, Qwen 3 Coder, Gemma 2 9B |
| ✨ Gemini | 2.0 Flash, 2.5 Flash |

## ⚡ Response speed / always-on hosting

`bot.py` supports two modes via the `RUN_DURATION` environment variable:

| `RUN_DURATION` | Behaviour |
| --- | --- |
| `0` or unset | Drain pending messages once, then exit (default). |
| e.g. `290` | Stay alive and long-poll Telegram for ~290s, replying instantly. |

### GitHub Actions (free, near real-time)

See `WORKFLOW_UPDATE.md`. With `RUN_DURATION: '290'` and a `*/5` cron, a run is
almost always listening. Caveat: GitHub's scheduler is best-effort and frequently
delayed, so short gaps happen.

### True 24/7 (recommended for a real bot)

Run it as a normal always-on process with `RUN_DURATION=86400` (or wrap in a
restart loop) on any of these free/cheap hosts:

- **Railway / Render / Fly.io** — deploy the repo, set the secrets as env vars,
  start command `python bot.py`.
- **Any VPS**: `RUN_DURATION=86400 python bot.py` under `systemd` or `tmux`.

GitHub Actions is not designed for persistent processes; a tiny always-on host is
the only way to get genuinely instant replies with no gaps.
