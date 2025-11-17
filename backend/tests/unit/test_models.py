from app.models import User, Project, Bug
from pydantic import ValidationError
import pytest

# -------------------------
# USER MODEL TESTS
# -------------------------

def test_user_model_valid():
    """Test creating a valid User model"""
    user = User(
        id="u123",
        name="Alice",
        email="alice@example.com",
        hashed_password="hashed123",
        role="developer",
        joined_date="2025-01-01"
    )
    assert user.name == "Alice"
    assert user.role == "developer"


def test_user_model_invalid_email():
    """User model should raise error for invalid email"""
    with pytest.raises(ValidationError):
        User(
            id="u123",
            name="Alice",
            email="not-an-email",
            hashed_password="hashed123",
            role="developer",
            joined_date="2025-01-01"
        )


def test_user_invalid_role():
    """Only admin/developer/user should be allowed as role"""
    with pytest.raises(ValidationError):
        User(
            id="u123",
            name="Alice",
            email="alice@example.com",
            hashed_password="hashed123",
            role="boss",  # invalid
            joined_date="2025-01-01"
        )


# -------------------------
# PROJECT MODEL TESTS
# -------------------------

def test_project_model_valid():
    project = Project(
        id=1,
        name="Bug Tracker",
        created_by="u123",
        created_at="2025-01-01"
    )
    assert project.id == 1
    assert project.name == "Bug Tracker"


# -------------------------
# BUG MODEL TESTS
# -------------------------

def test_bug_model_valid():
    bug = Bug(
        id=1,
        project_id=10,
        project_name="Bugify",
        title="Login issue",
        description="Fails on password mismatch",
        status="Open",
        priority="High",
        reported_by="u123",
        assigned_to="dev001",
        created_at="2025-01-01",
        updated_at="2025-01-02"
    )
    assert bug.status == "Open"
    assert bug.priority == "High"


def test_bug_invalid_status():
    """Only Open/In Progress/Resolved/Closed allowed"""
    with pytest.raises(ValidationError):
        Bug(
            id=1,
            project_id=10,
            project_name="Bugify",
            title="AAA",
            description="BBB",
            status="Doing",  # invalid
            priority="High",
            reported_by="u123",
            created_at="2025-01-01",
            updated_at="2025-01-02"
        )
