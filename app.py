import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()
TEMP_API_KEY = os.environ['TEMP_API_KEY']

conn = sqlite3.connect('sqlite.db')
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS temp \
    (id INTEGER PRIMARY KEY AUTOINCREMENT, date timestamp, temp INT);")
cursor.execute("CREATE TABLE IF NOT EXISTS history \
    (id INTEGER PRIMARY KEY AUTOINCREMENT, date timestamp, temp INT);")
