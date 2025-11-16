from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from app.schemas import ProfileUpdate, ProfileResponse, PasswordChange, ProfileStats
from app.database import get_database
from app.routers.dashboard import get_current_user
from app.utils.auth_helpers import verify_password, get_password_hash
from datetime import datetime

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get current user's profile"""
    database = await get_database()
    users_collection = database["users"]
    
    user = await users_collection.find_one({"id": current_user["id"]})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return ProfileResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        joined_date=user["joined_date"]
    )

@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_update: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile"""
    database = await get_database()
    users_collection = database["users"]
    
    # Check if new email is already taken by another user
    if profile_update.email:
        existing_user = await users_collection.find_one({
            "email": profile_update.email.lower(),
            "id": {"$ne": current_user["id"]}
        })
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already taken by another user"
            )
    
    # Build update dict
    update_data = {}
    
    if profile_update.name:
        update_data["name"] = profile_update.name
    
    if profile_update.email:
        update_data["email"] = profile_update.email.lower()
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Update user
    await users_collection.update_one(
        {"id": current_user["id"]},
        {"$set": update_data}
    )
    
    # Get updated user
    updated_user = await users_collection.find_one({"id": current_user["id"]})
    
    return ProfileResponse(
        id=updated_user["id"],
        name=updated_user["name"],
        email=updated_user["email"],
        role=updated_user["role"],
        joined_date=updated_user["joined_date"]
    )

@router.put("/me/password")
async def change_password(
    password_change: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change current user's password"""
    database = await get_database()
    users_collection = database["users"]
    
    # Get current user
    user = await users_collection.find_one({"id": current_user["id"]})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_change.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new password is same as current
    if verify_password(password_change.new_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Hash new password
    new_hashed_password = get_password_hash(password_change.new_password)
    
    # Update password
    await users_collection.update_one(
        {"id": current_user["id"]},
        {"$set": {"hashed_password": new_hashed_password}}
    )
    
    return {
        "message": "Password changed successfully"
    }

@router.get("/me/stats", response_model=ProfileStats)
async def get_profile_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get statistics for current user's profile"""
    database = await get_database()
    bugs_collection = database["bugs"]
    
    # Count bugs reported by user
    bugs_reported = await bugs_collection.count_documents({
        "reported_by": current_user["id"]
    })
    
    # Count bugs assigned to user
    bugs_assigned = await bugs_collection.count_documents({
        "assigned_to": current_user["id"]
    })
    
    return ProfileStats(
        bugs_reported=bugs_reported,
        bugs_assigned=bugs_assigned
    )

@router.get("/me/activity")
async def get_recent_activity(
    current_user: dict = Depends(get_current_user),
    limit: int = 5
):
    """Get recent activity for current user"""
    database = await get_database()
    bugs_collection = database["bugs"]
    
    # Get recent bugs where user is reporter or assignee
    query = {
        "$or": [
            {"reported_by": current_user["id"]},
            {"assigned_to": current_user["id"]}
        ]
    }
    
    activities = []
    cursor = bugs_collection.find(query).sort("updated_at", -1).limit(limit)
    
    async for bug in cursor:
        activity_type = "reported" if bug["reported_by"] == current_user["id"] else "assigned"
        
        activities.append({
            "bug_id": bug["id"],
            "title": bug["title"],
            "status": bug["status"],
            "activity_type": activity_type,
            "updated_at": bug["updated_at"]
        })
    
    return activities