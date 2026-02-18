from langchain_huggingface import HuggingFacePipeline
from transformers import AutoProcessor, AutoModelForCausalLM, AutoModel, pipeline
import torch
import os

# Local Model Paths
MEDASR_PATH = r"C:\xampp\htdocs\opik_Backend\medasr"
MEDGEMMA_PATH = r"C:\xampp\htdocs\opik_Backend\medgemma"
PATH_FOUNDATION_PATH = r"C:\xampp\htdocs\opik_Backend\path-foundation"
HEAR_PATH = r"C:\xampp\htdocs\opik_Backend\hear"

class MedVQA:
    def __init__(self):
        self.space_id = "nagireddy5/lifehealth"
        self.hf_token = os.getenv("HUGGINGFACE_API_KEY")
        print(f"Loading MedVQA from HF Space: {self.space_id}...")
        self.client = None
        
        try:
            from gradio_client import Client
            self.client = Client(self.space_id)
            print("MedVQA HF Space Client loaded.")
        except Exception as e:
            print(f"Warning: Could not connect to MedVQA Space {self.space_id}: {e}")

    def answer_question(self, question, image_path=None):
        if not self.client:
            try:
                from gradio_client import Client
                self.client = Client(self.space_id)
            except Exception as e:
                return f"Error: Model not connected. {e}"

        try:
            # API expects image_url (string) and question (string)
            # If image_path is provided, we assume it's a URL or handle upload?
            # User output says "image_url: str (optrional)".
            # If we have a local path but API wants URL, we have a problem unless gradio_client handles upload automatically
            # when passed to a Textbox component? Usually Textbox expects string.
            # However, docAgent passes a local path for downloaded images.
            # If the image was originally a URL, we should pass that URL.
            # Let's assume image_path might be a URL string if it starts with http.
            
            # If it is a local file path, gradio_client might not upload it for a Textbox input.
            # But let's check if the previous step downloaded it.
            
            image_url = image_path if image_path else None
            
            print(f"DEBUG: Sending to HF Space: question='{question}', image_url='{image_url}'")
            
            result = self.client.predict(
                image_url=image_url, 
                question=question, 
                api_name="/stream_answer" 
            )
            
            print(f"DEBUG: Space Response: {result}")
            return result
            
        except Exception as e:
            print(f"Inference Error: {e}")
            return f"Error processing request: {e}"

class PathFoundation:
    def __init__(self):
        self.model_id = PATH_FOUNDATION_PATH
        print(f"Loading PathFoundation from {self.model_id}...")
        try:
            self.model = AutoModel.from_pretrained(self.model_id, trust_remote_code=True, device_map="auto")
            print("PathFoundation loaded.")
        except Exception as e:
            print(f"Warning: Failed to load PathFoundation: {e}")

class HearModel:
    def __init__(self):
        self.model_id = HEAR_PATH
        print(f"Loading HeAR from {self.model_id}...")
        try:
            self.model = AutoModel.from_pretrained(self.model_id, trust_remote_code=True, device_map="auto")
            print("HeAR loaded.")
        except Exception as e:
            print(f"Warning: Failed to load HeAR: {e}")

class MedASR:
    def __init__(self):
        self.model_id = MEDASR_PATH
        self.pipeline = None
        print(f"Loading MedASR from {self.model_id}...")
        try:
             self.pipeline = pipeline(
                "automatic-speech-recognition", 
                model=self.model_id, 
                device=0 if torch.cuda.is_available() else -1,
                chunk_length_s=30,
                stride_length_s=5,
                trust_remote_code=True
            )
             print("MedASR Model loaded.")
        except Exception as e:
            print(f"Warning: Could not load MedASR from {self.model_id}: {e}")

    def transcribe(self, audio_input):
        if not self.pipeline: return ""
        return self.pipeline(audio_input)["text"]

# Singletons
llm_instance = None
path_instance = None
hear_instance = None
medasr_instance = None

def get_vqa_chain():
    global llm_instance
    if llm_instance is None:
        llm_instance = MedVQA()
    return llm_instance

def get_medasr_chain():
    global medasr_instance
    if medasr_instance is None:
        medasr_instance = MedASR()
    return medasr_instance

def get_path_foundation():
    global path_instance
    if path_instance is None:
        path_instance = PathFoundation()
    return path_instance

def get_hear_model():
    global hear_instance
    if hear_instance is None:
        hear_instance = HearModel()
    return hear_instance




