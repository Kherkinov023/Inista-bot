import telebot
import requests
import time
from flask import Flask
from threading import Thread

# Render tekin serveri o'chib qolmasligi uchun Flask serveri
app = Flask('')

@app.route('/')
def home():
    return "Bot faol ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

keep_alive()

# Telegram bot kodi
TOKEN = '8340529789:AAEr3H11UtmIRbQpqt40ZvwdpC1cMRQTKs'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Salom! Instagram video yoki Reels havolasini yuboring."
    )

@bot.message_handler(func=lambda msg: True)
def handle_instagram_link(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.send_message(message.chat.id, "Iltimos, to'g'ri Instagram havolasini yuboring.")
        return

    wait_msg = bot.send_message(message.chat.id, "Video yuklab olinmoqda, biroz kuting...")

    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        if data.get("status") in ["stream", "redirect"]:
            video_url = data.get("url")
            bot.send_video(message.chat.id, video_url)
            bot.delete_message(message.chat.id, wait_msg.message_id)
        elif data.get("status") == "picker":
            for item in data.get("picker", []):
                if item.get("type") == "video":
                    bot.send_video(message.chat.id, item.get("url"))
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(
                "Videoni yuklab bo'lmadi. Havolani tekshirib qaytadan yuboring.",
                message.chat.id,
                wait_msg.message_id
            )
    except Exception as e:
        bot.edit_message_text(
            "Xatolik yuz berdi. Qaytadan urinib ko'ring.",
            message.chat.id,
            wait_msg.message_id
        )

while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        time.sleep(5)
