from fastapi import  APIRouter , Depends
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
        
user_details = APIRouter( prefix="/user_details" , tags=['/user_details'])

@user_details.get('')
def user_detail(payload: str = Depends(current_user)):
    try:
        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()
        exist_user_query = ("select * from users where userid = %s")
        cur.execute(exist_user_query , (userid,))
        result = cur.fetchone()
        return {
            "user_details" : {
                "fname" : result[1],
                "lname" : result[2],
                "email" : result[3],
                "monumber" : result[4],
                "address" : result[6],
            }
        } 

    except Exception as e:
        logging.error(f"Error user login: {e}")
        return {"error": "Failed to register user"}
    finally:
        cur.close()
        conn.close()
        