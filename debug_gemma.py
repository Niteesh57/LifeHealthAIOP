from transformers import AutoProcessor, AutoModelForCausalLM
import torch
from PIL import Image
import os

MODEL_PATH = r"C:\xampp\htdocs\opik_Backend\medgemma"

def debug_gemma():
    print(f"Loading from {MODEL_PATH}...")
    try:
        processor = AutoProcessor.from_pretrained(MODEL_PATH)
        # model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, trust_remote_code=True, device_map="auto") 
        # Skip loading model to save time/mem, just check processor/tokenizer
    except Exception as e:
        print(f"Failed to load: {e}")
        return

    print(f"Processor: {type(processor)}")
    tokenizer = processor.tokenizer
    print(f"Tokenizer: {type(tokenizer)}")
    
    # Check special tokens
    print(f"Special Tokens Map: {tokenizer.special_tokens_map}")
    
    # Check for <image>
    img_token = tokenizer.convert_tokens_to_ids("<image>")
    print(f"'<image>' ID: {img_token}")
    
    # Check for <|image|>
    img_token_pipe = tokenizer.convert_tokens_to_ids("<|image|>")
    print(f"'<|image|>' ID: {img_token_pipe}")
    
    # Try chat template
    print("\n--- Chat Template Test ---")
    messages = [
        {"role": "user", "content": [{"type": "image"}, {"type": "text", "text": "Describe this."}]}
    ]
    if hasattr(processor, "apply_chat_template"):
        try:
            prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
            print(f"Generated Prompt: {prompt}")
        except Exception as e:
            print(f"Template failed: {e}")
    
    # Try tokenization
    print("\n--- Tokenization Test ---")
    text_with_token = "<image> Describe this."
    inputs = processor(text=text_with_token, return_tensors="pt")
    print(f"Tokenized '<image> ...': {inputs.input_ids[0].tolist()}")

    # Compare with text processing
    text_only = "Describe this."
    inputs_text = processor(text=text_only, return_tensors="pt")
    print(f"Tokenized text only: {inputs_text.input_ids[0].tolist()}")

if __name__ == "__main__":
    debug_gemma()
