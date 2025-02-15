import psycopg2
import psycopg2.extras
import json

with open("DB.json", "r") as json_file:
    DB_CONFIG = json.load(json_file)

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
    
