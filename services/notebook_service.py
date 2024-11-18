from sqlalchemy.orm import Session
from models import Notebook 

class NotebookService:
    @staticmethod
    def save_notebook(db :Session,notebook :Notebook):
        """
        saves the notebook to the database
        Args:
        db (Session): SQLAlchemy database session
        
        notebook : jupyter noteboook file .ipynb to be saved in the db
        """
        
        
        # Add and commit to database
        db.add(notebook)
        db.commit()
        db.refresh(notebook)
        return 
    
    @staticmethod
    def get_notebooks(db :Session, user_id_:int):
        return db.query(Notebook) \
            .filter(Notebook.user_id == user_id_) \
            .all()    
        
