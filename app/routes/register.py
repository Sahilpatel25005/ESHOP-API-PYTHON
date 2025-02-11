from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request,Depends, APIRouter
from app.database import get_db_connection
from app.models import register
import logging
from passlib.context import CryptContext

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


pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")

router = APIRouter( prefix="/register" , tags=['register'])

@router.post('')
def register_user(user : register):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        exist_user_query = ("select email from users where email = %s")
        cur.execute(exist_user_query , (user.email,))
        exist_user = cur.fetchone()
        if exist_user:
            return {"error" : "Email is already reagister."}
        else:
            hased_password = pwd_context.hash(user.password)
            query = ("insert into users (fname, lname, email, monumber, password, address) values(%s , %s , %s , %s ,%s , %s)")
            value = (user.fname , user.lname , user.email , user.monumber , hased_password , user.address,)
            cur.execute(query , value)
            conn.commit()
            return {"massage" : "User Register Successfully"} 

    except Exception as e:
        logging.error(f"Error user login: {e}")
        return {"error": "Failed to register user"}
    finally:
        cur.close()
        conn.close()
        