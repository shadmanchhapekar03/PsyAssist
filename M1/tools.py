# FILE: tools.py
# RESPONSIBILITY: M1 (Implementing M3's Tool Specs)

from langchain_core.messages import AIMessage

# --- 1. HYPERVENTILATION TOOL ---
# Source: "Tool Hyperventilation Calming Tool.txt"
def hyperventilation_tool(state):
    """
    Trigger: "I can't breathe", "Panic attack", "Chest tight", "Breathing too fast", "Hyperventilating"
    Action: Guide slow breathing.
    """
    print("   🛠️ Tool Triggered: Hyperventilation Support")
    
    script = """
    I hear that you are struggling to breathe. I am here with you. Let's slow things down together.
    
    Please try this simple grounding breath with me:
    1.  **Inhale** slowly through your nose for 4 seconds... (1, 2, 3, 4)
    2.  **Hold** that breath gently for 7 seconds... (1, 2, 3, 4, 5, 6, 7)
    3.  **Exhale** slowly through your mouth for 8 seconds... (1, 2, 3, 4, 5, 6, 7, 8)
    
    Let's do this one more time. How does your chest feel right now?
    """
    return {"messages": [AIMessage(content=script)]}

# --- 2. GREETING TOOL ---
# Source: "Hello_prompt.txt"
def greeting_tool(state):
    """
    Trigger: "Hi", "Hello", "Good morning" (without emotional content)
    Action: Warm welcome, no advice.
    """
    print("   🛠️ Tool Triggered: Greeting")
    
    # We can randomize these or keep it static
    script = "Hello! I am Somy Ali, your AI companion. I am here to listen and support you with whatever is on your mind. How are you feeling today?"
    
    return {"messages": [AIMessage(content=script)]}

# --- 3. GENERAL TOOL MAP ---
# Source: "Tool.txt" (General logic maps)
# We can use this to select the right 'mode' or system prompt dynamically
# These serve as guidelines for the system prompt selection logic, not necessarily standalone functions.
TOOL_PROMPTS = {
    "stress": "Respond calmly. Validate stress. Guide one simple grounding or breathing step. End with one gentle question.",
    "anxiety": "Use reassuring tone. Slow breathing or grounding. Keep steps simple. Ask one check-in question.",
    "sleep": "Speak softly. Suggest one relaxing habit or breathing exercise. Avoid advice overload. End with one question.",
    "hyperventilation": "Guide slow breathing step-by-step. Reassure safety. Stay present. Ask how breathing feels now.",
    "distress": "Validate feelings. Offer emotional presence. Encourage gentle self-care. Ask one reflective question.",
    "fatigue": "Acknowledge fatigue. Suggest rest, hydration, or pause. Keep it light. Ask what feels hardest right now.",
    "pain": "Respond gently. Encourage rest and relaxation. No diagnosis. Ask where discomfort feels strongest.",
    "focus": "Normalize distraction. Suggest one short grounding or focus reset. End with one question.",
    "mood": "Be encouraging. Highlight small positive steps. Avoid pressure. Ask what might help even a little."
}