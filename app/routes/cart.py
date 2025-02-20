from app.database import get_db_connection
from app.models.cart_model import cart
from fastapi import APIRouter, HTTPException , Depends
import logging
from app.verify_token import current_user 



add_cart_router = APIRouter(prefix= "/cart/add" , tags = ['cart/add'])

@add_cart_router.post('')
def add_to_cart(cart : cart , payload: str = Depends(current_user)):   
    try:
        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()
        query =  ("SELECT * FROM product WHERE productid = %s LIMIT 1;")
        cur.execute(query , (cart.productid,))
        product = cur.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        
        # create cart
        query = ("""
                WITH cart AS (
                    SELECT cartid FROM cart WHERE userid = %s
                ), 
                insertcart AS (
                    INSERT INTO cart (userid)
                    SELECT %s
                    WHERE NOT EXISTS (SELECT 1 FROM cart)
                    RETURNING cartid
                )
                SELECT * FROM cart
                UNION ALL
                SELECT * FROM insertcart; 
                """)
           
        cur.execute(query, (userid, userid))
        cartid_result = cur.fetchone()
        if not cartid_result:
            raise HTTPException(status_code=500, detail="Failed to create cart")
        cartid = cartid_result[0]

    # insert in cartitem or update    
        
        q =  (""" WITH updated AS (
                        UPDATE cartitem
                        SET qty = cartitem.qty + 1
                        WHERE cartid = %s AND productid = %s
                        RETURNING *
                        ), insertrow AS (
                        INSERT INTO cartitem (cartid, productid , qty)
                        SELECT %s, %s , 1
                        WHERE NOT EXISTS (SELECT 1 FROM updated)
                        RETURNING *
                        )
                        SELECT * FROM updated
                        UNION ALL
                        SELECT * FROM insertrow;
                            """)
        value = (cartid , cart.productid , cartid, cart.productid )
        cur.execute(q , value)
        cartitem = cur.fetchone()
        conn.commit()
        return {"message" : "product added to cart" , "data" : {
            "cartid": cartitem[1],
            "productid": cartitem[2],
            "qty": cartitem[3]
            
        }}
            
    except Exception as e:
        logging.error(f"Error add item: {e}")
        return {"error": "Failed to add item"}
    finally:
        cur.close()
        conn.close()
    
    
#******************************************* increse qty *******************************************
    
    

increse_qty_router = APIRouter(prefix= "/cart/increse" , tags = ['cart/increse'])

@increse_qty_router.post('')
def increse(cart : cart , payload: str = Depends(current_user)):   
    try:

        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()

        logging.info("Fetching cart ID for user.")
        q = "SELECT cartid FROM cart WHERE userid = %s"
        cur.execute(q, (userid,))
        result = cur.fetchone()

        # If the user doesn't have a cart, raise an error
        if not result:
            raise HTTPException(status_code=404, detail="Cart not found for the user")
        cartid = result[0]

        logging.info("Checking if product exists in cart.")
        check_query = "SELECT * FROM cartitem WHERE cartid = %s AND productid = %s"
        cur.execute(check_query, (cartid, cart.productid))
        row = cur.fetchone()

        # If the product is not in the cart, raise an error
        if not row:
            raise HTTPException(status_code=404, detail="Product not found in cart")

        # Increase the quantity by 1
        logging.info("Increasing the quantity of the product in the cart.")
        update_query = ("""
        UPDATE cartitem
        SET qty = qty + 1
        WHERE cartid = %s AND productid = %s
        RETURNING cartid, productid, qty;
        """)
        cur.execute(update_query, (cartid, cart.productid))
        updated_item = cur.fetchone()
        conn.commit()

        return {
            "message": "Quantity increased",
            "cart_item": {
                "cartid": updated_item[0],
                "productid": updated_item[1],
                "qty": updated_item[2]
            }
        }
    except Exception as e:
        logging.error(f"Error increse item: {e}")
        return {"error": "Failed to increse item"}
    finally:
        cur.close()
        conn.close()



#******************************************* decrese qty *******************************************


        
decrese_qty_router = APIRouter(prefix= "/cart/decrese" , tags = ['cart/decrese'])

