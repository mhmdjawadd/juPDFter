import unittest
import openai

class TestOpenAIAPIKey(unittest.TestCase):
    def test_api_key_validity(self):
        api_key = "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"
        
        openai.api_key = api_key
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            self.assertTrue(response.choices, "No response received from API.")
            print("✅ API key is working!")
        except openai.error.OpenAIError as e:
            self.fail(f"API key test failed: {e}")

if __name__ == "__main__":
    unittest.main()