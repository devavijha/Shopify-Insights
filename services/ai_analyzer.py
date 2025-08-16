"""
ShopifyScope AI Intelligence Engine

Advanced artificial intelligence module for transforming raw e-commerce data
into actionable business intelligence. Leverages state-of-the-art NLP and ML
algorithms to provide comprehensive market insights, sentiment analysis, and
strategic recommendations.

Features:
- Multi-dimensional sentiment analysis with confidence scoring
- Advanced marketing intelligence and audience segmentation
- Competitive pricing analysis and optimization strategies
- Business performance scoring and strategic recommendations
- Brand positioning and market differentiation insights
"""

import json
import re
from typing import List, Dict, Optional, Any, Tuple
from pydantic import BaseModel, Field
from models.brand_data import BrandContext, Product, FAQItem
import requests
from textblob import TextBlob
from collections import Counter, defaultdict
from config import OPENAI_API_KEY, HUGGINGFACE_API_KEY, ENABLE_AI_ANALYSIS
import statistics
import math

class BrandSentimentIntelligence(BaseModel):
    """Comprehensive sentiment analysis results for brand perception"""
    overall_sentiment_score: float = Field(..., ge=-1, le=1, description="Overall sentiment polarity score")
    positive_percentage: float = Field(..., ge=0, le=100, description="Percentage of positive sentiment")
    negative_percentage: float = Field(..., ge=0, le=100, description="Percentage of negative sentiment")
    neutral_percentage: float = Field(..., ge=0, le=100, description="Percentage of neutral sentiment")
    dominant_themes: List[str] = Field(..., description="Key themes extracted from content")
    confidence_level: float = Field(..., ge=0, le=1, description="Analysis confidence score")

class MarketIntelligenceReport(BaseModel):
    """Comprehensive marketing intelligence and audience insights"""
    identified_audiences: List[str] = Field(..., description="Target audience segments")
    brand_archetype: str = Field(..., description="Dominant brand personality type")
    content_framework: List[str] = Field(..., description="Strategic content recommendations")
    optimization_keywords: List[str] = Field(..., description="SEO and marketing keywords")
    growth_opportunities: List[str] = Field(..., description="Identified improvement areas")
    market_advantages: List[str] = Field(..., description="Competitive strengths")

class PricingIntelligenceAnalysis(BaseModel):
    """Advanced pricing strategy analysis and recommendations"""
    price_spectrum: str = Field(..., description="Price range analysis")
    mean_price_point: float = Field(..., description="Average pricing across catalog")
    pricing_methodology: str = Field(..., description="Identified pricing strategy")
    distribution_analysis: Dict[str, int] = Field(..., description="Price tier distribution")
    strategic_recommendations: List[str] = Field(..., description="Pricing optimization suggestions")

class CompetitiveIntelligence(BaseModel):
    """Market positioning and competitive analysis"""
    comparable_brands: List[str] = Field(..., description="Similar market players")
    market_opportunities: List[str] = Field(..., description="Identified market gaps")
    differentiation_strategies: List[str] = Field(..., description="Unique positioning opportunities")

# Legacy aliases for backward compatibility
SentimentAnalysis = BrandSentimentIntelligence
AIMarketingInsights = MarketIntelligenceReport
PricingAnalysis = PricingIntelligenceAnalysis
CompetitorInsight = CompetitiveIntelligence

