from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from models import Notebook
SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://localhost\\SQLEXPRESS:1433/sql_express?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
        pass  # db.close() is handled by get_db()

