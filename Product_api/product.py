from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging
import psycopg2
import psycopg2.extras



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ],
)

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Change to specific domains in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# fileName = 'fast_api.json'

# Define Pydantic Models
class Add_Product(BaseModel):
    productid : int
    name : str
    discription : str
    price : float
    image : str
    categoryid : int
    



# Helper Functions


# Middleware for logging requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming {request.method} request: {request.url}")
    if request.method in ['POST', 'PUT', 'DELETE']:
        body = await request.body()
        logging.info(f"Request body: {body.decode('utf-8')}")
    response = await call_next(request)
    logging.info(f"Response status code: {response.status_code}")
    return response 


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

# API Endpoints
@app.get('/listdata')
def list_product():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        logging.info("Fetching all video data.")
        query = "SELECT p.productid, p.name, p.description, p.price, p.image, p.categoryid, c.name AS categoryname FROM public.product p JOIN public.category c ON p.categoryid = c.categoryid order by image "
        cur.execute(query)
        col_names = [desc[0] for desc in cur.description]  # Get column names
        rows = cur.fetchall()
        # print(rows)
        result = []  # Initialize an empty list
        for row in rows:
            row_dict = {}  # Create an empty dictionary for each row
            for index, col_name in enumerate(col_names):
                row_dict[col_name] = row[index]  # Assign values to the dictionary
            result.append(row_dict)  # Add the dictionary to the result list
        return result
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return {"error": "Failed to fetch videos"}
    finally:
        cur.close()
        conn.close()
    
        

