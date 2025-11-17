import pytest
import bcrypt
from datetime import timedelta
from app.utils.auth_helpers import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)

# ---------------------
# Password Hashing Tests
# ---------------------

def test_get_password_hash_generates_valid_hash():
    password = "mypassword123"

    hashed = get_password_hash(password)

    # Hash must be a string
    assert isinstance(hashed, str)
    # bcrypt hashes always start with $2b or $2a
    assert hashed.startswith("$2b") or hashed.startswith("$2a")


def test_verify_password_correct():
    password = "hello123"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    password = "hello123"
    hashed = bcrypt.hashpw("wrongpass".encode(), bcrypt.gensalt()).decode()

    assert verify_password(password, hashed) is False


# ---------------------
# JWT Token Tests
# ---------------------

def test_create_access_token_returns_string():
    data = {"sub": "test@example.com"}

    token = create_access_token(data)

    assert isinstance(token, str)


def test_create_access_token_expiry():
    data = {"sub": "test@example.com"}

    token = create_access_token(data, expires_delta=timedelta(minutes=1))

    # token should decode successfully
    email = decode_access_token(token)
    assert email == "test@example.com"


def test_decode_access_token_invalid():
    invalid_token = "notatoken123"

    assert decode_access_token(invalid_token) is None
