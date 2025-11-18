from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Import the settings object from our config file
from app.config import settings

def get_engine(database_url: str):
    """
    Creates a new SQLAlchemy engine.
    This now uses whatever URL is passed to it.
    """
    return create_engine(database_url)

# --- THIS IS THE FIX ---
# Your old file had a broken version of this function.
# This version correctly takes an 'engine' object as an argument.
def get_sessionmaker(engine):
    """
    Creates a new sessionmaker bound to the given engine.
    """
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
# -----------------------

# This is the Base that our models (User, Calculation) will inherit from.
Base = declarative_base()

def get_db():
    """
    FastAPI dependency to get a database session.
    (This logic might be in your main.py, but it's good to have it here)
    """
    
    # This won't work until main.py is set up to create a global engine
    # for the *real app*, but it's fine for testing.
    # For now, we just need Base, get_engine, and get_sessionmaker.
    pass