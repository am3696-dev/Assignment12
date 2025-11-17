from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# --- Assume this Base is defined in your database.py ---
# from .database import Base
# If not, you'll need to define it:
Base = declarative_base()
# --------------------------------------------------------


# Your existing User model (from Module 10)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Add the relationship to calculations
    calculations = relationship("Calculation", back_populates="owner")


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
    
    # Foreign key to link to the User model
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationship to access the User object from a Calculation
    owner = relationship("User", back_populates="calculations")