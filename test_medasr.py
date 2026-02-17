from transformers import AutoProcessor, Wav2Vec2Processor
import torch

model_id = "google/medasr"

print(f"Attempting to load processor for {model_id}...")

try:
    processor = AutoProcessor.from_pretrained(model_id)
    print("Success with AutoProcessor")
except Exception as e:
    print(f"AutoProcessor failed: {e}")
    try:
        print("Attempting fallback to Wav2Vec2Processor...")
        processor = Wav2Vec2Processor.from_pretrained(model_id)
        print("Success with Wav2Vec2Processor")
    except Exception as e2:
        print(f"Wav2Vec2Processor failed: {e2}")
