import pytest
from httpx import AsyncClient
from app.main import app

pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="function", autouse=True)
async def setup_test_db():
    """Setup test database once for all tests"""
    from app.database import connect_to_mongo, close_mongo_connection, init_default_data, get_database
    
    await connect_to_mongo()
    
    database = await get_database()
    await database["users"].delete_many({})
    await database["projects"].delete_many({})
    await database["bugs"].delete_many({})
    await init_default_data()
    
    yield
    
    await close_mongo_connection()

@pytest.mark.asyncio
async def test_create_project_as_admin(setup_test_db):
    """Test creating a project as admin"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as admin
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Create project
        project_data = {
            "name": "Test Project",
            "description": "This is a test project"
        }
        
        response = await client.post(
            "/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        project = response.json()
        assert project["name"] == "Test Project"
        assert project["created_by"] == "admin1"

@pytest.mark.asyncio
async def test_create_project_duplicate_name(setup_test_db):
    """Test creating project with duplicate name"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        project_data = {
            "name": "Bugify Dashboard",  # Already exists
            "description": "Duplicate"
        }
        
        response = await client.post(
            "/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_project_as_non_admin(setup_test_db):
    """Test that non-admins cannot create projects"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        project_data = {
            "name": "Unauthorized Project",
            "description": "Should fail"
        }
        
        response = await client.post(
            "/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_empty_project(setup_test_db):
    """Test deleting a project with no bugs"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as admin
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Create a project to delete
        project_data = {
            "name": "Project To Delete",
            "description": "Will be deleted"
        }
        
        create_response = await client.post(
            "/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        project_id = create_response.json()["id"]
        
        # Delete the project
        response = await client.delete(
            f"/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

@pytest.mark.asyncio
async def test_delete_project_with_bugs(setup_test_db):
    """Test that projects with bugs cannot be deleted"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Try to delete project 1 (has bugs from init_default_data)
        response = await client.delete(
            "/projects/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "bug" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_get_all_bugs_for_management(setup_test_db):
    """Test getting all bugs for management"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        response = await client.get(
            "/manage/bugs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bugs = response.json()
        assert isinstance(bugs, list)

@pytest.mark.asyncio
async def test_assign_bug_to_developer(setup_test_db):
    """Test assigning a bug to a developer"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        assignment_data = {
            "assigned_to": "dev1"
        }
        
        response = await client.put(
            "/manage/bugs/1/assign",
            json=assignment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bug = response.json()
        assert bug["assigned_to"] == "dev1"

@pytest.mark.asyncio
async def test_unassign_bug(setup_test_db):
    """Test unassigning a bug"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        assignment_data = {
            "assigned_to": None
        }
        
        response = await client.put(
            "/manage/bugs/1/assign",
            json=assignment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bug = response.json()
        assert bug["assigned_to"] is None

@pytest.mark.asyncio
async def test_update_bug_status_as_admin(setup_test_db):
    """Test updating bug status as admin"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        status_data = {
            "status": "Resolved"
        }
        
        response = await client.put(
            "/manage/bugs/1/status",
            json=status_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bug = response.json()
        assert bug["status"] == "Resolved"

@pytest.mark.asyncio
async def test_non_admin_cannot_manage(setup_test_db):
    """Test that non-admins cannot access management endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        response = await client.get(
            "/manage/bugs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_developers_list(setup_test_db):
    """Test getting list of developers"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        response = await client.get(
            "/manage/developers",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        developers = response.json()
        assert len(developers) > 0
        assert all("name" in dev for dev in developers)

@pytest.mark.asyncio
async def test_assign_bug_to_invalid_developer(setup_test_db):
    """Test assigning bug to non-existent developer"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        assignment_data = {
            "assigned_to": "invalid_dev_id"
        }
        
        response = await client.put(
            "/manage/bugs/1/assign",
            json=assignment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "Developer not found" in response.json()["detail"]