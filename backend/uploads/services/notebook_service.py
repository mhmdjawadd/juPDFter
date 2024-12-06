from sqlalchemy.orm import Session
from models import Notebook 

class NotebookService:
    
    @staticmethod
    def get_notebooks(db :Session, user_id_:int):
        return db.query(Notebook) \
            .filter(Notebook.user_id == user_id_) \
            .all()    
        
