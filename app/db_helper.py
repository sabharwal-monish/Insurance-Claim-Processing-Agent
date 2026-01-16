import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        # PyMySQL uses similar arguments but a different SSL format
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 15215)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl={'ca': os.path.join(os.path.dirname(__file__), 'ca.pem')},
            cursorclass=pymysql.cursors.DictCursor # This makes results act like dictionaries
        )
        return conn
    except Exception as e:
        print(f"❌ Database Connection Failed: {e}")
        return None