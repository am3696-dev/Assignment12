# app/models/calculation.py
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    result = Column(Float, nullable=False)

    owner_id = Column(ForeignKey("users.id"))
    owner = relationship("User", back_populates="calculations")
