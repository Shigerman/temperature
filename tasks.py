from celery import Celery
from dateutil import tz
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
def periodic_temperature_to_sqlite():
    """
    Task gets the temperature value for Moscow and writes it into SQLIte
    """
    ENDPOINT = "http://api.openweathermap.org/data/2.5/weather"
    URL = f"{ENDPOINT}?q={CITY}&APPID={TEMP_API_KEY}"

    weather_json = requests.get(URL).json()
    temperature_in_kelvin = weather_json.get("main", {}).get("temp", None)

    if not temperature_in_kelvin:
        return
    temperature_in_celsius = kelvin_to_celsius(temperature_in_kelvin)

    Moscow_tz = tz.gettz("Europe/Moscow")
    now = datetime.datetime.now(tz=Moscow_tz)

    query = f"INSERT INTO temp(date, temp) VALUES (?, ?)"
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()
    cursor.execute(query, (now, temperature_in_celsius))
    conn.commit()
    cursor.close()


periodic_temperature_to_sqlite()


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
    yesterday_temps = cursor.fetchall()

    if len(yesterday_temps) > 0:
        max_temp = max([db_row[0] for db_row in yesterday_temps])
        conn.commit()
        cursor.close()
        return (yesterday_str, max_temp)
    return


@app.task
def save_max_temperature_to_sqlite(yesterday, max_temp):
    """
    Save the highest temperature for the previous day to the database.
    """
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()

    query_select = f'SELECT date FROM history WHERE date like "%{yesterday}%"'
    cursor.execute(query_select)
    yesterday_temps = cursor.fetchall()

    if len(yesterday_temps) == 0:
        query_insert = f"INSERT INTO history(date, temp) VALUES (?, ?)"
        cursor.execute(query_insert, (yesterday, max_temp))
        query_delete = f'DELETE FROM temp WHERE date like "%{yesterday}%"'
        cursor.execute(query_delete)
        conn.commit()
        cursor.close()


if calculate_max_temperature():
    yesterday, max_temp = calculate_max_temperature()
    save_max_temperature_to_sqlite(yesterday, max_temp)
