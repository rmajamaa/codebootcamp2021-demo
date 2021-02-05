import os
import pyowm
import pytz
import requests
import time
from pyowm.utils import timestamps
from datetime import timedelta, datetime

# PYOWM calls the 5-day weather forecast for selected city from Open Weather Map API
owm = pyowm.OWM(os.environ['OPEN_WEATHER_TOKEN'])
mgr = owm.weather_manager()

forecaster = mgr.forecast_at_place('Kuopio', '3h')
forecast = forecaster.forecast
weather_list = forecast.weathers

degree_sign = u'\N{DEGREE SIGN}'

# Converting degrees in Wind Direction to cardinal directions


def degrees_to_cardinal(angle):
    directions = ["North ↓", "North East ↙", "East ←", "South East ↖",
                  "South ↑", "South West ↗", "West →", "North West ↘"]
    ix = int((angle + 22.5) / 45)
    return directions[ix % 8]


# Selecting the first five 3h intervals from the 5 day forecast
for weather in weather_list[0:5]:
    # timezone conversion from unix time -> GMT -> UTC +2:00 by using PYTZ
    reference_unix = weather.reference_time()
    finland = pytz.timezone('Europe/Helsinki')
    gmt = pytz.timezone('GMT')
    my_timezone = datetime.utcfromtimestamp(reference_unix)
    my_timezone = gmt.localize(my_timezone)
    my_timezone_finland = my_timezone.astimezone(finland)

    # Parsing JSON data using PYOWM
    temp = weather.temperature(unit='celsius')['temp']
    feels_like = weather.temperature(unit='celsius')['feels_like']
    detailed_status = weather.detailed_status
    wind_speed = weather.wind('meters_sec')['speed']
    wind_direction = weather.wind()['deg']
    wind_direction_text = degrees_to_cardinal(int(wind_direction))
    snow = forecaster.most_snowy()
    rain = forecaster.most_rainy()

    # Collecting weather forecast information to be sent to Telegram
    weather_message = ('Hello, Risto! Here is the weather forecast for the next few hours:' f'\n{my_timezone_finland.strftime("%d-%m-%Y %H:%M:%S")}' +
                       f'\nTemperature: {temp}{degree_sign}C' + f'\nFeels Like: {feels_like}{degree_sign}C' + f'\nWeather description: {detailed_status}' +
                       f'\nWind speed: {wind_speed} m/s' + f'\nWind direction: {wind_direction_text}' + f'\nSnowfall: {snow}' + f'\nRain: {rain}')

    # Sending the weather message from the Telegram bot to the user
    telegram_bot_url = 'https://api.telegram.org/bot' + os.environ['TELEGRAM_BOT_TOKEN'] + '/sendMessage?chat_id=' + os.environ['TELEGRAM_CHAT_ID'] + '&text={}'.format(
        weather_message)

    # Sends the message at selected intervals (time in seconds), e.g one hour = 3600, three hours = 10800
    requests.get(telegram_bot_url)
    time.sleep(10)
