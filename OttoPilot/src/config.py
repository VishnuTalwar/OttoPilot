"""
Configuration settings for OVGU Chatbot
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # API Keys
    google_api_key: str = Field(..., description="Google Gemini API key")
    chroma_api_key: str = Field(..., description="ChromaDB Cloud API key")
    tavily_api_key: str = Field(..., description="Tavily API key for web search")
    
    # LangSmith settings (optional)
    langsmith_api_key: Optional[str] = Field(default=None)
    langsmith_tracing: Optional[str] = Field(default="false")
    langsmith_project: Optional[str] = Field(default="default")
    
    # ChromaDB Cloud settings
    chroma_tenant: str = Field(default="3f4a6571-5eb8-4b93-bd74-de15b8b8b6c8")
    chroma_database: str = Field(default="OttoPilot")
    chroma_collection_name: str = Field(default="ovgu_chatbot")
    
    # LLM settings
    gemini_model: str = Field(default="gemini-2.5-flash")
    embedding_model: str = Field(default="models/text-embedding-004")
    temperature: float = Field(default=0.3)
    
    # Document processing
    data_dir: str = Field(default="data/raw")
    chunk_size: int = Field(default=800)
    chunk_overlap: int = Field(default=150)
    
    # Retrieval settings
    top_k_docs: int = Field(default=5)
    similarity_threshold: float = Field(default=0.5)
    
    # Web search settings
    tavily_max_results: int = Field(default=5)
    tavily_search_depth: str = Field(default="basic")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()