import pytest , sys ,os
# Add root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.chatgpt_api_service import ChatGPTAPIService
@pytest.mark.real_api
def test_real_get_subtopic_content():
    """Test real API call to get subtopic content with actual OpenAI API."""
    
    api_key = "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"  

    # Initialize service
    api_service = ChatGPTAPIService(api_key=api_key, user_id=1, db=None)
    
    # Test parameters
    topic = "CNNs (Convolutional Neural Networks)"
    subtopic = "Convolutional Layers"
    Summary= "Convolutional layers are key components in CNNs that apply a set of filters to the input data to detect spatial features like edges, textures, and patterns, which help in understanding the visual structures in the data."
    Example= "In image recognition, a convolutional layer might use different filters to detect edges regarding horizontal, vertical, or diagonal orientations."
    
    
    try:
        # Make the API call
        result = api_service._get_content_for_subtopic(topic, subtopic,Example,Summary)
        
        # Print full result
        print(result)
        # Assertions
        assert result["status"] == "success"
        assert "content" in result
        assert "cells" in result["content"]
        
        # Verify cell structure
        cells = result["content"]["cells"]
        assert len(cells) > 0
        
        for cell in cells:
            assert "cell_type" in cell
            assert cell["cell_type"] in ["markdown", "code"]
            assert "source" in cell
            
            if cell["cell_type"] == "code":
                assert "outputs" in cell
                
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])