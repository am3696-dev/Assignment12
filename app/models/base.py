# app/models/base.py
from sqlalchemy.orm import declarative_base

# Single shared Base for all models
Base = declarative_base()
