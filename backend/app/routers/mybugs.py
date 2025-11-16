from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from app.schemas import BugResponse, BugStatusUpdate
from app.database import get_database
from app.routers.dashboard import get_current_user
from datetime import datetime

router = APIRouter(prefix="/mybugs", tags=["MyBugs"])

@router.get("/", response_model=List[BugResponse])
async def get_my_bugs(
    project_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get bugs assigned to current developer"""
    # Only developers can access this endpoint
    if current_user["role"] != "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only developers can access their assigned bugs"
        )
    
    database = await get_database()
    bugs_collection = database["bugs"]
    
    # Build query - only bugs assigned to current user
    query = {"assigned_to": current_user["id"]}
    
    if project_id:
        query["project_id"] = project_id
    
    if status_filter and status_filter != "all":
        query["status"] = status_filter
    
    bugs = []
    async for bug in bugs_collection.find(query):
        bugs.append(BugResponse(**bug))
    
    return bugs

@router.get("/stats")
async def get_my_bugs_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get statistics for bugs assigned to current developer"""
    if current_user["role"] != "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only developers can access their bug statistics"
        )
    
    database = await get_database()
    bugs_collection = database["bugs"]
    
    # Query for bugs assigned to current user
    query = {"assigned_to": current_user["id"]}
    
    total = await bugs_collection.count_documents(query)
    open_bugs = await bugs_collection.count_documents({**query, "status": "Open"})
    in_progress = await bugs_collection.count_documents({**query, "status": "In Progress"})
    resolved = await bugs_collection.count_documents({**query, "status": "Resolved"})
    closed = await bugs_collection.count_documents({**query, "status": "Closed"})
    
    return {
        "total": total,
        "open": open_bugs,
        "in_progress": in_progress,
        "resolved": resolved,
        "closed": closed
    }

@router.put("/{bug_id}/status", response_model=BugResponse)
async def update_my_bug_status(
    bug_id: int,
    status_update: BugStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update status of a bug assigned to current developer"""
    if current_user["role"] != "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only developers can update bug status"
        )
    
    database = await get_database()
    bugs_collection = database["bugs"]
    
    # Check if bug exists and is assigned to current user
    bug = await bugs_collection.find_one({
        "id": bug_id,
        "assigned_to": current_user["id"]
    })
    
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bug not found or not assigned to you"
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

@router.get("/projects", response_model=List[dict])
async def get_my_projects(
    current_user: dict = Depends(get_current_user)
):
    """Get list of projects that have bugs assigned to current developer"""
    if current_user["role"] != "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only developers can access this endpoint"
        )
    
    database = await get_database()
    bugs_collection = database["bugs"]
    projects_collection = database["projects"]
    
    # Get unique project IDs from bugs assigned to current user
    pipeline = [
        {"$match": {"assigned_to": current_user["id"]}},
        {"$group": {"_id": "$project_id"}},
        {"$project": {"project_id": "$_id", "_id": 0}}
    ]
    
    project_ids = []
    async for doc in bugs_collection.aggregate(pipeline):
        project_ids.append(doc["project_id"])
    
    # Get project details
    projects = []
    async for project in projects_collection.find({"id": {"$in": project_ids}}):
        projects.append({
            "id": project["id"],
            "name": project["name"]
        })
    
    return projects