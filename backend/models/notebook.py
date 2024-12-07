from sqlalchemy import Column, Integer, String, ForeignKey ,JSON
from sqlalchemy.orm import relationship
from database import Base

class Notebook(Base):
    """
    Model representing a Jupyter Notebook associated with a topic.
    """
    __tablename__ = 'NotebookTable'

    id = Column(Integer, primary_key=True)
    topic = Column(String(100))
    content = Column(JSON)  # .ipynb files are stored as JSON
    user_id = Column(Integer, ForeignKey('UserTable.id'),nullable=False)
    
    # Relationship back to user
    user = relationship("User", back_populates="notebooks",uselist=False)

    def __repr__(self):
        return f"Notebook(id={self.id}, topic='{self.topic}')" 
    