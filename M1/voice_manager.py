# FILE: voice_manager.py
# RESPONSIBILITY: M1 (Architect)
# STATUS: Week 5 (TTS Integration)

import os
import requests
import uuid

# --- CONFIGURATION ---
# Get this from https://elevenlabs.io/
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY") 
# This is a placeholder Voice ID (Rachel). Replace with the one you want.
VOICE_ID = os.getenv("VOICE_ID")

# Directory to save audio files
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def generate_audio(text: str) -> str:
    """
    Generates speech from text using ElevenLabs API.
    Returns the relative path to the saved audio file.
    """
    if not text or not ELEVENLABS_API_KEY:
        print("⚠️ TTS Skipped: No text or API Key.")
        return ""

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 401:
            print("🚫 ElevenLabs Unauthorized: Check API key or plan.")
            return ""

        if response.status_code == 200:
            # Generate a unique filename
            filename = f"speech_{uuid.uuid4()}.mp3"
            filepath = os.path.join(AUDIO_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            print(f"🔊 Audio generated: {filename}")
            # Return the path that the frontend will use to access the file
            # We assume the API mounts 'static' at the root
            return f"/static/audio/{filename}"
        else:
            print(f"❌ ElevenLabs Error: {response.status_code} - {response.text}")
            return ""
            
    except Exception as e:
        print(f"❌ TTS Exception: {e}")
        return ""