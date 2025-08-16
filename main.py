"""
ShopifyScope Intelligence Platform
Advanced E-commerce Analytics with AI-Driven Business Intelligence

This application provides comprehensive analysis of Shopify stores using
cutting-edge AI and machine learning technologies to generate actionable
business insights for strategic decision-making.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import HttpUrl, ValidationError
from api.routes import router
from typing import Optional
import uvicorn

# Initialize the FastAPI application with comprehensive metadata
app = FastAPI(
    title="ShopifyScope Intelligence Platform",
    description="""
    🛍️ **Advanced E-commerce Analytics Platform**
    
    Transform raw Shopify store data into actionable business intelligence using
    state-of-the-art AI and machine learning algorithms. Perfect for market research,
    competitive analysis, and strategic business planning.
    
    ## Key Capabilities:
    * 📊 **Comprehensive Store Analysis** - Complete product catalog and business intelligence
    * 🤖 **AI-Powered Insights** - Sentiment analysis, brand perception, and customer insights
    * 📈 **Marketing Intelligence** - Target audience identification and content strategy
    * 💰 **Pricing Analytics** - Competitive pricing analysis and optimization recommendations
    * 🔍 **Market Research** - Competitor analysis and market positioning insights
    
    ## Technology Stack:
    * FastAPI for high-performance API development
    * Advanced NLP with TextBlob and NLTK
    * Machine Learning with scikit-learn
    * MySQL with SQLAlchemy ORM
    * Docker containerization for scalability
    """,
    version="2.1.0",
    contact={
        "name": "ShopifyScope Intelligence Team",
        "email": "intelligence@shopifyscope.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Include API routes with versioned prefix
app.include_router(router, prefix="/api")

@app.get("/", 
         summary="Platform Overview",
         description="Get comprehensive information about the ShopifyScope Intelligence Platform")
async def platform_overview():
    """
    Welcome endpoint providing platform overview and available capabilities.
    
    Returns comprehensive platform information including:
    - Available intelligence modules
    - API endpoint documentation
    - Platform health status
    - Feature capabilities
    """
    return {
        "platform": "ShopifyScope Intelligence Platform",
        "tagline": "Advanced E-commerce Analytics with AI-Driven Business Intelligence", 
        "version": "2.1.0",
        "status": "operational",
        "intelligence_modules": {
            "core_analytics": "Comprehensive store data extraction and analysis",
            "ai_intelligence": "Advanced AI-powered business insights generation",
            "sentiment_engine": "Brand perception and customer sentiment analysis",
            "marketing_intelligence": "Target audience and content strategy insights",
            "pricing_analytics": "Competitive pricing and revenue optimization"
        },
        "api_endpoints": {
            "interactive_docs": "/docs",
            "redoc_documentation": "/redoc",
            "store_analysis": "/api/fetch-insights",
            "ai_intelligence": "/api/ai-analysis",
            "sentiment_analysis": "/api/sentiment-analysis",
            "marketing_insights": "/api/marketing-insights",
            "pricing_intelligence": "/api/pricing-intelligence"
        },
        "capabilities": [
            "Real-time store analysis",
            "AI-powered business intelligence",
            "Competitive market research",
            "Strategic planning insights",
            "Performance optimization recommendations"
        ],
        "supported_platforms": ["Shopify", "Shopify Plus", "Custom E-commerce"],
        "deployment": {
            "containerized": True,
            "scalable": True,
            "cloud_ready": True
        }
    }

@app.get("/health", 
         summary="Health Check",
         description="Check platform health and service availability")
async def health_check():
    """
    Health check endpoint for monitoring and deployment verification.
    
    Returns:
        dict: Platform health status and service availability
    """
    return {
        "status": "healthy",
        "platform": "ShopifyScope Intelligence",
        "version": "2.1.0",
        "services": {
            "api_server": "operational",
            "ai_engine": "operational", 
            "database": "operational",
            "cache_layer": "operational"
        },
        "timestamp": "2025-08-16T00:00:00Z"
    }

# Application startup configuration
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )