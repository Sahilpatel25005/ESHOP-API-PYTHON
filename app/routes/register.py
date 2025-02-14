from fastapi import  APIRouter
from app.database import get_db_connection
from app.models.register import register 
from passlib.context import CryptContext
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
            hased_password = pwd_context.hash(user.password)
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
        