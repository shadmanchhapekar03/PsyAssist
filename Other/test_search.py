#set1
# from langchain_ollama import OllamaEmbeddings
# from langchain_chroma import Chroma

# DB_PATH = "chroma_db"
# MODEL_NAME = "nomic-embed-text"

# embedding = OllamaEmbeddings(model=MODEL_NAME)
# db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)

# query = "I keep getting flashbacks of a past event and feel on edge"

# results = db.similarity_search(
#     query,
#     k=3,
#     filter={"category": "trauma"}
# )

# for r in results:
#     print(f"\n📄 Source: {r.metadata['source']}")
#     print(r.page_content[:200])


# set 2
# from langchain_ollama import OllamaEmbeddings
# from langchain_chroma import Chroma

# DB_PATH = "chroma_db"
# MODEL_NAME = "nomic-embed-text"

# embedding = OllamaEmbeddings(model=MODEL_NAME)
# db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)

# query = "Why do I feel anxious all the time?"

# results = db.similarity_search(
#     query,
#     k=3,
#     filter={"category": "anxiety"}
# )

# for r in results:
#     print(f"\n📄 Source: {r.metadata['source']}")
#     print(r.page_content[:200])


# #set 3
# from langchain_ollama import OllamaEmbeddings
# from langchain_chroma import Chroma

# DB_PATH = "chroma_db"
# MODEL_NAME = "nomic-embed-text"

# embedding = OllamaEmbeddings(model=MODEL_NAME)
# db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)

# query = "I feel dependent on substances and struggle to stop"

# results = db.similarity_search(
#     query,
#     k=3,
#     filter={"category": "addiction"}
# )

# for r in results:
#     print(f"\n📄 Source: {r.metadata['source']}")
#     print(r.page_content[:200])

# #set 4
# from langchain_ollama import OllamaEmbeddings
# from langchain_chroma import Chroma

# DB_PATH = "chroma_db"
# MODEL_NAME = "nomic-embed-text"

# embedding = OllamaEmbeddings(model=MODEL_NAME)
# db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)

# query = "How can I cope with emotional distress?"

# results = db.similarity_search(
#     query,
#     k=3,
#     # filter={"category": "addiction"}
# )

# for r in results:
#     print(f"\n📄 Source: {r.metadata['source']}")
#     print(r.page_content[:200])
    
    
    
# #set 5
# from langchain_ollama import OllamaEmbeddings
# from langchain_chroma import Chroma

# DB_PATH = "chroma_db"
# MODEL_NAME = "nomic-embed-text"

# embedding = OllamaEmbeddings(model=MODEL_NAME)
# db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)

# query = "How can I challenge irrational thoughts using REBT?"

# results = db.similarity_search(
#     query,
#     k=3,
#     filter={"category": "rebt_therapy"}
# )

# for r in results:
#     print(f"\n📄 Source: {r.metadata['source']}")
#     print(r.page_content[:200])


# #set 6
# from langchain_ollama import OllamaEmbeddings
# from langchain_chroma import Chroma

# DB_PATH = "chroma_db"
# MODEL_NAME = "nomic-embed-text"

# embedding = OllamaEmbeddings(model=MODEL_NAME)
# db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)

# query = "I lost someone close and I feel stuck in sadness"

# results = db.similarity_search(
#     query,
#     k=3,
#     filter={"category": "grief"}
# )

# for r in results:
#     print(f"\n📄 Source: {r.metadata['source']}")
#     print(r.page_content[:200])


#set 7
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

DB_PATH = "chroma_db"
MODEL_NAME = "nomic-embed-text"

embedding = OllamaEmbeddings(model=MODEL_NAME)
db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)

query = "I feel empty and have lost interest in things I used to enjoy"

results = db.similarity_search(
    query,
    k=3,
    filter={"category": "depression"}
)

for r in results:
    print(f"\n📄 Source: {r.metadata['source']}")
    print(r.page_content[:200])