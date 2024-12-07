from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://mhmdjawad:password@localhost:5432/db_490"

engine = create_engine(SQLALCHEMY_DATABASE_URL,echo = False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db(reset=False):
    from models.user import User
    from models.notebook import Notebook
    if reset:
        # Drop all tables if reset is True
        Base.metadata.drop_all(bind=engine)
    
    # Create all tables defined in the models
    Base.metadata.create_all(bind=engine)
    

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    db = next(get_db())
    try:
        yield db
    finally:
        pass
     

