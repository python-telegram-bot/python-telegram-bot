#!/usr/bin/env python3
# bot.py

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ===== إعدادات المستخدم: ضع هنا توكن البوت، والـ user_id للمشرفين، وقائمة المحادثات المسموح بها =====
BOT_TOKEN       = "https://gist.github.com/7ff40062d6665856c884918ab9feb6d4.git"
ADMIN_IDS       = [1650540925 , 987654321]     # Telegram user IDs للمشرفين
ALLOWED_CHAT_IDS = []                        # إن أردت تقييد البوت بمجموعات/قنوات معينة

# ===== قواميس الرسائل باللغتين =====
MESSAGES = {
    'start': {
        'en': "👋 Welcome! I'm your smart bot.\nUse /help to see available commands.",
        'ar': "👋 أهلاً! أنا بوتك الذكي.\nاستخدم /help لاطلاع على الأوامر المتاحة."
    },
    'help': {
        'en': (
            "/start - Welcome message\n"
            "/help  - This help text\n"
            "/getchatid - Get this chat's ID\n"
            "/question <text> - Ask me something\n"
            "/info - Bot info"
        ),
        'ar': (
            "/start - رسالة ترحيب\n"
            "/help  - قائمة الأوامر\n"
            "/getchatid - معرفة معرف المحادثة\n"
            "/question <نص> - اسألني سؤالاً\n"
            "/info - معلومات عن البوت"
        )
    },
    'getchatid': {
        'en': "This chat's ID is: `{}`",
        'ar': "معرّف هذه المحادثة هو: `{}`"
    },
    'unknown': {
        'en': "❓ Sorry, I didn't understand that command.",
        'ar': "❓ عذراً، لم أفهم الأمر."
    },
    'info': {
        'en': "🤖 *Bot Info*\n• Library: python-telegram-bot\n• Version: 20+\n• Author: Your Name",
        'ar': "🤖 *معلومات عن البوت*\n• المكتبة: python-telegram-bot\n• الإصدار: 20+\n• المطور: اسمك هنا"
    },
}

# ===== دالة لتحديد لغة المستخدم =====
def get_lang(update: Update) -> str:
    code = update.effective_user.language_code or ""
    return 'ar' if code.lower().startswith('ar') else 'en'

# ===== فلتر للتحقق من صلاحية الوصول =====
def is_allowed(update: Update) -> bool:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    if ADMIN_IDS and user_id in ADMIN_IDS:
        return True
    if ALLOWED_CHAT_IDS and chat_id in ALLOWED_CHAT_IDS:
        return True
    # في حال لم نحدد أي قوائم، نسمح لجميع المستخدمين
    return not (ADMIN_IDS or ALLOWED_CHAT_IDS)

# ===== Handler لأمر /start =====
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    lang = get_lang(update)
    await update.message.reply_text(MESSAGES['start'][lang])

# ===== Handler لأمر /help =====
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    lang = get_lang(update)
    await update.message.reply_text(MESSAGES['help'][lang])

# ===== Handler لأمر /getchatid =====
async def getchatid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    lang = get_lang(update)
    chat_id = update.effective_chat.id
    await update.message.reply_markdown_v2(MESSAGES['getchatid'][lang].format(chat_id))

# ===== Handler لأمر /info =====
async def info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    lang = get_lang(update)
    await update.message.reply_markdown(MESSAGES['info'][lang])

# ===== Handler لأمر /question =====
async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    lang = get_lang(update)
    text = update.message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await update.message.reply_text(
            "Usage: /question <your question>" if lang=='en' else "الاستخدام: /question <سؤالك>"
        )
        return
    question = parts[1]
    # هنا يمكنك إضافة استدعاء واجهة GPT أو منطقك الخاص
    answer = f"(تجريبي) لقد سألت: {question}"
    await update.message.reply_text(answer)

# ===== Handler للرسائل غير المعروفة =====
async def unknown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    lang = get_lang(update)
    await update.message.reply_text(MESSAGES['unknown'][lang])

# ===== نقطة الدخول الرئيسية =====
def main():
    # تفعيل سجل الأخطاء
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    app = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .build()

    # تسجيل الــ handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help",  help_handler))
    app.add_handler(CommandHandler("getchatid", getchatid_handler))
    app.add_handler(CommandHandler("info", info_handler))
    app.add_handler(CommandHandler("question", question_handler))

    # رسالة للـ unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, unknown_handler))

    # تشغيل البوت
    print("Bot is up and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
