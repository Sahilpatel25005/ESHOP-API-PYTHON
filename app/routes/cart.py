from app.models import cart
from app.database import get_db_connection
from fastapi import APIRouter, HTTPException , Depends
import logging
from app.verify_token import verify_token , oauth2_scheme


add_cart_router = APIRouter(prefix= "/cart/add" , tags = ['cart/add'])

@add_cart_router.post('')
def add_to_cart(cart : cart , token: str = Depends(oauth2_scheme)):   
    try:
        paylod = verify_token(token)
        userid = paylod['userid']
        conn = get_db_connection()
        cur = conn.cursor()
        query =  ("SELECT * FROM product WHERE productid = %s LIMIT 1;")
        cur.execute(query , (cart.productid,))
        product = cur.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        query =  ("SELECT * FROM cart WHERE userid = %s LIMIT 1")
        cur.execute(query , (userid,))
        cart_data = cur.fetchone()
        
        if not cart_data:
            insert_query = "insert into cart (userid) values(%s)"
            cur.execute(insert_query, (userid,))
            conn.commit()
        
        query = ("select * from cartitem where productid = %s")
        cur.execute(query ,(cart.productid,))
        cart_item = cur.fetchone()
        
        query = ("select cartid from cart where userid = %s")
        cur.execute(query ,(userid,))
        cart_row = cur.fetchone()
        cartid = cart_row[0]
        
        if cart_item:
            update_q = ("update cartitem set qty = qty + 1 where cartid = %s and productid = %s")
            update_v = (cartid , cart.productid)
            cur.execute(update_q , update_v)
            conn.commit()
        else:
            insert_q = ("insert into cartitem (cartid , productid , qty) values(%s , %s , %s)")
            insert_v = (cartid , cart.productid , 1)
            cur.execute(insert_q , insert_v)
            conn.commit()
            
        return {"message" : "product added to cart"}
            
    except Exception as e:
        logging.error(f"Error add item: {e}")
        return {"error": "Failed to add item"}
    finally:
        cur.close()
        conn.close()
    