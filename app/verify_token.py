import jwt
from fastapi import  HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = "b182763754ef087a53ff3bd4b9f66996b4a5f34748a3f0ad63f397ebed2e1478"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def current_user(token : str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
