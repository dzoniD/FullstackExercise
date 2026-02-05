from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    is_verified = Column(Boolean, default=False)
    
    # Relation with Task model
    tasks = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relation with User model
    owner = relationship("User", back_populates="tasks")
    tags = relationship("Tag", secondary=task_tags, backref="tasks", lazy="joined")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)