# 1. IMPORTS
# FastAPI: The framework that builds the web server.
# HTTPException: To send error messages (like "400 Bad Request") to the App.
from fastapi import FastAPI, HTTPException

# Pydantic: A tool that strictly checks if data is correct.
# It ensures the Flutter App sends exactly the data we expect.
from pydantic import BaseModel

# Uvicorn: The engine that runs this Python code as a web server.
import uvicorn

# 2. APP INITIALIZATION
# This creates the "Somy Ali" API application.
app = FastAPI(
    title="Somy Ali Brain",
    description="The backend API for the Somy Ali AI Psychologist",
    version="1.0.0"
)

# 3. DATA MODELS (The "Contracts")
# These classes define the "Shape" of the data. 
# If Flutter sends data that doesn't match this shape, FastAPI rejects it automatically.

class UserMessage(BaseModel):
    user_id: str  # We need to know WHO is talking (for memory later)
    text: str     # The actual message (e.g., "I feel sad")

class AIResponse(BaseModel):
    text: str          # The words Somy says back
    emotion: str       # The facial expression for Unity (happy, sad, neutral, concern)
    audio_url: str     # Link to the voice file (Empty for now)
    is_safe: bool      # A flag to tell the App if the topic was safe or blocked

# 4. SAFETY LOGIC (M4's Territory)
# Ideally, this would be in a separate file (safety.py), but we put it here for Week 1 simplicity.
def check_safety(user_text: str) -> bool:
    """
    Simple keyword check. 
    Returns False if dangerous words are found.
    """
    danger_words = ["die", "kill", "suicide", "hurt myself", "end it"]
    
    # Check if any danger word is in the user's text (case insensitive)
    for word in danger_words:
        if word in user_text.lower():
            return False  # DANGER DETECTED
            
    return True # SAFE

# 5. API ENDPOINTS (The "Doors")

@app.get("/")
def health_check():
    """
    A simple check to see if the server is online.
    Open http://localhost:8000/ in your browser to see this.
    """
    return {"status": "Somy is awake and listening.", "version": "1.0.0"}

@app.post("/chat", response_model=AIResponse)
def chat_endpoint(message: UserMessage):
    """
    The Main Brain Function.
    1. Receives JSON from Flutter.
    2. Checks Safety.
    3. (Later) Runs RAG/LLM.
    4. Returns JSON to Flutter.
    """
    print(f"📩 Received from User {message.user_id}: {message.text}")

    # STEP A: Safety Check
    if not check_safety(message.text):
        print("🚨 SAFETY ALERT TRIGGERED")
        return AIResponse(
            text="I am hearing that you are in pain. Please contact a professional or call a helpline immediately. I cannot continue this specific conversation.",
            emotion="concern",
            audio_url="",
            is_safe=False
        )

    # STEP B: The AI Logic (Week 1 Dummy)
    # In Week 2, we will replace this with LangGraph + Llama 3.1
    fake_ai_reply = f"I hear you saying: '{message.text}'. Tell me more about that. (Note: AI Brain is not connected yet)"
    
    # STEP C: Return the package to Flutter
    return AIResponse(
        text=fake_ai_reply,
        emotion="neutral",  # Default emotion
        audio_url="",       # No audio in Week 1
        is_safe=True
    )

# 6. SERVER RUNNER
# This block runs if you type 'python main.py' in the terminal.
if __name__ == "__main__":
    print("🚀 Starting Somy Ali Server...")
    # host="0.0.0.0" allows other devices on the network to see it (crucial for Ngrok)
    uvicorn.run(app, host="0.0.0.0", port=8000)