from celery import Celery
from dotenv import load_dotenv
import os
import requests
import sqlite3
#from icecream import ic


load_dotenv()
TEMP_API_KEY = os.environ['TEMP_API_KEY']
CITY = os.environ['CITY']

app = Celery('tasks', broker='redis://localhost')


def kelvin_to_celsius(number):
    return number - 273.15


@app.task
def periodic_temperature_to_db():
    """
    Task runs every minute and gets the temperature value for Moscow.
    Value is written into db.

    """
    ENDPOINT = "http://api.openweathermap.org/data/2.5/weather"
    URL = f"{ENDPOINT}?q={CITY}&APPID={TEMP_API_KEY}"
    weather_json = requests.get(URL).json()
    temperature_in_kelvin = weather_json.get("main", {}).get("temp", None)
    if not temperature_in_kelvin:
        return
    temperature_in_celsius = kelvin_to_celsius(temperature_in_kelvin)
    return temperature_in_celsius


periodic_temperature_to_db()
