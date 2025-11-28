from fastapi import  APIRouter , Depends, Query
from app.database import get_db_connection
from app.models.register import register 
from passlib.context import CryptContext
from app.verify_token import current_user 
import logging
import psycopg2


pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")

router = APIRouter( prefix="/register" , tags=['register'])

@router.post('')
def register_user(user: register):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1️⃣ Check if email exists
        cur.execute("SELECT email FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            return {"error": "Email is already registered."}

        # 2️⃣ Check if mobile number exists
        cur.execute("SELECT monumber FROM users WHERE monumber = %s", (user.monumber,))
        if cur.fetchone():
            return {"error": "Mobile number is already registered."}

        # 3️⃣ Validate input lengths
        if len(user.fname.strip()) > 50:
            return {"error": "First name is too long (max 50 characters)."}
        if len(user.lname.strip()) > 50:
            return {"error": "Last name is too long (max 50 characters)."}
        if len(user.email.strip()) > 100:
            return {"error": "Email is too long (max 100 characters)."}
        if len(user.password.strip()) > 72:
            return {"error": "Password is too long (max 72 characters)."}
        if len(user.address.strip()) > 200:
            return {"error": "Address is too long (max 200 characters)."}

        # 4️⃣ Hash password
        password = user.password.strip()
        hashed_password = pwd_context.hash(password)

        # 5️⃣ Insert into DB
        cur.execute(
            """
            INSERT INTO users (fname, lname, email, monumber, password, address)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user.fname.strip(), user.lname.strip(), user.email.strip(),
             user.monumber.strip(), hashed_password, user.address.strip())
        )
        conn.commit()

        return {"message": "✅ User registered successfully!"}

    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return {"error": "Database error occurred. Please try again later."}

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

    finally:
        cur.close()
        conn.close()
        
user_details = APIRouter( prefix="/user_details" , tags=['/user_details'])


@user_details.get('')
def get_user_details(
    payload: dict = Depends(current_user),
    promocode_name: str = Query(None, description="Optional promo code name to check value")
):
    """
    Fetch user details.
    If promocode_name is provided, return its value from promocodes table.
    """
    conn = None
    cur = None

    try:
        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT SUM(a.qty * b.price)
            FROM cartitem a
            JOIN product b ON a.productid = b.productid
            JOIN cart c ON a.cartid = c.cartid
            WHERE c.userid = %s;
            """,
            (userid,),
        )
        total_amount = cur.fetchone()[0] or 0

        # ✅ Fetch user details
        cur.execute("SELECT * FROM users WHERE userid = %s", (userid,))
        user_result = cur.fetchone()

        if not user_result:
            return {"error": "User not found"}

        user_data = {
            "FirstName": user_result[1],
            "LastName": user_result[2],
            "Email": user_result[3],
            "MobileNnumber": user_result[4],
            "Address": user_result[6]
        }

        # ✅ If a promo code name is passed → fetch its value
        if promocode_name:
            cur.execute("SELECT value FROM promocodes WHERE name = %s", (promocode_name,))
            promo = cur.fetchone()

            if promo:
                user_data["promocode_name"] = promocode_name
                user_data["promocode_value"] = promo[0]
            else:
                user_data["promocode_name"] = promocode_name
                user_data["promocode_value"] = "Invalid promo code"

        return {"total_amount": total_amount, "user_detail": user_data}

    except Exception as e:
        logging.error(f"Error in user detail: {e}")
        return {"error": "Failed to get user details"}
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
