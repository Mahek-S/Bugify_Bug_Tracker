import pytest
from pydantic import ValidationError
from app.schemas import (
    UserRegister,
    UserLogin,
    PasswordChange,
    BugCreate,
    BugUpdate,
    ProjectCreate,
    ProfileUpdate
)

# -----------------------------
# UserRegister model tests
# -----------------------------
def test_user_register_valid():
    user = UserRegister(
        name="John",
        email="john@test.com",
        password="password123",
        confirm_password="password123",
        role="developer"
    )
    assert user.name == "John"
    assert user.role == "developer"


def test_user_register_password_not_matching():
    with pytest.raises(ValidationError):
        UserRegister(
            name="John",
            email="john@test.com",
            password="password123",
            confirm_password="wrongpass",
            role="user"
        )


# -----------------------------
# UserLogin model tests
# -----------------------------
def test_user_login_valid():
    user = UserLogin(
        email="user@test.com",
        password="abcdef",
        role="user"
    )
    assert user.email == "user@test.com"


def test_user_login_invalid_role():
    with pytest.raises(ValidationError):
        UserLogin(
            email="user@test.com",
            password="abcdef",
            role="invalid"
        )


# -----------------------------
# PasswordChange tests
# -----------------------------
def test_password_change_valid():
    obj = PasswordChange(
        current_password="oldpass",
        new_password="newpass123",
        confirm_password="newpass123"
    )
    assert obj.new_password == "newpass123"


def test_password_change_mismatch():
    with pytest.raises(ValidationError):
        PasswordChange(
            current_password="oldpass",
            new_password="newpass123",
            confirm_password="wrong"
        )


# -----------------------------
# BugCreate tests
# -----------------------------
def test_bug_create_valid():
    bug = BugCreate(
        project_id=1,
        title="Bug title",
        description="This is a valid description",
        priority="High"
    )
    assert bug.priority == "High"


def test_bug_create_short_description():
    with pytest.raises(ValidationError):
        BugCreate(
            project_id=1,
            title="Bug",
            description="short",
            priority="Low"
        )


# -----------------------------
# BugUpdate tests
# -----------------------------
def test_bug_update_valid_status():
    bug = BugUpdate(status="Resolved")
    assert bug.status == "Resolved"


def test_bug_update_invalid_status():
    with pytest.raises(ValidationError):
        BugUpdate(status="SomethingElse")


# -----------------------------
# ProjectCreate tests
# -----------------------------
def test_project_create_valid():
    p = ProjectCreate(
        name="Project One",
        description="Test description"
    )
    assert p.name == "Project One"


def test_project_create_invalid_name():
    with pytest.raises(ValidationError):
        ProjectCreate(name="ab", description="short")


# -----------------------------
# ProfileUpdate tests
# -----------------------------
def test_profile_update_valid():
    p = ProfileUpdate(name="New Name")
    assert p.name == "New Name"


def test_profile_update_invalid_email():
    with pytest.raises(ValidationError):
        ProfileUpdate(email="notanemail")
