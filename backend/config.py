import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory (project root)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Server Configuration
    BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
    
    # LLM Configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # Scraper Configuration
    SCRAPER_TIMEOUT = int(os.getenv("SCRAPER_TIMEOUT", "30"))
    SCRAPER_MAX_RESULTS = int(os.getenv("SCRAPER_MAX_RESULTS", "10"))
    SCRAPER_RATE_LIMIT = float(os.getenv("SCRAPER_RATE_LIMIT", "2.0"))  # seconds between requests
    
    # Vector Store Configuration
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/chroma")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # RAG Configuration
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

config = Config()
