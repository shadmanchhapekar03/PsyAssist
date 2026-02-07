# FILE: auto_ingest_drive.py
# ROLE: M2 (Google Drive Dynamic RAG)
# WEEK: 6 – Auto Updates

import os
import io
import time
import datetime
import pymupdf4llm

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()
# ---------------- CONFIG ----------------
SERVICE_ACCOUNT_FILE = "service_account.json"
DRIVE_FOLDER_ID = "16IumuIvppPJo76UY4DVSJ5yESRIWg0mA"
DOWNLOAD_FOLDER = "data_pdfs"
LOG_FILE = "ingested_drive_log.txt"

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "somy-ali-brain"
EMBED_MODEL = "nomic-embed-text"

CHECK_INTERVAL = 300  # 5 minutes
# ---------------------------------------

if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY missing")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


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


def load_log():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f)


def log_file(file_id):
    with open(LOG_FILE, "a") as f:
        f.write(file_id + "\n")


def connect_drive():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def fetch_new_pdfs(service):
    results = service.files().list(
        q=f"'{DRIVE_FOLDER_ID}' in parents and mimeType='application/pdf'",
        fields="files(id, name)"
    ).execute()

    return results.get("files", [])


def download_pdf(service, file_id, filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    request = service.files().get_media(fileId=file_id)

    with io.FileIO(path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    return path


def ingest_pdf(filename):
    print(f"⚙️ Ingesting: {filename}")

    path = os.path.join(DOWNLOAD_FOLDER, filename)
    md_text = pymupdf4llm.to_markdown(path)

    category, audience = get_tags_from_filename(filename)

    doc = Document(
        page_content=md_text,
        metadata={
            "source": filename,
            "category": category,
            "audience": audience,
            "ingested_date": datetime.date.today().isoformat()
        }
    )

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents([doc])

    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=INDEX_NAME,
        pinecone_api_key=PINECONE_API_KEY
    )

    print(f"✅ Uploaded {filename} ({len(chunks)} chunks)")


def watchdog():
    print("👀 Google Drive Auto-Ingest Started")

    Pinecone(api_key=PINECONE_API_KEY)
    service = connect_drive()

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    while True:
        try:
            processed = load_log()
            files = fetch_new_pdfs(service)

            for file in files:
                if file["id"] not in processed:
                    print(f"\n🔍 New Drive file: {file['name']}")
                    download_pdf(service, file["id"], file["name"])
                    ingest_pdf(file["name"])
                    log_file(file["id"])

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n🛑 Stopped")
            break


if __name__ == "__main__":
    watchdog()
