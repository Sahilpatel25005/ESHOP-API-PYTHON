from fastapi import APIRouter
from fastapi.responses import JSONResponse
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

# Verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Authenticate user
def authenticate_user(email: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = "SELECT * FROM users WHERE email = %s LIMIT 1"
        cur.execute(query, (email,))
        user = cur.fetchone()
        if not user:
            return {"error": "Email not found."}

        if not verify_password(password, user["password"]):
            return {"error": "Incorrect password."}

        return user
    finally:
        cur.close()
        conn.close()

# Create JWT token
def create_access_token(data: dict):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expiration})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

login_router = APIRouter(prefix="/login", tags=['login'])

# Login endpoint
@login_router.post("/")
def login_user(login: LoginModel):
    user = authenticate_user(login.email, login.password)
    if "error" in user:
        # Return JSON with error key that frontend can directly show
        return JSONResponse(status_code=400, content={"error": user["error"]})

    token = create_access_token({'sub': user['email'], 'userid': user['userid']})
    return {"access_token": token, "token_type": "bearer"}
