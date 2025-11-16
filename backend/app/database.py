from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None 
    
db = Database()

async def get_database():
    database_name = os.getenv("DATABASE_NAME", "bugify_db")
    if db.client is None:
        raise RuntimeError("Database client is not initialized. Call connect_to_mongo() first.")
    return db.client[database_name]

async def connect_to_mongo():
    """Connect to MongoDB"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db.client = AsyncIOMotorClient(mongodb_url)
    print("✓ Connected to MongoDB")
    print(">>> ENV =", os.getenv("ENV"))
    print(">>> DATABASE_NAME =", os.getenv("DATABASE_NAME"))


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("✓ Closed MongoDB connection")

async def init_default_data():
    """Initialize default data for testing"""
    try:
        database = await get_database()
        users_collection = database["users"]
        projects_collection = database["projects"]
        bugs_collection = database["bugs"]
        
        # Check if users already exist
        existing_users = await users_collection.count_documents({})
        if existing_users > 0:
            print(f"✓ Found {existing_users} existing users, skipping initialization")
            return
        
        from app.utils.auth_helpers import get_password_hash
        
        # Test password hashing first
        print("Testing password hashing...")
        test_password = "test123"
        try:
            test_hash = get_password_hash(test_password)
            print(f"✓ Password hashing test successful")
            print(f"  Test password: {test_password}")
            print(f"  Hash length: {len(test_hash)}")
        except Exception as e:
            print(f"✗ Password hashing test FAILED: {e}")
            raise
        
        # Create default users
        print("Creating default users...")
        default_users = [
            {
                "id": "admin1",
                "name": "Sarah Admin",
                "email": "admin@bugify.com",
                "hashed_password": get_password_hash("admin123"),
                "role": "admin",
                "joined_date": "2025-09-01"
            },
            {
                "id": "dev1",
                "name": "John Developer",
                "email": "dev1@bugify.com",
                "hashed_password": get_password_hash("dev123"),
                "role": "developer",
                "joined_date": "2025-09-10"
            },
            {
                "id": "dev2",
                "name": "Emma Developer",
                "email": "dev2@bugify.com",
                "hashed_password": get_password_hash("dev123"),
                "role": "developer",
                "joined_date": "2025-09-15"
            },
            {
                "id": "user1",
                "name": "Mike User",
                "email": "user@bugify.com",
                "hashed_password": get_password_hash("user123"),
                "role": "user",
                "joined_date": "2025-09-20"
            }
        ]
        
        await users_collection.insert_many(default_users)
        print(f"✓ Created {len(default_users)} users")
        
        # Create default projects
        default_projects = [
            {"id": 1, "name": "Bugify Dashboard", "created_by": "admin1", "created_at": "2025-09-01"},
            {"id": 2, "name": "Bugify API", "created_by": "admin1", "created_at": "2025-09-05"},
            {"id": 3, "name": "Bugify Mobile App", "created_by": "admin1", "created_at": "2025-09-10"}
        ]
        
        await projects_collection.insert_many(default_projects)
        print(f"✓ Created {len(default_projects)} projects")
        
        # Create default bugs
        default_bugs = [
            {
                "id": 1,
                "project_id": 1,
                "project_name": "Bugify Dashboard",
                "title": "Login button not working",
                "description": "Login button on the dashboard doesn't trigger login action.",
                "status": "Open",
                "priority": "High",
                "reported_by": "user1",
                "assigned_to": "dev1",
                "created_at": "2025-10-07T10:00:00Z",
                "updated_at": "2025-10-07T10:00:00Z"
            },
            {
                "id": 2,
                "project_id": 1,
                "project_name": "Bugify Dashboard",
                "title": "Dark mode not saving preference",
                "description": "After refresh, the selected dark mode resets to light mode.",
                "status": "In Progress",
                "priority": "Medium",
                "reported_by": "admin1",
                "assigned_to": "dev1",
                "created_at": "2025-10-06T12:00:00Z",
                "updated_at": "2025-10-07T09:30:00Z"
            }
        ]
        
        await bugs_collection.insert_many(default_bugs)
        print(f"✓ Created {len(default_bugs)} bugs")
        
        print("✓ Initialized default data successfully")
        
    except Exception as e:
        print(f"✗ Failed to initialize default data: {e}")
        raise