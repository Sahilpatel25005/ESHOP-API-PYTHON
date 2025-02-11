from fastapi import FastAPI
from app.routes import login, product, register
import uvicorn

app = FastAPI(title="eShop API")

# Include Routers
app.include_router(login.login_router)
app.include_router(login.protected_router)
app.include_router(product.product)
app.include_router(register.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1" , port = 8000 , reload=True)
