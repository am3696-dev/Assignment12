import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# --- THE FIX ---
# We must import the functions AND the settings object
from app.database import Base, get_engine, get_sessionmaker
from app.config import settings
# ----------------

def test_base_declaration():
    """Test that Base is correctly declared."""
    assert Base is not None
    assert hasattr(Base, 'metadata')

def test_get_engine_success():
    """Test that get_engine returns a valid Engine instance."""
    # We must pass the DATABASE_URL, which we get from settings
    engine = get_engine(settings.DATABASE_URL)
    assert engine is not None
    assert isinstance(engine, Engine)

def test_get_engine_failure():
    """Test that get_engine fails with an invalid URL format."""
    # We test that SQLAlchemy raises an error, as expected.
    with pytest.raises(Exception):
        get_engine("not_a_real_database_url")

def test_get_sessionmaker():
    """Test that get_sessionmaker returns a valid sessionmaker."""
    # We need a real engine to create a sessionmaker
    engine = get_engine(settings.DATABASE_URL)
    
    SessionLocal = get_sessionmaker(engine)
    assert SessionLocal is not None
    
    # Try creating a session
    session = SessionLocal()
    assert session is not None
    session.close()