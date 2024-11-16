from typing import Dict
import requests
from sqlalchemy.orm import Session
from .models.notebook import Notebook
from .database import get_db


class NotebookAPILayer:
    def __init__(self, api_key: str, db: Session):
        self.api_key = api_key
        self.db = db
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.notebook_instructions = self._load_notebook_instructions()

    def _load_notebook_instructions(self) -> str:
        """Load notebook creation instructions from notebook_commands.txt"""
        try:
            with open('notebook_commands.txt', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return """Create a comprehensive study notebook that includes:
                     1. Main topic overview
                     2. Key concepts and definitions
                     3. Important examples
                     4. Practice questions
                     5. Summary points"""  # Default instructions

    def create_and_store_notebook(self, topic: str, file_id: str) -> Dict:
        """Generate a study notebook and store it in the database"""
        try:
            # Generate notebook content
            notebook_result = self._generate_notebook(topic)
            
            if notebook_result["status"] != "success":
                return notebook_result

            # Store in database
            notebook = Notebook(
                topic=topic,
                content=notebook_result["notebook"],
                file_id=file_id
            )
            
            self.db.add(notebook)
            self.db.commit()
            self.db.refresh(notebook)

            return {
                "status": "success",
                "topic": topic,
                "notebook_id": notebook.id,
                "notebook": notebook_result["notebook"]
            }

        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Failed to store notebook: {str(e)}"}

    def _generate_notebook(self, topic: str) -> Dict:
        """Generate notebook content using OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"{self.notebook_instructions}\n\nTopic: {topic}"
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are an expert educator creating detailed study materials."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2500
            }

            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            return {
                "status": "success",
                "notebook": response.json()["choices"][0]["message"]["content"]
            }

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"API request failed: {str(e)}"} 