@ -1,2 +1,40 @@
# Telegram Calculator Bot (دهان، طباعة، كاركون، جيسو، سيراميك) — Italy

بوت بسيط لحساب الكميات والتكلفة باليورو للخدمات: دهان، طباعة، كاركون، جيسو، سيراميك.

الملفات الرئيسية:
- [bot.py](bot.py) — كود البوت.
- [requirements.txt](requirements.txt) — تبعيات المشروع.

الإعداد والتشغيل

1. ثبت Python 3.7+ ثم أنشئ بيئة افتراضية إن رغبت.
2. ثبّت التبعيات:

```bash
pip install -r requirements.txt
```

3. عين متغيّر البيئة `TELEGRAM_TOKEN` إلى توكن البوت الذي تحصل عليه من BotFather:

Windows (PowerShell):

```powershell
$env:TELEGRAM_TOKEN = "<YOUR_TOKEN_HERE>"
python bot.py
```

Linux / macOS:

```bash
export TELEGRAM_TOKEN="<YOUR_TOKEN_HERE>"
python bot.py
```

4. افتح دردشة البوت في تلغرام، ارسل `/start` واتبع التعليمات لاختيار الخدمة، إدخال المساحة، معدل التغطية، وسعر الوحدة.

ملاحظات
- العملة الافتراضية في الحساب هي اليورو (€). يمكنك تعديل `DEFAULT_COVERAGE` في `bot.py` حسب معدلات التغطية الحقيقية للمواد في إيطاليا.
- إذا تريدني أضيف خيارات لحساب لترات لكل طبقة، خصم للنفايات، أو قائمة منتجات مع أسعار إيطالية افتراضية — أبلغني وسأضيفها.
# Y2COLORS-bot
Telegram Bot for Tile &amp; Painting Cost - Y2COLORS ✨
