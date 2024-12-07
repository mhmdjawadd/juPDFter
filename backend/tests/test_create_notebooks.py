# test_create_notebook.py
import os
import sys
import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
import nbformat
import json

# Add root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.chatgpt_api_service import ChatGPTAPIService

@pytest.mark.real_api
def test_real_create_notebooks():
    """Test notebook creation with real API calls"""
    
    api_key = "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"  

    # Mock database session
    mock_db = Mock(spec=Session)
    
    # Initialize service
    api_service = ChatGPTAPIService(
        api_key=api_key,
        user_id=1,
        db=mock_db
    )
    
    # Test content
    sample_text = """
    Deep Learning is a subset of machine learning that uses neural networks
    with multiple layers. These networks can automatically learn representations
    from data without explicit feature engineering. Key applications include
    computer vision, natural language processing, and reinforcement learning.
    """
    
    try:
        # Create notebooks
        result = api_service.create_notebooks(sample_text)
        
            
        print("\n=== Notebook Creation Results ===")
        print(f"Status: {result['status']}")
        
        # Verify basic structure
        assert result["status"] == "success", f"Failed with: {result.get('message', '')}"
        
        # Check if notebook was saved
        save_calls = mock_db.add.call_args_list
        print(f"\nNumber of notebooks saved: {len(save_calls)}")
        
        # Print notebook details
        for i, call in enumerate(save_calls):
            notebook = call[0][0]  # Get notebook object from call args
            print(f"\nNotebook {i+1}:")
            print(f"Topic: {notebook.topic}")
            
            # Parse notebook content
            nb_content = nbformat.reads(notebook.content, as_version=4)
            print(f"Number of cells: {len(nb_content.cells)}")
            
            # Print cell types distribution
            cell_types = {}
            for cell in nb_content.cells:
                cell_types[cell.cell_type] = cell_types.get(cell.cell_type, 0) + 1
            print("Cell types distribution:", cell_types)
            
            # Assertions for notebook structure
            assert len(nb_content.cells) > 0, "Notebook has no cells"
            assert any(cell.cell_type == "markdown" for cell in nb_content.cells), "No markdown cells found"
            assert any(cell.cell_type == "code" for cell in nb_content.cells), "No code cells found"
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])