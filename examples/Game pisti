
   import telebot
   import random

   # Telegram botunuzun token'ı
   TOKEN = 6626237816:AAHKfLmRfrlHesh3QgqLa-W5kTQlrJWQllA

   # Telebot'un bağlantı sağlayacağı Telegram botu
   bot = telebot.TeleBot(TOKEN)

   # Karıştırılmış bir iskambil destesi oluşturma
   def create_deck():
       suits = ['Kupa', 'Karo', 'Maça', 'Sinek']
       ranks = ['As', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Joker', 'Kız', 'Papaz']
       deck = [(suit, rank) for suit in suits for rank in ranks]
       random.shuffle(deck)
       return deck

   # İskambil destesi oluşturma komutunu dinleyen Telegram işlevi
   @bot.message_handler(commands=['create_deck'])
   def handle_create_deck(message):
       deck = create_deck()
       bot.send_message(message.chat.id, f"İskambil desteniz oluşturuldu!\n\n{deck}")

   # Telegram botunu çalıştırma komutu
   bot.polling()
   `
