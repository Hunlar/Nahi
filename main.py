import os
import openai
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ortam değişkenlerini yükle
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNjVncXRzaGczZWI0d29wNmF6YXMwdzVpY3Bpc2Y2aDZ0Y2VyaGZ1eiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/mCRJDo24UvJMA/giphy.gif"
    
    await update.message.reply_animation(gif_url)

    text = (
        "🇹🇷 Ben Türkiye Cumhuriyeti API destekli bir yapay zekâ botuyum.\n"
        "💬 Grup sohbetlerinde sormak istediğiniz soruları /nedersin komutu ile cevaplayabilirim.\n"
        "🧹 Sunucularım günlük ve haftalık periyotlarla temizlenmektedir."
    )
    keyboard = [
        [
            InlineKeyboardButton("📌 DESTEK", url="https://t.me/kizilsancaktr"),
            InlineKeyboardButton("👤 GELİŞTİRİCİ", url="https://t.me/ZeydBinhalit"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# /help komutu
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdW9sMmNudmQwMnQ1Nnh2Z2owYW13Z3Jia2xnMHpmeTdwZ2Rja2FzMyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/WXB88TeARFVvi/giphy.gif"
    
    await update.message.reply_animation(gif_url)

    text = (
        "🛠 Eğer grubumuzda çalışmıyorsam tek sebebi bazı yetkilerimin olmamasıdır.\n"
        "⚠️ Lütfen bana tüm yönetici yetkilerini verin."
    )
    keyboard = [
        [
            InlineKeyboardButton("📌 DESTEK", url="https://t.me/kizilsancaktr"),
            InlineKeyboardButton("👤 GELİŞTİRİCİ", url="https://t.me/ZeydBinhalit"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# /nedersin komutu
async def nedersin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type not in ["group", "supergroup"]:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Bu komutu bir mesaja cevap olarak kullanmalısın.")
        return

    hedef_mesaj = update.message.reply_to_message.text
    if not hedef_mesaj:
        await update.message.reply_text("Yanıtlanan mesajda metin yok.")
        return

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "Sen çok komik, esprili ve biraz da argo kullanan bir yapay zekâsın. "
                    "Cevapların samimi, rahat ve sokak ağzıyla olacak. "
                    "Hafif takıl, dalga geç, ama kırıcı olma."
                ),
            },
            {"role": "user", "content": hedef_mesaj},
        ]

        yanit = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.8,
        )
        cevap = yanit["choices"][0]["message"]["content"]
        await update.message.reply_text(cevap[:4096], reply_to_message_id=update.message.reply_to_message.message_id)

    except Exception:
        hazır_cümleler = [
            "Abi Ali yüzünden grup darmadağın oldu ha, resmen facia! 😂",
            "Ali yüzünden herkes kaçtı, adam resmen mafya patronu gibi takılıyor! 😎",
            "Kanka Ali olmasa grup bi' numaraydı, ama o var işte! 🙈",
            "Ali yüzünden grup boşaldı da biz hala ayaktayız, helal bize! 🤣",
        ]
        cevap = random.choice(hazır_cümleler)
        await update.message.reply_text(cevap, reply_to_message_id=update.message.reply_to_message.message_id)

# Botu başlat
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("nedersin", nedersin))

    print("🤖 Mizahi Telegram AI botu çalışıyor...")
    app.run_polling()
