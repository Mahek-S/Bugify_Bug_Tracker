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
async def test_get_my_bugs_as_developer(setup_test_db):
    """Test getting bugs assigned to developer"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Get my bugs
        response = await client.get(
            "/mybugs/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bugs = response.json()
        assert isinstance(bugs, list)
        # All bugs should be assigned to dev1
        for bug in bugs:
            assert bug["assigned_to"] == "dev1"

@pytest.mark.asyncio
async def test_get_my_bugs_without_auth(setup_test_db):
    """Test getting bugs without authentication"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/mybugs/")
        
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_my_bugs_as_non_developer(setup_test_db):
    """Test that non-developers cannot access mybugs endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as admin
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Try to get my bugs
        response = await client.get(
            "/mybugs/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Only developers" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_my_bugs_filtered_by_project(setup_test_db):
    """Test getting bugs filtered by project"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Get bugs for specific project
        response = await client.get(
            "/mybugs/?project_id=1",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bugs = response.json()
        for bug in bugs:
            assert bug["project_id"] == 1
            assert bug["assigned_to"] == "dev1"

@pytest.mark.asyncio
async def test_get_my_bugs_filtered_by_status(setup_test_db):
    """Test getting bugs filtered by status"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Get open bugs
        response = await client.get(
            "/mybugs/?status_filter=Open",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bugs = response.json()
        for bug in bugs:
            assert bug["status"] == "Open"
            assert bug["assigned_to"] == "dev1"

@pytest.mark.asyncio
async def test_get_my_bugs_stats(setup_test_db):
    """Test getting bug statistics"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Get stats
        response = await client.get(
            "/mybugs/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        stats = response.json()
        assert "total" in stats
        assert "open" in stats
        assert "in_progress" in stats
        assert "resolved" in stats
        assert "closed" in stats
        assert isinstance(stats["total"], int)

@pytest.mark.asyncio
async def test_update_my_bug_status(setup_test_db):
    """Test updating status of assigned bug"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Update bug status (bug 1 is assigned to dev1 in init_default_data)
        status_data = {
            "status": "In Progress"
        }
        
        response = await client.put(
            "/mybugs/1/status",
            json=status_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bug = response.json()
        assert bug["status"] == "In Progress"
        assert bug["assigned_to"] == "dev1"

@pytest.mark.asyncio
async def test_update_unassigned_bug_status(setup_test_db):
    """Test that developer cannot update bug not assigned to them"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as dev2
        login_response = await client.post("/auth/login", json={
            "email": "dev2@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Try to update bug 1 (assigned to dev1)
        status_data = {
            "status": "Closed"
        }
        
        response = await client.put(
            "/mybugs/1/status",
            json=status_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "not assigned to you" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_my_projects(setup_test_db):
    """Test getting projects with assigned bugs"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Get my projects
        response = await client.get(
            "/mybugs/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
        assert all("id" in p and "name" in p for p in projects)

@pytest.mark.asyncio
async def test_non_developer_cannot_get_stats(setup_test_db):
    """Test that non-developers cannot get bug stats"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as user
        login_response = await client.post("/auth/login", json={
            "email": "user@bugify.com",
            "password": "user123",
            "role": "user"
        })
        token = login_response.json()["access_token"]
        
        # Try to get stats
        response = await client.get(
            "/mybugs/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_bug_with_invalid_status(setup_test_db):
    """Test updating bug with invalid status"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Try to update with invalid status
        status_data = {
            "status": "Invalid Status"
        }
        
        response = await client.put(
            "/mybugs/1/status",
            json=status_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422  # Validation error