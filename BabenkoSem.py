import telebot
from telebot import types
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

bot = telebot.TeleBot("7894416776:AAF2Zz2m2PiYGryiKJFQaaHxFvEu0FeCYR0")

subscribed_users = set()

@bot.message_handler(commands=['start', 'back'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    user_id = message.chat.id
    log_message(user_id, False, message.text)
    current_weather_button = types.KeyboardButton('/weather')
    current_day_weather_button = types.KeyboardButton('/current-weather')
    schedule_button = types.KeyboardButton('/schedule')
    wind_map_button = types.KeyboardButton('/windmap')
    markup.add(current_weather_button, current_day_weather_button, schedule_button, wind_map_button)
    bot.send_message(message.chat.id, "Start keyboard", reply_markup=markup)
    log_message(user_id, True, "Start keyboard")

@bot.message_handler(commands=['weather'])
def send_weather(message):
    weather_data = get_weather()
    user_id = message.chat.id
    log_message(user_id, False, message.text)
    response = (
        f"Погода в Кемерово:\n"
        f"Сейчас: {weather_data['temp']}°C, {weather_data['description']}\n"
        f"Ощущается как: {weather_data['feels_like']}°C\n"
        f"Ветер: {weather_data['wind_speed']} м/с\n"
        f"Влажность: {weather_data['humidity']}%"
    )
        
    bot.reply_to(message, response)
    log_message(user_id, True, response)

@bot.message_handler(commands=['schedule'])
def start(message):

    user_id = message.chat.id
    log_message(user_id, False, message.text)

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    back_button = types.KeyboardButton('/back')
    subscribe_button = types.KeyboardButton('/subscribe')
    unsubscribe_button = types.KeyboardButton('/unsubscribe')
    markup.add(back_button, subscribe_button, unsubscribe_button)

    bot.send_message(message.chat.id, "Schedule keyboard", reply_markup=markup)
    log_message(user_id, True, "Schedule keyboard")

@bot.message_handler(commands=['current-weather'])
def subscribe_user(message):

    user_id = message.chat.id
    log_message(user_id, False, message.text)

    report = generate_hourly_report()
    bot.send_message(user_id, report, parse_mode="Markdown")

    log_message(user_id, True, report)

@bot.message_handler(commands=['subscribe'])
def subscribe_user(message):

    user_id = message.chat.id
    log_message(user_id, False, message.text)

    subscribed_users.add(user_id)
    bot.reply_to(message, "Вы подписались на ежедневный почасовой прогноз")

    log_message(user_id, True, "Вы подписались на ежедневный почасовой прогноз")

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe_user(message):

    user_id = message.chat.id
    log_message(user_id, False, message.text)

    if user_id in subscribed_users:
        subscribed_users.remove(user_id)
        bot.reply_to(message, "Вы отписались от уведомлений")

        log_message(user_id, True, "Вы отписались от уведомлений")

@bot.message_handler(commands=["windmap"])
def send_wind_map(message):

    user_id = message.chat.id
    log_message(user_id, False, message.text)

    url = "https://tile.openweathermap.org/map/wind_new/3/5/2.png?appid=1f1844ca48e868f68b02b7a76bff37c9"
    bot.send_photo(message.chat.id, url, caption="Карта ветров (OpenWeatherMap)")

    log_message(user_id, True, "Карта ветров (OpenWeatherMap)")

def get_weather():
    url = "http://api.openweathermap.org/data/2.5/weather?q=Kemerovo&appid=1f1844ca48e868f68b02b7a76bff37c9&units=metric&lang=ru"

    data = requests.get(url).json()

    return {
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
        "humidity": data["main"]["humidity"]
    }

def get_daily_forecast():
    url = "http://api.openweathermap.org/data/2.5/forecast?q=Kemerovo&appid=1f1844ca48e868f68b02b7a76bff37c9&units=metric&lang=ru"

    data = requests.get(url).json()
    
    return data["list"]

def generate_hourly_report():
    forecasts = get_daily_forecast()
    report = "Погода в Кемерово сегодня по часам:\n\n"
    
    now = datetime.now()
    today_forecasts = [
    f for f in forecasts 
    if (datetime.fromtimestamp(f["dt"]) >= now.replace(hour=6, minute=0, second=0) and
        datetime.fromtimestamp(f["dt"]) <= now.replace(hour=23, minute=0, second=0))
    ]
    
    for forecast in today_forecasts:
        time = datetime.fromtimestamp(forecast["dt"]).strftime("%H:%M")
        temp = forecast["main"]["temp"]
        feels_like = forecast["main"]["feels_like"]
        description = forecast["weather"][0]["description"]
        wind = forecast["wind"]["speed"]
        
        report += (
            f"{time}: {description.capitalize()}\n"
            f"{temp}°C (ощущается как {feels_like}°C)\n"
            f"Ветер: {wind} м/с\n\n"
        )
    
    return report

def send_daily_notification():
    report = generate_hourly_report()
    for user_id in subscribed_users:
        bot.send_message(user_id, report, parse_mode="Markdown")

def log_message(user_id, is_bot, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = "BOT" if is_bot else "USER"
    
    log_entry = f"[{timestamp}] {prefix}: {text}\n"
    
    with open(f'user_logs/{user_id}.log', 'a', encoding='utf-8') as file:
        file.write(log_entry)

@bot.message_handler(func=lambda message: True)
def handle_misc_messages(message):
    user_id = message.from_user.id
    log_message(user_id, False, message.text)



scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_notification, 'cron', hour=8, minute=0)
scheduler.start()
bot.polling()