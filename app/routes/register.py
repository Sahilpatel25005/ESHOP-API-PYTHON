from fastapi import  APIRouter , Depends, Query
from app.database import get_db_connection
from app.models.register import register 
from passlib.context import CryptContext
from app.verify_token import current_user 
import logging


pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")

router = APIRouter( prefix="/register" , tags=['register'])

@router.post('')
def register_user(user : register):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        exist_user_query = ("select email from users where email = %s")
        cur.execute(exist_user_query , (user.email,))
        exist_user = cur.fetchone()
        if exist_user:
            return {"error" : "Email is already reagister."}
        else:
            password = user.password.strip()  # remove spaces/newlines

            # bcrypt supports up to 72 bytes; normal 10-char passwords are fine
            if len(password.encode("utf-8")) > 72:
                password = password[:72]  # truncate only if user somehow sends huge input
            hased_password = pwd_context.hash(password)
            query = ("insert into users (fname, lname, email, monumber, password, address) values(%s , %s , %s , %s ,%s , %s)")
            value = (user.fname , user.lname , user.email , user.monumber , hased_password , user.address,)
            cur.execute(query , value)
            conn.commit()
            return {"massage" : "User Register Successfully"} 

    except Exception as e:
        logging.error(f"Error user login: {e}")
        return {"error": "Failed to register user"}
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

        # ✅ Fetch user details
        cur.execute("SELECT * FROM users WHERE userid = %s", (userid,))
        user_result = cur.fetchone()

        if not user_result:
            return {"error": "User not found"}

        user_data = {
            "fname": user_result[1],
            "lname": user_result[2],
            "email": user_result[3],
            "monumber": user_result[4],
            "address": user_result[6]
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

        return {"user_detail": user_data}

    except Exception as e:
        logging.error(f"Error in user detail: {e}")
        return {"error": "Failed to get user details"}
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
