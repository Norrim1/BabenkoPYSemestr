import telebot
from telebot import types
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

bot = telebot.TeleBot("7894416776:AAF2Zz2m2PiYGryiKJFQaaHxFvEu0FeCYR0")

subscribed_users = set()

@bot.message_handler(commands=['start', 'back'])
def start(message):
    try:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        user_id = message.chat.id
        log_message(user_id, False, message.text)
        current_weather_button = types.KeyboardButton('/weather-today')
        current_day_weather_button = types.KeyboardButton('/current-weather')
        schedule_button = types.KeyboardButton('/schedule')
        wind_map_button = types.KeyboardButton('/windmap')
        markup.add(current_weather_button, current_day_weather_button, schedule_button, wind_map_button)
        bot.send_message(message.chat.id, "Start keyboard", reply_markup=markup)
        log_message(user_id, True, "Start keyboard")
    except Exception as error:
        bot.send_message(message.chat.id, f"Ошибка: {error}")
        log_message(user_id, True, f"Ошибка: {error}")

@bot.message_handler(commands=['current-weather'])
def send_weather(message):
    try:
        weather_data = get_weather()
        user_id = message.chat.id
        log_message(user_id, False, message.text)
        response = (
            f"Погода в Кемерово:\n"
            f"Сейчас: {weather_data['temp']}°C, {weather_data['description']}\n"
            f"Ощущается как: {weather_data['feels_like']}°C\n"
            f"Ветер: {weather_data['wind_speed']} м/с\n"
            f"Влажность: {weather_data['humidity']}%\n"
            f"Рекомендации сейчас: {recommend(weather_data['temp'], weather_data['wind_speed'], weather_data['description'])}"
        )
        bot.reply_to(message, response)
        log_message(user_id, True, response)
    except Exception as error:
        bot.send_message(message.chat.id, f"Ошибка: {error}")
        log_message(user_id, True, f"Ошибка: {error}")

@bot.message_handler(commands=['schedule'])
def start(message):
    try:
        user_id = message.chat.id
        log_message(user_id, False, message.text)

        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        back_button = types.KeyboardButton('/back')
        subscribe_button = types.KeyboardButton('/subscribe')
        unsubscribe_button = types.KeyboardButton('/unsubscribe')
        markup.add(back_button, subscribe_button, unsubscribe_button)

        bot.send_message(message.chat.id, "Schedule keyboard", reply_markup=markup)
        log_message(user_id, True, "Schedule keyboard")
    except Exception as error:
        bot.send_message(message.chat.id, f"Ошибка: {error}")
        log_message(user_id, True, f"Ошибка: {error}")

@bot.message_handler(commands=['weather-today'])
def subscribe_user(message):
    try:
        user_id = message.chat.id
        log_message(user_id, False, message.text)

        report = generate_hourly_report()
        bot.send_message(user_id, report, parse_mode="Markdown")

        log_message(user_id, True, report)
    except Exception as error:
        bot.send_message(message.chat.id, f"Ошибка: {error}")
        log_message(user_id, True, f"Ошибка: {error}")

@bot.message_handler(commands=['subscribe'])
def subscribe_user(message):
    try:
        user_id = message.chat.id
        log_message(user_id, False, message.text)

        subscribed_users.add(user_id)
        bot.reply_to(message, "Вы подписались на ежедневный почасовой прогноз")

        log_message(user_id, True, "Вы подписались на ежедневный почасовой прогноз")
    except Exception as error:
        bot.send_message(message.chat.id, f"Ошибка: {error}")
        log_message(user_id, True, f"Ошибка: {error}")

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe_user(message):
    try:
        user_id = message.chat.id
        log_message(user_id, False, message.text)

        if user_id in subscribed_users:
            subscribed_users.remove(user_id)
            bot.reply_to(message, "Вы отписались от уведомлений")

            log_message(user_id, True, "Вы отписались от уведомлений")
    except Exception as error:
        bot.send_message(message.chat.id, f"Ошибка: {error}")
        log_message(user_id, True, f"Ошибка: {error}")

@bot.message_handler(commands=["windmap"])
def send_wind_map(message):
    try:
        user_id = message.chat.id
        log_message(user_id, False, message.text)

        url = "https://tile.openweathermap.org/map/wind_new/3/5/2.png?appid=1f1844ca48e868f68b02b7a76bff37c9"
        bot.send_photo(message.chat.id, url, caption="Карта ветров (OpenWeatherMap)")

        log_message(user_id, True, "Карта ветров (OpenWeatherMap)")
    except Exception as error:
        bot.send_message(message.chat.id, f"Ошибка: {error}")
        log_message(user_id, True, f"Ошибка: {error}")

