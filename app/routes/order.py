from app.database import get_db_connection
from fastapi import APIRouter, HTTPException , Depends
import logging
from app.verify_token import verify_token , oauth2_scheme

order_router = APIRouter(prefix="/order" , tags=['order'])

@order_router.post('')
def oredr_item(token: str = Depends(oauth2_scheme)):
    try:
        paylod = verify_token(token)
        userid = paylod['userid']
        conn = get_db_connection()
        cur = conn.cursor()
        
        # ****************** fetch cartid ******************
        
        cart_q = ("select cartid from cart where userid = %s")
        cur.execute(cart_q , (userid,))
        cart_row = cur.fetchone()
        cartid = cart_row[0]
        
        if cartid:
            order_q = ("INSERT INTO orders(userid, status, amount)VALUES (%s , %s ,%s) returning orderid")
            order_v = (userid , "Pending" ,0)
            cur.execute(order_q , order_v)
            orderid = cur.fetchone()[0]
            conn.commit()
        else:
            return {"error" : "Cart is empty"}
        
        if not orderid:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # ****************** select item from cartitem and insert into orderitem ******************
        
        insert_orderI = ("""   
                            INSERT INTO orderitem (orderid, productid, qty, price)
                            SELECT %s, a.productid, a.qty, b.price
                            FROM cartitem a
                            join product b
                            on a.productid = a.productid
                            WHERE cartid = %s ;
                        """)
        insert_orderV = ( orderid , cartid )
        cur.execute(insert_orderI , insert_orderV)
        conn.commit()
        
        # *****************  update order in amount ******************
        update_order_q = ("""UPDATE orders 
                            SET amount = (
                            SELECT SUM(qty * price) 
                            FROM orderitem 
                            WHERE orderitem.orderid = orders.orderid
                            )
                            WHERE orderid = %s""")
        cur.execute(update_order_q, (orderid,))
        conn.commit()
        return {"message" : "Order placed successfully and Amount is updated"}
    
    except Exception as e:
        logging.error(f"Error place order: {e}")
        return {"error": "Failed to place order"}
    finally:
        cur.close()
        conn.close()
    