from fastapi import HTTPException,APIRouter
from passlib.context import CryptContext
from app.database import get_db_connection
from app.models.login_model import LoginModel
import jwt
from datetime import datetime, timezone, timedelta


# JWT Config
SECRET_KEY = "b182763754ef087a53ff3bd4b9f66996b4a5f34748a3f0ad63f397ebed2e1478"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60



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
    token = create_access_token({'sub': user['email'] , 'userid' : user['userid']})
    return {"access_token": token, "token_type": "bearer"}


