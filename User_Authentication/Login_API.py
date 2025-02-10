from fastapi import FastAPI, Request,Depends, HTTPException
from pydantic import BaseModel , EmailStr 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timezone , timedelta
import logging
import psycopg2
import psycopg2.extras
from typing import Annotated
 
app = FastAPI()



# Configure logging
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



# Define Pydantic Models
class login(BaseModel):
    email : EmailStr
    password : str

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
    
conn = get_db_connection()
cur = conn.cursor()

secret_key = "b182763754ef087a53ff3bd4b9f66996b4a5f34748a3f0ad63f397ebed2e1478"
algoritham = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")


def login_user(email: str, password: str):
    query = ("SELECT * FROM users WHERE email = %s LIMIT 1")
    cur.execute(query, (email,))
    user = cur.fetchone()
    
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return user 

    
def verify_password(plain_password , hashed_password):
    return pwd_context.verify(plain_password , hashed_password)

def create_token(data:dict):
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    data.update({"exp": expiration})
    return jwt.encode(data, secret_key, algorithm=algoritham)


@app.post('/login')
def login_User(login : login):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        user = login_user(login.email, login.password)
        token = create_token({'sub' : user['email']})
        return {"access_token": token, "token_type": "bearer"}
        
    except Exception as e:
        logging.error(f"Error user login: {e}")
        return {"error": "Invalid Email or Password!!"}
    finally:
        cur.close()
        conn.close()
        
        
async def get_current_active_user(
    current_user: Annotated[login , Depends(login_user)],
):
    if current_user is None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/users/me")
async def read_users_me(current_user: Annotated[login, Depends(get_current_active_user)],):
    return current_user

def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algoritham])
        return {"message": "You are authenticated!", "user": payload["sub"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logging.error(f"Error in protected route: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
        

@app.get("/protected")
async def protected_route(request : Request):
    try:
        token = request.headers.get("Authorization")
        payload =  protected_route(token)
        return payload
    except jwt.ExpiredSignatureError:
        return "Token expired"
    except jwt.InvalidTokenError:
        return "Token invalid"
    except Exception as e:
        logging.error(f"Error in protected route: {e}")
        return "Token 1111"
    
