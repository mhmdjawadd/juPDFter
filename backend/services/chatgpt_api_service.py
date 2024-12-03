from typing import Dict
import requests
from sqlalchemy.orm import Session
import os
from models import Notebook

class ChatGPTAPIService:
    def __init__(self, api_key: str,user_id : int, db: Session = None):
        self.api_key = api_key
        self.user_id=user_id
        self.db = db
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.topic_prompt = self._load_topic_prompt()
        self.notebook_prompt=self._load_notebook_prompt() 

    def _load_topic_prompt(self) -> str:
        """Load topic prompt from get_topics_prompt.txt file"""
        try:
            prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'topics_prompt.txt')
            with open(prompt_path, 'r') as f:
                return "\n".join(line.strip() for line in f.readlines() if line.strip())
        except FileNotFoundError:
            return "Please extract the main topics from this text"  # Default prompt if file not found

    def _load_notebook_prompt(self) -> str:
        """Load notebook prompt from get_notebook_prompt.txt file"""
        try:
            prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'notebook_prompt.txt')
            with open(prompt_path, 'r') as f:
                return "\n".join(line.strip() for line in f.readlines() if line.strip())
        except FileNotFoundError:
            return "Please create a study notebook from this text"  # Default prompt if file not found  

    def _send_to_api(self, text: str , wanted_prompt:str) -> Dict:
        """Send text with specific command to OpenAI API
        Args:
            text (str): Text to send to the API where it is processed by FileProcessorService at app level
            wanted_prompt (str): custom prompt to send to the API
        Returns:
            Dict: Response from the API
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"{wanted_prompt}\n\nText: {text}"
            
            payload = {
                "model": "gpt-4o",
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

    def _get_notebook(self, topic: str) -> Dict:
        """Get Jupyter notebook content """
        # 1. Send to API and get JSON response
        response = self._send_to_api(topic, self.notebook_prompt)
        
        if response["status"] == "error":
            return response
        
        try:
            # 2. Extract the notebook JSON from the nested API response
            notebook_content = response["response"]["choices"][0]["message"]["content"]
            
            # 3. Return the notebook content for further processing
            return {
                "status": "success",
                "notebook_content": notebook_content
            }
            
        except (KeyError, IndexError) as e:
            return {
                "status": "error",
                "message": f"Failed to extract notebook content: {str(e)}"
            }

    def _get_topics(self, file_content: str) -> Dict:
        """Get main topics from the text
        Args:
            text (str): Text to extract topics from
        Returns:
            Dict: Contains status and list of topics
        """
        # 1. Send to API and get response
        response = self._send_to_api(file_content, self.topic_prompt)
        
        if response["status"] == "error":
            return response
        
        try:
            # 2. Extract the topics from the API response
            topics_content = response["response"]["choices"][0]["message"]["content"]
            
            # 3. Return the topics content
            return {
                "status": "success",
                "topics": topics_content
            }
            
        except (KeyError, IndexError) as e:
            return {
                "status": "error",
                "message": f"Failed to extract topics: {str(e)}"
            }

    def process_text_and_create_notebooks(self, text: str) -> Dict:
        """Process text to extract topics and create notebooks for each topic
        Args:
            text (str): Text to process , it is gicen as a file parsed format
            user_id (int): Current user's ID
        Returns:
            Dict: Status and list of created notebooks
        """

        # 1. Get topics from text
        topics_response = self._get_topics(text)
        if topics_response["status"] == "error":
            return topics_response
            
        try:
            
            
            # 3. Process each topic and create a notebook
            topics = topics_response["topics"]
            for topic in topics.split('\n'):  # Assuming topics are newline-separated
                if not topic.strip():  # Skip empty lines
                    continue
                    
                # Get notebook for this topic
                notebook_response = self._get_notebook(topic)
                if notebook_response["status"] == "error":
                    continue
                
                title = topic.split('.')[0].strip()  # Get everything before the first period
                # Create filename from topic (sanitize the topic string for filename)
                safe_topic = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_topic}_{self.user_id}.ipynb"
                
                # Save notebook to user's directory
                try:
                    
                    # Save notebook content and metadata using the service
                    notebook = Notebook(
                        user_id=self.user_id,
                        content=notebook_response["notebook_content"],
                        topic=filename
                    )
                    
                    self.db.add(notebook)
                    self.db.commit()
                
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Failed to save notebook for topic {topic}: {str(e)}"
                    }
            # 4. Return success with list of created notebooks
            return {
                "status": "success",
                "message":"Notebooks created successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process text and create notebooks: {str(e)}"
            }

    