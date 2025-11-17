# app/models/__init__.py

# This file ensures that all models are imported and known to SQLAlchemy's Base
# before they are used, preventing relationship errors.

# Import Base from user.py first, as calculation.py depends on it
from .user import Base
from .user import User
from .calculation import Calculation