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
async def test_get_my_profile(setup_test_db):
    """Test getting current user's profile"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Get profile
        response = await client.get(
            "/profile/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        profile = response.json()
        assert profile["email"] == "dev1@bugify.com"
        assert profile["role"] == "developer"
        assert "id" in profile
        assert "name" in profile
        assert "joined_date" in profile

@pytest.mark.asyncio
async def test_get_profile_without_auth(setup_test_db):
    """Test getting profile without authentication"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/profile/me")
        
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_profile_name(setup_test_db):
    """Test updating profile name"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as developer
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Update profile
        update_data = {
            "name": "John Updated Developer"
        }
        
        response = await client.put(
            "/profile/me",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        profile = response.json()
        assert profile["name"] == "John Updated Developer"
        assert profile["email"] == "dev1@bugify.com"

@pytest.mark.asyncio
async def test_update_profile_email(setup_test_db):
    """Test updating profile email"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as user
        login_response = await client.post("/auth/login", json={
            "email": "user@bugify.com",
            "password": "user123",
            "role": "user"
        })
        token = login_response.json()["access_token"]
        
        # Update profile
        update_data = {
            "email": "user.new@bugify.com"
        }
        
        response = await client.put(
            "/profile/me",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        profile = response.json()
        assert profile["email"] == "user.new@bugify.com"

@pytest.mark.asyncio
async def test_update_profile_duplicate_email(setup_test_db):
    """Test updating profile with email already taken"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as dev2
        login_response = await client.post("/auth/login", json={
            "email": "dev2@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Try to update to existing email
        update_data = {
            "email": "admin@bugify.com"  # Already exists
        }
        
        response = await client.put(
            "/profile/me",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"]

@pytest.mark.asyncio
async def test_update_profile_both_fields(setup_test_db):
    """Test updating both name and email"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as admin
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Update profile
        update_data = {
            "name": "Sarah Updated Admin",
            "email": "sarah.admin@bugify.com"
        }
        
        response = await client.put(
            "/profile/me",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        profile = response.json()
        assert profile["name"] == "Sarah Updated Admin"
        assert profile["email"] == "sarah.admin@bugify.com"

@pytest.mark.asyncio
async def test_change_password_success(setup_test_db):
    """Test changing password successfully"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as dev1
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Change password
        password_data = {
            "current_password": "dev123",
            "new_password": "newdev123",
            "confirm_password": "newdev123"
        }
        
        response = await client.put(
            "/profile/me/password",
            json=password_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()
        
        # Try logging in with new password
        login_response2 = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "newdev123",
            "role": "developer"
        })
        
        assert login_response2.status_code == 200

@pytest.mark.asyncio
async def test_change_password_wrong_current(setup_test_db):
    """Test changing password with wrong current password"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "dev2@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Try to change password with wrong current password
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        }
        
        response = await client.put(
            "/profile/me/password",
            json=password_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_change_password_same_as_current(setup_test_db):
    """Test changing password to same as current"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "user@bugify.com",
            "password": "user123",
            "role": "user"
        })
        token = login_response.json()["access_token"]
        
        # Try to change to same password
        password_data = {
            "current_password": "user123",
            "new_password": "user123",
            "confirm_password": "user123"
        }
        
        response = await client.put(
            "/profile/me/password",
            json=password_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "different" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_change_password_mismatch(setup_test_db):
    """Test changing password with mismatched confirmation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        token = login_response.json()["access_token"]
        
        # Try with mismatched passwords
        password_data = {
            "current_password": "admin123",
            "new_password": "newpass123",
            "confirm_password": "different123"
        }
        
        response = await client.put(
            "/profile/me/password",
            json=password_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_get_profile_stats(setup_test_db):
    """Test getting profile statistics"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",  # Using updated password from earlier test
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Get stats
        response = await client.get(
            "/profile/me/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        stats = response.json()
        assert "bugs_reported" in stats
        assert "bugs_assigned" in stats
        assert isinstance(stats["bugs_reported"], int)
        assert isinstance(stats["bugs_assigned"], int)

@pytest.mark.asyncio
async def test_get_recent_activity(setup_test_db):
    """Test getting recent activity"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "dev1@bugify.com",
            "password": "dev123",
            "role": "developer"
        })
        token = login_response.json()["access_token"]
        
        # Get activity
        response = await client.get(
            "/profile/me/activity",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, list)
        
        # Check activity structure if any exist
        if len(activities) > 0:
            activity = activities[0]
            assert "bug_id" in activity
            assert "title" in activity
            assert "status" in activity
            assert "activity_type" in activity
            assert "updated_at" in activity

@pytest.mark.asyncio
async def test_get_activity_with_limit(setup_test_db):
    """Test getting recent activity with custom limit"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "user@bugify.com",
            "password": "user123",
            "role": "user"
        })
        token = login_response.json()["access_token"]
        
        # Get activity with limit
        response = await client.get(
            "/profile/me/activity?limit=3",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, list)
        assert len(activities) <= 3