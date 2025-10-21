import requests
import telebot
import schedule
import time
from datetime import datetime
import pytz
import threading
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

# === НАСТРОЙКИ ===
BOT_TOKEN = "8293308425:AAGgSwxu7sOCk-h4RmEgmIvGHxiq_u8R3D4"  # токен бота
CHANNEL_ID = "@DailyNumbers"  # канал
TIMEZONE = pytz.timezone("Europe/Moscow")  # часовой пояс МСК

bot = telebot.TeleBot(BOT_TOKEN)

def get_currency_rates():
    try:
        # Курсы валют от ЦБ РФ
        r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js").json()
        usd = r["Valute"]["USD"]["Value"]
        eur = r["Valute"]["EUR"]["Value"]
        cny = r["Valute"]["CNY"]["Value"]

        # Курсы крипты с CoinGecko
        crypto = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd").json()
        btc = crypto["bitcoin"]["usd"]
        eth = crypto["ethereum"]["usd"]

        now = datetime.now(TIMEZONE).strftime("%d.%m.%Y %H:%M")

        text = f"""📊 Курсы на {now} (МСК)

💵 Валюта:
🇺🇸 USD: {usd:.2f} ₽
🇪🇺 EUR: {eur:.2f} ₽
🇨🇳 CNY: {cny:.2f} ₽

💰 Криптовалюта:
₿ Bitcoin: ${btc}
Ξ Ethereum: ${eth}

#DailyNumbers #курс"""
        return text
    except Exception as e:
        return f"Ошибка при получении данных: {e}"

def post_to_channel():
    try:
        msg = get_currency_rates()
        bot.send_message(CHANNEL_ID, msg)
        print(f"[{datetime.now(TIMEZONE)}] Пост отправлен!")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

# Расписание (по МСК)
schedule.every().day.at("09:00").do(post_to_channel)
schedule.every().day.at("18:00").do(post_to_channel)

def scheduler():
    print("Бот запущен и ждёт времени постинга...")
    while True:
        schedule.run_pending()
        time.sleep(30)

def run_server():
    """Фейковый HTTP-сервер, чтобы Render думал, что у нас веб-приложение"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"Фейковый сервер запущен на порту {port}")
    server.serve_forever()

if __name__ == "__main__":
    # Запускаем оба процесса параллельно
    threading.Thread(target=scheduler).start()
    run_server()
