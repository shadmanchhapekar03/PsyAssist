import os
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

# Import M3's Persona
from promptss import CORE_SYSTEM_PROMPT, THERAPY_SYSTEM_PROMPT, CRISIS_RESPONSE, SMALLTALK_SYSTEM_PROMPT

# --- CONFIGURATION ---
PINECONE_API_KEY = "pcsk_2YdHFw_67VFCkBgYApLCgajHUvuQEcgvjp2j6hX9sCetXd8RcLc2xumsEokE4zUpSSag8C" # Get from M2
INDEX_NAME = "somy-ali-brain"
LLM_MODEL = "llama3.1"
EMBED_MODEL = "nomic-embed-text"

# --- 1. SETUP MODELS ---
print("🔌 Connecting to Brain (Ollama)...")
try:
    # We use this SAME instance for both Routing and Chatting
    llm = ChatOllama(model=LLM_MODEL, temperature=0.7)
except Exception as e:
    print(f"❌ Error connecting to Ollama: {e}")
    llm = None

print("☁️ Connecting to Memory (Pinecone Cloud)...")
retriever = None

try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    vector_store = PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=embeddings,
        pinecone_api_key=PINECONE_API_KEY
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    print("   ✅ Connected to Pinecone Index.")
except Exception as e:
    print(f"   ⚠️ Pinecone Error: {e}")

# --- 2. DEFINE STATE ---
class AgentState(TypedDict):
    messages: List[BaseMessage] 
    context: str           
    is_safe: bool
    filter_category: str # <--- New State Field

# --- 3. DEFINE NODES ---

def safety_check(state: AgentState):
    """Worker 1: The Guardrail"""
    if not state["messages"]: return {"is_safe": True}
    last_msg = state["messages"][-1].content.lower()
    
    danger_words = ["kill myself", "suicide", "end my life", "want to die", "plan to die", "die in that"] # (Shortened for brevity)
    is_unsafe = any(word in last_msg for word in danger_words)
    
    if is_unsafe: print(f"🚨 GUARDRAIL HIT: '{last_msg}'")
    return {"is_safe": not is_unsafe}

def router_node(state: AgentState):
    """Worker 1.5: The AI Router (Reuses LLM)"""
    if not llm: return {"filter_category": "general"}
    
    user_text = state["messages"][-1].content
    
    # Fast Classification Prompt
    router_prompt = f"""
    Classify the following text into ONE category: 
    [anxiety, depression, trauma, anger, grief, sleep, addiction, child, general].
    
    Text: "{user_text}"
    
    Return ONLY the category word. No markdown, no punctuation.
    """
    
    try:
        print("🚦 Router Thinking...")
        # We reuse 'llm' here. No new memory used.
        response = llm.invoke([HumanMessage(content=router_prompt)])
        category = response.content.strip().lower()
        
        # Cleanup output (sometimes LLM says "Category: anxiety")
        valid_cats = ["anxiety", "depression", "trauma", "anger", "grief", "sleep", "addiction", "child"]
        found_cat = "general"
        for v in valid_cats:
            if v in category:
                found_cat = v
                break
                
        print(f"   ✅ AI Decided: {found_cat.upper()}")
        return {"filter_category": found_cat}
        
    except Exception as e:
        print(f"❌ Router Error: {e}")
        return {"filter_category": "general"}

def retrieve_knowledge(state: AgentState):
    """Worker 2: The Smart Librarian"""
    if not retriever: return {"context": "No manuals."}
    
    # Use the category decided by the Router
    target_category = state.get("filter_category", "general")
     
    filter_dict = None
    
    if target_category == "child":
        filter_dict = {"audience": "child"}
    elif target_category != "general":
        filter_dict = {
            "$or": [
                {"category": {"$eq": target_category}},
                {"category": {"$eq": "general"}} 
            ]
        }

    try:
        if filter_dict:
             docs = retriever.invoke(state["messages"][-1].content, filter=filter_dict)
        else:
            docs = retriever.invoke(state["messages"][-1].content)
            
        context_text = "\n\n".join([d.page_content for d in docs]) if docs else "No specific manual found."
        return {"context": context_text}
        
    except Exception as e:
        print(f"   ⚠️ Retrieval Failed: {e}")
        return {"context": "Error retrieving context."}

def generate_response(state: AgentState):
    """Worker 3: The Psychologist"""
    if not state.get("is_safe", True):
        return {"messages": [AIMessage(content=CRISIS_RESPONSE)]}
    
    target_category = state.get("filter_category", "general")
    
    # Define "Therapy Categories" that require the clinical persona
    clinical_categories = ["anxiety", "depression", "trauma", "anger", "grief", "sleep", "addiction", "child"]
    
     # Also check if we actually found helpful context (RAG success)
    has_context = state.get("context") and "No specific manual found" not in state.get("context")
    
        # DECISION: Therapy Mode vs Smalltalk Mode
    if target_category in clinical_categories or has_context:
        print(f"   🧠 Mode: THERAPY (Category: {target_category})")
        # Combine Core + Therapy Prompts
        final_system_prompt = CORE_SYSTEM_PROMPT + "\n" + THERAPY_SYSTEM_PROMPT.format(context=state.get("context", "No manuals."))
    else:
        print(f"   💬 Mode: SMALLTALK (Category: {target_category})")
        # Combine Core + Smalltalk Prompts
        final_system_prompt = CORE_SYSTEM_PROMPT + "\n" + SMALLTALK_SYSTEM_PROMPT
    
    print("🤖 Generating Response...")
    # filled_prompt = SOMY_SYSTEM_PROMPT.format(context=state.get("context", "No manuals."))
    conversation_for_llm = [SystemMessage(content=final_system_prompt)] + state["messages"]
    
    full_content = ""
    for chunk in llm.stream(conversation_for_llm):
        if chunk.content:
            full_content += chunk.content
            print(chunk.content, end="", flush=True)
    print("\n")
    return {"messages": [AIMessage(content=full_content)]}

# --- 4. BUILD THE GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("safety", safety_check)
workflow.add_node("router", router_node) # <--- Added Router
workflow.add_node("retrieve", retrieve_knowledge)
workflow.add_node("generate", generate_response)

workflow.set_entry_point("safety")

def route_safety(state: AgentState) -> Literal["router", "generate"]:
    if state.get("is_safe", True):
        return "router" # Safe -> Check Category
    else:
        return "generate" # Unsafe -> Crisis Message

workflow.add_conditional_edges("safety", route_safety)
workflow.add_edge("router", "retrieve") # Router -> Retriever
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app_graph = workflow.compile()