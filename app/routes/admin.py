from fastapi import HTTPException,APIRouter,Form,UploadFile
from passlib.context import CryptContext
from app.database import get_db_connection
from app.models.admin_model import AdminModel, UpdateStatusRequest, ProductUpdate
import logging
import jwt
from app.Logger_config import logger
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

# Path to store uploaded product images
# UPLOAD_FOLDER = r"C:\REACT PROGRAM\ResponsiveEcommerce\public\products"
# ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

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
        # image_filename = None
        # if image:
        #     ext = image.filename.split(".")[-1].lower()
        #     if ext not in ALLOWED_EXTENSIONS:
        #         raise HTTPException(status_code=400, detail="Invalid image type")
            
        #     # ✅ Ensure upload folder exists
        #     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        #     image_filename = image.filename
        #     save_path = os.path.join(UPLOAD_FOLDER, image_filename)
            
        #     # ✅ Save file
        #     with open(save_path, "wb") as buffer:
        #         shutil.copyfileobj(image.file, buffer)

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
        """, (name, description, price, image.filename, category_id))
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
        
        cur.execute("SELECT name FROM category")
        categories_row = cur.fetchall()

        if not categories_row:
            raise HTTPException(status_code=500, detail="No categories found in database")

        categories = [row[0] for row in categories_row]
        
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
        return {"categories" : categories,"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@admin_router.put("/update_product/{productid}")
def update_product(productid: int, payload: ProductUpdate):
    """
    Updates: name, description, price, categoryid (resolved from categoryname).
    Does NOT update image.

    Expects payload.categoryname to be a valid category name existing in `category` table.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1) Resolve categoryname -> categoryid
        if not payload.categoryname:
            raise HTTPException(status_code=400, detail="categoryname is required")

        cur.execute("SELECT categoryid, name FROM category WHERE name = %s", (payload.categoryname,))
        cat_row = cur.fetchone()
        if not cat_row:
            # Category not found — return a clear error so frontend can show a message
            raise HTTPException(status_code=400, detail=f"Category '{payload.categoryname}' not found")

        categoryid = cat_row["categoryid"]

        # 2) Update the product (set categoryid, not categoryname)
        cur.execute(
            """
            UPDATE product
            SET name = %s,
                description = %s,
                price = %s,
                categoryid = %s
            WHERE productid = %s
            RETURNING productid, name, description, price, image, categoryid
            """,
            (payload.name, payload.description, payload.price, categoryid, productid),
        )

        updated = cur.fetchone()
        conn.commit()
        cur.close()

        if not updated:
            raise HTTPException(status_code=404, detail="Product not found")

        # Build response: include categoryname as well for convenience
        resp = {
            "productid": updated["productid"],
            "name": updated["name"],
            "description": updated["description"],
            "price": float(updated["price"]),
            "image": updated["image"],
            "categoryid": updated["categoryid"],
            "categoryname": payload.categoryname,  # we resolved this earlier
        }
        return {"message": "Product updated", "product": resp}

    except HTTPException:
        # Re-raise known HTTP exceptions
        raise
    except Exception as e:
        # Log the error if you have logging; return 500 otherwise
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
    

# API Endpoints
@admin_router.get('/get_all_orders')
def product():
    try:   
        conn = get_db_connection()
        cur = conn.cursor()
        logger.info("Fetching all product data.")
        query = ("""
                    SELECT
                        o.OrderId,
                        o.OrderDate,
                        o.Status,
                        o.Amount,
                        ARRAY_AGG(p.Name) AS ProductNames
                    FROM
                        Orders o
                    JOIN
                        OrderItem oi ON o.OrderId = oi.OrderId
                    JOIN
                        Product p ON oi.ProductId = p.ProductId
                    GROUP BY
                        o.OrderId, o.UserId, o.OrderDate, o.Status, o.Amount
                    ORDER BY
                        o.OrderDate DESC
                """)

        cur.execute(query)
        rows = cur.fetchall()
        result = []
        for item in rows:
            result.append({"orderid" : item[0] , "orderdate" : item[1] , "status" : item[2] ,  "amount" : item[3] , "productname" : item[4]  })
            
        # If the order is not i, raise an error
        if not rows:
            return {"error": "order is not found"}
            # raise HTTPException(status_code=404, detail="order not found")
        return {
          "massage" : "order is get successfully.",
          "cartitem" : result
        }
        
    except Exception as e:
        logger.error(f"Error fetching order: {e}")
        return {"error": "Failed to get order"}
    finally:
        cur.close()
        conn.close()


@admin_router.put('/update_order_status')
def update_order_status(req: UpdateStatusRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print('hy')
        logger.info(f"Updating order {req.orderid} status to {req.status}")
        query = """
            UPDATE Orders
            SET Status = %s
            WHERE OrderId = %s
        """
        cur.execute(query, (req.status, req.orderid))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail='Order not found')
        return {"message": "Order status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(status_code=500, detail='Failed to update order status')
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()