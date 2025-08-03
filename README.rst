from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = '8003563260:AAE88rEMGyVPQg2BBY-g1g1miafzQ1iplCc'  # Replace with your token
UPLOAD_DIR = 'uploads'

# Make sure the uploads directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me any file and I will save it!")

# Handle document/file uploads
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.video or update.message.audio or update.message.photo[-1]
    file_id = file.file_id
    new_file = await context.bot.get_file(file_id)

    file_name = file.file_name if hasattr(file, 'file_name') else f"{file_id}.jpg"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    await new_file.download_to_drive(file_path)
    await update.message.reply_text(f"✅ File saved as: {file_name}")

# Run the bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL | filters.Audio.ALL | filters.Video.ALL | filters.PHOTO, handle_file))

app.run_polling()

