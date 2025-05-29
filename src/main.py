import os
import telebot
import requests
from dotenv import load_dotenv

#загрузка токена
load_dotenv("token.env")
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

#функция для получения гороскопа
def get_daily_horoscope(sign: str, day: str) -> dict:
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {"sign": sign, "day": day}
    response = requests.get(url, params)
    return response.json()

#обработчики команд
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот-гороскоп. Напиши /horoscope чтобы узнать свой гороскоп")

@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    text = "Какой у тебя знак зодиака?\nВыбери один: *Овен*, *Телец*, *Близнецы*, *Рак*, *Лев*, *Дева*, *Весы*, *Скорпион*, *Стрелец*, *Козерог*, *Водолей*, *Рыбы*."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler)

def day_handler(message):
    sign = message.text
    text = "На какой день?\nВыбери: *Сегодня*, *Завтра*, *Вчера* или введи дату в формате ГГГГ-ММ-ДД."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, fetch_horoscope, sign.capitalize())

def fetch_horoscope(message, sign):
    day = message.text
    try:
        horoscope = get_daily_horoscope(sign, day)
        data = horoscope["data"]
        response = f"""
*Гороскоп для {sign}*
*Дата:* {data["date"]}
*Прогноз:* {data["horoscope_data"]}
"""
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, "Что-то пошло не так. Попробуй еще раз.")

#запуск бота
print("Бот запущен!")
bot.infinity_polling()
