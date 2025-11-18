import uuid
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID

# Import the Base from your database file
from app.database import Base

# This is the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This is for JWT tokens. This is bad practice (should be in config)
# but it matches what your tests expect.
# !!! YOU MUST REPLACE THIS WITH YOUR OWN SECRET KEY !!!
SECRET_KEY = "your-secret-key-from-module-10"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class User(Base):
    """
    The "fat" User model, containing all fields and business logic
    that your tests expect.
    """
    __tablename__ = "users"

    # --- All the fields your tests expect ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationship
    calculations = relationship("Calculation", back_populates="owner")

    # --- All the methods your tests expect ---

    @staticmethod
    def hash_password(password: str) -> str:
        """Called by test_password_hashing"""
        return pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Called by test_password_hashing"""
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        """Called by test_token_creation_and_verification"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 

    @staticmethod
    def verify_token(token: str) -> dict | None:
        """Called by test_invalid_token and auth dependencies"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # The tests expect the payload (a dict) or None
            return payload
        except (jwt.PyJWTError, jwt.exceptions.DecodeError):
            return None
                
    @classmethod
    def register(cls, db: Session, user_data: dict):
        """Called by all test_user_registration tests"""
        password = user_data.get("password")
        if not password or len(password) < 6:
             raise ValueError("Password must be at least 6 characters long")
        
        # Check for duplicates
        existing = db.query(cls).filter(
            (cls.username == user_data['username']) | (cls.email == user_data['email'])
        ).first()
        if existing:
            raise ValueError("Username or email already exists")

        # Copy data, hash password, and remove plain text pass
        new_user_data = user_data.copy()
        new_user_data['hashed_password'] = cls.hash_password(password)
        del new_user_data['password']

        # Create User object, filtering out keys that aren't in the model
        model_fields = {c.name for c in cls.__table__.columns}
        filtered_data = {k: v for k, v in new_user_data.items() if k in model_fields}
        
        new_user = cls(**filtered_data)
        db.add(new_user)
        # We don't commit here; the test or service layer should commit.
        return new_user

    @classmethod
    def authenticate(cls, db: Session, username_or_email: str, password: str):
        """Called by test_user_authentication"""
        user = db.query(cls).filter(
            (cls.username == username_or_email) | (cls.email == username_or_email)
        ).first()
        
        if not user or not user.verify_password(password):
            return None # Auth failed
        
        # Update last_login
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        
        access_token = cls.create_access_token(data={"sub": user.username})
        
        # We must import here to avoid a circular import at the top
        from app.schemas.user import UserResponse
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }
            
    def __repr__(self):
        """Called by test_user_model_representation"""
        return f"<User(name={self.first_name} {self.last_name}, email={self.email})>"


# --- NEW FOR MODULE 11 ---

class Calculation(Base):
    """
    SQLAlchemy model for storing calculation records.
    """
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String, nullable=False) # Stores the string "Add", "Sub", etc.
    result = Column(Float, nullable=False) # Store the computed result
    
    # --- FIX ---
    # The Foreign key must point to 'users.id', which is now a UUID
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    # -----------

    # Relationship to access the User object from a Calculation
    owner = relationship("User", back_populates="calculations")