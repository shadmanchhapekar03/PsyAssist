from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

DB_PATH = "chroma_db"
MODEL_NAME = "nomic-embed-text"

def detect_category_from_query(query):
    q = query.lower()

    if "sad" in q or "empty" in q or "lost interest" in q or "hopeless" in q:
        return "depression"
    elif "anxiety" in q or "panic" in q or "fear" in q:
        return "anxiety"
    elif "trauma" in q or "ptsd" in q:
        return "trauma"
    elif "anger" in q or "angry" in q:
        return "anger"
    elif "grief" in q or "loss" in q:
        return "grief"
    elif "sleep" in q or "insomnia" in q:
        return "sleep"
    elif "addiction" in q or "substance" in q:
        return "addiction"
    else:
        return "general"

# --- Load DB ---
embedding = OllamaEmbeddings(model=MODEL_NAME)
db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)

# --- User Query ---
query = "I feel dependent on substances and struggle to stop"

category = detect_category_from_query(query)
print(f"🔍 Detected Category: {category}")

# --- Search ---
results = db.similarity_search(
    query,
    k=3,
    filter={"category": category}
)

# --- Output ---
for r in results:
    print("\n📄 Source   :", r.metadata["source"])
    print("🏷 Category :", r.metadata["category"])
    print(r.page_content[:200])