@decrese_qty_router.post('')
def decrese(cart : cart , payload: str = Depends(current_user)):   
    try:
        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()

        logging.info("Fetching cart ID for user.")
        q = "SELECT cartid FROM cart WHERE userid = %s"
        cur.execute(q, (userid,))
        result = cur.fetchone()

        # If the user doesn't have a cart, raise an error
        if not result:
            raise HTTPException(status_code=404, detail="Cart not found for the user")
        cartid = result[0]

        logging.info("Checking if product exists in cart.")
        check_query = "SELECT * FROM cartitem WHERE cartid = %s AND productid = %s"
        cur.execute(check_query, (cartid, cart.productid))
        row = cur.fetchone()

        # If the product is not in the cart, raise an error
        if not row:
            raise HTTPException(status_code=404, detail="Product not found in cart")

        # decrease the quantity by 1
        logging.info("Decreasing the quantity of the product in the cart.")
        update_query = ("""
        UPDATE cartitem
        SET qty = qty - 1
        WHERE cartid = %s AND productid = %s
        RETURNING cartid, productid, qty;
        """)
        cur.execute(update_query, (cartid, cart.productid))
        updated_item = cur.fetchone()
        conn.commit()

        return {
            "message": "Quantity decreased",
            "cart_item": {
                "cartid": updated_item[0],
                "productid": updated_item[1],
                "qty": updated_item[2]
            }
        }
            
    except Exception as e:
        logging.error(f"Error decrese item: {e}")
        return {"error": "Failed to decrese item"}
    finally:
        cur.close()
        conn.close()
        
        
        
#******************************************* delete item*******************************************
        
        
        
        
delete_item_router = APIRouter(prefix= "/cart/delete" , tags = ['cart/delete'])

@delete_item_router.delete('')
def delete(cart : cart , payload: str = Depends(current_user)):   
    try:
        userid = payload['userid']
        conn = get_db_connection()
        cur = conn.cursor()

        logging.info("Fetching cart ID for user.")
        q = "SELECT cartid FROM cart WHERE userid = %s"
        cur.execute(q, (userid,))
        result = cur.fetchone()

        # If the user doesn't have a cart, raise an error
        if not result:
            return {"error": "User does not have a cart"}
            # raise HTTPException(status_code=404, detail="Cart not found for the user")
        cartid = result[0]
       
        

        logging.info("Checking if product exists in cart.")
        check_query = "SELECT * FROM cartitem WHERE cartid = %s AND productid = %s"
        cur.execute(check_query, (cartid, cart.productid))
        row = cur.fetchone()

        # If the product is not in the cart, raise an error
        if not row:
            return {"error": "Product not found in cart"}
            # raise HTTPException(status_code=404, detail="Product not found in cart")
       

        # delete item
        logging.info("Deleting the product in the cart.")
        delete_query = ("""
        delete from cartitem
        WHERE cartid = %s AND productid = %s
        """)
        cur.execute(delete_query, (cartid, cart.productid))
        conn.commit()

        return {
            "delete_item" : {
                "productid" :  cart.productid
            },
            "message": "Item is delete successfully!!",
        }
            
    except Exception as e:
        logging.error(f"Error delete item: {e}")
        return {"error": "Failed to delete item"}
    finally:
        cur.close()
        conn.close()
        
        
        
#******************************************* show cart item *******************************************#
        
        
        
        
show_cart_item = APIRouter(prefix= "/cart/cart_item" , tags = ['cart/cart_item'])

@show_cart_item.get('')
def item(payload: dict = Depends(current_user)):   
    try:
        userid = payload['userid']
        logging.info(f"Fetching cart items for user ID: {userid}")
        conn = get_db_connection()
        cur = conn.cursor()

        logging.info("Fetching cart ID for user.")
        q = "SELECT cartid FROM cart WHERE userid = %s"
        cur.execute(q, (userid,))
        result = cur.fetchone()
        
        if not result:
            return {"massage" : " Cart is empty!!"}
        cartid = result[0]

        logging.info("Checking if product exists in cart.")
        check_query = ("SELECT c.* , p.name,p.image , p.price FROM cartitem as c join product as p on c.productid = p.productid where cartid = %s ")
        cur.execute(check_query, (cartid,))
        row = cur.fetchall()
        result = []
        for item in row:
            result.append({"cartitemid" : item[0] , "cartid" : item[1] , "productid" : item[2] , "qty" : item[3] , "name" : item[4] , "image" : item[5] , "price" : item[6]  })
            
        # If the product is not in the cart, raise an error
        if not row:
            return {"error": "Cart is not found"}
            # raise HTTPException(status_code=404, detail="Product not found in cart")
            
        return {
          "massage" : "Cart item is get successfully.",
          "cartitem" : result
        }
            
    except Exception as e:
        logging.error(f"Error get item: {e}")
        return {"error": "Failed to fetch item"}
    finally:
        cur.close()
        conn.close()