from typing import Dict
from sqlalchemy.orm import Session
import os , nbformat , json , requests , re , uuid
from models import Notebook

class ChatGPTAPIService:
    def __init__(self, api_key: str,user_id : int, db: Session = None):
        self.api_key = api_key
        self.user_id=user_id
        self.db = db
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.topic_prompt = self._load_topic_prompt()

    def _load_topic_prompt(self) -> str:
        """Load topic prompt from get_topics_prompt.txt file"""
        try:
            prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'topics_prompt.txt')
            with open(prompt_path, 'r') as f:
                return "\n".join(line.strip() for line in f.readlines() if line.strip())
        except FileNotFoundError:
            return "Please extract the main topics from this text"  # Default prompt if file not found

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
        """args: string with the intial raw text
        returns: dictionary with the main ideas , summary and subtopics extracted from the text
        format : [
        {"Main Idea": ..., "Summary": ..., "Subtopics": [
            {"Subtopic": ... , "Summary": ... , "Example": ...},
            {"Subtopic": ... , "Summary": ... , "Example": ...}
            ]
        }
        ]
        """
        response = self._send_to_api(file_content, self.topic_prompt)
        
        if response["status"] == "error":
            return response
        
        try:
            topics_content = response["response"]["choices"][0]["message"]["content"]
            
            # Extract the JSON part by removing the ```json prefix and suffix
            json_content = re.search(r'```json\n(.*?)```', topics_content, flags=re.DOTALL)

            # Parse the JSON content
            if json_content:
                json_content = json_content.group(1).strip()
                json_parsed = json.loads(json_content)
                main_ideas = json_parsed["main_ideas"]

                return {
                    "status": "success",
                    "main_ideas": main_ideas
                }
            else:
                return {"status": "error",
                "message":"No valid JSON content found between ```json and ```."}
            
            
        except (KeyError, IndexError) as e:
            return {
                "status": "error",
                "message": f"Failed to extract topics: {str(e)}"
            }

    def _get_content_for_subtopic(self, topic: str, subtopic: str , sub_example :str , sub_summary :str) -> Dict:
        content_prompt = (
    f"for the main topic '{topic}' , i want you to create a jupyter notebook file where you craete minimum of 2 but maximum of 4 'markdown' files but with minimum of 5 and maximum of 8 'code' cells regarding the subtopic and its examples. let the output be in JSON format.\n\n"
    "please do not include anyinformation what so ever about the main topic since it is already annotated .Include the following subtopics with their details:\n\n" +
    "\n".join(
        [
            f"Subtopic: {subtopic}\n"
            f"   - Summary: {sub_summary}\n"
            f"   - Example: {sub_example}\n"
        ]
    )
        )
        

        response = self._send_to_api("", content_prompt)

        if response["status"] == "error":
            return response

        try:
            subtopic_content = response["response"]["choices"][0]["message"]["content"]
            if not subtopic_content:
                return {
                    "status": "error",
                    "message": f"API returned empty content for subtopic '{subtopic}'."
                }
            
            
            # Extract JSON content between ```json and ```
            match = re.search(r'```json(.*?)```', subtopic_content, re.DOTALL)
            if match:
                json_content = match.group(1).strip()
            else:
                return {
                    "status": "error",
                    "message": "Failed to extract JSON content from the response."
                }

            notebook_json = json.loads(json_content)
            return {
                "status": "success",
                "content": notebook_json
            }
        except(json.JSONDecodeError)  as e  :
            content_prompt=(f"i had a problem with this JSONdecode error with this error {str(e)} for this file, please fix it {json_content}")
            response = self._send_to_api("", content_prompt)
            if response["status"] == "error":
                return response

            try:
                subtopic_content = response["response"]["choices"][0]["message"]["content"]
                if not subtopic_content:
                    return {
                        "status": "error",
                        "message": f"API returned empty content for subtopic '{subtopic}'."
                    }
                
                
                # Extract JSON content between ```json and ```
                match = re.search(r'```json(.*?)```', subtopic_content, re.DOTALL)
                if match:
                    json_content = match.group(1).strip()
                else:
                    return {
                        "status": "error",
                        "message": "Failed to extract JSON content from the response."
                    }

                notebook_json = json.loads(json_content)
                return {
                    "status": "success",
                    "content": notebook_json
                }
            except (KeyError, IndexError,requests.exceptions.RequestException) as e:
                exception_type = type(e).__name__
                return {
                    "status": "error",
                    "message": f"Failed to extract content for subtopic due to a {exception_type} : {str(e)}"
                }
        except (KeyError, IndexError,requests.exceptions.RequestException) as e:
            exception_type = type(e).__name__
            return {
                "status": "error",
                "message": f"Failed to extract content for subtopic due to a {exception_type} : {str(e)}"
            }

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

    def create_notebooks(self, text: str) -> Dict:
        """Process text to extract topics, subtopics, and create notebooks."""
        topics_response = self._get_topics(text)
        if topics_response["status"] == "error":
            return topics_response
        try:
            main_ideas = topics_response["main_ideas"]
            for main_idea in main_ideas:
                
                notebook_cells = []
                main_idea_title = main_idea["Main Idea"]
                main_idea_summary = main_idea["Summary"]
                print(f"Processing main_idea: {main_idea_title}")
                # Add main idea title and summary as markdown
                notebook_cells.append(nbformat.v4.new_markdown_cell(f"## {main_idea_title}"))
                notebook_cells.append(nbformat.v4.new_markdown_cell(main_idea_summary))

                for subtopic in main_idea["Subtopics"]:
                    print(f"Processing subtopic: {subtopic['Subtopic']}")
                    # Add subtopic title and summary as markdown
                    #notebook_cells.append(nbformat.v4.new_markdown_cell(f"### {subtopic['Subtopic']}"))
                    notebook_cells.append(nbformat.v4.new_markdown_cell(subtopic['Summary']))
                    notebook_cells.append(nbformat.v4.new_markdown_cell(subtopic['Example']))

                    # Get content for subtopic
                    content_response = self._get_content_for_subtopic(
                        main_idea_title, subtopic['Subtopic'],subtopic['Example'],subtopic['Summary']
                    )
                    
                    if content_response["status"] == "success":
                        for cell_data in content_response.get('content', {}).get('cells', []):
                            if cell_data.get('cell_type') == 'markdown':
                                notebook_cells.append(nbformat.v4.new_markdown_cell(source=''.join(cell_data.get('source', []))))
                            elif cell_data.get('cell_type') == 'code':
                                notebook_cells.append(
                                    nbformat.v4.new_code_cell(
                                        source=''.join(cell_data.get('source', [])),
                                        execution_count=None,
                                        outputs=[],
                                        metadata=cell_data.get('metadata', {})
                                    )
                                )
                            
                    else:
                        return {
                            "status": "error",
                            "message": f"Failed to get content for subtopic  while reading cells from api'{subtopic['Subtopic']}': {content_response.get('message', '')}"
                        }
                # Assemble and save the notebook
                notebook_content = nbformat.v4.new_notebook()
                notebook_content.cells = notebook_cells  
                notebook_content.metadata = {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3"
                    },
                    "language_info": {
                    "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.8.5"
                    }
                }
                notebook_content.nbformat = 4
                notebook_content.nbformat_minor = 5
                
                print("saving notebook")
                self._save_notebook(main_idea_title, notebook_content)
                
                

            return {"status": "success", 
                    "message": "Notebooks created successfully"}

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process and create notebooks: {str(e)}"
            }
