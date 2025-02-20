from app.database import get_db_connection
from fastapi import APIRouter, HTTPException , Depends
import logging
from app.verify_token import current_user 


order_router = APIRouter(prefix="/order" , tags=['order'])

@order_router.post('')
def oredr_item(payload: str = Depends(current_user)):
    try:
        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()
        
        # ****************** fetch cartid ******************
        
        cart_q = ("select cartid from cart where userid = %s")
        cur.execute(cart_q , (userid,))
        cart_row = cur.fetchone()
        cartid = cart_row[0]
        
        if cartid == None:
            return {"error" : "Cart is empty"}
        else:
            order_q = ("INSERT INTO orders(userid, status, amount)VALUES (%s , %s ,%s) returning orderid")
            order_v = (userid , "Pending" ,0)
            cur.execute(order_q , order_v)
            orderid = cur.fetchone()[0]
            conn.commit()
        
        if not orderid:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # ****************** select item from cartitem and insert into orderitem ******************
        
        insert_orderI = ("""   
                            INSERT INTO orderitem (orderid, productid, qty, price)
                            SELECT %s, a.productid, a.qty, b.price
                            FROM cartitem a
                            join product b
                            on a.productid = b.productid
                            WHERE cartid = %s ;
                        """)
        insert_orderV = ( orderid , cartid )
        cur.execute(insert_orderI , insert_orderV)
        conn.commit()
        
        # *****************  update order in amount ******************
        update_order_q = ("""
                          UPDATE orders 
                            SET amount = (
                            SELECT SUM(qty * price) 
                            FROM orderitem 
                            WHERE orderitem.orderid = orders.orderid
                            )
                            WHERE orderid = %s""")
        cur.execute(update_order_q, (orderid,))
        conn.commit()
        
        clear_cart_q = ("delete from cart where cartid = %s")
        cur.execute(clear_cart_q, (cartid,))
        conn.commit()
        
        return {"message" : "Order placed successfully and Amount is updated"
                
                }
    
    except Exception as e:
        logging.error(f"Error place order: {e}")
        return {"error": "Failed to place order"}
    finally:
        cur.close()
        conn.close()
        
        
        
pending_orders = APIRouter( prefix="/order/pending_orders" , tags=['/order/pending_orders'])

# API Endpoints
@pending_orders.get('')
def product(payload: str = Depends(current_user)):
    try:
        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()
        logging.info("Fetching all product data.")
        query = (""" SELECT
                    o.OrderId,
                    o.OrderDate,
                    o.Status,
                    o.Amount,   
                    ARRAY_AGG(p.Name) as ProductNames
                FROM
                    Orders o
                JOIN
                    OrderItem oi ON o.OrderId = oi.OrderId
                JOIN
                    Product p ON oi.ProductId = p.ProductId
                where o.UserId = %s and o.Status = 'Pending'
                GROUP BY
                    o.OrderId, o.UserId, o.OrderDate, o.Status, o.Amount
                order by
                    o.OrderDate desc
                    """)
        cur.execute(query , (userid,))
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
        logging.error(f"Error fetching order: {e}")
        return {"error": "Failed to get order"}
    finally:
        cur.close()
        conn.close()
        
        

# ********************* get all order of this user fro order history **************************

all_orders = APIRouter( prefix="/order/all_orders" , tags=['/order/all_orders'])

# API Endpoints
@all_orders.get('')
def product(payload: str = Depends(current_user)):
    try:
        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()
        logging.info("Fetching all product data.")
        query = (""" SELECT
                    o.OrderId,
                    o.OrderDate,
                    o.Status,
                    o.Amount,
                    ARRAY_AGG(p.Name) as ProductNames
                FROM
                    Orders o
                JOIN
                    OrderItem oi ON o.OrderId = oi.OrderId
                JOIN
                    Product p ON oi.ProductId = p.ProductId
                where o.UserId = %s 
                GROUP BY
                    o.OrderId, o.UserId, o.OrderDate, o.Status, o.Amount
                order by
                    o.OrderDate desc
                    """)
        cur.execute(query , (userid,))
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
        logging.error(f"Error fetching order: {e}")
        return {"error": "Failed to get order"}
    finally:
        cur.close()
        conn.close()
        
        
# product = APIRouter( prefix="/order/get_order" , tags=['/order/get_order'])

# # API Endpoints
# @product.get('')
# def product(payload: str = Depends(current_user)):
#     try:
#         userid = payload['userid']
#         conn = get_db_connection()
#         cur = conn.cursor()
#         logging.info("Fetching all product data.")
#         query = "SELECT * from orderitem where userid = %s "
#         cur.execute(query , (userid,))
#         rows = cur.fetchall()
#         result = []
#         for item in rows:
#             result.append({"cartitemid" : item[0] , "cartid" : item[1] , "productid" : item[2] , "qty" : item[3] , "name" : item[4]  })
            
#         # If the product is not in the cart, raise an error
#         if not rows:
#             return {"error": "Cart is not found"}
#             # raise HTTPException(status_code=404, detail="Product not found in cart")
            
#         return {
#           "massage" : "Cart item is get successfully.",
#           "cartitem" : result
#         }
        
#     except Exception as e:
#         logging.error(f"Error fetching data: {e}")
#         return {"error": "Failed to fetch videos"}
#     finally:
#         cur.close()
#         conn.close()
        
        
    