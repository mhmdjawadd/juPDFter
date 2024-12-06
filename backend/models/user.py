from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base
from flask_login import UserMixin

class User(Base,UserMixin):
    __tablename__ = 'UserTable'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(120), unique=True)
    password = Column(String(250))
    
    # Relationship with notebooks
    notebooks = relationship("Notebook", back_populates="user", lazy=True) 

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')" 