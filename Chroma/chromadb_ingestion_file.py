import os
import shutil
import time
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# --- CONFIGURATION ---
BASE_PATH = r"C:\Users\Shaziya khan\Desktop\Somyali_backend_project"
MD_PATH = os.path.join(BASE_PATH, "md_files")
DB_PATH = os.path.join(BASE_PATH, "chroma_db")
MODEL_NAME = "nomic-embed-text"

def get_tags_from_filename(filename):
    name = filename.lower()

    category = "general"
    audience = "adult"

    if "anxiety" in name or "panic" in name:
        category = "anxiety"
    elif "depression" in name:
        category = "depression"
    elif "trauma" in name or "ptsd" in name:
        category = "trauma"
    elif "anger" in name:
        category = "anger"
    elif "grief" in name:
        category = "grief"
    elif "sleep" in name:
        category = "sleep"
    elif "addiction" in name or "substance" in name:
        category = "addiction"

    if "child" in name or "teen" in name:
        audience = "child"

    return category, audience

def create_master_db():
    print("🚀 Creating Super Database from Markdown files...")

    if not os.path.exists(MD_PATH):
        print(f"❌ md_files not found: {MD_PATH}")
        return

    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print("🗑️ Old DB deleted")

    print("📖 Loading Markdown files...")
    loader = DirectoryLoader(
        MD_PATH,
        glob="*.md",
        loader_cls=lambda p: TextLoader(p, encoding="utf-8")
    )

    raw_docs = loader.load()
    print(f"✅ Loaded {len(raw_docs)} files")

    tagged_docs = []
    for doc in raw_docs:
        filename = os.path.basename(doc.metadata["source"])
        category, audience = get_tags_from_filename(filename)

        tagged_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={
                    "source": filename,
                    "category": category,
                    "audience": audience
                }
            )
        )

    print("✂ Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(tagged_docs)
    print(f"✅ Created {len(chunks)} chunks")

    print("🧠 Creating embeddings...")
    embedding = OllamaEmbeddings(model=MODEL_NAME)
    db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)

    for i in range(0, len(chunks), 50):
        db.add_documents(chunks[i:i + 50])
        time.sleep(0.2)

    print("🎉 Super Database ready!")

if __name__ == "__main__":
    create_master_db()
