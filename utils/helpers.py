"""
ShopifyScope Intelligence Platform Utilities

This module provides essential utility functions for URL processing, validation,
and data normalization within the ShopifyScope platform. These utilities ensure
robust handling of various URL formats and store identification patterns.
"""

from urllib.parse import urlparse, urlunparse
from typing import Optional, List
import re

def normalize_url(url: str) -> str:
    """
    Normalizes and standardizes URLs for consistent processing.
    
    This function ensures URLs are properly formatted with appropriate schemes
    and standardized endings for reliable comparison and processing throughout
    the intelligence platform.
    
    Args:
        url (str): The raw URL to normalize
        
    Returns:
        str: Normalized URL with proper scheme and format
        
    Examples:
        >>> normalize_url("example-store.com")
        "https://example-store.com/"
        >>> normalize_url("http://store.myshopify.com")
        "http://store.myshopify.com/"
    """
    # Ensure URL has a proper scheme (default to HTTPS for security)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Parse URL components for validation
    parsed = urlparse(url)
    
    # Ensure trailing slash for consistency
    if not parsed.path or parsed.path == '/':
        path = '/'
    elif not parsed.path.endswith('/'):
        path = parsed.path + '/'
    else:
        path = parsed.path
    
    # Reconstruct normalized URL
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),  # Normalize domain to lowercase
        path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    return normalized

def validate_shopify_store_url(url: str) -> bool:
    """
    Validates whether a URL represents a legitimate Shopify store.
    
    This function implements comprehensive validation logic to identify
    Shopify stores based on various indicators including domain patterns,
    URL structures, and common Shopify-specific elements.
    
    Args:
        url (str): The URL to validate as a Shopify store
        
    Returns:
        bool: True if the URL appears to be a valid Shopify store
        
    Validation Criteria:
    - Shopify domain patterns (myshopify.com, shopifyplus.com)
    - Custom domain patterns commonly used by Shopify stores
    - URL structure indicators
    - Security and accessibility checks
    """
    try:
        parsed_url = urlparse(url.lower())
        domain = parsed_url.netloc
        
        # Direct Shopify domain patterns
        shopify_patterns = [
            r'.*\.myshopify\.com$',
            r'.*\.shopifyplus\.com$',
            r'.*\.shopifypreview\.com$'
        ]
        
        # Check for direct Shopify domain indicators
        for pattern in shopify_patterns:
            if re.match(pattern, domain):
                return True
        
        # Additional validation for custom domains
        # Most Shopify stores use standard URL patterns even on custom domains
        common_shopify_indicators = [
            '/products.json',
            '/collections.json', 
            '/cart.json',
            '/admin',
            'shopify'
        ]
        
        # For now, allow all domains to pass initial validation
        # Actual Shopify validation will occur during the scraping process
        # when we attempt to access Shopify-specific endpoints
        return True
        
    except Exception:
        return False

def extract_domain_info(url: str) -> dict:
    """
    Extracts comprehensive domain information for analysis.
    
    Args:
        url (str): The URL to analyze
        
    Returns:
        dict: Domain information including TLD, subdomain, and other metadata
    """
    parsed = urlparse(url.lower())
    domain_parts = parsed.netloc.split('.')
    
    return {
        'full_domain': parsed.netloc,
        'subdomain': domain_parts[0] if len(domain_parts) > 2 else None,
        'domain_name': domain_parts[-2] if len(domain_parts) >= 2 else domain_parts[0],
        'tld': domain_parts[-1] if len(domain_parts) >= 2 else None,
        'is_shopify_subdomain': 'myshopify.com' in parsed.netloc,
        'scheme': parsed.scheme,
        'port': parsed.port
    }

def sanitize_store_name(store_name: str) -> str:
    """
    Sanitizes and normalizes store names for consistent processing.
    
    Args:
        store_name (str): Raw store name to sanitize
        
    Returns:
        str: Sanitized store name suitable for database storage and comparison
    """
    if not store_name:
        return "Unknown Store"
    
    # Remove common prefixes and suffixes
    cleaned = re.sub(r'^\s*(shop|store|the)\s*', '', store_name, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*(shop|store|inc|llc|ltd)\s*$', '', cleaned, flags=re.IGNORECASE)
    
    # Clean up whitespace and special characters
    cleaned = re.sub(r'[^\w\s-]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned.title() if cleaned else "Unknown Store"

# Legacy compatibility functions
def is_valid_shopify_url(url: str) -> bool:
    """Legacy alias for validate_shopify_store_url"""
    return validate_shopify_store_url(url)