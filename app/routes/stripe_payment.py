import os
import traceback

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv

from app.models.stripe_payment_model import CheckoutRequest
from app.database import get_db_connection
from app.verify_token import current_user
import stripe

load_dotenv()

payment_router = APIRouter(prefix="/stripe_payment", tags=["stripe_payment"])

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL")
URL = os.getenv("URL")

stripe.api_key = STRIPE_SECRET_KEY


@payment_router.post("/create-checkout-session")
async def create_checkout_session(
    promo_name: CheckoutRequest,
    payload: dict = Depends(current_user),
):
    """Create Stripe checkout session based on user's cart"""
    try:
        promocode_name = promo_name.promocode
        userid = payload["userid"]

        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ calculate cart total
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

        if total_amount <= 0:
            raise HTTPException(status_code=400, detail="Cart is empty or invalid")

        # ✅ apply promocode if valid
        if promocode_name:
            cur.execute("SELECT value FROM promocodes WHERE name = %s", (promocode_name,))
            promo = cur.fetchone()
            promo_value = promo[0] if promo else 0
            if total_amount >= int(promo_value):
                total_amount -= promo_value

        # ✅ Stripe minimum (50 cents ≈ ₹42–₹45)
        if total_amount < 50:
            # total_amount is in INR, adjust based on your business rule
            raise HTTPException(
                status_code=400,
                detail="Order amount too low for Stripe minimum charge.",
            )

        # ✅ Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {"name": "Smart Gadget Order"},
                        "unit_amount": int(total_amount * 100),  # convert to paise
                    },
                    "quantity": 1,
                }
            ],
            success_url=(
                "http://127.0.0.1:8000/stripe_payment/payment-success"
                f"?session_id={{CHECKOUT_SESSION_ID}}&userid={userid}"
            ),
            cancel_url=f"{FRONTEND_URL}/payment-failed",
        )
        print("*" * 100)
        print(session)

        cur.close()
        
        conn.close()

        print("*" * 80)
        print("FRONTEND_URL:", FRONTEND_URL)
        print("*" * 80)

        return JSONResponse({"url": session.url})

    except Exception as e:
        print("Error creating checkout session:", e)
        raise HTTPException(status_code=500, detail=str(e))


@payment_router.get("/payment-success")
async def payment_success(session_id: str, userid: int):
    """Verify Stripe payment and insert order into DB"""
    try:
        print("Verifying session:", session_id)
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand=["payment_intent"],
        )
        print("Stripe session status:", session.status)

        payment_intent = session.payment_intent
        print("payment status", payment_intent.status)

        # ✅ Check payment status properly
        if not payment_intent or payment_intent.status != "succeeded":
            return RedirectResponse(url=f"{FRONTEND_URL}/payment-failed")

        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ Get cartid
        cur.execute("SELECT cartid FROM cart WHERE userid = %s", (userid,))
        cart_row = cur.fetchone()
        if not cart_row:
            return RedirectResponse(url=f"{FRONTEND_URL}/payment-failed")

        cartid = cart_row[0]

        # ✅ Insert order
        cur.execute(
            """
            INSERT INTO orders(userid, status, amount, stripe_id)
            VALUES (%s, %s, %s, %s)
            RETURNING orderid
            """,
            (userid, "Pending", session.amount_total / 100, session.id),
        )
        orderid = cur.fetchone()[0]

        # ✅ Insert order items
        cur.execute(
            """
            INSERT INTO orderitem (orderid, productid, qty, price)
            SELECT %s, a.productid, a.qty, b.price
            FROM cartitem a
            JOIN product b ON a.productid = b.productid
            WHERE cartid = %s
            """,
            (orderid, cartid),
        )

        # ✅ Clear cart
        cur.execute("DELETE FROM cart WHERE cartid = %s", (cartid,))
        conn.commit()

        cur.close()
        conn.close()

        print(f"✅ Order {orderid} placed for user {userid}")

        return RedirectResponse(url=f"{FRONTEND_URL}/payment-success")

    except Exception as e:
        print("❌ Exception in payment_success:")
        traceback.print_exc()
        return RedirectResponse(url=f"{FRONTEND_URL}/payment-failed")
