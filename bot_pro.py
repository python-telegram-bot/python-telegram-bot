import json
import os
import time
import random
import string
import subprocess
import requests
from bs4 import BeautifulSoup

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# ================= CONFIG =================

TOKEN = "8595132005:AAFCGhlGgHbpoZ-LPbYhIA9vN0z706p0WRk"          # Remplace par ton token
ADMINS = [8547509346]             # Remplace par ton ID
ADMIN_USERNAME = "DLGOFFICIEL"  # Sans @

PRICE = 500
FREE_VIDEO_LIMIT = 3

DB_FILE = "users.json"
CODES_FILE = "codes.json"
PAY_FILE = "payments.json"

# ==========================================

# =============== INIT FILES ===============
def init_file(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)

init_file(DB_FILE, {"users": {}})
init_file(CODES_FILE, {"codes": []})
init_file(PAY_FILE, {"payments": []})

# =============== UTILS ====================
def load(file):
    with open(file) as f:
        return json.load(f)

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def is_admin(uid):
    return uid in ADMINS

def generate_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ============ VIDEO LIMIT ============
video_count = {}
video_reset = time.time()
def reset_video_limit():
    global video_reset
    if time.time() - video_reset > 86400:
        video_count.clear()
        video_reset = time.time()

# =============== MENUS ====================
def main_menu(uid):
    buttons = [
        [InlineKeyboardButton("🔎 Rechercher", callback_data="search")],
        [InlineKeyboardButton("📥 Télécharger Vidéo", callback_data="download")],
        [InlineKeyboardButton("🎬 Booster Vidéos", callback_data="boost")],
        [InlineKeyboardButton("💎 Devenir Premium", callback_data="buy")],
        [InlineKeyboardButton("📞 Contacter l’admin", url=f"https://t.me/{ADMIN_USERNAME}")],
        [InlineKeyboardButton("📜 Mon historique", callback_data="history")],
        [InlineKeyboardButton("ℹ️ Mon compte", callback_data="account")]
    ]
    if is_admin(uid):
        buttons.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(buttons)

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("💳 Paiements", callback_data="all_pay")],
        [InlineKeyboardButton("🔑 Générer Code", callback_data="gen")],
        [InlineKeyboardButton("⬅️ Retour", callback_data="back")]
    ])

# =============== COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    db = load(DB_FILE)
    new_user = False

    if uid not in db["users"]:
        db["users"][uid] = {"name": user.first_name, "premium": False, "joined": time.time()}
        save(DB_FILE, db)
        new_user = True

    # Message de bienvenue et présentation
    welcome_text = (
        f"👋 Salut {user.first_name} !\n\n"
        "Bienvenue sur *Bot Premium* 🤖\n\n"
        "Avec ce bot, tu peux :\n"
        "🔎 Rechercher sur le web\n"
        "📥 Télécharger des vidéos YouTube\n"
        "🎬 Recevoir des vidéos liées à tes recherches\n"
        "💎 Passer Premium pour débloquer toutes les fonctionnalités\n\n"
        "Commence par choisir une option ci-dessous !"
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_menu(user.id)
    )

    # Message incitatif Premium si nouvel utilisateur
    if new_user:
        premium_text = (
            "💎 Astuce : En tant qu'utilisateur Free, tu as accès à certaines fonctionnalités limitées.\n"
            "🚀 Passe Premium pour :\n"
            "- Télécharger des vidéos illimitées\n"
            "- Recevoir toutes les vidéos liées à tes recherches\n"
            "- Accéder à toutes les options du bot\n\n"
            "Clique sur 💎 Devenir Premium pour débloquer tout ça !"
        )
        await update.message.reply_text(
            premium_text,
            reply_markup=main_menu(user.id)
        )

async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Ton ID: {update.effective_user.id}")

