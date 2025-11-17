import pytest
from httpx import AsyncClient
from app.main import app

# Mark all tests as async
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="function", autouse=True)
async def setup_test_db():
    """Setup test database once for all tests"""
    from app.database import connect_to_mongo, close_mongo_connection, init_default_data, get_database
    
    await connect_to_mongo()
    
    # Clear and initialize data
    database = await get_database()
    await database["users"].delete_many({})
    await database["projects"].delete_many({})
    await database["bugs"].delete_many({})
    await init_default_data()
    
    yield
    
    await close_mongo_connection()


@pytest.mark.asyncio
async def test_get_users_with_auth(setup_test_db):
    """Test getting all users with authentication"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Get users
        response = await client.get(
            "/dashboard/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        users = response.json()
        assert len(users) > 0


@pytest.mark.asyncio
async def test_get_users_without_auth(setup_test_db):
    """Test getting users without authentication"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/dashboard/users")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_projects(setup_test_db):
    """Test getting all projects"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Get projects
        response = await client.get(
            "/dashboard/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) > 0


@pytest.mark.asyncio
async def test_get_all_bugs(setup_test_db):
    """Test getting all bugs"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Get bugs
        response = await client.get(
            "/dashboard/bugs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bugs = response.json()
        assert isinstance(bugs, list)


@pytest.mark.asyncio
async def test_get_bugs_filtered_by_project(setup_test_db):
    """Test getting bugs filtered by project"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Get filtered bugs
        response = await client.get(
            "/dashboard/bugs?project_id=1",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bugs = response.json()
        for bug in bugs:
            assert bug["project_id"] == 1


@pytest.mark.asyncio
async def test_get_dashboard_stats(setup_test_db):
    """Test getting dashboard statistics"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Get stats
        response = await client.get(
            "/dashboard/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        stats = response.json()
        assert "total" in stats


@pytest.mark.asyncio
async def test_user_sees_only_their_bugs(setup_test_db):
    """Test that users only see bugs they reported"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as user
        login_response = await client.post("/auth/login", json={
            "email": "user@bugify.com",
            "password": "user123",
            "role": "user"
        })
        token = login_response.json()["access_token"]
        
        # Get bugs
        response = await client.get(
            "/dashboard/bugs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bugs = response.json()
        for bug in bugs:
            assert bug["reported_by"] == "user1"