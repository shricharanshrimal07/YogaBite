
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "yogabite_db")
        )

        print("YogaBite MySQL connected successfully!")
        return connection

    except mysql.connector.Error as error:
        print("MySQL connection error:", error)
        return None
