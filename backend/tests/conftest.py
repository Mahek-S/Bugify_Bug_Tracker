import os
print(">>> LOADING TEST ENVIRONMENT BEFORE IMPORTS <<<")

from dotenv import load_dotenv
load_dotenv(".env.test")
os.environ["ENV"] = "test"

print(">>> ENV =", os.getenv("ENV"))
print(">>> DB NAME =", os.getenv("DATABASE_NAME"))

# NOW IMPORT ANYTHING
from app.main import app
from app.database import connect_to_mongo, close_mongo_connection, get_database, init_default_data
import pytest
from httpx import AsyncClient

@pytest.fixture(scope="function")
async def test_db():
    # Connect fresh EACH test
    await connect_to_mongo()
    db = await get_database()

    # CLEAN DB before test
    collections = await db.list_collection_names()
    for coll in collections:
        await db.drop_collection(coll)

    # Insert default test data
    await init_default_data()

    yield db

    # CLEAN DB after test
    collections = await db.list_collection_names()
    for coll in collections:
        await db.drop_collection(coll)

    await close_mongo_connection()


@pytest.fixture(scope="function")
async def async_client(test_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
