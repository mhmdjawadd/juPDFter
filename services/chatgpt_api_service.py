from typing import Dict
import requests
from sqlalchemy.orm import Session
import os
from models import Notebook
import nbformat

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
            
            system_prompt = (
            "You are an expert educator and data scientist specializing in creating detailed and comprehensive "
            "Jupyter notebooks for advanced topics. When provided with a topic, you generate a well-structured "
            "notebook that includes explanations, code examples, data visualizations, and exercises. Ensure that "
            "**the first sentence of the notebook is the title**. "
            "Make sure the notebook is thorough, suitable "
            "for graduate-level studies, and covers the topic in depth."
        )

            payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt},
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

    def _get_subtopics(self, topic: str) -> Dict:
        """Get subtopics from a main topic."""
        # Define a prompt to extract subtopics
        subtopic_prompt = (
            f"I have a topic about {topic}. I want you to give me an output in text where you provide "
            "subtopics about the topic I just gave you, so that I can include it in a Jupyter notebook "
            "where it would be easier for learners to learn from. Remember, no .ipynb files; I just want the topics."
            "i want the text to be seperated by a new line and be raw text only"
        )

        response = self._send_to_api("", subtopic_prompt)

        if response["status"] == "error":
            return response

        try:
            # Extract the subtopics from the API response
            subtopics_content = response["response"]["choices"][0]["message"]["content"]

            # Return the subtopics content
            return {
                "status": "success",
                "subtopics": subtopics_content
            }

        except (KeyError, IndexError) as e:
            return {
                "status": "error",
                "message": f"Failed to extract subtopics: {str(e)}"
            }
    
    def _get_content_for_subtopic(self, topic: str, subtopic: str) -> Dict:
        """Generate content for a subtopic within the given topic."""
        content_prompt = (
            f"Please provide an educational explanation on the subtopic '{subtopic}' under the main topic '{topic}'. "
            "Include examples, especially those present in the original file, to illustrate the concepts. "
            "The content should be suitable for inclusion in a Jupyter notebook cell for learners to understand easily."
        )

        response = self._send_to_api("", content_prompt)

        if response["status"] == "error":
            return response

        try:
            subtopic_content = response["response"]["choices"][0]["message"]["content"]
            return {
                "status": "success",
                "content": subtopic_content
            }

        except (KeyError, IndexError) as e:
            return {
                "status": "error",
                "message": f"Failed to extract content for subtopic: {str(e)}"
            }

    def _assemble_notebook(self, title: str, cells: list) -> nbformat.NotebookNode:
        """Assemble notebook content using nbformat."""
        nb = nbformat.v4.new_notebook()
        nb_cells = []

        # Add the title as the first cell
        nb_cells.append(nbformat.v4.new_markdown_cell(f"# {title}"))

        # Add the rest of the cells
        for cell in cells:
            if cell["type"] == "markdown":
                nb_cells.append(nbformat.v4.new_markdown_cell(cell["content"]))
            elif cell["type"] == "code":
                nb_cells.append(nbformat.v4.new_code_cell(cell["content"]))

        nb['cells'] = nb_cells
        return nb

    def _save_notebook(self, topic_title: str, notebook_content: nbformat.NotebookNode):
        """Save the notebook content to the database."""
        try:
            notebook_json = nbformat.writes(notebook_content)

            safe_topic = "".join(c for c in topic_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_topic}_{self.user_id}.ipynb"

            notebook = Notebook(
                user_id=self.user_id,
                content=notebook_json,
                topic=filename
            )

            self.db.add(notebook)
            self.db.commit()

        except Exception as e:
            raise Exception(f"Failed to save notebook for topic '{topic_title}': {str(e)}")

    def process_text_and_create_notebooks(self, text: str) -> Dict:
        """Process text to extract topics, subtopics, and create notebooks."""
        topics_response = self._get_topics(text)
        if topics_response["status"] == "error":
            return topics_response

        try:
            topics = topics_response["topics"]
            for topic_line in topics.split('\n'):
                topic = topic_line.strip()
                if not topic:
                    continue

                # Extract the main topic title
                topic_title = topic.split('.')[1].strip() if '.' in topic else topic

                # Get subtopics for this topic
                subtopics_response = self._get_subtopics(topic_title)
                if subtopics_response["status"] == "error":
                    continue

                subtopics = subtopics_response["subtopics"]

                # Generate content for each subtopic
                notebook_cells = []
                for subtopic_line in subtopics.split('\n'):
                    subtopic = subtopic_line.strip()
                    if not subtopic:
                        continue

                    content_response = self._get_content_for_subtopic(topic_title, subtopic)
                    if content_response["status"] == "error":
                        continue

                    subtopic_content = content_response["content"]

                    # Add the content as a cell
                    notebook_cells.append({
                        "type": "markdown",
                        "content": subtopic_content
                    })

                if not notebook_cells:
                    continue

                # Assemble the notebook
                notebook_content = self._assemble_notebook(topic_title, notebook_cells)

                # Save the notebook
                self._save_notebook(topic_title, notebook_content)

            return {
                "status": "success",
                "message": "Notebooks created successfully"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process text and create notebooks: {str(e)}"
            }