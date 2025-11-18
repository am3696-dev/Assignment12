# app/models/__init__.py

# Import the models from their respective files
# This ensures both are registered with SQLAlchemy's Base
# when the 'app.models' package is imported.
from .user import User
from .calculation import Calculation

# This __all__ list tells Python what to export
# when someone does `from app.models import *`
# (It's good practice, though not strictly required for this fix)
__all__ = ["User", "Calculation"]