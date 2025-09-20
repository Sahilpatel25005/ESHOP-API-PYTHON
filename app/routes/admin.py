from fastapi import HTTPException,APIRouter,Depends
from passlib.context import CryptContext
from app.database import get_db_connection
from app.models.admin_model import AdminModel,admin_insert_product
from app.verify_token import current_user
import logging
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
    query = "SELECT * FROM admin WHERE email = %s LIMIT 1"
    cur.execute(query, (email,))
    user = cur.fetchone()
    
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail={"error" :"Invalid email or password"})
    
    cur.close()
    conn.close()
    return user

# Function to create JWT token
def create_access_token(data: dict):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expiration})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

admin_router = APIRouter(prefix="/admin", tags=['admin'])

# Login API
@admin_router.post('/')
def login_user(admin: AdminModel):
    user = authenticate_user(admin.email, admin.password)
    token = create_access_token({'sub': user['email'] , 'userid' : user['id']})
    return {"access_token": token, "token_type": "bearer"}


# ********************* admin add product **************************

admin_add_product = APIRouter(prefix='/admin_add_product', tags=['admin_add_product'])

@admin_add_product.post('/')
def add_product(admin : admin_insert_product):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("select categoryid from category where name = %s", (admin.category,))
        category_ids = cur.fetchone()
        if not category_ids:
            raise HTTPException(status_code=400, detail="Category not found")
        
        category_id = category_ids[0]
        
        cur.execute("INSERT INTO product (name, description, price , image, categoryid) VALUES (%s, %s, %s, %s, %s)",
                   (admin.name, admin.description,admin.price, admin.image, category_id))
        conn.commit()
        cur.close()
        conn.close()    
        return {"message": "Product added successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"error" :"Token has expired"})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={"error" :"Invalid token"})
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail={"error" :"Invalid token"})
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail={"error" :"Invalid token"})
    except Exception as e:
        logging.error(f"Error adding product: {e}")
        return {"error": "Failed to add product"}
    finally:
        cur.close()
        conn.close()
        
   

