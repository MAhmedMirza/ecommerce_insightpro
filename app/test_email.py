import pyodbc
from app.config import Config

def test_connection():
    try:
        conn = pyodbc.connect(Config.get_connection_string())
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("Connection successful!")
        conn.close()
    except pyodbc.Error as e:
        print(f"Connection failed: {str(e)}")