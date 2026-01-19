import logging
import os
import math
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# تحذير: لا تضع التوكن مباشرة في الكود إذا كنت ستشاركه أو تنشره على GitHub، استخدم متغير بيئة بدلاً من ذلك.
TELEGRAM_TOKEN = "8570383855:AAFpGoZq-tPcyP6cHKR6WOSfWYyIivhDuQY"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE, PRODUCT, AREA, COVERAGE, PRICE = range(5)

SERVICES = ['دهان', 'طباعة', 'كاركون', 'جيسو', 'سيراميك']

# افتراضيات معدلات التغطية لكل خدمة (متر مربع لكل وحدة)
DEFAULT_COVERAGE = {
    'دهان': 10.0,    # متر مربع لكل لتر (مثال)
    'طباعة': 1.0,    # متر مربع لكل وحدة طباعة (تغيير حسب الاستخدام)
    'كاركون': 5.0,
    'جيسو': 6.0,
    'سيراميك': 1.5
}

# قائمة منتجات مع أسعار افتراضية (يورو لكل وحدة) - يمكن تعديلها حسب السوق الإيطالي
PRODUCTS = {
    'دهان': {
        'دهان أبيض': 15.0,
        'دهان ملون': 20.0,
        'دهان مقاوم للماء': 25.0
    },
    'طباعة': {
        'ورق طباعة عادي': 5.0,
        'ورق فوتو': 10.0,
        'لوحات إعلانية': 50.0
    },
    'كاركون': {
        'كاركون عادي': 8.0,
        'كاركون مقاوم': 12.0
    },
    'جيسو': {
        'جيسو أبيض': 6.0,
        'جيسو ملون': 9.0
    },
    'سيراميك': {
        'بلاط سيراميك عادي': 3.0,
        'بلاط سيراميك فاخر': 7.0
    }
}

def start(update: Update, context: CallbackContext):
    keyboard = [[s] for s in SERVICES]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        'مرحباً! أنا بوت آلة حاسبة للدهان والطباعة والمواد الأخرى في إيطاليا. اختر الخدمة للبدء:',
        reply_markup=reply_markup
    )
    return SERVICE

def service_chosen(update: Update, context: CallbackContext):
    service = update.message.text.strip()
    if service not in SERVICES:
        update.message.reply_text('الرجاء اختيار خدمة من القائمة. ارسل /cancel للإلغاء.')
        return SERVICE
    context.user_data['service'] = service
    products = PRODUCTS.get(service, {})
    if products:
        keyboard = [[p] for p in products.keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text(f'اختر منتج من {service}:', reply_markup=reply_markup)
        return PRODUCT
    else:
        update.message.reply_text('أدخل المساحة بالمتر المربع (مثال: 25.5):', reply_markup=ReplyKeyboardRemove())
        return AREA

def product_chosen(update: Update, context: CallbackContext):
    product = update.message.text.strip()
    service = context.user_data['service']
    products = PRODUCTS.get(service, {})
    if product not in products:
        update.message.reply_text('الرجاء اختيار منتج من القائمة. ارسل /cancel للإلغاء.')
        return PRODUCT
    context.user_data['product'] = product
    context.user_data['price'] = products[product]  # تعيين السعر الافتراضي
    update.message.reply_text('أدخل المساحة بالمتر المربع (مثال: 25.5):', reply_markup=ReplyKeyboardRemove())
    return AREA

def area_received(update: Update, context: CallbackContext):
    text = update.message.text.replace(',', '.')
    try:
        area = float(text)
        if area <= 0:
            raise ValueError()
    except ValueError:
        update.message.reply_text('قيمة المساحة غير صالحة. أدخل رقمًا موجبًا (مثال: 12.5).')
        return AREA
    context.user_data['area'] = area
    service = context.user_data['service']
    default_cov = DEFAULT_COVERAGE.get(service, 1.0)
    update.message.reply_text(
        f'معدل التغطية الافتراضي لـ {service} هو {default_cov} متر مربع لكل وحدة. ' 
        'إذا أردت استخدامه ارسل رقمًا فارغًا أو اكتب معدل التغطية الذي تفضله (مثال: 10):'
    )
    return COVERAGE

def coverage_received(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    service = context.user_data['service']
    if text == '' or text.lower() in ['default', 'd']:
        coverage = DEFAULT_COVERAGE.get(service, 1.0)
    else:
        try:
            coverage = float(text.replace(',', '.'))
            if coverage <= 0:
                raise ValueError()
        except ValueError:
            update.message.reply_text('قيمة معدل التغطية غير صالحة. أدخل رقمًا موجبًا (مثال: 10).')
            return COVERAGE
    context.user_data['coverage'] = coverage
    default_price = context.user_data.get('price')
    if default_price is not None:
        update.message.reply_text(f'السعر الافتراضي للمنتج: {default_price:.2f} €. إذا أردت استخدامه ارسل رقمًا فارغًا، أو اكتب سعرًا آخر (مثال: 15.5):')
    else:
        update.message.reply_text('أدخل سعر الوحدة باليورو (مثال: 12.5):')
    return PRICE

def price_received(update: Update, context: CallbackContext):
    text = update.message.text.replace(',', '.')
    default_price = context.user_data.get('price')
    if text == '' and default_price is not None:
        price = default_price
    else:
        try:
            price = float(text)
            if price < 0:
                raise ValueError()
        except ValueError:
            update.message.reply_text('قيمة السعر غير صالحة. أدخل رقمًا (مثال: 15.5).')
            return PRICE

    context.user_data['price'] = price

    area = context.user_data['area']
    coverage = context.user_data['coverage']
    units = math.ceil(area / coverage)
    total = units * price
    service = context.user_data['service']
    product = context.user_data.get('product', 'غير محدد')

    update.message.reply_text(
        f'الخدمة: {service}\n'
        f'المنتج: {product}\n'
        f'المساحة: {area} م²\n'
        f'معدل التغطية: {coverage} م²/وحدة\n'
        f'الوحدات المطلوبة: {units}\n'
        f'سعر الوحدة: {price:.2f} €\n'
        f'التكلفة الإجمالية: {total:.2f} €\n\n'
        'إذا أردت حسابًا آخر ارسل /start. لإلغاء ارسل /cancel.'
    )
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('تم الإلغاء. لإعادة البدء ارسل /start.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def error(update: Update, context: CallbackContext):
    logger.warning('Update caused error: %s', context.error)

def main():
    token = TELEGRAM_TOKEN
    if not token:
        print('Error: TELEGRAM_TOKEN not set')
        return

    try:
        updater = Updater(token=token, use_context=True)
        dp = updater.dispatcher

        conv = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                SERVICE: [MessageHandler(Filters.text & ~Filters.command, service_chosen)],
                PRODUCT: [MessageHandler(Filters.text & ~Filters.command, product_chosen)],
                AREA: [MessageHandler(Filters.text & ~Filters.command, area_received)],
                COVERAGE: [MessageHandler(Filters.text & ~Filters.command, coverage_received)],
                PRICE: [MessageHandler(Filters.text & ~Filters.command, price_received)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        dp.add_handler(conv)
        dp.add_error_handler(error)

        print('Bot is running. Press Ctrl-C to stop.')
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(f'Error starting bot: {e}')
        logger.error(f'Error starting bot: {e}')

if __name__ == '__main__':
    main()
