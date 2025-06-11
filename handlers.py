import telebot
from weatherReport import get_weather, generate_hourly_report, recommend
from telebot import types
from logger import log_message
from backScheduler import setup_backgroud_scheduler_handlers, scheduler, send_daily_notification
from globals import subscribed_users

def setup_main_command_handlers(bot: telebot.TeleBot):
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
            main_response = (
                "Вы на главной клавиатуре бота по поиску погоды в городе Кемерово:\n"
                "Основные функции: \n"
                "Погода сейчас - подробное описание текущей погоды, а также рекомендации по выбору соответствующей одежды.\n"
                "Погода сегодня - расписание погоды на весь день. \n"
                "Расписание - возможность подписки на ежедневную рассылку информации о погоде \n"
                "Карта ветров - для просмотра текущей активности ветра в регионе \n"
            )
            bot.send_message(message.chat.id, main_response, reply_markup=markup)
            log_message(user_id, True, main_response)
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
            bot.send_message(message.chat.id, response)
            log_message(user_id, True, response)
        except Exception as error:
            bot.send_message(message.chat.id, f"Ошибка: {error}")
            log_message(user_id, True, f"Ошибка: {error}")

    @bot.message_handler(commands=['weather-today'])
    def weather_3_hour(message):
        try:
            user_id = message.chat.id
            log_message(user_id, False, message.text)

            report = generate_hourly_report()
            bot.send_message(user_id, report, parse_mode="Markdown")

            log_message(user_id, True, report)
        except Exception as error:
            bot.send_message(message.chat.id, f"Ошибка: {error}")
            log_message(user_id, True, f"Ошибка: {error}")

    @bot.message_handler(commands=['schedule'])
    def schedule(message):
        try:
            user_id = message.chat.id
            log_message(user_id, False, message.text)

            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            back_button = types.KeyboardButton('/back')
            schedule_test_button = types.KeyboardButton('/schedule-test')
            subscribe_button = types.KeyboardButton('/subscribe')
            unsubscribe_button = types.KeyboardButton('/unsubscribe')
            markup.add(back_button, schedule_test_button, subscribe_button, unsubscribe_button)
            schedule_response = (
                "Вы на экране ежедневной подписки:\n"
                "Основные функции: \n"
                "Подписка/отписка на ежедневную рассылку погоды.\n"
                "ТЕСТ ПОДПИСКИ\n"
            )
            bot.send_message(message.chat.id, schedule_response, reply_markup=markup)
            log_message(user_id, True, schedule_response)
        except Exception as error:
            bot.send_message(message.chat.id, f"Ошибка: {error}")
            log_message(user_id, True, f"Ошибка: {error}")

    @bot.message_handler(commands=['schedule-test'])
    def scheduleTest(message):
        try:
            user_id = message.chat.id
            log_message(user_id, False, message.text)
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            back_button = types.KeyboardButton('/back')
            schedule_test_stop_button = types.KeyboardButton('/schedule-test-stop')
            subscribe_button = types.KeyboardButton('/subscribe')
            unsubscribe_button = types.KeyboardButton('/unsubscribe')
            markup.add(back_button, schedule_test_stop_button, subscribe_button, unsubscribe_button)
            scheduler.add_job(send_daily_notification,'interval',seconds=10, id="test")
            bot.reply_to(message, "Вы подписались на ежедневный прогноз будет показываться каждые 10 секунд", reply_markup=markup)
            log_message(user_id, True, "Вы подписались на ежедневный прогноз будет показываться каждые 10 секунд")
        except Exception as error:
            bot.send_message(message.chat.id, f"Ошибка: {error}")
            log_message(user_id, True, f"Ошибка: {error}")

    @bot.message_handler(commands=['schedule-test-stop'])
    def scheduleTestStop(message):
        try:
            user_id = message.chat.id
            log_message(user_id, False, message.text)
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            back_button = types.KeyboardButton('/back')
            schedule_test_button = types.KeyboardButton('/schedule-test')
            subscribe_button = types.KeyboardButton('/subscribe')
            unsubscribe_button = types.KeyboardButton('/unsubscribe')
            markup.add(back_button, schedule_test_button, subscribe_button, unsubscribe_button)
            if scheduler.get_job('test'):
                scheduler.remove_job('test')
            bot.reply_to(message, "Тест ежедневного прогноза окончен", reply_markup=markup)
            log_message(user_id, True, "Тест ежедневного прогноза окончен")
        except Exception as error:
            bot.send_message(message.chat.id, f"Ошибка: {error}")
            log_message(user_id, True, f"Ошибка: {error}")

    @bot.message_handler(commands=['subscribe'])
    def subscribe_user(message):
        try:
            user_id = message.chat.id
            log_message(user_id, False, message.text)

            subscribed_users.add(user_id)
            bot.reply_to(message, "Вы подписались на ежедневный прогноз погоды")

            log_message(user_id, True, "Вы подписались на ежедневный прогноз погоды")
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
    
def setup_misc_messages_handler(bot: telebot.TeleBot):
    @bot.message_handler(func=lambda message: True)
    def handle_misc_messages(message):
        user_id = message.from_user.id
        log_message(user_id, False, message.text)
        bot.reply_to(message, "Используйте команды меню. Перейти к ним можно при помощи команд /start и /back.")
        log_message(user_id, True, "Используйте команды меню. Перейти к ним можно при помощи команд /start и /back.")