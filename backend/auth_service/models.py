from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    is_verified = Column(Boolean, default=False)
    
    # # Relation with Task model
    # tasks = relationship("Task", back_populates="owner")