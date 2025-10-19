from fastapi import HTTPException,APIRouter,Form,UploadFile
from passlib.context import CryptContext
from app.database import get_db_connection
from app.models.admin_model import AdminModel,admin_insert_product
from app.verify_token import current_user
import logging
import jwt
from datetime import datetime, timezone, timedelta
import os
import shutil


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

# Path to store uploaded product images
UPLOAD_FOLDER = r"C:\REACT PROGRAM\ResponsiveEcommerce\public\products"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

@admin_add_product.post("/")
async def add_product(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    image: UploadFile = None
):
    conn = None
    cur = None
    try:
        # ✅ Validate file extension
        image_filename = None
        if image:
            ext = image.filename.split(".")[-1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail="Invalid image type")
            
            # ✅ Ensure upload folder exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image_filename = image.filename
            save_path = os.path.join(UPLOAD_FOLDER, image_filename)
            
            # ✅ Save file
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        # ✅ Connect to DB
        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ Get category ID
        cur.execute("SELECT categoryid FROM category WHERE name = %s", (category,))
        category_row = cur.fetchone()
        if not category_row:
            raise HTTPException(status_code=400, detail="Category not found")
        category_id = category_row[0]

        # ✅ Insert product
        cur.execute("""
            INSERT INTO product (name, description, price, image, categoryid)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, description, price, image_filename, category_id))
        conn.commit()

        return {"message": "✅ Product added successfully!"}

    except Exception as e:
        logging.error(f"Error adding product: {e}")
        return {"error": str(e)}

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@admin_router.get('/get_all_products')
def get_all_products():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.productid, p.name, p.description, p.price, p.image, 
                   p.categoryid, c.name AS categoryname 
            FROM public.product p 
            JOIN public.category c ON p.categoryid = c.categoryid
            ORDER BY image
        """)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        products = [dict(zip(columns, row)) for row in rows]
        cur.close()
        conn.close()
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@admin_router.delete("/delete_product/{productid}")
def delete_product(productid: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM public.product WHERE productid = %s RETURNING *;", (productid,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if not deleted:
            raise HTTPException(status_code=404, detail="Product not found")

        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))