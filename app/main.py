from app.Logger_config import logger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
 
from app.routes import login, product, register, cart, order,admin,search, generate_product_details, stripe_payment, promocode
import uvicorn

app = FastAPI(title="eShop API")


# CORS Middleware
origins = [
    "https://fresho-veggies.netlify.app",  # your frontend
    "http://localhost:5173",                # for local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for testing (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming {request.method} request: {request.url}")
    if request.method in ['POST', 'PUT', 'DELETE']:
        body = await request.body()
        try:
            logger.info(f"Request body: {body.decode('utf-8')}")
        except UnicodeDecodeError:
            logger.info("Request body: (binary or non-UTF-8 data)")
    response = await call_next(request)
    logger.info(f"Response status code: {response.status_code}")
    return response



# Include Routers
app.include_router(login.login_router)
app.include_router(admin.admin_router)
app.include_router(admin.admin_add_product)
app.include_router(cart.add_cart_router)
app.include_router(cart.increse_qty_router)
app.include_router(cart.decrese_qty_router)
app.include_router(cart.delete_item_router)
app.include_router(cart.show_cart_item)
app.include_router(product.product)
app.include_router(order.order_router)
app.include_router(order.all_orders)
app.include_router(order.pending_orders)
app.include_router(register.user_details)
app.include_router(register.router)
app.include_router(search.search_router)
app.include_router(generate_product_details.generate_product_details_router)
app.include_router(stripe_payment.payment_router)
app.include_router(promocode.router)



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)