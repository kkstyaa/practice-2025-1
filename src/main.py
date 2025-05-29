import os
import telebot
import requests
from dotenv import load_dotenv

#инициализируем бота
load_dotenv("token.env")
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)


#функция для получения гороскопа
def get_daily_horoscope(sign: str, day: str) -> dict:
    #словари для перевода на английский
    sign_translation = {
        'овен': 'aries', 'телец': 'taurus', 'близнецы': 'gemini',
        'рак': 'cancer', 'лев': 'leo', 'дева': 'virgo',
        'весы': 'libra', 'скорпион': 'scorpio', 'стрелец': 'sagittarius',
        'козерог': 'capricorn', 'водолей': 'aquarius', 'рыбы': 'pisces'
    }

    day_translation = {
        'сегодня': 'TODAY',
        'завтра': 'TOMORROW',
        'вчера': 'YESTERDAY'
    }

    try:
        #преобразуем входные данные
        sign_lower = sign.strip().lower()
        day_lower = day.strip().lower()

        #перевод на английский
        sign_en = sign_translation.get(sign_lower, sign_lower)
        day_en = day_translation.get(day_lower, day_lower)

        #формировние ссылки 
        url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
        params = {"sign": sign_en, "day": day_en}

        #отправка запроса
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  #проверка http ошибок

        #парсинг
        data = response.json()

        #проверка успешности ответа
        if not data.get('success', False):
            raise ValueError("API вернуло неуспешный ответ")

        return data

    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
    except ValueError as e:
        print(f"Ошибка данных: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

    return None


#обработчики команд
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот-гороскоп ✨. Напиши /horoscope чтобы узнать свой гороскоп 🔮")


@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    text = "Какой у тебя знак зодиака? ♌️\nВыбери один: Овен, Телец, Близнецы, Рак, Лев, Дева, Весы, Скорпион, Стрелец, Козерог, Водолей, Рыбы."
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, day_handler)


def day_handler(message):
    sign = message.text
    text = "На какой день? 📅\nВыбери: Сегодня, Завтра, Вчера или введи дату в формате ГГГГ-ММ-ДД."
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, fetch_horoscope, sign.capitalize())


def fetch_horoscope(message, sign):
    day = message.text
    try:
        #получение данных
        horoscope = get_daily_horoscope(sign, day)

        if not horoscope:
            raise Exception("API не ответило")

        data = horoscope.get('data', {})

        #проверка наличия данных
        if not data.get('date') or not data.get('horoscope_data'):
            raise ValueError("Неполные данные в ответе")

        #форматирование ответа
        response = f"""
✨ *Гороскоп для {sign}* ✨
📅 *Дата:* {data['date']}
🔮 *Прогноз:* {data['horoscope_data']}
"""
        bot.send_message(message.chat.id, response, parse_mode="Markdown")

    except Exception as e:
        print(f"Ошибка при формировании гороскопа: {e}")
        error_msg = """
⚠️ *Не удалось получить гороскоп!*

_Возможные причины:_
- Неправильно указан знак зодиака
- Ошибка в формате даты
- Временная недоступность сервиса гороскопов

Попробуйте снова, используя:
- Один из 12 знаков зодиака (например, "Овен")
- "Сегодня", "Завтра" или "Вчера"
- Дату в формате ГГГГ-ММ-ДД
"""
        bot.send_message(message.chat.id, error_msg, parse_mode="Markdown")


#запуск бота
if __name__ == "__main__":
    print("✅ Бот запущен и готов к работе!")
    bot.infinity_polling()
