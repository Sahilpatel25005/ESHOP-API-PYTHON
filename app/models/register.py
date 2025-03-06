from pydantic import BaseModel, EmailStr, field_validator


class register(BaseModel):
    fname: str
    lname: str
    email: EmailStr
    monumber: str
    password: str
    address: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
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
