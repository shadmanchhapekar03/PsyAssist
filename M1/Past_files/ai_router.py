from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from typing import TypedDict

# --- CONFIGURATION ---
LLM_MODEL = "llama3.1"

# --- SETUP MODEL ---
# remove comments later

# try:
#     llm = ChatOllama(model=LLM_MODEL, temperature=0.0) # Low temp for strict classification
# except Exception as e:
#     print(f"❌ Error connecting to Ollama for Router: {e}")
#     llm = None

# --- ROUTER PROMPT ---
ROUTER_SYSTEM_PROMPT = """
You are an expert Triage System for a Mental Health AI.
Your job is to classify the user's input into exactly ONE of the following categories.

CATEGORIES:
1. **ANXIETY** (Panic, worry, stress, fear, nervousness)
2. **DEPRESSION** (Sadness, hopelessness, low energy, despair)
3. **TRAUMA** (PTSD, abuse, flashbacks, past events)
4. **ANGER** (Rage, frustration, irritability)
5. **GRIEF** (Loss, death, mourning, breakup)
6. **SLEEP** (Insomnia, nightmares, trouble sleeping)
7. **ADDICTION** (Substance use, drinking, drugs, dependency)
8. **CHILD** (Parenting, issues with children/teens)
9. **GENERAL** (Everything else, or if unsure)

INSTRUCTIONS:
- Analyze the user's text carefully.
- Return ONLY the category word (e.g., "ANXIETY"). 
- Do not write a sentence. Do not add punctuation.
"""

# def router_node(state: dict):
#     """
#     Worker: The AI Traffic Cop.
#     Decides which manual to read based on meaning, not just keywords.
#     """
#     if not llm:
#         return {"filter_category": "general"}
        
#     user_text = state["messages"][-1].content
    
#     # Construct the prompt
#     conversation = [
#         SystemMessage(content=ROUTER_SYSTEM_PROMPT),
#         HumanMessage(content=f"User Input: {user_text}")
#     ]
    
#     try:
#         # Ask the AI
#         print("🚦 Router is thinking...")
#         response = llm.invoke(conversation)
#         category = response.content.strip().lower()
        
#         # Validate output (Safety fallback)
#         valid_categories = ["anxiety", "depression", "trauma", "anger", "grief", "sleep", "addiction", "child", "general"]
        
#         # Simple mapping for common AI mis-outputs
#         if "panic" in category: category = "anxiety"
#         if "sad" in category: category = "depression"
        
#         if category not in valid_categories:
#             print(f"   ⚠️ Router returned invalid category '{category}'. Defaulting to 'general'.")
#             category = "general"
            
#         print(f"   ✅ Router Output: {category.upper()}")
#         return {"filter_category": category}

#     except Exception as e:
#         print(f"❌ Router Error: {e}")
#         return {"filter_category": "general"}

def router_node(state: dict):
    """
    Worker: The Traffic Cop (Lightweight Version).
    Decides which manual to read based on keywords to save RAM.
    """
    user_text = state["messages"][-1].content.lower()
    
    # Default category
    category = "general"

    # --- LIGHTWEIGHT LOGIC (No LLM) ---
    if "child" in user_text or "teen" in user_text or "son" in user_text or "daughter" in user_text:
        category = "child"
    elif "panic" in user_text or "anxiety" in user_text or "worry" in user_text or "stress" in user_text:
        category = "anxiety"
    elif "sad" in user_text or "depress" in user_text or "hopeless" in user_text or "cry" in user_text:
        category = "depression"
    elif "trauma" in user_text or "ptsd" in user_text or "abuse" in user_text or "flashback" in user_text:
        category = "trauma"
    elif "anger" in user_text or "mad" in user_text or "rage" in user_text:
        category = "anger"
    elif "grief" in user_text or "loss" in user_text or "death" in user_text or "died" in user_text:
        category = "grief"
    elif "sleep" in user_text or "insomnia" in user_text or "awake" in user_text or "nightmare" in user_text:
        category = "sleep"
    elif "addiction" in user_text or "drug" in user_text or "alcohol" in user_text or "drink" in user_text:
        category = "addiction"

    print(f"🚦 Router (Lite) decided: '{category.upper()}'")
    return {"filter_category": category}