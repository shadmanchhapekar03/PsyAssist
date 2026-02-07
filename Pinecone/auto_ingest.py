# FILE: auto_ingest.py
# ROLE: M2 (Dynamic RAG Updater)
# WEEK: 6 – Deployment & Auto Updates

import os
import time
import datetime
import pymupdf4llm

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# ---------------- CONFIG ----------------
WATCH_FOLDER = "data_pdfs"
LOG_FILE = "ingested_log.txt"

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "somy-ali-brain"
EMBED_MODEL = "nomic-embed-text"

CHECK_INTERVAL = 60  # seconds
# ---------------------------------------

# ---------- SAFETY CHECK ----------
if not PINECONE_API_KEY:
    raise ValueError(
        "❌ PINECONE_API_KEY is missing.\n"
        "Set it as an environment variable before running the script."
    )
# ----------------------------------


# --------- TAGGING LOGIC ----------
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
    elif "sleep" in name or "insomnia" in name:
        category = "sleep"
    elif "addiction" in name:
        category = "addiction"

    if "child" in name or "teen" in name:
        audience = "child"

    return category, audience
# ----------------------------------


def load_ingested_files():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)


def log_file(filename):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(filename + "\n")


def ingest_pdf(filename):
    try:
        print(f"⚙️ Ingesting: {filename}")
        path = os.path.join(WATCH_FOLDER, filename)

        # 1. Convert PDF → Markdown
        md_text = pymupdf4llm.to_markdown(path)

        category, audience = get_tags_from_filename(filename)

        # 2. Create LangChain Document
        doc = Document(
            page_content=md_text,
            metadata={
                "source": filename,
                "category": category,
                "audience": audience,
                "ingested_date": datetime.date.today().isoformat()
            }
        )

        # 3. Chunking
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents([doc])

        # 4. Embeddings
        embeddings = OllamaEmbeddings(model=EMBED_MODEL)

        # 5. Upload to Pinecone (incremental)
        PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            index_name=INDEX_NAME,
            pinecone_api_key=PINECONE_API_KEY
        )

        # 6. Log success
        log_file(filename)
        print(f"✅ Done: {filename} ({len(chunks)} chunks)")

    except Exception as e:
        print(f"❌ Failed to ingest {filename}: {e}")


def start_watchdog():
    print("👀 Somy Ali Auto-Updater Started")
    print(f"📂 Watching folder: {WATCH_FOLDER}")

    # Initialize Pinecone (connection check)
    Pinecone(api_key=PINECONE_API_KEY)
    print("☁️ Pinecone connected")

    while True:
        try:
            processed = load_ingested_files()
            current_files = {
                f for f in os.listdir(WATCH_FOLDER)
                if f.lower().endswith(".pdf")
            }

            new_files = current_files - processed

            if new_files:
                print(f"\n🔍 Found {len(new_files)} new file(s)")
                for pdf in new_files:
                    ingest_pdf(pdf)

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n🛑 Watchdog stopped by user")
            break
        except Exception as e:
            print(f"❌ Watchdog error: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    if not os.path.exists(WATCH_FOLDER):
        os.makedirs(WATCH_FOLDER)
        print(f"📁 Created folder: {WATCH_FOLDER}")

    start_watchdog()
