import telebot

TOKEN = '8196119736:AAG2dckHkbBEqqg406-lSRyusxX0qNXJik8'
bot = telebot.TeleBot(TOKEN)

def predict(number, last_size):
    mod = number % 3
    color = {0: 'Violet', 1: 'Green', 2: 'Red'}[mod]
    size = 'Big' if last_size.lower() == 'small' else 'Small'
    return color, size

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Send /predict <number> <size> (e.g., /predict 8 Small)")

@bot.message_handler(commands=['predict'])
def handle_predict(message):
    try:
        _, num, size = message.text.split()
        number = int(num)
        pred_color, pred_size = predict(number, size)
        bot.reply_to(message, f"🎯 Prediction:\n🎨 Color: {pred_color}\n🔢 Size: {pred_size}")
    except:
        bot.reply_to(message, "❌ Usage: /predict <number> <Big/Small>")

bot.polling()
