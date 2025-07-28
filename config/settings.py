"""
Configuration settings for AI Market Intelligence Tool
Handles all environment variables, API keys, and application settings
"""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings with environment variable support"""

    # Base Configuration
    BASE_DIR = Path(__file__).resolve().parent.parent
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # API Keys - Multiple providers for redundancy
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/intelligence.db")

    # Web Scraping Configuration
    USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; AIIntelligence/1.0; +https://example.com)")
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "2.0"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT = int(os.getenv("TIMEOUT", "30"))
    CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", "5"))

    # Content Analysis Settings
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))
    MIN_CONTENT_LENGTH = int(os.getenv("MIN_CONTENT_LENGTH", "100"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.8"))

    # LLM Configuration
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

    # Vector Database Settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "384"))
    INDEX_TYPE = os.getenv("INDEX_TYPE", "flat")

    # Report Generation
    REPORT_TEMPLATE_DIR = BASE_DIR / "src" / "reports" / "templates"
    OUTPUT_FORMATS = os.getenv("OUTPUT_FORMATS", "html,pdf,json").split(",")

    # Alert System
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

    # Scheduling
    SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))
    REPORT_INTERVAL_HOURS = int(os.getenv("REPORT_INTERVAL_HOURS", "24"))
    CLEANUP_INTERVAL_DAYS = int(os.getenv("CLEANUP_INTERVAL_DAYS", "30"))

    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Data Directories
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    REPORTS_DIR = DATA_DIR / "reports"
    CACHE_DIR = DATA_DIR / "cache"
    LOGS_DIR = BASE_DIR / "logs"

    # Target Sources (configurable list)
    DEFAULT_NEWS_SOURCES = [
        "https://techcrunch.com",
        "https://venturebeat.com", 
        "https://www.theverge.com",
        "https://arstechnica.com",
        "https://www.wired.com"
    ]

    NEWS_SOURCES = os.getenv("NEWS_SOURCES", ",".join(DEFAULT_NEWS_SOURCES)).split(",")

    # Keywords and Topics
    DEFAULT_KEYWORDS = [
        "artificial intelligence",
        "machine learning", 
        "AI startup",
        "venture capital",
        "tech innovation",
        "digital transformation"
    ]

    MONITORING_KEYWORDS = os.getenv("MONITORING_KEYWORDS", ",".join(DEFAULT_KEYWORDS)).split(",")

    # Performance Settings
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    MAX_MEMORY_USAGE_MB = int(os.getenv("MAX_MEMORY_USAGE_MB", "1024"))

    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR, 
            cls.PROCESSED_DATA_DIR,
            cls.REPORTS_DIR,
            cls.CACHE_DIR,
            cls.LOGS_DIR,
            cls.REPORT_TEMPLATE_DIR
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        print(f"✅ Created directory structure at {cls.BASE_DIR}")

    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings"""
        errors = []
        warnings = []

        # Check API keys
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY and not cls.HUGGINGFACE_API_KEY:
            errors.append("At least one LLM API key must be configured")

        # Check email settings if alerts enabled
        if cls.EMAIL_USER and not cls.EMAIL_PASSWORD:
            warnings.append("Email user configured but no password provided")

        # Check directories
        if not cls.BASE_DIR.exists():
            errors.append(f"Base directory not found: {cls.BASE_DIR}")

        # Validate numeric ranges
        if cls.REQUEST_DELAY < 0.1:
            warnings.append("Request delay is very low - may cause rate limiting")

        if cls.MAX_TOKENS > 4000:
            warnings.append("Max tokens is high - may increase API costs")

        # Print validation results
        if errors:
            print("❌ Configuration Errors:")
            for error in errors:
                print(f"  - {error}")
            raise ValueError("Configuration validation failed")

        if warnings:
            print("⚠️  Configuration Warnings:")
            for warning in warnings:
                print(f"  - {warning}")

        print("✅ Configuration validation passed")

    @classmethod
    def get_llm_config(cls):
        """Get LLM configuration for current provider"""
        if cls.OPENAI_API_KEY:
            return {
                "provider": "openai",
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.DEFAULT_MODEL,
                "max_tokens": cls.MAX_TOKENS,
                "temperature": cls.TEMPERATURE
            }
        elif cls.ANTHROPIC_API_KEY:
            return {
                "provider": "anthropic", 
                "api_key": cls.ANTHROPIC_API_KEY,
                "model": "claude-3-haiku-20240307",
                "max_tokens": cls.MAX_TOKENS,
                "temperature": cls.TEMPERATURE
            }
        elif cls.HUGGINGFACE_API_KEY:
            return {
                "provider": "huggingface",
                "api_key": cls.HUGGINGFACE_API_KEY,
                "model": "microsoft/DialoGPT-medium",
                "max_tokens": cls.MAX_TOKENS
            }
        else:
            raise ValueError("No LLM API key configured")

# Create global settings instance
settings = Settings()

# Auto-create directories on import
settings.create_directories()