from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

# Import the settings object from our config file
from app.config import settings

def get_engine(database_url: str):
    """
    Creates a new SQLAlchemy engine.
    This now uses whatever URL is passed to it.
    """
    return create_engine(database_url)

def get_sessionmaker(engine):
    """
    Creates a new sessionmaker bound to the given engine.
    """
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the Base that our models (User, Calculation) will inherit from.
Base = declarative_base()

# --- THIS IS THE FIX ---
# Create the *application's* engine and sessionmaker
# These will correctly use the DATABASE_URL from the environment.
app_engine = get_engine(settings.DATABASE_URL)
SessionLocal = get_sessionmaker(app_engine)

@contextmanager
def managed_db_session():
    """
    Context manager for safe database session handling.
    This is the function 'app/auth/dependencies.py' needs.
    """
    session = SessionLocal()
    try:
        yield session
    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}") # Use print for visibility
        session.rollback()
        raise
    finally:
        session.close()

# This is the real FastAPI dependency
def get_db():
    """
    FastAPI dependency to get a database session.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()