# =============== CALLBACKS ================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)
    db = load(DB_FILE)
    pays = load(PAY_FILE)
    data = query.data

    if data == "search":
        context.user_data["mode"] = "search"
        await query.edit_message_text("🔎 Envoie ton mot-clé pour rechercher.", reply_markup=main_menu(query.from_user.id))
    elif data == "download":
        context.user_data["wait_video"] = True
        await query.edit_message_text("📥 Envoie le lien de la vidéo", reply_markup=main_menu(query.from_user.id))
    elif data == "boost":
        context.user_data["mode"] = "boost"
        await query.edit_message_text(
            "🎬 Envoie le nom de l'artiste ou sujet pour recevoir 2 vidéos gratuites (illimité pour Premium).",
            reply_markup=main_menu(query.from_user.id)
        )
    elif data == "buy":
        await query.edit_message_text(
            f"💎 PREMIUM À VIE — {PRICE} FCFA\n\nPaiement Mobile Money\nClique sur 📞 Contacter l’admin après paiement.",
            reply_markup=main_menu(query.from_user.id)
        )
    elif data == "history":
        history = [p for p in pays["payments"] if p["user"] == uid]
        text = "📜 Historique:\n\n" + "\n".join([f"{p['amount']} FCFA — {time.strftime('%d/%m/%Y', time.localtime(p['date']))}" for p in history[-5:]]) if history else "📜 Aucun paiement."
        await query.edit_message_text(text, reply_markup=main_menu(query.from_user.id))
    elif data == "account":
        user = db["users"][uid]
        status = "💎 PREMIUM" if user["premium"] else "FREE"
        text = f"👤 Compte\n\nNom: {user['name']}\nStatut: {status}\n"
        await query.edit_message_text(text, reply_markup=main_menu(query.from_user.id))
    elif data == "admin" and is_admin(int(uid)):
        await query.edit_message_text("⚙️ Panel Admin", reply_markup=admin_menu())
    elif data == "stats" and is_admin(int(uid)):
        total = len(db["users"])
        premium = sum(1 for u in db["users"].values() if u["premium"])
        await query.edit_message_text(f"📊 Stats\n\nUsers: {total}\nPremium: {premium}", reply_markup=admin_menu())
    elif data == "all_pay" and is_admin(int(uid)):
        text = "💳 Paiements:\n\n" + "\n".join([f"{p['user']} | {p['amount']} | {time.strftime('%d/%m/%Y', time.localtime(p['date']))}" for p in pays["payments"][-10:]])
        await query.edit_message_text(text, reply_markup=admin_menu())
    elif data == "gen" and is_admin(int(uid)):
        context.user_data["wait_gen"] = True
        await query.edit_message_text("✍️ Envoie l'ID du client", reply_markup=admin_menu())
    elif data == "back":
        await query.edit_message_text("Menu principal", reply_markup=main_menu(query.from_user.id))

# =============== MESSAGES =================
async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()
    db = load(DB_FILE)
    pays = load(PAY_FILE)

    # Admin: Générer code
    if context.user_data.get("wait_gen") and is_admin(update.effective_user.id):
        target = text
        if target not in db["users"]:
            await update.message.reply_text("❌ ID invalide")
            return
        codes = load(CODES_FILE)["codes"]
        code = generate_code()
        while code in codes:
            code = generate_code()
        codes.append(code)
        save(CODES_FILE, {"codes": codes})
        await context.bot.send_message(target, f"💎 Ton code Premium:\n\n{code}\n\n/redeem {code}")
        context.user_data["wait_gen"] = False
        return

    # Redeem code
    if text.startswith("/redeem"):
        parts = text.split()
        if len(parts) != 2: return
        code = parts[1]
        codes = load(CODES_FILE)["codes"]
        if code not in codes:
            await update.message.reply_text("❌ Code invalide")
            return
        db["users"][uid]["premium"] = True
        save(DB_FILE, db)
        codes.remove(code)
        save(CODES_FILE, {"codes": codes})
        pays["payments"].append({"user": uid, "amount": PRICE, "date": time.time()})
        save(PAY_FILE, pays)
        await update.message.reply_text("🎉 Premium activé !")
        return

    # Video download
    if context.user_data.get("wait_video"):
        reset_video_limit()
        user = db["users"][uid]
        if not user["premium"]:
            used = video_count.get(uid, 0)
            if used >= FREE_VIDEO_LIMIT:
                await update.message.reply_text("🚫 Limite atteinte (3/jour).\nPasse Premium 💎")
                context.user_data["wait_video"] = False
                return
            video_count[uid] = used + 1
        await update.message.reply_text("⏳ Téléchargement...")
        try:
            file_name = f"video_{uid}.mp4"
            subprocess.run(["yt-dlp", "-f", "mp4", "-o", file_name, text], check=True)
            await update.message.reply_video(video=open(file_name, "rb"))
            os.remove(file_name)
            await update.message.reply_text("✅ Terminé")
        except:
            await update.message.reply_text("❌ Erreur téléchargement")
        context.user_data["wait_video"] = False
        return

    # Web search
    if context.user_data.get("mode") == "search":
        query = text
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", class_="result__a", href=True)][:5]
        text_reply = "🔎 Résultats :\n" + "\n".join(links) if links else "❌ Aucun résultat trouvé."
        await update.message.reply_text(text_reply)
        return

    # Boost video
    if context.user_data.get("mode") == "boost":
        user = db["users"][uid]
        limit = 2 if not user["premium"] else 10
        await update.message.reply_text(f"⏳ Recherche et téléchargement de {limit} vidéos...")
        for i in range(limit):
            file_name = f"video_{uid}_{i}.mp4"
            cmd = f'yt-dlp "ytsearch{limit}:{text}" -f mp4 -o "{file_name}" --quiet --no-warnings'
            os.system(cmd)
            if os.path.exists(file_name):
                await update.message.reply_video(video=open(file_name, "rb"))
                os.remove(file_name)
        if not user["premium"] and limit == 2:
            await update.message.reply_text("🚀 Tu as reçu 2 vidéos gratuites.\n💎 Pour toutes les vidéos, passe Premium !")
        return

# =============== MAIN =====================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", my_id))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT, messages))

print("✅ Bot lancé")
app.run_polling()
      
