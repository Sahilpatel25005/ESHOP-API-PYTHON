from fastapi import FastAPI,Depends, HTTPException,APIRouter
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from app.database import get_db_connection
import jwt
from datetime import datetime, timezone, timedelta
import logging


app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Change to specific domains in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define Pydantic Models
class LoginModel(BaseModel):
    email: EmailStr
    password: str


# JWT Config
SECRET_KEY = "b182763754ef087a53ff3bd4b9f66996b4a5f34748a3f0ad63f397ebed2e1478"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

# Helper function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to authenticate user
def authenticate_user(email: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM users WHERE email = %s LIMIT 1"
    cur.execute(query, (email,))
    user = cur.fetchone()
    
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    cur.close()
    conn.close()
    return user

# Function to create JWT token
def create_access_token(data: dict):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expiration})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

login_router = APIRouter(prefix="/login", tags=['login'])

# Login API
@login_router.post('')
def login_user(login: LoginModel):
    user = authenticate_user(login.email, login.password)
    token = create_access_token({'sub': user['email']})
    return {"access_token": token, "token_type": "bearer"}

# Verify JWT Token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Protected API
protected_router = APIRouter(prefix="/protected", tags=['protected'])

@protected_router.get('')
async def protected_route(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    return {"message": "You are authenticated!", "user": payload}
