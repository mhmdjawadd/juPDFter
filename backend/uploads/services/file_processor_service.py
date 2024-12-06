import os
from werkzeug.datastructures import FileStorage
import PyPDF2
from docx import Document
class FileProcessorService:
    @staticmethod
    def process_file(file: FileStorage) -> str:
        """
        Process the uploaded file and extract its text content.
        
        Supports PDF, DOCX, and TXT files.
        
        Args:
            file (FileStorage): The uploaded file.
        
        Returns:
            str: Extracted text content.
        
        Raises:
            ValueError: If the file type is unsupported or if extraction fails.
        """
        filename = file.filename
        if not filename:
            raise ValueError("No file name provided.")
        
        # Extract file extension
        _, file_extension = os.path.splitext(filename.lower())
        
        if file_extension == '.pdf':
            return FileProcessorService._extract_text_from_pdf(file)
        elif file_extension == '.docx':
            return FileProcessorService._extract_text_from_docx(file)
        elif file_extension == '.txt':
            return FileProcessorService._extract_text_from_txt(file)
        else:
            raise ValueError(f"Unsupported file type: '{file_extension}'. Supported types are PDF, DOCX, and TXT.")
    
    @staticmethod
    def _extract_text_from_pdf(file: FileStorage) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file (FileStorage): The uploaded PDF file.
        
        Returns:
            str: Extracted text.
        
        Raises:
            ValueError: If the PDF is invalid or contains no extractable text.
        """
        try:
            pdf_reader = PyPDF2.PdfReader(file.stream)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    print(f"Warning: No text found on page {page_num}.")
            
            extracted_text = text.strip()
            if not extracted_text:
                raise ValueError("The uploaded PDF is empty or contains no extractable text.")
            
            return extracted_text
        except PyPDF2.errors.PdfReadError:
            raise ValueError("The uploaded file is not a valid PDF.")
        
    @staticmethod
    def _extract_text_from_docx(file: FileStorage) -> str:
        """
        Extract text from a DOCX file.
        
        Args:
            file (FileStorage): The uploaded DOCX file.
        
        Returns:
            str: Extracted text.
        
        Raises:
            ValueError: If extraction fails or contains no text.
        """
        try:
            document = Document(file.stream)
            text = "\n".join([para.text for para in document.paragraphs])
            extracted_text = text.strip()
            if not extracted_text:
                raise ValueError("The uploaded DOCX is empty or contains no extractable text.")
            return extracted_text
        except Exception as e:
            raise ValueError(f"Failed to process DOCX file: {e}")
        
    @staticmethod
    def _extract_text_from_txt(file: FileStorage) -> str:
        """
        Extract text from a TXT file.
        
        Args:
            file (FileStorage): The uploaded TXT file.
        
        Returns:
            str: Extracted text.
        
        Raises:
            ValueError: If extraction fails or contains no text.
        """
        try:
            stream = file.stream
            stream.seek(0)  # Ensure we're at the start of the file
            text = stream.read().decode('utf-8').strip()
            if not text:
                raise ValueError("The uploaded TXT file is empty.")
            return text
        except UnicodeDecodeError:
            raise ValueError("The TXT file contains non-UTF-8 characters.")
        except Exception as e:
            raise ValueError(f"Failed to process TXT file: {e}")

        