"""
ShopifyScope Intelligence Platform API Routes

This module defines the RESTful API endpoints for the ShopifyScope platform,
providing access to comprehensive e-commerce intelligence capabilities including
AI-powered analysis, sentiment analysis, and market insights.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import HttpUrl, ValidationError
from sqlalchemy.orm import Session
import re
import requests
from typing import Dict, Any

from services.scraper import WebScraper
from services.parser import ShopifyParser
from services.ai_analyzer import AIAnalyzer
from models.brand_data import BrandContext
from utils.helpers import normalize_url, is_valid_shopify_url
from database.dependencies import get_db
from database import crud
from database.models import create_db_tables
from config import ENABLE_AI_ANALYSIS

# Initialize API router with versioning
router = APIRouter(
    tags=["E-commerce Intelligence"],
    responses={
        404: {"description": "Store not found"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"}
    }
)

# Ensure database tables are created
create_db_tables()


@router.get("/fetch-insights", 
           response_model=BrandContext, 
           summary="Comprehensive Store Intelligence Analysis",
           description="Extract complete business intelligence from any Shopify store")
async def extract_store_intelligence(
    website_url: HttpUrl, 
    db: Session = Depends(get_db)
) -> BrandContext:
    """
    Performs comprehensive intelligence extraction from a Shopify store.
    
    This endpoint analyzes the target store and extracts:
    - Complete product catalog with detailed metadata
    - Business policies and customer service information
    - Brand messaging and communication strategies
    - Social media presence and digital footprint
    - Contact information and support channels
    - Navigation structure and user experience elements
    
    The system implements intelligent caching to optimize performance and
    reduce redundant processing for frequently analyzed stores.

    Args:
        website_url (HttpUrl): Target Shopify store URL for analysis
        db (Session): Database session for data persistence

    Returns:
        BrandContext: Comprehensive store intelligence report

    Raises:
        HTTPException: For invalid URLs, inaccessible stores, or processing errors
    """
    normalized_url = normalize_url(str(website_url))

    # Check for cached intelligence data
    cached_intelligence = crud.get_brand_insights_from_db(db, normalized_url)
    if cached_intelligence:
        print(f"Intelligence data for {normalized_url} retrieved from cache.")
        return cached_intelligence

    try:
        # Validate target URL as Shopify store
        if not is_valid_shopify_url(normalized_url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Target URL is not a valid Shopify store. Please provide a valid Shopify store URL."
            )

        # Initialize intelligence extraction components
        scraper = WebScraper(normalized_url)
        parser = ShopifyParser(normalized_url)
        
        # Create intelligence context container
        brand_context = BrandContext(website_url=website_url)

        # Extract product catalog intelligence
        products_json = scraper.fetch_json("/products.json")
        if products_json:
            brand_context.product_catalog = parser.parse_product_catalog(products_json)
        else:
            print(f"Warning: Could not fetch products.json for {normalized_url}. It might not be a standard Shopify store or products are hidden.")

        homepage_soup = scraper.fetch_html("/")
        if homepage_soup:
            brand_context.hero_products = parser.parse_hero_products(homepage_soup)

            # --- Privacy Policy ---
            privacy_policy_url_found = None
            # Try common paths first
            for path in ["/policies/privacy-policy", "/pages/privacy-policy"]:
                url_to_fetch = normalized_url + path
                temp_soup = scraper.fetch_html(url_to_fetch)
                if temp_soup:
                    # Pass the exact URL fetched
                    brand_context.privacy_policy = parser.parse_policy(temp_soup, "privacy_policy", page_url=url_to_fetch)
                    privacy_policy_url_found = url_to_fetch
                    break
            
            # Fallback: search for a privacy policy link on the homepage
            if not brand_context.privacy_policy and homepage_soup:
                privacy_link = homepage_soup.find('a', href=re.compile(r'privacy-policy|privacy', re.IGNORECASE))
                if privacy_link and privacy_link.get('href'):
                    abs_url_from_link = parser._get_absolute_url(privacy_link['href'])
                    if abs_url_from_link:
                        temp_soup = scraper.fetch_html(abs_url_from_link)
                        if temp_soup:
                            # Pass the exact URL fetched from the link
                            brand_context.privacy_policy = parser.parse_policy(temp_soup, "privacy_policy", page_url=abs_url_from_link)
                            privacy_policy_url_found = abs_url_from_link

            # Ensure the policy object has the URL if successfully parsed
            if brand_context.privacy_policy and not brand_context.privacy_policy.url and privacy_policy_url_found:
                brand_context.privacy_policy.url = privacy_policy_url_found


            # --- Return, Refund Policies ---
            return_refund_policy_url_found = None
            for path in ["/policies/refund-policy", "/policies/returns-policy", "/pages/return-policy"]:
                url_to_fetch = normalized_url + path
                temp_soup = scraper.fetch_html(url_to_fetch)
                if temp_soup:
                    brand_context.return_refund_policy = parser.parse_policy(temp_soup, "return_refund_policy", page_url=url_to_fetch)
                    return_refund_policy_url_found = url_to_fetch
                    break
            
            if not brand_context.return_refund_policy and homepage_soup:
                refund_link = homepage_soup.find('a', href=re.compile(r'refund-policy|return-policy|returns', re.IGNORECASE))
                if refund_link and refund_link.get('href'):
                    abs_url_from_link = parser._get_absolute_url(refund_link['href'])
                    if abs_url_from_link:
                        temp_soup = scraper.fetch_html(abs_url_from_link)
                        if temp_soup:
                            brand_context.return_refund_policy = parser.parse_policy(temp_soup, "return_refund_policy", page_url=abs_url_from_link)
                            return_refund_policy_url_found = abs_url_from_link
            
            if brand_context.return_refund_policy and not brand_context.return_refund_policy.url and return_refund_policy_url_found:
                brand_context.return_refund_policy.url = return_refund_policy_url_found


            # --- Brand FAQs ---
            faq_url_found = None
            for path in ["/pages/faqs", "/community/faq", "/apps/help-center/faq"]: 
                url_to_fetch = normalized_url + path
                temp_soup = scraper.fetch_html(url_to_fetch)
                if temp_soup:
                    brand_context.faqs = parser.parse_faqs(temp_soup)
                    faq_url_found = url_to_fetch
                    break
            
            if not brand_context.faqs and homepage_soup: 
                faq_link = homepage_soup.find('a', href=re.compile(r'faq|frequently-asked-questions|help', re.IGNORECASE))
                if faq_link and faq_link.get('href'):
                    abs_url_from_link = parser._get_absolute_url(faq_link['href'])
                    if abs_url_from_link:
                        temp_soup = scraper.fetch_html(abs_url_from_link)
                        if temp_soup:
                            brand_context.faqs = parser.parse_faqs(temp_soup)
                            faq_url_found = abs_url_from_link
            # Note: FAQs don't have a direct 'url' attribute in your model, so no need to assign it here.

            brand_context.social_handles = parser.parse_social_handles(homepage_soup)
            brand_context.contact_details = parser.parse_contact_details(homepage_soup)
            brand_context.brand_text_context = parser.parse_brand_text_context(homepage_soup)
            brand_context.important_links = parser.parse_important_links(homepage_soup)
            
            title_tag = homepage_soup.find('title')
            if title_tag:
                brand_name = title_tag.get_text(strip=True)
                brand_name = re.sub(r'\s*\|\s*Shopify.*$', '', brand_name, flags=re.IGNORECASE)
                brand_name = re.sub(r'\s*-\s*Powered by Shopify.*$', '', brand_name, flags=re.IGNORECASE)
                brand_context.brand_name = brand_name.strip()

        if not brand_context.product_catalog and not brand_context.hero_products and not homepage_soup:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not access the website or retrieve any meaningful data. It might not be a standard Shopify store or is unreachable.")

        crud.create_brand_insights(db, brand_context)
        print(f"Insights for {normalized_url} scraped and saved to DB.")
        
        return brand_context

    except requests.exceptions.MissingSchema:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL format. Please ensure it includes http:// or https://")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found or unreachable. Please check the URL.")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Data validation error: {e.errors()}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal server error occurred: {e}")


@router.get("/ai-analysis", summary="Get AI-powered analysis of a Shopify store")
async def get_ai_analysis(website_url: HttpUrl, db: Session = Depends(get_db)):
    """
    Get comprehensive AI-powered analysis including sentiment, marketing insights, 
    pricing intelligence, and strategic recommendations.
    
    Args:
        website_url (HttpUrl): The URL of the Shopify store
        db (Session): Database session dependency
        
    Returns:
        Dict: Comprehensive AI analysis report
    """
    if not ENABLE_AI_ANALYSIS:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, 
            detail="AI analysis is currently disabled. Enable it in configuration."
        )
    
    try:
        # First get the basic insights
        normalized_url = normalize_url(str(website_url))
        brand_data = crud.get_brand_insights_from_db(db, normalized_url)
        
        if not brand_data:
            # If no data exists, scrape first
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No data found for this URL. Please fetch basic insights first using /fetch-insights endpoint."
            )
        
        # Initialize AI analyzer
        ai_analyzer = AIAnalyzer()
        
        # Generate comprehensive AI report
        ai_report = ai_analyzer.generate_comprehensive_ai_report(brand_data)
        
        return {
            "status": "success",
            "message": "AI analysis completed successfully",
            "basic_insights": brand_data.dict(),
            "ai_intelligence_report": ai_report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"AI analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"AI analysis failed: {e}"
        )


@router.get("/sentiment-analysis", summary="Get sentiment analysis of brand content")
async def get_sentiment_analysis(website_url: HttpUrl, db: Session = Depends(get_db)):
    """
    Analyze sentiment of brand content using AI/NLP techniques.
    
    Args:
        website_url (HttpUrl): The URL of the Shopify store
        db (Session): Database session dependency
        
    Returns:
        SentimentAnalysis: Detailed sentiment analysis results
    """
    try:
        normalized_url = normalize_url(str(website_url))
        brand_data = crud.get_brand_insights_from_db(db, normalized_url)
        
        if not brand_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No data found. Please fetch basic insights first."
            )
        
        ai_analyzer = AIAnalyzer()
        sentiment_result = ai_analyzer.analyze_brand_sentiment(brand_data)
        
        return {
            "status": "success",
            "brand_name": brand_data.brand_name,
            "sentiment_analysis": sentiment_result.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentiment analysis failed: {e}"
        )


@router.get("/marketing-insights", summary="Get AI-powered marketing insights")
async def get_marketing_insights(website_url: HttpUrl, db: Session = Depends(get_db)):
    """
    Generate AI-powered marketing insights and recommendations.
    
    Args:
        website_url (HttpUrl): The URL of the Shopify store
        db (Session): Database session dependency
        
    Returns:
        AIMarketingInsights: Marketing intelligence and recommendations
    """
    try:
        normalized_url = normalize_url(str(website_url))
        brand_data = crud.get_brand_insights_from_db(db, normalized_url)
        
        if not brand_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No data found. Please fetch basic insights first."
            )
        
        ai_analyzer = AIAnalyzer()
        marketing_insights = ai_analyzer.generate_marketing_insights(brand_data)
        
        return {
            "status": "success",
            "brand_name": brand_data.brand_name,
            "marketing_intelligence": marketing_insights.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Marketing insights error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Marketing insights generation failed: {e}"
        )


@router.get("/pricing-intelligence", summary="Get AI-powered pricing analysis")
async def get_pricing_intelligence(website_url: HttpUrl, db: Session = Depends(get_db)):
    """
    Analyze pricing strategy and get intelligent recommendations.
    
    Args:
        website_url (HttpUrl): The URL of the Shopify store
        db (Session): Database session dependency
        
    Returns:
        PricingAnalysis: Comprehensive pricing intelligence
    """
    try:
        normalized_url = normalize_url(str(website_url))
        brand_data = crud.get_brand_insights_from_db(db, normalized_url)
        
        if not brand_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No data found. Please fetch basic insights first."
            )
        
        ai_analyzer = AIAnalyzer()
        pricing_analysis = ai_analyzer.analyze_pricing_intelligence(brand_data)
        
        return {
            "status": "success",
            "brand_name": brand_data.brand_name,
            "pricing_intelligence": pricing_analysis.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Pricing analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pricing analysis failed: {e}"
        )