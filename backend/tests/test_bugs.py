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
async def test_create_bug_as_user(setup_test_db):
    """Test creating a bug as a regular user"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as user
        login_response = await client.post("/auth/login", json={
            "email": "user@bugify.com",
            "password": "user123",
            "role": "user"
        })
        token = login_response.json()["access_token"]
        
        # Create bug
        bug_data = {
            "project_id": 1,
            "title": "Test bug from user",
            "description": "This is a test bug description that is long enough to pass validation",
            "priority": "High"
        }
        
        response = await client.post(
            "/bugs/",
            json=bug_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        bug = response.json()
        assert bug["title"] == bug_data["title"]
        assert bug["status"] == "Open"
        assert bug["reported_by"] == "user1"
        assert bug["assigned_to"] is None

@pytest.mark.asyncio
async def test_create_bug_as_developer(setup_test_db):
    """Test creating a bug as a developer"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Create bug
        bug_data = {
            "project_id": 2,
            "title": "Test bug from developer",
            "description": "This is another test bug with sufficient description length",
            "priority": "Medium"
        }
        
        response = await client.post(
            "/bugs/",
            json=bug_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        bug = response.json()
        assert bug["title"] == bug_data["title"]
        assert bug["reported_by"] == "dev1"

@pytest.mark.asyncio
async def test_create_bug_without_auth(setup_test_db):
    """Test creating a bug without authentication"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        bug_data = {
            "project_id": 1,
            "title": "Unauthorized bug",
            "description": "This should fail due to lack of authentication",
            "priority": "Low"
        }
        
        response = await client.post("/bugs/", json=bug_data)
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_bug_invalid_project(setup_test_db):
    """Test creating a bug with invalid project ID"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "user@bugify.com",
            "password": "user123",
            "role": "user"
        })
        token = login_response.json()["access_token"]
        
        # Create bug with non-existent project
        bug_data = {
            "project_id": 9999,
            "title": "Bug in non-existent project",
            "description": "This project does not exist in the database",
            "priority": "Medium"
        }
        
        response = await client.post(
            "/bugs/",
            json=bug_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "Project not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_bug_validation_errors(setup_test_db):
    """Test bug creation with validation errors"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "user@bugify.com",
            "password": "user123",
            "role": "user"
        })
        token = login_response.json()["access_token"]
        
        # Bug with too short title
        bug_data = {
            "project_id": 1,
            "title": "AB",  # Too short
            "description": "Description is long enough to pass",
            "priority": "High"
        }
        
        response = await client.post(
            "/bugs/",
            json=bug_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_get_bug_by_id(setup_test_db):
    """Test getting a bug by ID"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Get bug (from default data)
        response = await client.get(
            "/bugs/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bug = response.json()
        assert bug["id"] == 1

@pytest.mark.asyncio
async def test_update_bug_status(setup_test_db):
    """Test updating bug status"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Update bug status
        update_data = {
            "status": "In Progress"
        }
        
        response = await client.put(
            "/bugs/1",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bug = response.json()
        assert bug["status"] == "In Progress"

@pytest.mark.asyncio
async def test_user_cannot_update_bug(setup_test_db):
    """Test that regular users cannot update bugs"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as user
        login_response = await client.post("/auth/login", json={
            "email": "user@bugify.com",
            "password": "user123",
            "role": "user"
        })
        token = login_response.json()["access_token"]
        
        # Try to update bug
        update_data = {
            "status": "Closed"
        }
        
        response = await client.put(
            "/bugs/1",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Users cannot update bugs" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_bug_as_admin(setup_test_db):
    """Test deleting a bug as admin"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as admin
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # First create a bug to delete
        bug_data = {
            "project_id": 1,
            "title": "Bug to be deleted",
            "description": "This bug will be deleted in the test",
            "priority": "Low"
        }
        
        create_response = await client.post(
            "/bugs/",
            json=bug_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        bug_id = create_response.json()["id"]
        
        # Delete the bug
        response = await client.delete(
            f"/bugs/{bug_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204

@pytest.mark.asyncio
async def test_non_admin_cannot_delete_bug(setup_test_db):
    """Test that non-admins cannot delete bugs"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Try to delete bug
        response = await client.delete(
            "/bugs/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Only admins can delete bugs" in response.json()["detail"]