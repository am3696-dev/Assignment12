from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# --- THIS IS THE FIX ---
from app.models import User  # Changed from app.models.user import User
# -----------------------

from app.schemas.user import UserResponse
from app.database import managed_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(
    db: Session = Depends(managed_db_session), 
    token: str = Depends(oauth2_scheme)
) -> UserResponse:
    """
    Get the current user from the provided token.
    """
    token_data = User.verify_token(token)
    if not token_data or "sub" not in token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Use the 'sub' (username) from the token to find the user
    username = token_data["sub"]
    
    # Query the database for the user
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return the user as a Pydantic model
    return UserResponse.from_orm(user)

def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Get the current active user.
    Raises an exception if the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user