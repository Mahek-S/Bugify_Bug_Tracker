from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from app.schemas import BugResponse, BugAssignment, BugStatusUpdate
from app.database import get_database
from app.routers.dashboard import get_current_user
from datetime import datetime

router = APIRouter(prefix="/manage", tags=["Manage"])

@router.get("/bugs", response_model=List[BugResponse])
async def get_all_bugs_for_management(
    project_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all bugs for management (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access bug management"
        )
    
    database = await get_database()
    bugs_collection = database["bugs"]
    
    # Build query
    query = {}
    if project_id:
        query["project_id"] = project_id
    if status_filter and status_filter != "all":
        query["status"] = status_filter
    
    bugs = []
    async for bug in bugs_collection.find(query):
        bugs.append(BugResponse(**bug))
    
    return bugs

@router.put("/bugs/{bug_id}/assign", response_model=BugResponse)
async def assign_bug_to_developer(
    bug_id: int,
    assignment: BugAssignment,
    current_user: dict = Depends(get_current_user)
):
    """Assign a bug to a developer (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign bugs"
        )
    
    database = await get_database()
    bugs_collection = database["bugs"]
    users_collection = database["users"]
    
    # Check if bug exists
    bug = await bugs_collection.find_one({"id": bug_id})
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bug not found"
        )
    
    # Validate developer if assigning (not unassigning)
    if assignment.assigned_to:
        developer = await users_collection.find_one({
            "id": assignment.assigned_to,
            "role": "developer"
        })
        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Developer not found"
            )
    
    # Update bug assignment
    update_data = {
        "assigned_to": assignment.assigned_to,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    await bugs_collection.update_one(
        {"id": bug_id},
        {"$set": update_data}
    )
    
    # Get updated bug
    updated_bug = await bugs_collection.find_one({"id": bug_id})
    
    return BugResponse(**updated_bug)

@router.put("/bugs/{bug_id}/status", response_model=BugResponse)
async def update_bug_status_admin(
    bug_id: int,
    status_update: BugStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update bug status (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update bug status"
        )
    
    database = await get_database()
    bugs_collection = database["bugs"]
    
    bug = await bugs_collection.find_one({"id": bug_id})
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bug not found"
        )
    
    # Update bug status
    update_data = {
        "status": status_update.status,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    await bugs_collection.update_one(
        {"id": bug_id},
        {"$set": update_data}
    )
    
    # Get updated bug
    updated_bug = await bugs_collection.find_one({"id": bug_id})
    
    return BugResponse(**updated_bug)

@router.get("/developers", response_model=List[dict])
async def get_developers(
    current_user: dict = Depends(get_current_user)
):
    """Get all developers (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view developers list"
        )
    
    database = await get_database()
    users_collection = database["users"]
    
    developers = []
    async for user in users_collection.find({"role": "developer"}):
        developers.append({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        })
    
    return developers