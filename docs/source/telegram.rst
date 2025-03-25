import asyncio
import requests
from telegram import Bot
from telegram.ext import Application, CommandHandler

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
BITBAY_URL = "https://api.zonda.exchange/rest/trading/ticker/BTC-USD"

previous_prices = {"binance": None, "bitbay": None}
THRESHOLD = 5  # Порог изменения в процентах

async def get_binance_price():
    try:
        response = requests.get(BINANCE_URL).json()
        return float(response["price"])
    except Exception:
        return None

async def get_bitbay_price():
    try:
        response = requests.get(BITBAY_URL).json()
        return float(response["ticker"]["last"])
    except Exception:
        return None

async def send_notification():
    global previous_prices
    bot = Bot(token=TOKEN)

    while True:
        binance_price = await get_binance_price()
        bitbay_price = await get_bitbay_price()

        change_binance = (
            (abs(binance_price - previous_prices["binance"]) / previous_prices["binance"]) * 100
            if previous_prices["binance"] and binance_price else 0
        )

        change_bitbay = (
            (abs(bitbay_price - previous_prices["bitbay"]) / previous_prices["bitbay"]) * 100
            if previous_prices["bitbay"] and bitbay_price else 0
        )

        if change_binance >= THRESHOLD or change_bitbay >= THRESHOLD:
            message = f"⚡ Курс BTC изменился более чем на {THRESHOLD}%!\n"
            message += f"📌 Binance: {binance_price} USDT ({change_binance:.2f}%)\n"
            message += f"📌 BitBay: {bitbay_price} USD ({change_bitbay:.2f}%)"
            await bot.send_message(chat_id=CHAT_ID, text=message)

        if binance_price:
            previous_prices["binance"] = binance_price
        if bitbay_price:
            previous_prices["bitbay"] = bitbay_price

        await asyncio.sleep(10)  # Проверка каждые 10 секунд

async def start(update, context):
    await update.message.reply_text("Бот запущен. Следит за изменением BTC на 5%.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    loop = asyncio.get_event_loop()
    loop.create_task(send_notification())
    app.run_polling()

if __name__ == "__main__":
    main()
