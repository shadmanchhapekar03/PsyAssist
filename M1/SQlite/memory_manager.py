# FILE: memory_manager.py
# RESPONSIBILITY: M1 (Architect)
# STATUS: Week 4 (SQLite Implementation)

import os
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# --- 1. SQLITE SETUP ---
# Use absolute path to ensure we know where the DB is
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "somy_memory.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"💽 Database Path: {DB_PATH}")

# Base class for all our models
Base = declarative_base()

# The Engine is the starting point for any SQLAlchemy application
# connect_args={"check_same_thread": False} is needed for SQLite to work with FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is a factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 2. DEFINE THE TABLE ---
class ChatMessage(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True) # Unique ID for every row
    user_id = Column(String, index=True)               # The user's ID (e.g., "user_123")
    thread_id = Column(String, index=True)             # The Session (e.g. "uuid-123") <--- NEW
    role = Column(String)                              # "human" or "ai"
    content = Column(Text)                             # The actual text of the message
    timestamp = Column(DateTime, default=datetime.utcnow) # When it happened

# Create the tables in the database (if they don't exist yet)
Base.metadata.create_all(bind=engine)

# --- 3. MEMORY FUNCTIONS ---

def get_db():
    """Helper to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_chat_history(user_id: str, thread_id: str, limit: int = 10) -> List[BaseMessage]:
    """
    Loads the last N messages for a specific user from SQLite.
    Returns them as LangChain Message objects (HumanMessage/AIMessage).
    """
    db = SessionLocal()
    try:
        # Query: Select * from chat_history where user_id matches
        # Order by newest first, take the top 'limit'
        history = (
            db.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .filter(ChatMessage.thread_id == thread_id) # <--- NEW FILTER
            .order_by(ChatMessage.timestamp.desc())
            .limit(limit)
            .all()
        )
        
        # We got them Newest->Oldest (for the limit), but AI needs Oldest->Newest
        history.reverse() 

        messages = []
        for msg in history:
            if msg.role == "human":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "ai":
                messages.append(AIMessage(content=msg.content))
        
        print(f"📂 Loaded {len(messages)} msgs for User: {user_id} | Thread: {thread_id}")
        return messages
    except Exception as e:
        print(f"⚠️ Database Load Error: {e}")
        return []
    finally:
        db.close()

def save_chat_history(user_id: str, thread_id: str, new_messages: List[BaseMessage]):
    """
    Saves a list of new messages (HumanMessage or AIMessage) to SQLite.
    """
    db = SessionLocal()
    try:
        for msg in new_messages:
            # Determine role based on the message type
            role = "human" if isinstance(msg, HumanMessage) else "ai"
            
            # Create a new row object
            db_msg = ChatMessage(
                user_id=user_id, 
                thread_id=thread_id, # <--- NEW FIELD
                role=role, 
                content=msg.content
            )
            
            # Add to the session
            db.add(db_msg)
        
        # Commit (Save) all changes to the file
        db.commit()
        print(f"💾 Saved {len(new_messages)} msgs to Thread: {thread_id}")
    except Exception as e:
        print(f"⚠️ Database Save Error: {e}")
        db.rollback() # Rollback on error
    finally:
        db.close()
        
def get_user_threads(user_id: str):
    """(Optional) Returns a list of all thread IDs for a user."""
    db = SessionLocal()
    try:
        # Get distinct thread_ids
        threads = db.query(ChatMessage.thread_id).filter(ChatMessage.user_id == user_id).distinct().all()
        return [t[0] for t in threads]
    finally:
        db.close()
        

# NEW FUNCTION
def delete_thread_history(user_id: str, thread_id: str):
    """Deletes all messages for a specific thread."""
    db = SessionLocal()
    try:
        # Delete query
        db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.thread_id == thread_id
        ).delete()
        
        db.commit()
        print(f"🗑️ Deleted Thread: {thread_id} for User: {user_id}")
        return True
    except Exception as e:
        print(f"⚠️ Delete Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()