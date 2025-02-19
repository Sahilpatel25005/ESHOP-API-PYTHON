from fastapi import APIRouter , Depends
from app.database import get_db_connection
import logging
from app.verify_token import current_user 
from time import sleep



product = APIRouter( prefix="/list_product" , tags=['product'])

# API Endpoints
@product.get('')
def list_product(payload: str = Depends(current_user)):
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
        logging.error(f"Error fetching product: {e}")
        return {"error": "Failed to fetch product"}
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
        
        
    

    
        

