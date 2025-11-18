# tests/test_auth_dependencies.py

import pytest
from unittest.mock import MagicMock, patch, ANY
from fastapi import HTTPException, status
from app.auth.dependencies import get_current_user, get_current_active_user
from app.schemas.user import UserResponse
from app.models import User, Calculation  # <-- THE CRITICAL FIX IS HERE
from uuid import uuid4
from datetime import datetime

@pytest.fixture
def mock_db():
    """Fixture for a mock database session."""
    return MagicMock()

@pytest.fixture
def mock_token_data():
    """Fixture for mock token data."""
    return {"sub": "johndoe"}

@pytest.fixture
def fake_active_user():
    """Fixture for a fake active user."""
    return User(
        id=uuid4(),
        username="johndoe",
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

@pytest.fixture
def fake_inactive_user():
    """Fixture for a fake inactive user."""
    return User(
        id=uuid4(),
        username="inactivejohn",
        email="inactive@example.com",
        first_name="John",
        last_name="Doe",
        is_active=False,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

@patch("app.auth.dependencies.User.verify_token")
@patch("app.auth.dependencies.get_user_by_username_or_email")
def test_get_current_user_success(mock_get_user, mock_verify_token, mock_db, mock_token_data, fake_active_user):
    """Test successful retrieval of current user."""
    mock_verify_token.return_value = mock_token_data
    mock_get_user.return_value = fake_active_user

    token = "fake.token.string"
    user = get_current_user(db=mock_db, token=token)

    assert user is not None
    assert user.username == fake_active_user.username
    mock_verify_token.assert_called_once_with(token)
    mock_get_user.assert_called_once_with(db=mock_db, username_or_email=mock_token_data["sub"])

@patch("app.auth.dependencies.User.verify_token")
def test_get_current_user_invalid_token(mock_verify_token, mock_db):
    """Test retrieval with an invalid or expired token."""
    mock_verify_token.return_value = None
    token = "invalid.token.string"

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db, token=token)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in exc_info.value.detail

@patch("app.auth.dependencies.User.verify_token")
@patch("app.auth.dependencies.get_user_by_username_or_email")
def test_get_current_user_not_found(mock_get_user, mock_verify_token, mock_db, mock_token_data):
    """Test retrieval when user in token does not exist in DB."""
    mock_verify_token.return_value = mock_token_data
    mock_get_user.return_value = None  # User not found
    token = "fake.token.string"

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db, token=token)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in exc_info.value.detail

def test_get_current_active_user_success(fake_active_user):
    """Test retrieval of an active user."""
    # We now pass the user *schema* (or a mock of it) to this function
    # Assuming get_current_user returns a Pydantic model
    user_schema = UserResponse.from_orm(fake_active_user)
    
    active_user = get_current_active_user(current_user=user_schema)
    assert active_user is not None
    assert active_user.username == fake_active_user.username

def test_get_current_active_user_inactive(fake_inactive_user):
    """Test retrieval of an inactive user raises exception."""
    user_schema = UserResponse.from_orm(fake_inactive_user)