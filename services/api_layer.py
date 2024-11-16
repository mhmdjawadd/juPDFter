from .file_processor import FileProcessor
from typing import Dict, List
import requests
from sqlalchemy.orm import Session
from .notebook_api_layer import NotebookAPILayer


class APILayer:
    def __init__(self, api_key: str, storage_dir: str = "processed_files", db: Session = None):
        self.api_key = api_key
        self.file_processor = FileProcessor(storage_dir=storage_dir)
        self.notebook_api = NotebookAPILayer(api_key=api_key, db=db)
        self.db = db
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.commands = self._load_commands()

    def _load_commands(self) -> List[str]:
        """Load commands from commands.txt file"""
        try:
            with open('commands.txt', 'r') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            return ["Please extract topics from this text"]  # Default command if file not found

    def process_document(self, file_path: str) -> Dict:
        # Process the file and extract text
        process_result = self.file_processor.process_file(file_path)
        
        if process_result["status"] != "success":
            return {"status": "error", "message": f"File processing failed: {process_result['message']}"}

        # Get the extracted text
        text_result = self.file_processor.get_text(process_result["file_id"])
        
        if text_result["status"] != "success":
            return {"status": "error", "message": f"Text retrieval failed: {text_result['message']}"}

        # Process each command and collect responses
        all_responses = []
        for command in self.commands:
            response = self._send_to_api(text_result["text"], command)
            if response["status"] == "success":
                all_responses.append({
                    "command": command,
                    "response": response["response"]
                })
            else:
                return response  # Return error if any command fails

        return {
            "status": "success",
            "file_id": process_result["file_id"],
            "responses": all_responses
        }

    def _send_to_api(self, text: str, command: str) -> Dict:
        """Send text with specific command to OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"{command}\n\nText: {text}"
            
            payload = {
                "model": "gpt-4-turbo-128k",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that processes documents according to specific commands."},
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            return {
                "status": "success",
                "response": response.json()
            }

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"API request failed: {str(e)}"}

    def process_document_and_create_notebook(self, file_path: str) -> Dict:
        # First process the document as before
        result = self.process_document(file_path)
        
        if result["status"] != "success":
            return result

        # Extract topics from the responses
        topics = []
        for response in result["responses"]:
            if "keywords" in response["command"].lower() or "main topics" in response["command"].lower():
                topics = self._extract_topics(response["response"])
                break

        if not topics:
            return {
                "status": "error",
                "message": "No topics found in the document analysis"
            }

        # Create and store notebooks for each topic
        notebooks = []
        for topic in topics:
            notebook_result = self.notebook_api.create_and_store_notebook(
                topic=topic,
                file_id=result["file_id"]
            )
            if notebook_result["status"] == "success":
                notebooks.append(notebook_result)

        return {
            "status": "success",
            "file_id": result["file_id"],
            "original_analysis": result["responses"],
            "notebooks": notebooks
        }

    def _extract_topics(self, response: str) -> List[str]:
        """Extract topics from the response text"""
        # Implement your logic to extract topics from the response text
        # For example, you can use regular expressions or a topic extraction library
        # Here, we'll use a simple approach to split the response text by spaces
        return response.split()