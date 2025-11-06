import requests
import time
from telegram import Bot

# === Your Personal Info ===
BOT_TOKEN = "8388984179:AAFMf_A4_ehHffdKxgES-EmNy3Npyx1yA3w"
CHAT_ID = "5570281457"

bot = Bot(token=BOT_TOKEN)

DEXSCREENER_API = "https://api.dexscreener.io/latest/dex/search?q=bsc"

def fetch_new_pairs():
    try:
        response = requests.get(DEXSCREENER_API)
        if response.status_code == 200:
            data = response.json()
            pairs = data.get("pairs", [])
            return pairs[:5]  # Fetch top 5 new pairs
        else:
            return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def send_alert(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    seen_tokens = set()
    while True:
        pairs = fetch_new_pairs()
        for p in pairs:
            address = p.get("pairAddress")
            if address not in seen_tokens:
                seen_tokens.add(address)
                name = p.get("baseToken", {}).get("name", "Unknown")
                symbol = p.get("baseToken", {}).get("symbol", "???")
                liquidity = p.get("liquidity", {}).get("usd", 0)
                message = f"🆕 New BSC Pair Detected!\n\nName: {name}\nSymbol: {symbol}\nLiquidity: ${liquidity}\nAddress: {address}"
                send_alert(message)
        time.sleep(60)

if __name__ == "__main__":
    main()
