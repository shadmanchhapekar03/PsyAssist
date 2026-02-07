# FILE: voice_manager.py
# RESPONSIBILITY: M1 (Architect)
# STATUS: Week 5 (TTS Integration - Switched to OpenAI)

import os
from openai import OpenAI
import uuid

# --- CONFIGURATION ---
# Get this from https://platform.openai.com/
OPENAI_API_KEY = os.getenv("YOUR_OPENAI_API_KEY") 

# Directory to save audio files
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Initialize Client
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"⚠️ OpenAI Client Init Failed: {e}")
    client = None

def generate_audio(text: str) -> str:
    """
    Generates speech from text using OpenAI TTS.
    Returns the relative path to the saved audio file.
    """
    if not text or not client:
        print("⚠️ TTS Skipped: No text or OpenAI Client.")
        return ""

    try:
        response = client.audio.speech.create(
            model="tts-1",       # "tts-1" is fast, "tts-1-hd" is higher quality
            voice="shimmer",     # Options: alloy, echo, fable, onyx, nova, shimmer
            input=text
        )
        
        # Generate a unique filename
        filename = f"speech_{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        # Save to file
        response.stream_to_file(filepath)
        
        print(f"🔊 Audio generated: {filename}")
        # Return relative path for frontend
        return f"/static/audio/{filename}"
            
    except Exception as e:
        print(f"❌ OpenAI TTS Exception: {e}")
        return ""