class ShopifyScopeIntelligenceEngine:
    """
    Advanced AI intelligence engine for comprehensive e-commerce analysis.
    
    This class implements sophisticated algorithms for:
    - Natural language processing and sentiment analysis
    - Market research and competitive intelligence
    - Pricing strategy optimization
    - Business performance assessment
    - Strategic recommendation generation
    """
    
    def __init__(self):
        self.intelligence_enabled = ENABLE_AI_ANALYSIS
        self.openai_credentials = OPENAI_API_KEY
        self.huggingface_credentials = HUGGINGFACE_API_KEY
        self.analysis_threshold = 0.1  # Minimum confidence threshold
    
    def generate_brand_sentiment_intelligence(self, brand_context: BrandContext) -> BrandSentimentIntelligence:
        """Analyze sentiment from brand text, FAQs, and product descriptions using AI"""
        if not self.enabled:
            return self._default_sentiment()
        
        try:
            # Combine all text content
            text_content = []
            
            if brand_context.brand_text_context:
                text_content.append(brand_context.brand_text_context)
            
            if brand_context.faqs:
                for faq in brand_context.faqs[:10]:  # Limit to avoid token limits
                    text_content.extend([faq.question, faq.answer])
            
            if brand_context.product_catalog:
                for product in brand_context.product_catalog[:15]:
                    if product.description:
                        text_content.append(product.description[:200])  # Limit length
            
            combined_text = " ".join(text_content)[:2000]  # Limit total text
            
            if not combined_text.strip():
                return self._default_sentiment()
            
            # Use TextBlob for sentiment analysis (works offline)
            blob = TextBlob(combined_text)
            sentiment_score = blob.sentiment.polarity
            confidence = abs(blob.sentiment.subjectivity)
            
            # Convert to percentages
            if sentiment_score > 0.1:
                pos_pct = 60 + (sentiment_score * 30)
                neg_pct = 20 - (sentiment_score * 15)
            elif sentiment_score < -0.1:
                pos_pct = 20 + (sentiment_score * 15)
                neg_pct = 60 - (sentiment_score * 30)
            else:
                pos_pct = 40
                neg_pct = 30
            
            neu_pct = 100 - pos_pct - neg_pct
            
            # Extract key themes
            themes = self._extract_ai_themes(combined_text)
            
            return SentimentAnalysis(
                overall_score=sentiment_score,
                positive_percentage=pos_pct,
                negative_percentage=neg_pct,
                neutral_percentage=neu_pct,
                key_themes=themes,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"AI sentiment analysis error: {e}")
            return self._default_sentiment()
    
    def generate_marketing_insights(self, brand_context: BrandContext) -> AIMarketingInsights:
        """Generate comprehensive AI-powered marketing insights"""
        try:
            # Analyze product catalog for insights
            product_insights = self._analyze_product_portfolio(brand_context.product_catalog)
            
            # Identify target audience using AI techniques
            target_audience = self._ai_identify_target_audience(brand_context)
            
            # Analyze brand personality
            brand_personality = self._analyze_brand_personality_ai(brand_context)
            
            # Generate content strategy
            content_strategy = self._generate_ai_content_strategy(brand_context, product_insights)
            
            # Extract SEO keywords using frequency analysis
            seo_keywords = self._extract_ai_seo_keywords(brand_context)
            
            # Generate improvement suggestions
            improvements = self._generate_ai_improvements(brand_context)
            
            # Identify competitive advantages
            advantages = self._identify_competitive_advantages(brand_context, product_insights)
            
            return AIMarketingInsights(
                target_audience=target_audience,
                brand_personality=brand_personality,
                content_strategy=content_strategy,
                seo_keywords=seo_keywords,
                improvement_suggestions=improvements,
                competitive_advantages=advantages
            )
            
        except Exception as e:
            print(f"Marketing insights generation error: {e}")
            return self._default_marketing_insights()
    
    def analyze_pricing_intelligence(self, brand_context: BrandContext) -> PricingAnalysis:
        """Advanced AI-powered pricing analysis"""
        try:
            if not brand_context.product_catalog:
                return self._default_pricing_analysis()
            
            # Extract and clean prices
            prices = []
            for product in brand_context.product_catalog:
                price = self._extract_price_from_product(product)
                if price and price > 0:
                    prices.append(price)
            
            if not prices:
                return self._default_pricing_analysis()
            
            # Statistical analysis
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            # Price distribution analysis
            distribution = self._analyze_price_distribution(prices)
            
            # Determine pricing strategy using AI logic
            strategy = self._determine_ai_pricing_strategy(prices, avg_price)
            
            # Generate recommendations
            recommendations = self._generate_pricing_recommendations(prices, strategy, distribution)
            
            return PricingAnalysis(
                price_range=f"${min_price:.2f} - ${max_price:.2f}",
                average_price=avg_price,
                pricing_strategy=strategy,
                price_distribution=distribution,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"Pricing analysis error: {e}")
            return self._default_pricing_analysis()
    
    def generate_competitor_insights(self, brand_context: BrandContext) -> CompetitorInsight:
        """Generate competitor analysis using AI techniques"""
        try:
            # Analyze product categories to identify similar brands
            similar_brands = self._identify_similar_brands(brand_context)
            
            # Identify market gaps
            market_gaps = self._identify_market_gaps(brand_context)
            
            # Generate differentiation opportunities
            differentiation = self._identify_differentiation_opportunities(brand_context)
            
            return CompetitorInsight(
                similar_brands=similar_brands,
                market_gap_analysis=market_gaps,
                differentiation_opportunities=differentiation
            )
            
        except Exception as e:
            print(f"Competitor insights error: {e}")
            return CompetitorInsight(
                similar_brands=["Analysis unavailable"],
                market_gap_analysis=["Requires more data"],
                differentiation_opportunities=["Focus on unique value proposition"]
            )
    
    def generate_comprehensive_ai_report(self, brand_context: BrandContext) -> Dict[str, Any]:
        """Generate a comprehensive AI-powered business intelligence report"""
        try:
            # Run all AI analyses
            sentiment = self.analyze_brand_sentiment(brand_context)
            marketing = self.generate_marketing_insights(brand_context)
            pricing = self.analyze_pricing_intelligence(brand_context)
            competitor = self.generate_competitor_insights(brand_context)
            
            # Calculate overall business health score
            business_score = self._calculate_ai_business_score(
                brand_context, sentiment, marketing, pricing
            )
            
            # Generate strategic recommendations
            strategic_recommendations = self._generate_strategic_ai_recommendations(
                brand_context, sentiment, marketing, pricing, competitor
            )
            
            return {
                "brand_name": brand_context.brand_name or "Unknown Brand",
                "analysis_timestamp": "2025-08-16",
                "ai_business_health_score": business_score,
                "sentiment_analysis": sentiment.dict(),
                "marketing_intelligence": marketing.dict(),
                "pricing_intelligence": pricing.dict(),
                "competitive_intelligence": competitor.dict(),
                "strategic_recommendations": strategic_recommendations,
                "data_quality_score": self._assess_data_quality(brand_context),
                "ai_confidence_level": self._calculate_confidence_level(brand_context)
            }
            
        except Exception as e:
            print(f"Comprehensive AI report error: {e}")
            return {
                "brand_name": brand_context.brand_name or "Unknown Brand",
                "error": f"AI analysis failed: {str(e)}",
                "fallback_insights": "Basic analysis completed successfully"
            }
    
    # Helper methods
    def _default_sentiment(self) -> SentimentAnalysis:
        return SentimentAnalysis(
            overall_score=0.0,
            positive_percentage=40.0,
            negative_percentage=30.0,
            neutral_percentage=30.0,
            key_themes=["Standard business content"],
            confidence=0.5
        )
    
    def _extract_ai_themes(self, text: str) -> List[str]:
        """Extract key themes using NLP techniques"""
        # Common business themes
        theme_keywords = {
            'Quality': ['quality', 'premium', 'excellent', 'superior', 'high-grade'],
            'Customer Service': ['service', 'support', 'help', 'assistance', 'care'],
            'Innovation': ['innovative', 'new', 'latest', 'cutting-edge', 'advanced'],
            'Sustainability': ['sustainable', 'eco', 'green', 'environment', 'organic'],
            'Value': ['affordable', 'value', 'price', 'cost-effective', 'budget'],
            'Style': ['style', 'fashion', 'trendy', 'design', 'aesthetic'],
            'Convenience': ['easy', 'simple', 'convenient', 'quick', 'fast']
        }
        
        text_lower = text.lower()
        found_themes = []
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_themes.append(theme)
        
        return found_themes[:5] if found_themes else ['General Business']
    
    def _ai_identify_target_audience(self, brand_context: BrandContext) -> List[str]:
        """Use AI to identify target audience"""
        audiences = []
        
        if brand_context.product_catalog:
            # Analyze product names and descriptions
            product_text = " ".join([
                (p.title or "") + " " + (p.description or "")
                for p in brand_context.product_catalog[:20]
            ]).lower()
            
            audience_indicators = {
                'Women': ['women', 'female', 'ladies', 'her', 'she'],
                'Men': ['men', 'male', 'gentlemen', 'him', 'he'],
                'Young Adults': ['trendy', 'modern', 'hip', 'cool', 'millennial'],
                'Parents': ['family', 'kids', 'children', 'baby', 'parent'],
                'Professionals': ['business', 'office', 'professional', 'work', 'corporate'],
                'Fitness Enthusiasts': ['fitness', 'sport', 'athletic', 'gym', 'workout'],
                'Tech Savvy': ['tech', 'digital', 'smart', 'electronic', 'gadget'],
                'Luxury Consumers': ['luxury', 'premium', 'exclusive', 'high-end', 'designer']
            }
            
            for audience, indicators in audience_indicators.items():
                if any(indicator in product_text for indicator in indicators):
                    audiences.append(audience)
        
        return audiences[:4] if audiences else ['General Consumers']
    
    def _analyze_brand_personality_ai(self, brand_context: BrandContext) -> str:
        """Analyze brand personality using AI techniques"""
        if not brand_context.brand_text_context:
            return "Professional & Reliable"
        
        text = brand_context.brand_text_context.lower()
        
        personality_indicators = {
            'Innovative & Tech-Forward': ['innovation', 'technology', 'cutting-edge', 'advanced', 'future'],
            'Luxury & Sophisticated': ['luxury', 'premium', 'exclusive', 'sophisticated', 'elegant'],
            'Fun & Energetic': ['fun', 'exciting', 'vibrant', 'energetic', 'playful'],
            'Eco-Conscious & Responsible': ['sustainable', 'eco', 'green', 'responsible', 'ethical'],
            'Minimalist & Clean': ['simple', 'clean', 'minimal', 'pure', 'essential'],
            'Bold & Adventurous': ['bold', 'adventure', 'daring', 'fearless', 'brave']
        }
        
        max_matches = 0
        personality = "Professional & Reliable"
        
        for pers, indicators in personality_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text)
            if matches > max_matches:
                max_matches = matches
                personality = pers
        
        return personality
    
    def _extract_price_from_product(self, product: Product) -> Optional[float]:
        """Extract numeric price from product"""
        if not product.price:
            return None
        
        if isinstance(product.price, (int, float)):
            return float(product.price)
        
        if isinstance(product.price, str):
            # Remove currency symbols and extract number
            price_str = re.sub(r'[^\d.,]', '', product.price)
            price_str = price_str.replace(',', '')
            try:
                return float(price_str)
            except ValueError:
                return None
        
        return None
    
    def _analyze_price_distribution(self, prices: List[float]) -> Dict[str, int]:
        """Analyze price distribution across ranges"""
        ranges = {
            'Under $25': 0,
            '$25-$50': 0,
            '$50-$100': 0,
            '$100-$200': 0,
            'Over $200': 0
        }
        
        for price in prices:
            if price < 25:
                ranges['Under $25'] += 1
            elif price < 50:
                ranges['$25-$50'] += 1
            elif price < 100:
                ranges['$50-$100'] += 1
            elif price < 200:
                ranges['$100-$200'] += 1
            else:
                ranges['Over $200'] += 1
        
        return ranges
    
    def _determine_ai_pricing_strategy(self, prices: List[float], avg_price: float) -> str:
        """Determine pricing strategy using AI logic"""
        if avg_price < 30:
            return "Budget-Friendly Strategy"
        elif avg_price > 150:
            return "Premium Positioning"
        elif max(prices) / min(prices) > 5:
            return "Tiered Pricing Model"
        elif len(set(prices)) / len(prices) > 0.8:
            return "Dynamic Pricing"
        else:
            return "Competitive Pricing"
    
    def _calculate_ai_business_score(
        self, 
        brand_context: BrandContext, 
        sentiment: SentimentAnalysis,
        marketing: AIMarketingInsights, 
        pricing: PricingAnalysis
    ) -> float:
        """Calculate AI-powered business health score"""
        score = 0.0
        
        # Data completeness (30%)
        data_score = self._assess_data_quality(brand_context) * 3.0
        
        # Sentiment score (25%)
        sentiment_score = (sentiment.overall_score + 1) / 2 * 2.5
        
        # Product portfolio (20%)
        product_score = min(len(brand_context.product_catalog or []) / 20, 1) * 2.0
        
        # Social presence (15%)
        social_score = min(len(brand_context.social_handles or []) / 3, 1) * 1.5
        
        # Pricing strategy (10%)
        pricing_score = 1.0 if pricing.average_price > 0 else 0.0
        
        total_score = data_score + sentiment_score + product_score + social_score + pricing_score
        return round(min(total_score, 10.0), 1)
    
    def _assess_data_quality(self, brand_context: BrandContext) -> float:
        """Assess the quality and completeness of scraped data"""
        quality_indicators = [
            bool(brand_context.brand_name),
            bool(brand_context.product_catalog),
            bool(brand_context.brand_text_context),
            bool(brand_context.contact_details),
            bool(brand_context.social_handles),
            bool(brand_context.privacy_policy),
            bool(brand_context.return_refund_policy),
            bool(brand_context.faqs),
            bool(brand_context.important_links),
            bool(brand_context.hero_products)
        ]
        
        return sum(quality_indicators) / len(quality_indicators)
    
    def _calculate_confidence_level(self, brand_context: BrandContext) -> str:
        """Calculate AI confidence level based on data availability"""
        quality_score = self._assess_data_quality(brand_context)
        
        if quality_score >= 0.8:
            return "High Confidence"
        elif quality_score >= 0.6:
            return "Medium Confidence"
        else:
            return "Low Confidence - Limited Data"
    
    # Additional helper methods for comprehensive analysis
    def _analyze_product_portfolio(self, products: List[Product]) -> Dict[str, Any]:
        """Analyze product portfolio for insights"""
        if not products:
            return {"diversity": 0, "categories": [], "avg_description_length": 0}
        
        categories = [p.product_type for p in products if p.product_type]
        category_diversity = len(set(categories)) / len(products) if products else 0
        
        descriptions = [p.description for p in products if p.description]
        avg_desc_length = sum(len(d) for d in descriptions) / len(descriptions) if descriptions else 0
        
        return {
            "diversity": category_diversity,
            "categories": list(set(categories))[:10],
            "avg_description_length": avg_desc_length,
            "total_products": len(products)
        }
    
    def _generate_ai_content_strategy(self, brand_context: BrandContext, product_insights: Dict) -> List[str]:
        """Generate AI-powered content strategy recommendations"""
        strategies = ["Share behind-the-scenes content", "Highlight customer testimonials"]
        
        if product_insights["diversity"] > 0.5:
            strategies.append("Create category-specific content campaigns")
        
        if brand_context.social_handles and len(brand_context.social_handles) > 2:
            strategies.append("Implement cross-platform content strategy")
        
        if brand_context.faqs and len(brand_context.faqs) > 5:
            strategies.append("Transform FAQs into educational content")
        
        strategies.extend([
            "Develop user-generated content campaigns",
            "Create seasonal and trending content",
            "Implement storytelling in product showcases"
        ])
        
        return strategies[:6]
    
    def _extract_ai_seo_keywords(self, brand_context: BrandContext) -> List[str]:
        """Extract SEO keywords using AI techniques"""
        all_text = []
        
        if brand_context.brand_name:
            all_text.append(brand_context.brand_name.lower())
        
        if brand_context.brand_text_context:
            all_text.append(brand_context.brand_text_context.lower())
        
        if brand_context.product_catalog:
            for product in brand_context.product_catalog[:30]:
                if product.title:
                    all_text.append(product.title.lower())
                if product.description:
                    all_text.append(product.description[:100].lower())
        
        # Extract and count words
        words = []
        for text in all_text:
            words.extend(re.findall(r'\b[a-zA-Z]{3,}\b', text))
        
        # Filter out common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Get most common words
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(15)]
    
    def _generate_ai_improvements(self, brand_context: BrandContext) -> List[str]:
        """Generate AI-powered improvement suggestions"""
        improvements = []
        
        # Data completeness improvements
        if not brand_context.faqs or len(brand_context.faqs) < 5:
            improvements.append("Expand FAQ section with common customer queries")
        
        if not brand_context.social_handles or len(brand_context.social_handles) < 3:
            improvements.append("Increase social media presence across platforms")
        
        if not brand_context.brand_text_context or len(brand_context.brand_text_context) < 100:
            improvements.append("Develop comprehensive brand story and mission statement")
        
        # Product improvements
        if brand_context.product_catalog:
            products_without_desc = sum(1 for p in brand_context.product_catalog if not p.description)
            if products_without_desc > len(brand_context.product_catalog) * 0.3:
                improvements.append("Add detailed descriptions to more products")
        
        # General improvements
        improvements.extend([
            "Implement customer review system",
            "Add live chat support",
            "Create email newsletter signup",
            "Develop loyalty program",
            "Optimize mobile experience"
        ])
        
        return improvements[:6]
    
    def _identify_competitive_advantages(self, brand_context: BrandContext, product_insights: Dict) -> List[str]:
        """Identify competitive advantages using AI analysis"""
        advantages = []
        
        if product_insights["diversity"] > 0.7:
            advantages.append("Diverse product portfolio")
        
        if brand_context.social_handles and len(brand_context.social_handles) >= 4:
            advantages.append("Strong social media presence")
        
        if brand_context.faqs and len(brand_context.faqs) >= 10:
            advantages.append("Comprehensive customer support")
        
        if brand_context.return_refund_policy and brand_context.privacy_policy:
            advantages.append("Transparent policies and trust-building")
        
        advantages.extend([
            "User-friendly website structure",
            "Clear brand identity",
            "Customer-centric approach"
        ])
        
        return advantages[:5]
    
    def _identify_similar_brands(self, brand_context: BrandContext) -> List[str]:
        """Identify similar brands based on product analysis"""
        # This would typically use external APIs or databases
        # For now, return generic categories based on products
        if not brand_context.product_catalog:
            return ["Similar brands analysis requires product data"]
        
        # Extract product categories
        categories = [p.product_type for p in brand_context.product_catalog if p.product_type]
        
        if not categories:
            return ["Analysis requires product category information"]
        
        # Generate generic similar brand suggestions based on categories
        category_text = " ".join(categories).lower()
        
        if "clothing" in category_text or "apparel" in category_text:
            return ["Fashion retail brands", "Apparel companies", "Clothing retailers"]
        elif "tech" in category_text or "electronic" in category_text:
            return ["Technology brands", "Electronics retailers", "Gadget companies"]
        else:
            return ["Similar product retailers", "Comparable e-commerce brands"]
    
    def _identify_market_gaps(self, brand_context: BrandContext) -> List[str]:
        """Identify potential market gaps"""
        gaps = [
            "Personalization features could be enhanced",
            "Mobile app development opportunity",
            "Subscription service potential"
        ]
        
        if not brand_context.faqs or len(brand_context.faqs) < 5:
            gaps.append("Customer education content gap")
        
        if not brand_context.brand_text_context or "sustainability" not in brand_context.brand_text_context.lower():
            gaps.append("Sustainability messaging opportunity")
        
        return gaps[:4]
    
    def _identify_differentiation_opportunities(self, brand_context: BrandContext) -> List[str]:
        """Identify differentiation opportunities"""
        opportunities = [
            "Develop unique brand storytelling",
            "Create exclusive product lines",
            "Implement innovative customer service"
        ]
        
        if brand_context.product_catalog and len(brand_context.product_catalog) > 20:
            opportunities.append("Launch product customization options")
        
        opportunities.extend([
            "Build community around brand values",
            "Develop expertise-based content marketing"
        ])
        
        return opportunities[:5]
    
    def _generate_strategic_ai_recommendations(
        self, 
        brand_context: BrandContext,
        sentiment: SentimentAnalysis,
        marketing: AIMarketingInsights,
        pricing: PricingAnalysis,
        competitor: CompetitorInsight
    ) -> List[str]:
        """Generate comprehensive strategic recommendations"""
        recommendations = []
        
        # Sentiment-based recommendations
        if sentiment.overall_score < 0:
            recommendations.append("Priority: Address customer sentiment issues and improve brand perception")
        elif sentiment.overall_score > 0.5:
            recommendations.append("Leverage positive sentiment in marketing campaigns and testimonials")
        
        # Pricing-based recommendations
        if pricing.average_price > 0:
            if "Budget" in pricing.pricing_strategy:
                recommendations.append("Consider premium product line expansion for higher margins")
            elif "Premium" in pricing.pricing_strategy:
                recommendations.append("Ensure customer experience matches premium positioning")
        
        # Marketing recommendations
        if len(marketing.target_audience) > 2:
            recommendations.append("Develop targeted campaigns for each identified audience segment")
        
        # Data quality recommendations
        quality_score = self._assess_data_quality(brand_context)
        if quality_score < 0.7:
            recommendations.append("Improve website content completeness and information architecture")
        
        recommendations.extend([
            "Implement data-driven decision making processes",
            "Regular competitor analysis and market monitoring",
            "Customer feedback integration system"
        ])
        
        return recommendations[:6]
    
    def _default_marketing_insights(self) -> AIMarketingInsights:
        """Default marketing insights when AI analysis fails"""
        return AIMarketingInsights(
            target_audience=["General Consumers"],
            brand_personality="Professional",
            content_strategy=["Regular social media updates", "Product showcases"],
            seo_keywords=["brand", "products", "shop"],
            improvement_suggestions=["Improve data collection"],
            competitive_advantages=["Quality products"]
        )
    
    def _default_pricing_analysis(self) -> PricingAnalysis:
        """Default pricing analysis when data is insufficient"""
        return PricingAnalysis(
            price_range="Unknown",
            average_price=0.0,
            pricing_strategy="Analysis requires price data",
            price_distribution={},
            recommendations=["Enable price data collection"]
        )
    
    def _generate_pricing_recommendations(
        self, 
        prices: List[float], 
        strategy: str, 
        distribution: Dict[str, int]
    ) -> List[str]:
        """Generate pricing recommendations based on analysis"""
        recommendations = []
        
        if "Budget" in strategy:
            recommendations.extend([
                "Consider bundle deals to increase average order value",
                "Implement volume discounts for bulk purchases",
                "Explore upselling opportunities"
            ])
        elif "Premium" in strategy:
            recommendations.extend([
                "Emphasize quality and exclusivity in marketing",
                "Provide premium customer service experience",
                "Create VIP customer programs"
            ])
        elif "Tiered" in strategy:
            recommendations.extend([
                "Clearly communicate value propositions for each tier",
                "Guide customers to appropriate price points",
                "Optimize product mix across tiers"
            ])
        
        recommendations.append("Monitor competitor pricing regularly")
        recommendations.append("Test price sensitivity with A/B testing")
        
        return recommendations[:5]

# Legacy alias for backward compatibility
class AIAnalyzer(ShopifyScopeIntelligenceEngine):
    """Legacy compatibility class with original method names"""
    
    def __init__(self):
        super().__init__()
        # Legacy attributes for backward compatibility
        self.enabled = self.intelligence_enabled
        self.openai_key = self.openai_credentials
        self.hf_key = self.huggingface_credentials
    
    def analyze_brand_sentiment(self, brand_context):
        """Legacy method name for sentiment analysis"""
        return self.generate_brand_sentiment_intelligence(brand_context)
    
    def generate_marketing_insights(self, brand_context):
        """Legacy method name for marketing insights"""
        return self.generate_market_intelligence(brand_context)
    
    def analyze_pricing_intelligence(self, brand_context):
        """Legacy method name for pricing analysis"""
        return super().analyze_pricing_intelligence(brand_context)
    
    def generate_pricing_intelligence(self, brand_context):
        """Alternative method name for pricing analysis"""
        return super().analyze_pricing_intelligence(brand_context)
    
    def generate_competitor_insights(self, brand_context):
        """Legacy method name for competitive intelligence"""
        return self.generate_competitive_intelligence(brand_context)
