import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # API Keys
    OMDB_API_KEY: str = Field("4977b044")
    FANART_API_KEY: str = Field("fb2b79b4e05ed6d3452f751ddcf38bda")
    TMDB_API_KEY: str = Field("demo_key_12345")
    YOUTUBE_API_KEY: Optional[str] = Field(None)
    GEMINI_API_KEY: Optional[str] = Field(None)
    
    # Reddit API Configuration
    REDDIT_CLIENT_ID: Optional[str] = Field(None)
    REDDIT_CLIENT_SECRET: Optional[str] = Field(None)
    REDDIT_USER_AGENT: str = Field("CineScopeAnalyzer/2.0 (Enhanced Movie Analysis Bot)")
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: Optional[str] = Field(None)
    FIREBASE_PRIVATE_KEY_JSON_PATH: Optional[str] = Field(None)  # Path to service account JSON
    
    # Database / Cache Configuration
    DATABASE_URL: str = Field("sqlite:///./movie_analysis.db")
    
    # Scraping Configuration
    SCRAPING_DELAY: int = Field(2)
    MAX_CONCURRENT_REQUESTS: int = Field(8)
    SCRAPY_ENV: str = Field("development")
    
    # Analysis Configuration
    ENABLE_DEEP_ANALYSIS: bool = Field(True)
    ENABLE_REDDIT_ANALYSIS: bool = Field(True)
    ENABLE_WEB_SCRAPING: bool = Field(True)
    
    # Performance & Logging
    LOG_LEVEL: str = Field("INFO")
    DEBUG_MODE: bool = Field(True)
    
    # Pydantic Configuration
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
