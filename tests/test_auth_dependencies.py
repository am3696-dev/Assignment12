# tests/test_auth_dependencies.py

import pytest
from unittest.mock import MagicMock, patch, ANY
from fastapi import HTTPException, status
from app.auth.dependencies import get_current_user, get_current_active_user
from app.schemas.user import UserResponse
from app.models import User, Calculation  # Correct import
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

# --- THIS IS THE FIX ---
# We are changing the mock strategy to be simpler and correct.
# We will mock the `db` object (mock_db) instead of patching functions.

def test_get_current_user_success(mock_db, mock_token_data, fake_active_user):
    """Test successful retrieval of current user."""
    # Simulate User.verify_token returning the user's "sub" (username)
    with patch("app.auth.dependencies.User.verify_token") as mock_verify_token:
        mock_verify_token.return_value = mock_token_data
        
        # Simulate the db.query().filter().first() chain
        mock_db.query.return_value.filter.return_value.first.return_value = fake_active_user

        token = "fake.token.string"
        user = get_current_user(db=mock_db, token=token)

        assert user is not None
        assert user.username == fake_active_user.username
        mock_verify_token.assert_called_once_with(token)
        # Check that the db was queried with the User model
        mock_db.query.assert_called_once_with(User)

# -------------------------

@patch("app.auth.dependencies.User.verify_token")
def test_get_current_user_invalid_token(mock_verify_token, mock_db):
    """Test retrieval with an invalid or expired token."""
    mock_verify_token.return_value = None
    token = "invalid.token.string"

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db, token=token)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in exc_info.value.detail

# --- THIS IS THE SECOND PART OF THE FIX ---
def test_get_current_user_not_found(mock_db, mock_token_data):
    """Test retrieval when user in token does not exist in DB."""
    # Simulate User.verify_token returning the user's "sub" (username)
    with patch("app.auth.dependencies.User.verify_token") as mock_verify_token:
        mock_verify_token.return_value = mock_token_data

        # Simulate the db.query()... chain returning None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        token = "fake.token.string"

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(db=mock_db, token=token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in exc_info.value.detail
# -------------------------

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

    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(current_user=user_schema)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Inactive user" in exc_info.value.detail