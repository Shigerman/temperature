import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()
TEMP_API_KEY = os.environ['TEMP_API_KEY']


conn = sqlite3.connect('sqlite.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS temp \
    (date DATETIME DEFAULT CURRENT_TIMESTAMP, temp INT);")
cursor.execute("CREATE TABLE IF NOT EXISTS history \
    (date DATETIME DEFAULT CURRENT_TIMESTAMP, temp INT);")
