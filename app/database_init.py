# We need the 'Base' to know *what* tables to create/drop
from app.database import Base

# We need the *settings* to find the database URL
from app.config import settings

# We need the *function* to create an engine, not the variable
from app.database import get_engine

# --- THIS IS THE FIX ---
# We must import the models *in this file* so that Base.metadata
# is populated *before* init_db() is called.
from app.models import User, Calculation
# -----------------------


# Create a *local* engine for this script to use,
# correctly reading the DATABASE_URL from our environment.
script_engine = get_engine(settings.DATABASE_URL)
# ----------------

def init_db():
    """Creates all tables in the database."""
    # Now Base.metadata will contain User and Calculation tables
    Base.metadata.create_all(bind=script_engine)

def drop_db():
    """Drops all tables from the database."""
    # Now Base.metadata will contain User and Calculation tables
    Base.metadata.drop_all(bind=script_engine)