from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    hashed_password: str
    role: Literal["admin", "developer", "user"]
    joined_date: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "dev123",
                "name": "John Doe",
                "email": "john@bugify.com",
                "hashed_password": "$2b$12$...",
                "role": "developer",
                "joined_date": "2025-01-15"
            }
        }
    }

class Project(BaseModel):
    id: int
    name: str
    created_by: str
    created_at: str

class Bug(BaseModel):
    id: int
    project_id: int
    project_name: str
    title: str
    description: str
    status: Literal["Open", "In Progress", "Resolved", "Closed"]
    priority: Literal["High", "Medium", "Low"]
    reported_by: str
    assigned_to: Optional[str] = None
    created_at: str
    updated_at: str