#PsyAssist  
AI-Powered Psychology Assistant Chatbot

## About the Project
Somy Ali is an AI-powered psychology assistant chatbot designed to provide empathetic, supportive, and context-aware conversations related to mental health and emotional well-being.  

The project focuses on exploring how Large Language Models (LLMs) can be combined with structured prompts and document-based knowledge to assist users with topics such as anxiety, stress, depression, trauma, and self-reflection—while maintaining ethical boundaries and privacy awareness.

PsyAssist is not a replacement for professional therapy,but a supportive conversational tool intended for educational and emotional support purpose.

## Key Features
- Empathetic, psychology-oriented conversational responses  
- Context-aware dialogue handling  
- Modular backend architecture for scalability  
- Retrieval-based responses using psychology-related documents  
- Designed with mental health sensitivity and ethical considerations  
- Secure handling of environment variables and secrets  

## Tech Stack
- Programming Language:Python  
- Framework: FastAPI  
- LLM Orchestration: LangChain / LangGraph  
- Vector Databases: ChromaDB, Pinecone  
- Data Processing: PDF to Markdown ingestion  
- Environment Management: `.env` variables  

## Project Architecture (High Level)
1. User sends a message to the chatbot  
2. Input is processed and routed through the conversation logic  
3. Relevant context is retrieved from vector databases (if required)  
4. The LLM generates a response grounded in the retrieved context  
5. A structured and empathetic reply is returned to the user  
