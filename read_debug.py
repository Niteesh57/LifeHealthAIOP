import sys
import os
# Ensure stdout is utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Import the existing script or copy logic
from transformers import AutoProcessor

MODEL_PATH = r"C:\xampp\htdocs\opik_Backend\medgemma"

def run():
    print(f"Loading from {MODEL_PATH}...")
    try:
        processor = AutoProcessor.from_pretrained(MODEL_PATH)
        tokenizer = processor.tokenizer
        
        with open("read_debug_files.txt", "w", encoding="utf-8") as f:
            f.write(f"Special Tokens Map: {tokenizer.special_tokens_map}\n")
            
            candidates = ["<image>", "<|image|>", "<image_token>", "<|image_token|>", "<|image|>"]
            found = False
            for c in candidates:
                tid = tokenizer.convert_tokens_to_ids(c)
                f.write(f"Token '{c}' ID: {tid}\n")
                if tid != tokenizer.unk_token_id:
                    found = True
            
            if not found:
                f.write("Searching vocab for 'image'...\n")
                vocab = tokenizer.get_vocab()
                matches = [k for k in vocab.keys() if "image" in k]
                f.write(f"Vocab matches (first 20): {matches[:20]}\n")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
