import pytest
from unittest.mock import patch, MagicMock
from app.database import (
    db, 
    get_database, 
    connect_to_mongo, 
    close_mongo_connection,
    init_default_data
)

# -----------------------------
# Test get_database()
# -----------------------------
@pytest.mark.asyncio
async def test_get_database_success():
    """Should return database object when client exists."""
    
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = "mock_db"

    db.client = mock_client

    database = await get_database()
    assert database == "mock_db"


@pytest.mark.asyncio
async def test_get_database_not_initialized():
    """Should raise error if client is None."""
    
    db.client = None

    with pytest.raises(RuntimeError):
        await get_database()


# -----------------------------
# Test connect_to_mongo()
# -----------------------------
@pytest.mark.asyncio
async def test_connect_to_mongo():
    """Should create a new MongoDB client."""
    
    with patch("app.database.AsyncIOMotorClient") as MockMotor:
        mock_client = MagicMock()
        MockMotor.return_value = mock_client

        await connect_to_mongo()

        assert db.client == mock_client
        MockMotor.assert_called_once()


# -----------------------------
# Test close_mongo_connection()
# -----------------------------
@pytest.mark.asyncio
async def test_close_mongo_connection():
    """Should close the MongoDB client if it exists."""
    
    mock_client = MagicMock()
    db.client = mock_client

    await close_mongo_connection()

    mock_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_close_mongo_connection_no_client():
    """Should do nothing if client is None."""
    
    db.client = None

    # Should NOT raise an error
    await close_mongo_connection()


# -----------------------------
# Test init_default_data() (PARTIAL)
# -----------------------------
@pytest.mark.asyncio
async def test_init_default_data_skip_if_users_exist():
    """Should skip initialization if users already exist."""
    
    mock_db = MagicMock()
    mock_users_collection = MagicMock()

    mock_users_collection.count_documents.return_va
