from celery import Celery
import datetime
from dotenv import load_dotenv
import os
import requests
import sqlite3


load_dotenv()
TEMP_API_KEY = os.environ['TEMP_API_KEY']
CITY = os.environ['CITY']

app = Celery('tasks', broker='redis://localhost')


def kelvin_to_celsius(number):
    return int(number - 273.15)


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
    query = f"INSERT INTO temp(temp) VALUES ({temperature_in_celsius})"

    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()

periodic_temperature_to_db()


@app.task
def calculate_max_temperature():
    """
    Once a day the highest temperature for the previous day is
    calculated and kept in the db.
    All values for the previous day are deleted.
    """
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()

    today_date = datetime.datetime.now()
    one_day = datetime.timedelta(hours=24)
    yesterday = today_date - one_day
    yesterday_str = yesterday.strftime('%Y-%m-%d')

    query = f'SELECT temp FROM temp WHERE date like "%{yesterday_str}%"'
    cursor.execute(query)
    temps = cursor.fetchall()

    max_temp = max([temp[0] for temp in temps])
    conn.commit()
    cursor.close()
    return (yesterday_str, max_temp)


yesterday, max_temp = calculate_max_temperature()


@app.task
def save_max_temperature(yesterday, max_temp):
    """
    Save the highest temperature for the previous day to the database.
    """
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()
    query = f"INSERT INTO history(date, temp) VALUES({yesterday}, {max_temp})"
    cursor.execute(query)
    conn.commit()
    cursor.close()

save_max_temperature(yesterday, max_temp)
