import os
import logging
import random
import time
import requests
from collections import defaultdict
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Tokenlar
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

# Log
logging.basicConfig(level=logging.INFO)

# Kullanıcı mesaj zamanları (flood kontrol)
kullanici_mesajlari = defaultdict(list)

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gif_url = "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif"
    await update.message.reply_animation(animation=gif_url)

    text = (
        "Ben Türkiye Cumhuriyeti API Destekli Bir Yapay Zeka Botuyum 🇹🇷\n"
        "`/nedersin` komutuyla grup mesajlarına mizahi cevaplar verebilirim.\n"
        "_Sunucularım periyodik olarak temizlenmektedir._"
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
        "Eğer grubunuzda çalışmıyorsam, tek sebebi bazı yetkilerimin verilmemiş olmasıdır.\n"
        "🔧 Lütfen botun tüm yetkilere sahip olduğundan emin olun."
    )
    buttons = [
        [InlineKeyboardButton("📌 DESTEK", url="https://t.me/kizilsancaktr")],
        [InlineKeyboardButton("👨‍💻 GELİŞTİRİCİ", url="https://t.me/ZeydBinhalit")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# /nedersin komutu
async def nedersin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Lütfen bir mesaja cevap vererek `/nedersin` komutunu kullan.")
        return

    kim = update.message.reply_to_message.from_user.first_name
    mesaj = update.message.reply_to_message.text
    hedef_mesaj = f"{kim} adlı kullanıcı şöyle dedi: \"{mesaj}\". Buna komik ve hafif argo bir yorum yap."

    system_prompt = (
        "Sen mizahi, sokak ağzıyla konuşan bir yapay zekâsın. "
        "Rahat, esprili, bazen argo, ama kırıcı olmayan cevaplar veriyorsun."
    )

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": hedef_mesaj}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        cevap = response.json()["choices"][0]["message"]["content"]
        await update.message.reply_text(cevap[:4096], reply_to_message_id=update.message.reply_to_message.message_id)

    except Exception as e:
        print("OpenRouter API hatası:", e)
        yedek_cevaplar = [
            f"{kim} gene bi’ şey demiş ama sanki modem fişi çekili gibi konuşuyor 😂",
            f"{kim} susunca grup güzelleşiyor, bence alışkanlık haline getirsin 😏",
            f"{kim} bu cümleyi kurarken kesin yüksekten düşmüş olmalı 🤡",
            f"{kim} laf atmış ama tutmamış gibi, tekrar denesin 😬",
            f"{kim} harbi kelime israfı yapmış ha, doğaya yazık 🌳",
            f"{kim} yazarken klavye ağlamış olabilir, dikkat etsin 🫣",
            f"{kim} öyle bir şey demiş ki grup 10 IQ kaybetti 😵",
            f"{kim} mesaj attı ama ben hâlâ ‘neden’ diye sorguluyorum 😐",
            f"{kim} yazmadan önce iki kere düşünseydi keşke 🙄",
            f"{kim} bugün dilini eğitime yollamamış galiba 😂",
            f"{kim} felsefe yapmış ama Platon mezarında dönüyor olabilir 😅",
            f"{kim} yazınca grupun havası değişti, yağmur bastı ☔️",
            f"{kim} yine laf salatası yapmış, üstüne limon sıktım 🍋",
            f"{kim} cümle kurmuş ama gramer kaçmış gibi 😬",
            f"{kim} tam ‘bunu yazmasan da olurdu’ örneği bırakmış 🤐",
            f"{kim} yorum yapmış ama Google Translate bile çeviremedi 🤯",
            f"{kim} yine derin düşüncelerle grubu salladı (!?) 🌊",
            f"{kim} yazınca grup sessize aldı kendini 📴",
            f"{kim} bi' şey demiş ama ben hâlâ anlam yüklemeye çalışıyorum 🧠",
            f"{kim} beynini uçak moduna alıp yazmış olabilir 🛫"
        ]
        await update.message.reply_text(random.choice(yedek_cevaplar), reply_to_message_id=update.message.reply_to_message.message_id)

# Flood kontrol (3 mesaj arka arkaya)
async def mesaj_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type not in ["group", "supergroup"]:
        return

    user_id = update.message.from_user.id
    now = time.time()

    # Eski mesajları temizle (15 saniyede sadece son 3)
    kullanici_mesajlari[user_id] = [
        t for t in kullanici_mesajlari[user_id] if now - t < 15
    ]

    kullanici_mesajlari[user_id].append(now)

    if len(kullanici_mesajlari[user_id]) >= 3:
        await update.message.reply_text("Yavaş lan yavşak 😡", reply_to_message_id=update.message.message_id)
        kullanici_mesajlari[user_id] = []  # sayaç sıfırla

# Botu başlat
if __name__ == "__main__":
    if TELEGRAM_TOKEN is None or OPENROUTER_KEY is None:
        raise ValueError("Gerekli API anahtarları eksik!")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Komutlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("nedersin", nedersin))

    # Flood kontrol
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_kontrol))

    print("Bot başlatıldı...")
    app.run_polling()
