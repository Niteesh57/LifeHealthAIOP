"""
Voice Agent - Medical Speech-to-Text using Google MedASR
WebSocket endpoint to receive audio, transcribe using google/medasr, 
and return text. Runs on GPU if available.
"""
import io
import logging
import numpy as np
import torch
import librosa
from transformers import pipeline
import logging
import numpy as np
import torch
import librosa
import io

logger = logging.getLogger(__name__)

from app.agent.LLM.llm import MEDASR_PATH

from app.agent.LLM.llm import get_medasr_chain

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000

def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe raw audio bytes (WAV / raw PCM) to text using MedASR pipeline from llm.py.
    """
    medasr = get_medasr_chain()
    
    # ─── 1. Decode Audio to Numpy (32-bit float @ 16kHz) ───
    speech = None
    
    # Try detecting WAV header
    is_wav = audio_bytes.startswith(b'RIFF')
    
    if is_wav:
        try:
            # Load with librosa (supports WAV, WebM if codecs exist)
            speech, _ = librosa.load(io.BytesIO(audio_bytes), sr=SAMPLE_RATE)
        except Exception:
            pass

    if speech is None:
        # Fallback: Treat as Raw 16-bit PCM @ 16kHz
        try:
            raw = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            if len(raw) == 0: return ""
            
            # Resample if needed (though we expect 16kHz from frontend now)
            if SAMPLE_RATE != 16000:
                speech = librosa.resample(raw, orig_sr=SAMPLE_RATE, target_sr=16000)
            else:
                speech = raw
        except Exception as e:
            logger.error(f"Audio decoding failed: {e}")
            return ""

    if len(speech) < 100: # specific tiny check
        return ""

    # ─── 2. Run Pipeline ───
    try:
        return medasr.transcribe(speech)
    except Exception as e:
        logger.error(f"Pipeline inference error: {e}")
        # Don't raise, just return empty to keep stream alive? 
        return ""


