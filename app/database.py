import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "host": "localhost",
    "dbname": "ESHOP",
    "user": "postgres",
    "password": "password",
    "port": 5432,
}

# Utility function to connect to the database
def get_db_connection():
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"],
        cursor_factory=psycopg2.extras.DictCursor,
    )
    
