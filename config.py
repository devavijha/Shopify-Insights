"""
ShopifyScope Intelligence Platform Configuration

Central configuration module for the ShopifyScope platform, managing
database connections, AI service integrations, and application settings.
This module follows enterprise-grade configuration patterns for
scalability and maintainability.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Core Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+mysqlconnector://shopifyscope:intelligence123@localhost:3306/shopifyscope_intelligence_db"
)

# AI Service Integration Keys (Optional - platform gracefully degrades without them)
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY", "")

# Intelligence Engine Configuration
ENABLE_AI_ANALYSIS: bool = os.getenv("ENABLE_AI_ANALYSIS", "true").lower() == "true"
ENABLE_COMPETITIVE_INTELLIGENCE: bool = os.getenv("ENABLE_COMPETITIVE_INTELLIGENCE", "true").lower() == "true"
ENABLE_ADVANCED_ANALYTICS: bool = os.getenv("ENABLE_ADVANCED_ANALYTICS", "true").lower() == "true"

# Performance and Caching Configuration
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour default
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "15"))  # 15 seconds
MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))

# AI Analysis Configuration
SENTIMENT_ANALYSIS_THRESHOLD: float = float(os.getenv("SENTIMENT_THRESHOLD", "0.1"))
CONFIDENCE_MINIMUM_SCORE: float = float(os.getenv("CONFIDENCE_MINIMUM", "0.2"))

class ShopifyScopeSettings:
    """
    Comprehensive application settings for the ShopifyScope Intelligence Platform.
    
    This class centralizes all configuration parameters and provides
    type-safe access to application settings with sensible defaults.
    """
    
    # Platform Identity
    PLATFORM_NAME: str = "ShopifyScope Intelligence Platform"
    PLATFORM_VERSION: str = "2.1.0"
    PLATFORM_DESCRIPTION: str = "Advanced E-commerce Analytics with AI-Driven Business Intelligence"
    
    # Database Configuration
    DATABASE_URL: str = DATABASE_URL
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # HTTP Client Configuration
    USER_AGENT: str = (
        "ShopifyScope-Intelligence-Bot/2.1.0 "
        "(E-commerce Analytics Platform; +https://shopifyscope.intelligence)"
    )
    REQUEST_TIMEOUT: int = REQUEST_TIMEOUT
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 0.3
    
    # AI Intelligence Configuration
    AI_ENABLED: bool = ENABLE_AI_ANALYSIS
    COMPETITIVE_INTELLIGENCE_ENABLED: bool = ENABLE_COMPETITIVE_INTELLIGENCE
    ADVANCED_ANALYTICS_ENABLED: bool = ENABLE_ADVANCED_ANALYTICS
    
    # Performance Optimization
    CACHE_TTL: int = CACHE_TTL_SECONDS
    MAX_CONCURRENT_REQUESTS: int = MAX_CONCURRENT_REQUESTS
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Analysis Thresholds
    SENTIMENT_THRESHOLD: float = SENTIMENT_ANALYSIS_THRESHOLD
    CONFIDENCE_MINIMUM: float = CONFIDENCE_MINIMUM_SCORE
    
    # Security Configuration
    ALLOWED_DOMAINS: list = ["shopify.com", "myshopify.com", "shopifyplus.com"]
    BLOCKED_USER_AGENTS: list = ["bot", "crawler", "spider"]
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Development Configuration  
    DEBUG_MODE: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

# Global settings instance
settings = ShopifyScopeSettings()

# Environment-specific configurations
class DevelopmentConfig(ShopifyScopeSettings):
    """Development environment specific configuration"""
    DEBUG_MODE: bool = True
    LOG_LEVEL: str = "DEBUG"
    CACHE_TTL: int = 60  # Shorter cache for development

class ProductionConfig(ShopifyScopeSettings):
    """Production environment specific configuration"""
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "WARNING"
    CACHE_TTL: int = 3600  # Longer cache for production

class TestingConfig(ShopifyScopeSettings):
    """Testing environment specific configuration"""
    DEBUG_MODE: bool = True
    DATABASE_URL: str = "sqlite:///./test_shopifyscope.db"
    AI_ENABLED: bool = False  # Disable AI for faster tests

# Configuration factory
def get_config() -> ShopifyScopeSettings:
    """
    Factory function to get appropriate configuration based on environment.
    
    Returns:
        ShopifyScopeSettings: Configuration instance for current environment
    """
    env = os.getenv("ENVIRONMENT", "production").lower()
    
    config_mapping = {
        "development": DevelopmentConfig(),
        "testing": TestingConfig(),
        "production": ProductionConfig()
    }
    
    return config_mapping.get(env, ProductionConfig())


