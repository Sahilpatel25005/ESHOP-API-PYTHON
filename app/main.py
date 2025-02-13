from fastapi import FastAPI , Request
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.routes import login, product, register , cart , order
import uvicorn

app = FastAPI(title="eShop API")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ],
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Change to specific domains in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming {request.method} request: {request.url}")
    if request.method in ['POST', 'PUT', 'DELETE']:
        body = await request.body()
        logging.info(f"Request body: {body.decode('utf-8')}")
    response = await call_next(request)
    logging.info(f"Response status code: {response.status_code}")
    return response 

# Include Routers
app.include_router(login.login_router)
app.include_router(cart.add_cart_router)
app.include_router(product.product)
app.include_router(order.order_router)
app.include_router(register.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1" , port = 8000 , reload=True)
