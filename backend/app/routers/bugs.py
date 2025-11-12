from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional, List
from app.schemas import BugCreate, BugResponse, BugUpdate
from app.database import get_database
from app.routers.dashboard import get_current_user
from datetime import datetime

router = APIRouter(prefix="/bugs", tags=["Bugs"])

@router.post("/", response_model=BugResponse, status_code=status.HTTP_201_CREATED)
async def create_bug(
    bug_data: BugCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new bug report"""
    database = await get_database()
    bugs_collection = database["bugs"]
    projects_collection = database["projects"]
    
    # Verify project exists
    project = await projects_collection.find_one({"id": bug_data.project_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get the next bug ID
    latest_bug = await bugs_collection.find_one(
        sort=[("id", -1)]
    )
    next_id = (latest_bug["id"] + 1) if latest_bug else 1
    
    # Create new bug
    new_bug = {
        "id": next_id,
        "project_id": bug_data.project_id,
        "project_name": project["name"],
        "title": bug_data.title,
        "description": bug_data.description,
        "status": "Open",
        "priority": bug_data.priority,
        "reported_by": current_user["id"],
        "assigned_to": None,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    await bugs_collection.insert_one(new_bug)
    
    return BugResponse(**new_bug)

@router.get("/{bug_id}", response_model=BugResponse)
async def get_bug(
    bug_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific bug by ID"""
    database = await get_database()
    bugs_collection = database["bugs"]
    
    bug = await bugs_collection.find_one({"id": bug_id})
    
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bug not found"
        )
    
    # Check permissions for users (they can only see their own bugs)
    if current_user["role"] == "user" and bug["reported_by"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this bug"
        )
    
    return BugResponse(**bug)

@router.put("/{bug_id}", response_model=BugResponse)
async def update_bug(
    bug_id: int,
    bug_update: BugUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a bug (status, assignment, etc.)"""
    database = await get_database()
    bugs_collection = database["bugs"]
    
    bug = await bugs_collection.find_one({"id": bug_id})
    
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bug not found"
        )
    
    # Permission checks
    if current_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users cannot update bugs"
        )
    
    # Build update dict
    update_dict = {
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    if bug_update.status is not None:
        update_dict["status"] = bug_update.status
    
    if bug_update.assigned_to is not None:
        update_dict["assigned_to"] = bug_update.assigned_to
    
    if bug_update.priority is not None:
        update_dict["priority"] = bug_update.priority
    
    # Update the bug
    await bugs_collection.update_one(
        {"id": bug_id},
        {"$set": update_dict}
    )
    
    # Get updated bug
    updated_bug = await bugs_collection.find_one({"id": bug_id})
    
    return BugResponse(**updated_bug)

@router.delete("/{bug_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bug(
    bug_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a bug (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete bugs"
        )
    
    database = await get_database()
    bugs_collection = database["bugs"]
    
    result = await bugs_collection.delete_one({"id": bug_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bug not found"
        )
    
    return None