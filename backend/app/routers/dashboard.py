from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
from app.schemas import UserResponse, BugResponse, ProjectResponse
from app.database import get_database
from app.utils.auth_helpers import decode_access_token

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

async def get_current_user(authorization: str = Header(None)) -> dict:
    """Dependency to get current user from token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    email = decode_access_token(token)
    
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    database = await get_database()
    user = await database["users"].find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (for displaying reported_by and assigned_to names)"""
    database = await get_database()
    users_collection = database["users"]
    
    users = []
    async for user in users_collection.find():
        users.append(UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            role=user["role"],
            joined_date=user["joined_date"]
        ))
    
    return users

@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(current_user: dict = Depends(get_current_user)):
    """Get all projects based on user role"""
    database = await get_database()
    projects_collection = database["projects"]
    
    projects = []
    async for project in projects_collection.find():
        projects.append(ProjectResponse(
            id=project["id"],
            name=project["name"],
            created_by=project["created_by"],
            created_at=project["created_at"]
        ))
    
    return projects

@router.get("/bugs", response_model=List[BugResponse])
async def get_bugs(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get bugs based on filters and user role"""
    database = await get_database()
    bugs_collection = database["bugs"]
    
    # Build query based on filters
    query = {}
    
    if project_id:
        query["project_id"] = project_id
    
    if status and status != "all":
        query["status"] = status
    
    # Filter based on user role
    if current_user["role"] == "user":
        # Users only see bugs they reported
        query["reported_by"] = current_user["id"]
    # Admin and developer see all bugs (no additional filter needed)
    
    bugs = []
    async for bug in bugs_collection.find(query):
        bugs.append(BugResponse(
            id=bug["id"],
            project_id=bug["project_id"],
            project_name=bug["project_name"],
            title=bug["title"],
            description=bug["description"],
            status=bug["status"],
            priority=bug["priority"],
            reported_by=bug["reported_by"],
            assigned_to=bug.get("assigned_to"),
            created_at=bug["created_at"],
            updated_at=bug["updated_at"]
        ))
    
    return bugs

@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics"""
    database = await get_database()
    bugs_collection = database["bugs"]
    
    # Build query based on user role
    query = {}
    if current_user["role"] == "user":
        query["reported_by"] = current_user["id"]
    
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