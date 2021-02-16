import os
import pyowm
import pytz
import requests
import time
from pyowm.utils import timestamps
from datetime import timedelta, datetime
import dotenv
from dotenv import load_dotenv

load_dotenv()
"""Loading the value keys for OPEN_WEATHER_TOKEN and TELEGRAM_BOT_TOKEN from the .env file"""

owm = pyowm.OWM(os.environ['OPEN_WEATHER_TOKEN'])
"""
Using PyOWM wrapper library

PyOWM calls the 5-day weather forecast for selected city from Open Weather Map API
Place is predefined and we want the forecast with 3 hour intervals
"""
mgr = owm.weather_manager()
forecaster = mgr.forecast_at_place('Kuopio', '3h')
forecast = forecaster.forecast
weather_list = forecast.weathers


degree_sign = u'\N{DEGREE SIGN}'
"""Degree sign for the weather message temperatures"""


def degrees_to_cardinal(angle):
    """Converting degrees in Wind Direction to cardinal directions"""

    directions = ['North ↓', 'North East ↙', 'East ←', 'South East ↖',
                  'South ↑', 'South West ↗', 'West →', 'North West ↘']
    ix = int((angle + 22.5) / 45)
    return directions[ix % 8]


for weather in weather_list[0:5]:
    """Selecting the first five 3h intervals from the 5 day forecast using For loop"""

    reference_unix = weather.reference_time()
    finland = pytz.timezone('Europe/Helsinki')
    gmt = pytz.timezone('GMT')
    my_timezone = datetime.utcfromtimestamp(reference_unix)
    my_timezone = gmt.localize(my_timezone)
    my_timezone_finland = my_timezone.astimezone(finland)
    """
    Using PYTZ module for timezone conversions

    Timezone conversion from unix time -> GMT/UTC +2:00
    """

    temp = weather.temperature(unit='celsius')['temp']
    feels_like = weather.temperature(unit='celsius')['feels_like']
    detailed_status = weather.detailed_status
    wind_speed = weather.wind('meters_sec')['speed']
    wind_direction = weather.wind()['deg']
    """Parsing JSON data using PYOWM"""

    wind_direction_text = degrees_to_cardinal(int(wind_direction))
    """The 'degrees_to_cardinal' function defined earlier converts degrees into cardinal directions"""

    snow = forecaster.most_snowy()
    rain = forecaster.most_rainy()
    """
    The highest amount of rain/snow in the forecast will be presented here
    If the value from 'all' key is missing from the JSON response, this returns value 'None'
    """

    weather_message = ('Hello, Risto! Here is the weather forecast for the next few hours:' f'\n{my_timezone_finland.strftime("%d-%m-%Y %H:%M:%S")}' +
                       f'\nTemperature: {temp}{degree_sign}C' + f'\nFeels Like: {feels_like}{degree_sign}C' + f'\nWeather description: {detailed_status}' +
                       f'\nWind speed: {wind_speed} m/s' + f'\nWind direction: {wind_direction_text}' + f'\nSnowfall: {snow}' + f'\nRain: {rain}')
    """Compiling the weather forecast information message to be sent to Telegram"""

    telegram_bot_url = 'https://api.telegram.org/bot' + os.environ['TELEGRAM_BOT_TOKEN'] + '/sendMessage?chat_id=' + os.environ['TELEGRAM_CHAT_ID'] + '&text={}'.format(
        weather_message)
    """Sending the weather message from the Telegram bot to the user"""

    requests.get(telegram_bot_url)
    time.sleep(10800)
    continue
    """
    Sends the message at selected intervals (time in seconds), e.g one hour = 3600, three hours = 10800

    For loop continues until all five forecasts have been sent, then stops the program.
    """
