from fastapi import FastAPI, Request,APIRouter
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db_connection
from app.models import product_name
import logging

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
    allow_origins=["http://localhost:5173"],  # Allows all origins. Change to specific domains in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

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


product = APIRouter( prefix="/list_product" , tags=['product'])

# API Endpoints
@product.get('')
def list_product():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        logging.info("Fetching all product data.")
        query = "SELECT p.productid, p.name, p.description, p.price, p.image, p.categoryid, c.name AS categoryname FROM public.product p JOIN public.category c ON p.categoryid = c.categoryid order by image "
        cur.execute(query)
        col_names = [desc[0] for desc in cur.description]  # Get column names
        rows = cur.fetchall()
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
        
        
# @product.post('')
# def list_product_by_name(product : product_name):
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
#         query = ("select * from product where name = %s")
#         value = (product.name,)
#         cur.execute(query , value)
#         col_names = [desc[0] for desc in cur.description]  # Get column names
#         rows = cur.fetchall()
#         result = []  # Initialize an empty list
#         for row in rows:
#             row_dict = {}  # Create an empty dictionary for each row
#             for index, col_name in enumerate(col_names):
#                 row_dict[col_name] = row[index]  # Assign values to the dictionary
#             result.append(row_dict)  # Add the dictionary to the result list
#         return result
#     except Exception as e:
#         logging.error(f"Error fetching data: {e}")
#         return {"error": "Failed to fetch videos"}
#     finally:
#         cur.close()
#         conn.close()
        
        
    

    
        

