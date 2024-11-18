from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base
from flask_login import UserMixin

class User(Base,UserMixin ):
    __tablename__ = 'UserTable'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(120))
    
    # Relationship with notebooks
    notebooks = relationship("NotebookTable", back_populates="user", cascade="all, delete-orphan") 

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')" 