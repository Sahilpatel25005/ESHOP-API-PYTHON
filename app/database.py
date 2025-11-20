import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
load_dotenv()

# with open("app/DB.json", "r") as json_file:
#     DB_CONFIG = json.load(json_file)

# Utility function to connect to the database
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("HOST"),
        dbname=os.getenv("DBNAME"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        port=5432,
        cursor_factory=psycopg2.extras.DictCursor,
    )
    