def get_weather():
    try:
        url = "http://api.openweathermap.org/data/2.5/weather?q=Kemerovo&appid=1f1844ca48e868f68b02b7a76bff37c9&units=metric&lang=ru"

        data = requests.get(url).json()

        return {
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "humidity": data["main"]["humidity"]
        }
    except Exception as error:
        print( f"Ошибка: {error}")

def get_daily_forecast():
    try:
        url = "http://api.openweathermap.org/data/2.5/forecast?q=Kemerovo&appid=1f1844ca48e868f68b02b7a76bff37c9&units=metric&lang=ru"

        data = requests.get(url).json()
        
        return data["list"]
    except Exception as error:
        print( f"Ошибка: {error}")

def generate_hourly_report():
    try:
        forecasts = get_daily_forecast()
        report = "Погода в Кемерово сегодня по часам:\n\n"
        
        now = datetime.now()
        today_forecasts = [
        f for f in forecasts 
        if (datetime.fromtimestamp(f["dt"]) >= now.replace(hour=6, minute=0, second=0) and
            datetime.fromtimestamp(f["dt"]) <= now.replace(hour=23, minute=0, second=0))
        ]
        
        for forecast in today_forecasts:        
            report += (
                f"{datetime.fromtimestamp(forecast["dt"]).strftime("%H:%M")}: {forecast["weather"][0]["description"].capitalize()}\n"
                f"{forecast["main"]["temp"]}°C (ощущается как {forecast["main"]["feels_like"]}°C)\n"
                f"Ветер: {forecast["wind"]["speed"]} м/с\n\n"
            )
        return report
    except Exception as error:
        print( f"Ошибка: {error}")

def send_daily_notification():
    try:
        report = generate_hourly_report()
        for user_id in subscribed_users:
            bot.send_message(user_id, report, parse_mode="Markdown")
    except Exception as error:
        print( f"Ошибка отправки ежедневой погоды: {error}")

def log_message(user_id, is_bot, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = "BOT" if is_bot else "USER"
    
    log_entry = f"[{timestamp}] {prefix}: {text}\n"
    
    with open(f'user_logs/{user_id}.log', 'a', encoding='utf-8') as file:
        file.write(log_entry)

def recommend(temp, wind, desc):
    try:
        current_month = datetime.now().month
        recommendations = ""
        if current_month in [12, 1, 2]:
            if temp < -25:
                recommendations += "Одевайтесь максимально тепло.\n"
            elif temp < -15:
                recommendations += "Наденьте тёплую куртку, шапку и перчатки.\n"
            else:
                recommendations += "Наденьте тёплую куртку.\n"
                
        elif current_month in [6, 7, 8]:
            if temp > 25:
                recommendations += "Наденьте лёгкую одежду, футболку или шорты.\n"
            elif temp < 15:
                recommendations += "Наденьте лёгкую куртку или ветровку."
            else:
                recommendations += "Подойдёт лёгкая рубашка или футболка.\n"

        else:
            if temp < 0:
                recommendations += "Наденьте тёплую куртку, шапку и перчатки.\n"
            elif temp < 10:
                recommendations += "Одевайтесь тепло, подойдёт демисезонная куртка.\n"
            elif temp > 20:
                recommendations += "Подойдёт лёгкая рубашка или футболка.\n"
            else:
                recommendations += "Наденьте лёгкую куртку или пальто.\n"
                
        if desc.lower() in ['дождь', 'ливень', 'морось']:
            recommendations += "Не забудьте взять зонт!\n"
            
        if wind > 5:
            recommendations += "Учитывайте сильный ветер при выборе одежды.\n"
            
        return recommendations
    except Exception as error:
        print( f"Ошибка: {error}")

@bot.message_handler(func=lambda message: True)
def handle_misc_messages(message):
    user_id = message.from_user.id
    log_message(user_id, False, message.text)
    bot.reply_to(message, "Используйте команды меню. Перейти к ним можно при помощи команд /start и /back.")
    log_message(user_id, True, "Используйте команды меню. Перейти к ним можно при помощи команд /start и /back.")

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_notification, 'cron', hour=8, minute=0)
scheduler.start()
bot.polling()