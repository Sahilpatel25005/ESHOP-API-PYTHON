from pydantic import BaseModel, EmailStr, field_validator, ValidationError

class LoginModel(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        """Custom password validator."""
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one number.")
        if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in value):
            raise ValueError("Password must contain at least one special character.")
        return value

# Example usage:
# try:
#     user = LoginModel(email="test@example.com", password="WeakPass")
# except ValidationError as e:
#     print(e)  # This will show validation errors



class register(BaseModel):
    fname : str
    lname :str
    email : EmailStr
    monumber : str
    password : str
    address : str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        """Custom password validator."""
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one number.")
        if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in value):
            raise ValueError("Password must contain at least one special character.")
        return value

# Example usage:
# try:
#     user = register(email="test@example.com", password="WeakPass")
# except ValidationError as e:
#     print(e)  # Th
    
class cart(BaseModel):
    productid : int
    qty: int
    price : int
    
    
class product_name(BaseModel):
    name : str
    

    
    
    
    