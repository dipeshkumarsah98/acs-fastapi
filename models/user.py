from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegistration(BaseModel):
    fullname: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=16)
    confirm_password: str
    gender: str = Field(..., pattern="^(male|female|other)$")

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "john@example.com",
                "password": "StrongP@ssw0rd123",
                "confirm_password": "StrongP@ssw0rd123",
                "gender": "male"
            }
        } 