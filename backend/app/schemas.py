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

class ProjectResponse(BaseModel):
    id: int
    name: str
    created_by: str
    created_at: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Bugify Dashboard",
                "created_by": "admin1",
                "created_at": "2025-09-01"
            }
        }
    }

class BugResponse(BaseModel):
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
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "project_id": 1,
                "project_name": "Bugify Dashboard",
                "title": "Login button not working",
                "description": "Login button doesn't respond",
                "status": "Open",
                "priority": "High",
                "reported_by": "user1",
                "assigned_to": "dev1",
                "created_at": "2025-10-07T10:00:00Z",
                "updated_at": "2025-10-07T10:00:00Z"
            }
        }
    }

class DashboardStats(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int

class BugCreate(BaseModel):
    project_id: int
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    priority: Literal["High", "Medium", "Low"] = "Medium"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": 1,
                "title": "Login button not working",
                "description": "The login button does not respond when clicked on mobile devices",
                "priority": "High"
            }
        }
    }

class BugUpdate(BaseModel):
    status: Optional[Literal["Open", "In Progress", "Resolved", "Closed"]] = None
    assigned_to: Optional[str] = None
    priority: Optional[Literal["High", "Medium", "Low"]] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "In Progress",
                "assigned_to": "dev1",
                "priority": "High"
            }
        }
    }

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Bugify Mobile App",
                "description": "iOS and Android mobile application"
            }
        }
    }

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_by: str
    created_at: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Bugify Dashboard",
                "description": "Main dashboard project",
                "created_by": "admin1",
                "created_at": "2025-09-01"
            }
        }
    }

class BugAssignment(BaseModel):
    assigned_to: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "assigned_to": "dev1"
            }
        }
    }

class BugStatusUpdate(BaseModel):
    status: Literal["Open", "In Progress", "Resolved", "Closed"]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "In Progress"
            }
        }
    }

class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john.doe@bugify.com"
            }
        }
    }

class ProfileResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    joined_date: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "dev1",
                "name": "John Developer",
                "email": "dev1@bugify.com",
                "role": "developer",
                "joined_date": "2025-09-10"
            }
        }
    }

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "oldpass123",
                "new_password": "newpass123",
                "confirm_password": "newpass123"
            }
        }
    }

class ProfileStats(BaseModel):
    bugs_reported: int
    bugs_assigned: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "bugs_reported": 5,
                "bugs_assigned": 8
            }
        }
    }
