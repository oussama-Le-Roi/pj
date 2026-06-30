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
