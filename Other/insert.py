# insert a new PDF book into Chroma DB with tagging and splitting

import os
import pymupdf4llm
import re
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- CONFIGURATION ---
pdf_path = r"C:\Users\Shaziya khan\Desktop\Somyali_backend_project\Data\Depression PDF.pdf"  # path to your new PDF
output_folder = r"C:\Users\Shaziya khan\Desktop\Somyali_backend_project\md_files"
os.makedirs(output_folder, exist_ok=True)

# --- STEP 1: Convert PDF to Markdown ---
md_filename = os.path.basename(pdf_path).replace(".pdf", ".md")
md_path = os.path.join(output_folder, md_filename)

try:
    md_text = pymupdf4llm.to_markdown(pdf_path)
    md_text = re.sub(r'\nPage \d+\n', '\n', md_text)  # optional: remove page numbers

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    print(f"✅ PDF converted to Markdown: {md_filename}")
except Exception as e:
    print(f"❌ Error converting PDF: {e}")
    exit()

# --- STEP 2: Load Markdown and Tag Document ---
loader = TextLoader(md_path, encoding="utf-8")
new_doc = loader.load()[0]  # load returns a list

# Add metadata tags
tagged_doc = Document(
    page_content=new_doc.page_content,
    metadata={
        "source": md_filename,
        "category": "depression",  # change category if needed
        "audience": "adult"         # change audience if needed
    }
)

print("✅ Tagged document ready for Chroma DB")
# After Step 2: tagged_doc is ready
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents([tagged_doc])
print(f"✅ Document split into {len(chunks)} chunks")

# Step 4: Add chunks to Chroma DB
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embedding = OllamaEmbeddings(model="nomic-embed-text")
db = Chroma(persist_directory="chroma_db", embedding_function=embedding)

for i in range(0, len(chunks), 50):  # batch of 50
    db.add_documents(chunks[i:i+50])
print("✅ New book added to the Super Database!")
