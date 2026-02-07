# FILE: main.py
# RESPONSIBILITY: M1 (Architect)
# STATUS: Week 2 Integration (LangGraph Connected)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from langchain_core.messages import HumanMessage, AIMessage
from fastapi.staticfiles import StaticFiles 
import os
from fastapi.middleware.cors import CORSMiddleware

# --- IMPORT THE BRAIN ---
# This imports the compiled graph from your 'agent_graph.py' file
# Make sure agent_graph.py is in the same folder as this file!
try:
    from agent_graph import app_graph
    print("✅ LangGraph successfully imported.")
except ImportError:
    print("❌ CRITICAL ERROR: Could not import 'app_graph' from 'agent_graph.py'.")
    print("   Make sure agent_graph.py exists and has no syntax errors.")
    app_graph = None

# --- IMPORT MEMORY MANAGER (NEW) ---
# This connects to the SQLite database logic
try:
    from SQlite.memory_manager import load_chat_history, save_chat_history, get_user_threads, delete_thread_history
    print("✅ Memory Manager successfully imported.")
except ImportError as e:
    print(f"❌ CRITICAL ERROR: Could not import 'memory_manager': {e}")
    # Define dummy functions so the app doesn't crash, but memory won't work
    def load_chat_history(user_id, limit=10): return []
    def save_chat_history(user_id, messages): pass

# --- IMPORT VOICE MANAGER ---
try:
    from voice_manager import generate_audio
    print("✅ Voice Manager imported.")
except ImportError as e:
    print(f"⚠️ Voice Manager not found. Audio will be disabled.")
    def generate_audio(text): return "" # Fallback

# --- APP SETUP ---
app = FastAPI(
    title="Somy Ali Brain V2", 
    description="AI Psychologist Backend with LangGraph Logic",
    version="2.3.0"
)

# --- MOUNT STATIC FILES ---
# This serves the generated audio files to the frontend
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define who can knock on the door
# ["*"] means "Anyone on the internet" (Perfect for testing)
origins = ["*"]

# Add the "Bouncer" (Middleware) to the App
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Who can connect? (Everyone)
    allow_credentials=True,       # Can they send cookies? (Yes)
    allow_methods=["*"],          # What methods? (GET, POST, etc.)
    allow_headers=["*"],          # What headers? (All of them)
)

# --- DATA MODELS (The Contract with Flutter) ---
class UserMessage(BaseModel):
    user_id: str  # e.g., "user_123"
    thread_id: str # <--- Required for multi-thread support
    text: str     # e.g., "I feel anxious"

class AIResponse(BaseModel):
    text: str          # The AI's reply
    emotion: str       # "happy", "sad", "concern", "neutral"
    audio_url: str     # (Empty for Week 2)
    is_safe: bool      # True/False

# --- ROUTES ---

@app.get("/")
def health_check():
    """Checks if the brain is online."""
    status = "Online" if app_graph else "Offline (Graph Missing)"
    return {"status": status, "version": "2.0.0"}

# --- NEW: GET THREADS LIST ---
@app.get("/threads/{user_id}")
def get_threads_endpoint(user_id: str):
    """Returns a list of all conversation IDs for a user (Sidebar History)."""
    try:
        threads = get_user_threads(user_id)
        return {"user_id": user_id, "threads": threads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# --- NEW: DELETE CHAT ---
@app.delete("/threads/{user_id}/{thread_id}")
def delete_chat_endpoint(user_id: str, thread_id: str):
    """Deletes a specific conversation history (Privacy/Cleanup)."""
    try:
        success = delete_thread_history(user_id, thread_id)
        if success:
            return {"status": "deleted", "thread_id": thread_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete chat (Thread not found or DB error)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=AIResponse)
async def chat_endpoint(message: UserMessage):
    """
    The Thinking Endpoint.
    1. Receives Text.
    2. Sends to LangGraph (Safety -> RAG -> Llama).
    3. Returns Final Answer.
    """
    print(f"\n📩 User: {message.user_id} | Thread: {message.thread_id} | Msg: {message.text}")

    if not app_graph:
        raise HTTPException(status_code=500, detail="AI Brain not loaded.")

    # 2. LOAD HISTORY (NEW)
    # We fetch the last 10 messages from SQLite for this user_id
    try:
        history = load_chat_history(message.user_id, message.thread_id, limit=20)
    except Exception as e:
        print(f"⚠️ Error loading history: {e}")
        history = [] # Fallback
    
    # 3. PREPARE INPUT
    current_human_message = HumanMessage(content=message.text)
    
    # Combine SQLite History + Current Message
    # LangGraph will now see the full context of the conversation
    full_conversation = history + [current_human_message]
    
    # 1. PREPARE INPUT STATE
    # We create the initial state dictionary that LangGraph expects
    initial_state = {
        "messages": full_conversation,
        "is_safe": True, # Default assumption
        "context": ""    # Empty context to start
    }

    # 2. RUN THE GRAPH (Thinking Process)
    try:
        # .invoke() runs the entire workflow from Start -> End
        final_state = app_graph.invoke(initial_state)
        
        # 3. EXTRACT RESULTS
        # Get the very last message added to the list (The AI's response)
        ai_message = final_state["messages"][-1]
        
        # Verify it IS an AI message (not just our own input back)
        if isinstance(ai_message, HumanMessage):
             # If the last msg is Human, it means AI didn't reply!
             response_text = "Error: I couldn't generate a response."
             was_safe = False
        else:
             response_text = ai_message.content
             was_safe = final_state.get("is_safe", True)
        
        # 4. SAVE MEMORY & GENERATE AUDIO
        audio_link = ""
        
        # 5. SAVE MEMORY (NEW)
        # If the conversation was safe, save the new turn (Human + AI) to SQLite
        # We define a helper to check if the message is a system error
        is_error_message = response_text.startswith("Error:") or response_text.startswith("System Error:")
        
        if was_safe and isinstance(ai_message, AIMessage) and not is_error_message:
            # We create a list of the NEW messages to save
            new_turn = [current_human_message, ai_message]
            save_chat_history(message.user_id, message.thread_id, new_turn) # <--- Pass thread_id
            
            # Generate Audio
            # We construct the relative path. Frontend should handle base URL.
            relative_path = generate_audio(response_text)
            if relative_path:
                audio_link = relative_path
        else:
            print("   🚫 Unsafe content. Not saving/generating audio.")

    except Exception as e:
        print(f"❌ Error during Graph Execution: {e}")
        response_text = "I am having trouble processing that right now. Please try again."
        was_safe = True
        audio_link = ""

    # 4. DETERMINE EMOTION (Simple Logic for Week 2)
    # If the graph marked it unsafe, look concerned. Otherwise, look neutral/warm.
    # (In Week 5, we can use an AI to pick the exact emotion)
    current_emotion = "concern" if not was_safe else "neutral"

    print(f"📤 Sending Response: {response_text[:50]}... | Audio: {audio_link}")

    # 5. RETURN TO FLUTTER
    return AIResponse(
        text=response_text,
        emotion=current_emotion,
        audio_url=audio_link,
        is_safe=was_safe
    )

if __name__ == "__main__":
    print("🚀 Starting Somy Ali Brain...")
    uvicorn.run(app, host="0.0.0.0", port=8000)