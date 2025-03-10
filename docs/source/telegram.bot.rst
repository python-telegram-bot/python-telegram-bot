Bot
===

.. autoclass:: telegram.Bot
    :members:
    :show-inheritance:
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import youtube_dl
import instaloader
from TikTokDownload import snaptik
import re

TOKEN = "7743692962:AAHidumHYvyVw6CgseTCIy3j7iNJwemH0Iw"

# رد على أمر /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحبًا! أرسل رابط فيديو من يوتيوب، إنستجرام، أو تيك توك.")

    # تحديد نوع الرابط
    def handle_url(update: Update, context: CallbackContext):
        url = update.message.text
            chat_id = update.message.chat_id

                if re.search(r"youtube\.com|youtu\.be", url):
                        download_youtube(url, chat_id, context)
                            elif re.search(r"instagram\.com", url):
                                    download_instagram(url, chat_id, context)
                                        elif re.search(r"tiktok\.com", url):
                                                download_tiktok(url, chat_id, context)
                                                    else:
                                                            update.message.reply_text("الرابط غير مدعوم!")

                                                            # تحميل من يوتيوب
                                                            def download_youtube(url, chat_id, context):
                                                                try:
                                                                        ydl = youtube_dl.YoutubeDL({'outtmpl': 'video.mp4'})
                                                                                info = ydl.extract_info(url, download=True)
                                                                                        context.bot.send_video(chat_id=chat_id, video=open('video.mp4', 'rb'))
                                                                                            except Exception as e:
                                                                                                    context.bot.send_message(chat_id, f"خطأ: {e}")

                                                                                                    # تحميل من إنستجرام
                                                                                                    def download_instagram(url, chat_id, context):
                                                                                                        try:
                                                                                                                L = instaloader.Instaloader()
                                                                                                                        shortcode = url.split("/")[-2]
                                                                                                                                post = instaloader.Post.from_shortcode(L.context, shortcode)
                                                                                                                                        L.download_post(post, target="downloads")
                                                                                                                                                context.bot.send_video(chat_id=chat_id, video=open(f"downloads/{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}.mp4", 'rb'))
                                                                                                                                                    except Exception as e:
                                                                                                                                                            context.bot.send_message(chat_id, f"خطأ: {e}")

                                                                                                                                                            # تحميل من تيك توك
                                                                                                                                                            def download_tiktok(url, chat_id, context):
                                                                                                                                                                try:
                                                                                                                                                                        video_url = snaptik(url).get_media()[0]
                                                                                                                                                                                context.bot.send_video(chat_id=chat_id, video=video_url)
                                                                                                                                                                                    except Exception as e:
                                                                                                                                                                                            context.bot.send_message(chat_id, f"خطأ: {e}")

                                                                                                                                                                                            # تشغيل البوت
                                                                                                                                                                                            def main():
                                                                                                                                                                                                updater = Updater(TOKEN)
                                                                                                                                                                                                    dp = updater.dispatcher
                                                                                                                                                                                                        dp.add_handler(CommandHandler("start", start))
                                                                                                                                                                                                            dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_url))
                                                                                                                                                                                                                updater.start_polling()
                                                                                                                                                                                                                    updater.idle()

                                                                                                                                                                                                                    if __name__ == '__main__':
                                                                                                                                                                                                                        main()