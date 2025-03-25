from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import logging

# تنظیمات ربات (جایگزینی شده)
BOT_TOKEN = "7476042325:AAGSDvxelE4p2zEqtC0OeuDDz4pA6MqD61w"  # 🚨 توکن جدید
CHANNEL_USERNAME = "@Ray_Action"  # یوزرنیم کانال

# فعالسازی سیستم لاگگیری
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# تابع بررسی عضویت کاربر در کانال
async def is_user_member(user_id: int, context: CallbackContext) -> bool:
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"خطای بررسی عضویت: {e}")
        return False

# دستور /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    welcome_message = (
        f"سلام {user.mention_html()}! به ربات خوش آمدید. 🌟\n\n"
        "🔐 **برای استفاده، ابتدا در کانال زیر عضو شوید:**\n"
        f"▫️ {CHANNEL_USERNAME}\n\n"
        "پس از عضویت، دکمه «بررسی» را فشار دهید."
    )
    
    # دکمههای اینلاین
    buttons = [
        [InlineKeyboardButton("🎯 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("✅ بررسی عضویت", callback_data="verify_membership")]
    ]
    
    await update.message.reply_html(
        text=welcome_message,
        reply_markup=InlineKeyboardMarkup(buttons)
    
# پاسخ به دکمه بررسی عضویت
async def check_membership(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    if await is_user_member(query.from_user.id, context):
        await query.edit_message_text("✅ عضویت شما تایید شد! از امکانات ربات استفاده کنید.")
    else:
        await query.edit_message_text("❌ هنوز عضو کانال نشدید! لطفاً ابتدا عضو شوید.")

# مسدودسازی دستورات غیرمجاز
async def block_commands(update: Update, context: CallbackContext) -> None:
    if not await is_user_member(update.effective_user.id, context):
        await update.message.reply_text(
            "⛔ دسترسی غیرفعال! لطفاً ابتدا در کانال عضو شوید:\n" + CHANNEL_USERNAME
        )

def main() -> None:
    # راه‌اندازی ربات
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    # ثبت دستورات
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(check_membership, pattern="verify_membership"))
    
    # مسدودسازی سایر دستورات (مثال: help, info)
    dispatcher.add_handler(CommandHandler("help", block_commands))
    dispatcher.add_handler(CommandHandler("info", block_commands))
    
    # شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import logging

# تنظیمات ربات (جایگزینی شده)
BOT_TOKEN = "7476042325:AAGSDvxelE4p2zEqtC0OeuDDz4pA6MqD61w"  # 🚨 توکن جدید
CHANNEL_USERNAME = "@Ray_Action"  # یوزرنیم کانال

# فعالسازی سیستم لاگگیری
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# تابع بررسی عضویت کاربر در کانال
async def is_user_member(user_id: int, context: CallbackContext) -> bool:
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"خطای بررسی عضویت: {e}")
        return False

# دستور /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    welcome_message = (
        f"سلام {user.mention_html()}! به ربات خوش آمدید. 🌟\n\n"
        "🔐 **برای استفاده، ابتدا در کانال زیر عضو شوید:**\n"
        f"▫️ {CHANNEL_USERNAME}\n\n"
        "پس از عضویت، دکمه «بررسی» را فشار دهید."
    )
    
    # دکمههای اینلاین
    buttons = [
        [InlineKeyboardButton("🎯 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("✅ بررسی عضویت", callback_data="verify_membership")]
    ]
    
    await update.message.reply_html(
        text=welcome_message,
        reply_markup=InlineKeyboardMarkup(buttons)
    
# پاسخ به دکمه بررسی عضویت
async def check_membership(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    if await is_user_member(query.from_user.id, context):
        await query.edit_message_text("✅ عضویت شما تایید شد! از امکانات ربات استفاده کنید.")
    else:
        await query.edit_message_text("❌ هنوز عضو کانال نشدید! لطفاً ابتدا عضو شوید.")

# مسدودسازی دستورات غیرمجاز
async def block_commands(update: Update, context: CallbackContext) -> None:
    if not await is_user_member(update.effective_user.id, context):
        await update.message.reply_text(
            "⛔ دسترسی غیرفعال! لطفاً ابتدا در کانال عضو شوید:\n" + CHANNEL_USERNAME
        )

def main() -> None:
    # راه‌اندازی ربات
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    # ثبت دستورات
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(check_membership, pattern="verify_membership"))
    
    # مسدودسازی سایر دستورات (مثال: help, info)
    dispatcher.add_handler(CommandHandler("help", block_commands))
    dispatcher.add_handler(CommandHandler("info", block_commands))
    
    # شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
