import PyPDF2
from docx import Document
import os
import time
import uuid
from typing import Dict, Optional

class FileProcessor:
    def __init__(self, storage_dir: str = "processed_files"):
        """Initialize FileProcessor with a storage directory."""
        self.storage_dir = storage_dir
        self._ensure_storage_exists()
        self.supported_extensions = {'.pdf', '.docx', '.doc', '.txt'}
        
    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist."""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def process_file(self, file_path: str) -> Dict[str, str]:
        """
        Process the input file and store its text content.
        Returns a dictionary with status and file_id or error message.
        """
        if not os.path.exists(file_path):
            return {"status": "error", "message": "File not found"}

        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in self.supported_extensions:
            return {"status": "error", "message": "Unsupported file type"}

        try:
            extracted_text = self._extract_text(file_path, file_extension)
            if extracted_text is None:
                return {"status": "error", "message": "Text extraction failed"}

            # Generate a unique file ID using UUID
            file_id = f"{os.path.splitext(os.path.basename(file_path))[0]}_{str(uuid.uuid4())}"
            
            # Store the extracted text
            stored_path = self._store_text(extracted_text, file_id)
            
            return {"status": "success", "file_id": file_id}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _extract_text(self, file_path: str, extension: str) -> Optional[str]:
        """Extract text from the file based on its extension."""
        try:
            if extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif extension in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            elif extension == '.txt':
                return self._read_text_file(file_path)
            return None
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            return None

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def _read_text_file(self, file_path: str) -> str:
        """Read text from TXT file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _store_text(self, text: str, file_id: str) -> str:
        """Store the extracted text in a file."""
        output_path = os.path.join(self.storage_dir, f"{file_id}.txt")
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(text)
        return output_path

    def get_text(self, file_id: str) -> Dict[str, str]:
        """Retrieve the stored text for a given file_id."""
        try:
            file_path = os.path.join(self.storage_dir, f"{file_id}.txt")
            if not os.path.exists(file_path):
                return {"status": "error", "message": "File not found"}

            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return {"status": "success", "text": text}
        except Exception as e:
            return {"status": "error", "message": str(e)} 