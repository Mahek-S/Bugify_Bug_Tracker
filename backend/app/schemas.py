from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Literal

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)
    role: Literal["admin", "developer", "user"] = "user"
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john@bugify.com",
                "password": "password123",
                "confirm_password": "password123",
                "role": "developer"
            }
        }
    }

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: Literal["admin", "developer", "user"]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@bugify.com",
                "password": "admin123",
                "role": "admin"
            }
        }
    }

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    joined_date: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "admin1",
                "name": "Sarah Admin",
                "email": "admin@bugify.com",
                "role": "admin",
                "joined_date": "2025-09-01"
            }
        }
    }

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None