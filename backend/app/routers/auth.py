from fastapi import APIRouter, HTTPException, status
from app.schemas import UserRegister, UserLogin, Token, UserResponse
from app.database import get_database
from app.utils.auth_helpers import verify_password, get_password_hash, create_access_token
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user"""
    database = await get_database()
    users_collection = database["users"]
    
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = {
        "id": f"{user_data.role}{int(datetime.now().timestamp())}",
        "name": user_data.name,
        "email": user_data.email.lower(),
        "hashed_password": get_password_hash(user_data.password),
        "role": user_data.role,
        "joined_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    await users_collection.insert_one(new_user)
    
    # Return user without password
    return UserResponse(
        id=new_user["id"],
        name=new_user["name"],
        email=new_user["email"],
        role=new_user["role"],
        joined_date=new_user["joined_date"]
    )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user and return JWT token"""
    database = await get_database()
    users_collection = database["users"]
    
    # Find user by email and role
    user = await users_collection.find_one({
        "email": credentials.email.lower(),
        "role": credentials.role
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email, password, or role",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email, password, or role",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["email"], "role": user["role"]})
    
    # Return token and user data
    user_response = UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        joined_date=user["joined_date"]
    )
    
    return Token(
        access_token=access_token,
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str):
    """Get current user from token"""
    from app.utils.auth_helpers import decode_access_token
    
    email = decode_access_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    database = await get_database()
    users_collection = database["users"]
    user = await users_collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        joined_date=user["joined_date"]
    )