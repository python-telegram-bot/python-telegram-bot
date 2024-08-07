   import telebot
   from pytube import YouTube
   import os

  
   BOT_TOKEN = '6430978277:AAHHAC_o4YHsOHbcOo7OFgHOD8joiNMXsK0'
   CHANNEL_USERNAME = '@warring_b'  

   bot = telebot.TeleBot(BOT_TOKEN)

   def check_subscription(user_id):
       try:
           chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
           return chat_member.status in ['member', 'administrator', 'creator']
       except:
           return False

   @bot.message_handler(commands=['start'])
   def send_welcome(message):
       bot.reply_to(message, "مرحبًا! أرسل رابط فيديو يوتيوب لتحميله.")

   @bot.message_handler(func=lambda message: True)
   def download_video(message):
       if not check_subscription(message.from_user.id):
           bot.reply_to(message, f"يرجى الاشتراك في القناة أولاً: {CHANNEL_USERNAME}")
           return

       try:
           url = message.text
           yt = YouTube(url)

           video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
           audio_stream = yt.streams.filter(only_audio=True).first()

           video_filename = video_stream.download()
           audio_filename = audio_stream.download()

           bot.send_video(message.chat.id, open(video_filename, 'rb'))
           bot.send_audio(message.chat.id, open(audio_filename, 'rb'))

           os.remove(video_filename)
           os.remove(audio_filename)
       except Exception as e:
           bot.reply_to(message, "حدث خطأ أثناء تحميل الفيديو. يرجى المحاولة مرة أخرى.")
           print(e)

   bot.polling()
  
