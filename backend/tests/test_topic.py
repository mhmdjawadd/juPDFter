# test_topic_real.py
import os
import pytest
from services.chatgpt_api_service import ChatGPTAPIService
import json 
@pytest.mark.real_api
def test_real_get_topics():
    """Test real API call to get topics. Requires OPENAI_API_KEY environment variable."""
    
    # Get API key from environment
    api_key = "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"  
    
    
    # Initialize service
    api_service = ChatGPTAPIService(api_key=api_key, user_id=1, db=None)
    
    message = (
    f"**CNNs (Convolutional Neural Networks):**\n"
    f"CNNs are a type of deep learning model primarily used for analyzing visual data. They work by using convolutional layers that apply filters to input data to capture spatial features like edges, textures, and patterns. Pooling layers in CNNs reduce dimensionality, making the model computationally efficient while retaining important information. They're commonly used in tasks like image recognition, object detection, and video processing. CNN architectures, like AlexNet, ResNet, and VGG, have revolutionized computer vision and enabled state-of-the-art performance across multiple domains.\n\n"
    f"**`java.util` Class:**\n"
    f"The `java.util` package in Java contains a collection of utility classes and interfaces that provide data structures (like `ArrayList`, `HashMap`, and `HashSet`), date and time utilities, random number generation, and more. It's a foundational package for handling common programming needs like collections, which simplify managing groups of objects. The package also includes classes like `Scanner` for user input and `Calendar` for date manipulations. Many modern Java applications rely heavily on the tools provided by this package to streamline development."
)


    try:
        # Make the API call
        result = api_service._get_topics(message)
        
        # Print full result
        print("\n=== API Response ===")
        print(f"Status: {result['status']}")
        print("\nFull Response:")
        print(result)
        
        # Basic validation
        assert result["status"] == "success"
        assert "main_ideas" in result
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise