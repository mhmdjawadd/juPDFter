from .file_processor import FileProcessor
from typing import Dict, List
import requests


class APILayer:
    def __init__(self, api_key: str, storage_dir: str = "processed_files"):
        self.api_key = api_key
        self.file_processor = FileProcessor(storage_dir=storage_dir)
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
                "model": "gpt-3.5-turbo",
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