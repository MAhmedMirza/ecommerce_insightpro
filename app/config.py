import os
from dotenv import load_dotenv
import urllib.parse
import pyodbc

# Load environment variables from .env file
load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', '99e67fe9014a0678ca8e0166d278b7bee745e63ebc173e1d866a7fb4bb70c9d7')

    # SQL Server Configuration
    DB_SERVER = os.getenv('DB_SERVER', r'AHMEDPROBOOK\SQLEXPRESS')
    DB_NAME = os.getenv('DB_NAME', 'EcommerceInsightPro')
    DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Ahmed@4u4')
    DB_PORT = os.getenv('DB_PORT', '1433')
    DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    DB_CONNECTION_TIMEOUT = int(os.getenv('DB_CONNECTION_TIMEOUT', '30'))
    DB_LOGIN_TIMEOUT = int(os.getenv('DB_LOGIN_TIMEOUT', '10'))

    # Celery Configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

    @classmethod
    def get_connection_string(cls):
        """Build and return the most reliable connection string"""
        connection_options = [
            # Primary connection string with instance name
            (
                f"DRIVER={{{cls.DB_DRIVER}}};"
                f"SERVER={cls.DB_SERVER};"
                f"DATABASE={cls.DB_NAME};"
                f"UID={cls.DB_USERNAME};"
                f"PWD={cls.DB_PASSWORD};"
                "TrustServerCertificate=yes;"
                f"Connection Timeout={cls.DB_CONNECTION_TIMEOUT};"
                f"Login Timeout={cls.DB_LOGIN_TIMEOUT};"
            ),
            # Fallback with port instead of instance name
            (
                f"DRIVER={{{cls.DB_DRIVER}}};"
                f"SERVER={cls.DB_SERVER.split('\\')[0]},{cls.DB_PORT};"
                f"DATABASE={cls.DB_NAME};"
                f"UID={cls.DB_USERNAME};"
                f"PWD={cls.DB_PASSWORD};"
                "TrustServerCertificate=yes;"
                f"Connection Timeout={cls.DB_CONNECTION_TIMEOUT};"
                f"Login Timeout={cls.DB_LOGIN_TIMEOUT};"
            )
        ]
        
        for conn_str in connection_options:
            try:
                with pyodbc.connect(conn_str) as conn:
                    conn.execute("SELECT 1")
                    return conn_str
            except pyodbc.Error as e:
                continue
        
        raise RuntimeError("Could not establish database connection with any connection method")
    CELERY = {
        'broker_url': CELERY_BROKER_URL,
        'result_backend': CELERY_RESULT_BACKEND,
        'task_serializer': 'json',
        'result_serializer': 'json',
        'accept_content': ['json'],
        'timezone': 'UTC',
        'enable_utc': True,
        'worker_send_task_events': True,
        'task_send_sent_event': True,
        'task_track_started': True,
        'task_acks_late': True,
        'worker_prefetch_multiplier': 1,
        'task_create_missing_queues': True,
        'task_default_queue': 'celery',
        'task_always_eager': False,
        'result_extended': True,
        'result_backend_transport_options': {
            'retry_policy': {
                'timeout': 5.0
            }
        }
    }

# Configure SQLAlchemy
Config.SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(Config.get_connection_string())}"
Config.SQLALCHEMY_TRACK_MODIFICATIONS = False
Config.SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 5,
    'max_overflow': 10,
    'pool_timeout': 30,
    'connect_args': {
        'timeout': Config.DB_CONNECTION_TIMEOUT,
        'login_timeout': Config.DB_LOGIN_TIMEOUT
    }
}

