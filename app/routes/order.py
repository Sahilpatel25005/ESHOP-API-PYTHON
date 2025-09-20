from app.database import get_db_connection
from fastapi import APIRouter, HTTPException, Depends
from app.verify_token import current_user
from app.Logger_config import logger
import razorpay
from decimal import Decimal

RAZORPAY_KEY_ID = 'rzp_test_xSeVesER0OFBb1'
RAZORPAY_KEY_SECRET = 'UbchyLSqq7AkRKLfga85rUtv'
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

order_router = APIRouter(prefix="/order", tags=['order'])

@order_router.post('')
def order_item(payload: str = Depends(current_user)):
    try:
        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch cartid
        cart_q = "SELECT cartid FROM cart WHERE userid = %s"
        cur.execute(cart_q, (userid,))
        cart_row = cur.fetchone()
        
        if not cart_row:
            return {"error": "Cart is empty"}
        
        cartid = cart_row[0]
        
        # Insert new order
        order_q = """
            INSERT INTO orders(userid, status, amount, razorpay_order_id)
            VALUES (%s, %s, %s, %s) RETURNING orderid
        """
        order_v = (userid, "Pending", 0, None)
        cur.execute(order_q, order_v)
        orderid = cur.fetchone()[0]
        conn.commit()
        
        if not orderid:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Insert order items
        insert_orderI = """
            INSERT INTO orderitem (orderid, productid, qty, price)
            SELECT %s, a.productid, a.qty, b.price
            FROM cartitem a
            JOIN product b ON a.productid = b.productid
            WHERE cartid = %s;
        """
        cur.execute(insert_orderI, (orderid, cartid))
        conn.commit()
        
        # Update order amount
        update_order_q = """
            UPDATE orders 
            SET amount = (
                SELECT SUM(qty * price) 
                FROM orderitem 
                WHERE orderitem.orderid = orders.orderid
            )
            WHERE orderid = %s;
        """
        cur.execute(update_order_q, (orderid,))
        conn.commit()
        
        # Fetch total amount
        cur.execute("SELECT amount FROM orders WHERE orderid = %s", (orderid,))
        total_amount = cur.fetchone()[0]
        
        if isinstance(total_amount, Decimal):
            total_amount = float(total_amount)
        
        # Create Razorpay order
        razorpay_order = client.order.create({
            "amount": int(total_amount * 100),  # amount in paise
            "currency": "INR",
            "payment_capture": 1,
        })
        
        # Update order with Razorpay order ID
        update_razorpay_q = """
            UPDATE orders
            SET razorpay_order_id = %s
            WHERE orderid = %s;
        """
        cur.execute(update_razorpay_q, (razorpay_order["id"], orderid))
        conn.commit()
        
        # Clear cart
        clear_cart_q = "DELETE FROM cart WHERE cartid = %s"
        cur.execute(clear_cart_q, (cartid,))
        conn.commit()
        
        return {
            "message": "Order placed successfully",
            "orderid": orderid,
            "razorpay_order_id": razorpay_order["id"],
            "amount": total_amount,
            "currency": "INR",
        }
    
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return {"error": "Failed to place order"}
    
    finally:
        cur.close()
        conn.close()

        
        
        
# ********************* get all pending order of this user fro order history **************************
        
        
        
pending_orders = APIRouter( prefix="/order/pending_orders" , tags=['/order/pending_orders'])

# API Endpoints
@pending_orders.get('')
def product(payload: str = Depends(current_user)):
    try:
        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()
        logger.info("Fetching all product data.")
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
        logger.error(f"Error fetching order: {e}")
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
        logger.info("Fetching all product data.")
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
        logger.error(f"Error fetching order: {e}")
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
#         logger.info("Fetching all product data.")
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
#         logger.error(f"Error fetching data: {e}")
#         return {"error": "Failed to fetch videos"}
#     finally:
#         cur.close()
#         conn.close()
        
        
    