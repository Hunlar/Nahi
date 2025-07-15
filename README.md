# 🇹🇷 Nahi - Mizahi Yapay Zeka Telegram Botu

Grup sohbetlerinde eğlenceli, argo ve samimi cevaplar vermek için geliştirilen GPT destekli bir Telegram botudur.  
Mesajlara `/nedersin` komutuyla cevap vererek olaylara yapay zekâ dokunuşu katar 😎

---

## 🚀 Heroku'da Tek Tıkla Kurulum

Aşağıdaki butona tıklayarak botu Heroku'ya kolayca kurabilirsiniz:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Hunlar/Nahi)

### 🛠 Gerekli Config Vars:

| Anahtar           | Açıklama                                |
|-------------------|------------------------------------------|
| `TELEGRAM_TOKEN`  | @BotFather'dan alınan Telegram bot token |
| `OPENAI_API_KEY`  | https://platform.openai.com üzerinden alınan API anahtarı |

---

## 🔧 Manuel Kurulum (Geliştiriciler İçin)

```bash
git clone https://github.com/Hunlar/Nahi.git
cd Nahi

python -m venv venv
source venv/bin/activate        # Windows için: venv\Scripts\activate

pip install -r requirements.txt

# Ortam değişkenlerini .env dosyasına gir (sadece yerel için)
echo TELEGRAM_TOKEN=xxxxx > .env
echo OPENAI_API_KEY=sk-xxxxx >> .env

python main.py
