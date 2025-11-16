from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.schemas import ProjectCreate, ProjectResponse
from app.database import get_database
from app.routers.dashboard import get_current_user
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new project (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create projects"
        )
    
    database = await get_database()
    projects_collection = database["projects"]
    
    # Check if project name already exists
    existing_project = await projects_collection.find_one({"name": project_data.name})
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists"
        )
    
    # Get the next project ID
    latest_project = await projects_collection.find_one(sort=[("id", -1)])
    next_id = (latest_project["id"] + 1) if latest_project else 1
    
    # Create new project
    new_project = {
        "id": next_id,
        "name": project_data.name,
        "description": project_data.description if project_data.description else "",
        "created_by": current_user["id"],
        "created_at": datetime.utcnow().strftime("%Y-%m-%d")
    }
    
    await projects_collection.insert_one(new_project)
    
    return ProjectResponse(**new_project)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific project by ID"""
    database = await get_database()
    projects_collection = database["projects"]
    
    project = await projects_collection.find_one({"id": project_id})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectResponse(**project)

@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(
    project_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a project (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete projects"
        )
    
    database = await get_database()
    projects_collection = database["projects"]
    bugs_collection = database["bugs"]
    
    # Check if project exists
    project = await projects_collection.find_one({"id": project_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if project has bugs
    bug_count = await bugs_collection.count_documents({"project_id": project_id})
    if bug_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete project. It has {bug_count} bug(s). Please delete or reassign the bugs first."
        )
    
    # Delete the project
    result = await projects_collection.delete_one({"id": project_id})
    
    return {
        "message": f"Project '{project['name']}' deleted successfully",
        "deleted_count": result.deleted_count
    }