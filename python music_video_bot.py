import logging
import os
import tempfile
import shutil
from functools import partial

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)

import yt_dlp

# ---------- Настройки ----------
TELEGRAM_TOKEN = "8485637506:AAHmTDFOuWkinhLDNvlWns8jVbh7KkcU45o"
MAX_RESULTS = 5
# -------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Я музыкальный бот.\n"
        "Используй команду:\n"
        "/search <запрос> — найти треки на YouTube"
    )


def search(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Пожалуйста, укажи поисковый запрос, например:\n/search Imagine Dragons Believer")
        return

    msg = update.message.reply_text(f"Ищу «{query}»...")

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',  # чтобы быстро получить список результатов
        'default_search': f'ytsearch{MAX_RESULTS}:',
        'dump_single_json': True,
        # не выводим лишнее
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
        except Exception as e:
            logger.exception("Ошибка при поиске")
            msg.edit_text("Ошибка при поиске: " + str(e))
            return

    # info['entries'] содержит результаты
    entries = info.get('entries') or []
    if not entries:
        msg.edit_text("Ничего не найдено.")
        return

    buttons = []
    text_lines = []
    for i, entry in enumerate(entries, start=1):
        title = entry.get('title') or 'Без названия'
        url = entry.get('url') or entry.get('webpage_url')
        # Если 'url' — относительный id, сформируем полную страницу
        if url and not url.startswith('http'):
            url = f"https://www.youtube.com/watch?v={url}"
        text_lines.append(f"{i}. {title}")
        # callback data: dl::<url>
        buttons.append([InlineKeyboardButton(f"{i}. {title}", callback_data=f"dl::{url}")])

    reply_text = "Результаты поиска:\n\n" + "\n".join(text_lines) + "\n\nВыберите трек, чтобы скачать аудио."
    msg.edit_text(reply_text, reply_markup=InlineKeyboardMarkup(buttons))


def download_and_send_audio(url: str, title: str, chat_id: int, context: CallbackContext, message_id=None):
    """Скачивает аудио через yt-dlp в tmp и отправляет как audio."""
    tempdir = tempfile.mkdtemp(prefix="tg_music_")
    try:
        out_template = os.path.join(tempdir, "%(title)s.%(ext)s")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_template,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
            # чтобы yt-dlp не пытался выводить прогресс в консоль
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # найти получившийся файл
        files = os.listdir(tempdir)
        mp3_files = [f for f in files if f.lower().endswith('.mp3')]
        if not mp3_files:
            context.bot.send_message(chat_id=chat_id, text="Не удалось получить mp3-файл.")
            return

        mp3_path = os.path.join(tempdir, mp3_files[0])
        # Отправляем как audio (лучше для треков) с указанием title/performer при возможности
        performer = info.get('uploader') or None
        audio_title = info.get('title') or title or os.path.splitext(mp3_files[0])[0]

        with open(mp3_path, 'rb') as audio_file:
            context.bot.send_chat_action(chat_id=chat_id, action="upload_audio")
            context.bot.send_audio(chat_id=chat_id, audio=audio_file, title=audio_title, performer=performer)

    except Exception as e:
        logger.exception("Ошибка при скачивании/отправке")
        context.bot.send_message(chat_id=chat_id, text="Ошибка при скачивании: " + str(e))
    finally:
        try:
            shutil.rmtree(tempdir)
        except Exception:
            pass


def callback_query_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data or ""
    query.answer()

    if data.startswith("dl::"):
        url = data.split("dl::", 1)[1]
        # acknowledge and inform user
        query.edit_message_text("Скачиваю и конвертирую в mp3 — это может занять несколько секунд...")
        # Запускаем скачивание (в отдельном потоке через job_queue, чтобы не блокировать main loop)
        # Но python-telegram-bot v13 обработчики работают в отдельных потоках, поэтому можно вызвать напрямую.
        # В любом случае используем context.job_queue.run_once для безопасной работы.
        job_cb = partial(download_and_send_audio, url, None, query.message.chat.id, context)
        # запуск мгновенно (delay=0)
        context.job_queue.run_once(lambda c, j=job_cb: j(), when=0)


def error_handler(update: object, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("search", search))
    dp.add_handler(CallbackQueryHandler(callback_query_handler))
    dp.add_error_handler(error_handler)

    print("Бот запущен. Ctrl+C для остановки.")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
