import os
import time
from uuid import uuid4

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore


# --- CONFIGURATION ---
BASE_PATH = r"C:\Users\Shaziya khan\Desktop\Somyali_backend_project"
MD_PATH = os.path.join(BASE_PATH, "md_files")

MODEL_NAME = "nomic-embed-text"

PINECONE_API_KEY = "pcsk_2YdHFw_67VFCkBgYApLCgajHUvuQEcgvjp2j6hX9sCetXd8RcLc2xumsEokE4zUpSSag8C"   # 🔐 Put in .env later
INDEX_NAME = "somy-ali-brain"
DIMENSION = 768  # nomic-embed-text


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
    print("🚀 Creating Pinecone Vector Database from Markdown files...")

    if not os.path.exists(MD_PATH):
        print(f"❌ md_files not found: {MD_PATH}")
        return

    # --- STEP 1: Pinecone Setup ---
    pc = Pinecone(api_key=PINECONE_API_KEY)

    existing_indexes = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        print(f"☁️ Creating Pinecone index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        time.sleep(5)
    else:
        print(f"✅ Pinecone index '{INDEX_NAME}' already exists")

    # --- STEP 2: Load Markdown ---
    print("📖 Loading Markdown files...")
    loader = DirectoryLoader(
        MD_PATH,
        glob="*.md",
        loader_cls=lambda p: TextLoader(p, encoding="utf-8")
    )

    raw_docs = loader.load()
    print(f"✅ Loaded {len(raw_docs)} files")

    # --- STEP 3: Add Metadata ---
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

    # --- STEP 4: Chunking ---
    print("✂ Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(tagged_docs)
    print(f"✅ Created {len(chunks)} chunks")

    # --- STEP 5: Embeddings ---
    print("🧠 Creating embeddings...")
    embedding = OllamaEmbeddings(model=MODEL_NAME)

    # --- STEP 6: Upload to Pinecone ---
    print("⬆️ Uploading to Pinecone (this may take time)...")

    vectorstore = PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=embedding,
        pinecone_api_key=PINECONE_API_KEY
    )

    for i in range(0, len(chunks), 50):
        batch = chunks[i:i + 50]
        ids = [str(uuid4()) for _ in batch]

        vectorstore.add_documents(
            documents=batch,
            ids=ids
        )
        time.sleep(0.2)

    print("🎉 Pinecone Vector Database ready!")


if __name__ == "__main__":
    create_master_db()
