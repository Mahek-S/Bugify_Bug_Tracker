import pytest
from httpx import AsyncClient
from app.main import app
from app.database import get_database, connect_to_mongo, close_mongo_connection, init_default_data

@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Setup database connection before all tests"""
    await connect_to_mongo()
    await init_default_data()
    yield
    await close_mongo_connection()

@pytest.mark.asyncio
async def test_register_user():
    """Test user registration"""
    database = await get_database()
    
    # 🧹 Delete the test user if it already exists before running the test
    await database["users"].delete_one({"email": "test@bugify.com"})

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/register", json={
            "name": "Test User",
            "email": "test@bugify.com",
            "password": "test123",
            "confirm_password": "test123",
            "role": "developer"
        })

        print(response.json())

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@bugify.com"
        assert data["role"] == "developer"
        assert "hashed_password" not in data
        
@pytest.mark.asyncio
async def test_login_user():
    """Test user login with default credentials"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "admin"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "admin@bugify.com"
        assert data["user"]["role"] == "admin"

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "wrongpassword",
            "role": "admin"
        })
        
        assert response.status_code == 401
        assert "Invalid email, password, or role" in response.json()["detail"]

@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Test registration with existing email"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/register", json={
            "name": "Another User",
            "email": "admin@bugify.com",  # Already exists
            "password": "test123",
            "confirm_password": "test123",
            "role": "user"
        })
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_wrong_role():
    """Test login with correct credentials but wrong role"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/login", json={
            "email": "admin@bugify.com",
            "password": "admin123",
            "role": "developer"  # Wrong role (should be admin)
        })
        
        assert response.status_code == 401
        assert "Invalid email, password, or role" in response.json()["detail"]