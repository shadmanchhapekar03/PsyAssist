import os
import shutil
import time
from langchain_community.document_loaders import DirectoryLoader, TextLoader
# UPDATED IMPORT: Using the new standalone package
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# --- CONFIGURATION ---
# Base folder in your Drive
BASE_DRIVE_PATH = r"C:\Users\Shaziya khan\Downloads\Somy Backend"
DATA_PATH = BASE_DRIVE_PATH + r"\md_files"
DB_PATH = "chroma_db"        # Folder where we will save the Brain
MODEL_NAME = "nomic-embed-text" # The specific embedding model

def create_vector_db():
      # 1. CHECK FOR DATA
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: '{DATA_PATH}' folder not found. Did you finish Week 1?")
        return

    # 2. LOAD DOCUMENTS (The "Reading" Phase)
    print("📖 Loading Markdown files...")
    # This glob="*.md" means "Find every file ending in .md"
    loader = DirectoryLoader(DATA_PATH, glob="*.md", loader_cls=lambda path: TextLoader(path, encoding="utf-8"))
    documents = loader.load()

    if not documents:
        print("⚠ No documents found. Please check your processed_data folder.")
        return

    print(f"   ✅ Loaded {len(documents)} documents.")

    # 3. SPLIT TEXT (The "Chunking" Phase)
    print("✂ Splitting text into chunks...")
    # chunk_size=1000: Each index card has ~1000 characters
    # chunk_overlap=200: We repeat 200 chars to ensure context isn't cut in the middle
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True, # Keeps track of where in the book this came from
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   ✅ Created {len(chunks)} knowledge chunks.")

    # 5. INITIALIZE EMBEDDINGS
    print(f"🧠 Initializing {MODEL_NAME}...")
    try:
        embedding_function = OllamaEmbeddings(model=MODEL_NAME)
    except Exception as e:
        print(f"❌ Error initializing embeddings: {e}")
        return

    # 6. CREATE DATABASE WITH BATCHING
    if os.path.exists(DB_PATH):
        print(f"   🗑 Clearing old database at {DB_PATH}...")
        shutil.rmtree(DB_PATH)

    print(f"🗂 Creating Chroma Database in Drive at: {DB_PATH}")
    
    try:
        # BATCH PROCESSING FIX
        # Instead of one giant command, we process chunks in groups of 50
        batch_size = 50
        total_chunks = len(chunks)
        
        # Initialize empty DB first
        db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function)
        
        print(f"   Processing {total_chunks} chunks in batches of {batch_size}...")
        
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]
            print(f"   - Embeding batch {i//batch_size + 1}/{(total_chunks//batch_size)+1}...")
            
            # Add batch to DB
            db.add_documents(batch)
            
            # Tiny sleep to let Ollama cool down/reset connection
            time.sleep(0.5) 

        print(f"✅ Success! Database saved to Google Drive.")
        print(f"   Path: {DB_PATH}")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("   Ensure Ollama is running in the background.")

# --- VERIFICATION FUNCTION ---
def test_retrieval():
    """
    Simulates what the API will do.
    """
    print("\n🔎 TESTING RETRIEVAL...")
    try:
        embedding_function = OllamaEmbeddings(model=MODEL_NAME)
        db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function)

        # Ask a medical question to see if it finds the right book
        query = "What are the symptoms of panic disorder?"
        results = db.similarity_search_with_score(query, k=3) # Get top 3 matches

        print(f"   Query: {query}")
        print("   Results:")
        if not results:
            print("   ⚠ No results found. DB might be empty.")

        for doc, score in results:
            # Score close to 0 is better (0 = exact match)
            print(f"   - [Score {score:.4f}] ...{doc.page_content[:100]}...")

    except Exception as e:
        print(f"❌ Error testing retrieval: {e}")

if __name__ == "__main__":
    create_vector_db()
    test_retrieval()