import jwt
from fastapi import  HTTPException,APIRouter
from fastapi.security import OAuth2PasswordBearer



SECRET_KEY = "b182763754ef087a53ff3bd4b9f66996b4a5f34748a3f0ad63f397ebed2e1478"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# protected_router = APIRouter(prefix="/protected", tags=['protected'])

# @protected_router.get('')
# async def protected_route(token: str = Depends(oauth2_scheme)):
#     payload = verify_token(token)
#     return {"message": "You are authenticated!", "user": payload}


