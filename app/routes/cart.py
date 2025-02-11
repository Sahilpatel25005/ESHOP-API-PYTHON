from app.models import cart
from app.database import get_db_connection
from fastapi import APIRouter, FastAPI , HTTPException
import logging
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ],
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Change to specific domains in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

add_cart_router = APIRouter(prefix= "/cart/add" , tags = ['cart/add'])

@add_cart_router.post('')
def add_to_cart(cart : cart):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query =  ("SELECT * FROM product WHERE id = %s LIMIT 1;")
        value = (cart.productid,)
        cur.execute(query , value)
        product = cur.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        query =  ("SELECT * FROM cart WHERE user_id = %s LIMIT 1")
        value = (cart.userid,)  
        cur.execute(query , value)
        cart = cur.fetchone()
        if not cart:
            query = ("insert into cart (userid) values(%s)")
            value = (cart.userid,)
            


    except Exception as e:
        logging.error(f"Error user login: {e}")
        return {"error": "Failed to register user"}
    finally:
        cur.close()
        conn.close()
    