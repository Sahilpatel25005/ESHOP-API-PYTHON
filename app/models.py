from pydantic import BaseModel , EmailStr

class LoginModel(BaseModel):
    email: EmailStr
    password: str
    
    
class product_name(BaseModel):
    name : str
    
    
class register(BaseModel):
    fname : str
    lname :str
    email : EmailStr
    monumber : int
    password : str
    address : str
    
class cart(BaseModel):
    productid : int
    userid : int
    qty: int
    
    
    
    