import os
from dotenv import load_dotenv
from gradio_client import Client

# Load environment variables
load_dotenv()

token = os.getenv("HUGGINGFACE_API_KEY")
print(f"Token found: {'Yes' if token else 'No'}")

def test_connection():
    try:
        # Try connecting without explicit token first, or check if 'hf_token' is valid for this version
        # Some versions might default to logged-in user or just don't need it if public.
        client = Client("nagireddy5/lifehealth")
        print("Connected.")
        
        question = "What is a common symptom of flu?"
        print(f"Testing prediction with question: '{question}' (no image)")
        
        # api_name="/stream_answer"
        result = client.predict(
            image_url="",
            question=question, 
            api_name="/stream_answer"
        )
        print(f"Response: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()
