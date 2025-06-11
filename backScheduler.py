import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from weatherReport import generate_hourly_report
from globals import bot, subscribed_users

scheduler = BackgroundScheduler()

def setup_backgroud_scheduler_handlers(bot: telebot.TeleBot):
    scheduler.add_job(send_daily_notification, 'cron', hour=8, minute=0)
    scheduler.start()

def send_daily_notification():
    try:
        report = generate_hourly_report()
        for user_id in subscribed_users:
            bot.send_message(user_id, report, parse_mode="Markdown")
    except Exception as error:
        print( f"Ошибка отправки ежедневой погоды: {error}")