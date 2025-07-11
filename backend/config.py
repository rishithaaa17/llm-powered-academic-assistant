import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

# ChromaDB Configuration
CHROMA_COLLECTION_NAME = "study_chunks"

# Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "openai/llama3-70b-8192"
GROQ_API_BASE = "https://api.groq.com/openai/v1"

# Text Processing Configuration
CHUNK_SIZE = 400
RETRIEVAL_K = 3

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
] 