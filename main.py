import telebot
import requests
import time
from flask import Flask
from threading import Thread

# Render tekin serveri o'chib qolmasligi uchun mini veb-server
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
TOKEN = '8340529789:AAFutYS4NvkcGe-02aDTwI3Ccc24I0jar8o'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id, 
        "Salom! Instagram video yoki Reels havolasini yuboring, men uni yuklab beraman."
    )

@bot.message_handler(func=lambda msg: msg.text and 'instagram.com' in msg.text)
def handle_instagram_link(message):
    wait_msg = bot.send_message(message.chat.id, "Video yuklanmoqda, iltimos kuting...")
    
    url = message.text.strip()
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=20)
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
                "Videoni yuklab bo'lmadi. Havola to'g'riligini tekshiring.", 
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
        bot.polling(none_stop=True, interval=1, timeout=60)
    except Exception as e:
        time.sleep(5)
