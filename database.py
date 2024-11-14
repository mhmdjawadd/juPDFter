from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
import os

DATABASE_URL = "mysql+pymysql://root:1234@localhost/db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    pdf_file_path = Column(String(255))           # Path to the uploaded PDF
    notebook_file_path = Column(String(255))    # Path to the generated .ipynb


# Create tables
# Base.metadata.create_all(bind=engine)


def add_user(session, username, email, password, pdf_file_path=None, notebook_file_path=None):
    user = User(
        username=username,
        email=email,
        password=password,
        pdf_file_path=pdf_file_path,
        notebook_file_path=notebook_file_path
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_users(session):
    return session.query(User).all()


def update_user(session, user_id, username=None, email=None, password=None, pdf_file_path=None, notebook_file_path=None):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = password
        if pdf_file_path:
            user.pdf_file_path = pdf_file_path
        if notebook_file_path:
            user.notebook_file_path = notebook_file_path
        session.commit()
    return user


def delete_user(session, user_id):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        session.delete(user)
        session.commit()


def save_file(file_content, filename, folder="pdf_files"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(file_content)
    return path


# Example usage:
# pdf_path = save_file(pdf_content, "user_pdf.pdf", folder="pdf_files")
# notebook_path = save_file(notebook_content, "user_notebook.ipynb", folder="notebook_files")
# new_user = add_user(session, "username", "email@example.com", "password", pdf_file_path=pdf_path, notebook_file_path=notebook_path)

# Initialize a new session
# session = SessionLocal()

# Example usage:
# pdf_path = save_file(b"PDF content here", "user_pdf.pdf", folder="pdf_files")
# notebook_path = save_file(b"Notebook content here", "user_notebook.ipynb", folder="notebook_files")

# new_user = add_user(session, "username1", "email@example.com", "securepassword", pdf_file_path=pdf_path, notebook_file_path=notebook_path)
# all_users = get_users(session)
# updated_user = update_user(session, new_user.id, username="new_username")
# # delete_user(session, new_user.id)

# # Close the session when done
# session.close()
