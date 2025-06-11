import requests
from datetime import datetime
from globals import bot, subscribed_users

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