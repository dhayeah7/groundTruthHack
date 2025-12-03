"""Intent and Sentiment Classifier - Section 3 of Architecture."""
from enum import Enum
from typing import Dict, List
from pydantic import BaseModel


class IntentCategory(str, Enum):
    """User intent categories."""
    PRODUCT_AVAILABILITY = "product_availability"
    STORE_LOCATOR = "store_locator"
    RECOMMENDATIONS = "recommendations"
    PROMOTIONS = "promotions"
    GENERAL_QUERY = "general_query"


class Sentiment(str, Enum):
    """User sentiment/tone."""
    URGENT = "urgent"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    NEUTRAL = "neutral"


class ClassificationResult(BaseModel):
    """Classification result structure."""
    intent: IntentCategory
    sentiment: Sentiment
    confidence: float
    detected_keywords: List[str]


class IntentClassifier:
    """Lightweight intent and sentiment classifier using keyword matching."""
    
    # Intent detection patterns
    INTENT_PATTERNS = {
        IntentCategory.PRODUCT_AVAILABILITY: [
            "do you have", "in stock", "available", "availability",
            "size", "color", "variant", "check stock"
        ],
        IntentCategory.STORE_LOCATOR: [
            "where", "location", "nearest", "store", "address",
            "directions", "how to get", "find store", "near me"
        ],
        IntentCategory.RECOMMENDATIONS: [
            "recommend", "suggest", "what should", "best for",
            "looking for", "need", "want", "show me", "help me find"
        ],
        IntentCategory.PROMOTIONS: [
            "sale", "discount", "promo", "offer", "deal",
            "coupon", "loyalty", "member", "save", "cheap"
        ]
    }
    
    # Sentiment detection patterns
    SENTIMENT_PATTERNS = {
        Sentiment.URGENT: [
            "asap", "urgent", "quick", "immediately", "right now",
            "hurry", "need soon", "time sensitive"
        ],
        Sentiment.FRUSTRATED: [
            "frustrated", "annoyed", "disappointed", "unhappy",
            "terrible", "bad", "worst", "still waiting", "why"
        ],
        Sentiment.EXCITED: [
            "excited", "love", "awesome", "amazing", "great",
            "can't wait", "fantastic", "perfect", "yes!"
        ]
    }
    
    def classify(self, message: str, location: dict = None) -> ClassificationResult:
        """
        Classify user message into intent category and sentiment.
        
        Args:
            message: User's message text
            location: Optional location data (if provided, may influence intent)
        
        Returns:
            ClassificationResult with intent, sentiment, and confidence
        """
        message_lower = message.lower()
        detected_keywords = []
        
        # Detect intent
        intent_scores = {}
        for intent, keywords in self.INTENT_PATTERNS.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                intent_scores[intent] = score
                detected_keywords.extend([kw for kw in keywords if kw in message_lower])
        
        # Store locator gets boost if location provided
        if location and IntentCategory.STORE_LOCATOR in intent_scores:
            intent_scores[IntentCategory.STORE_LOCATOR] += 1
        
        # Determine primary intent
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[primary_intent] / 3.0, 1.0)  # Normalize
        else:
            primary_intent = IntentCategory.GENERAL_QUERY
            confidence = 0.5
        
        # Detect sentiment
        sentiment_scores = {}
        for sentiment, keywords in self.SENTIMENT_PATTERNS.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                sentiment_scores[sentiment] = score
        
        # Determine sentiment (default to neutral)
        if sentiment_scores:
            detected_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        else:
            detected_sentiment = Sentiment.NEUTRAL
        
        return ClassificationResult(
            intent=primary_intent,
            sentiment=detected_sentiment,
            confidence=confidence,
            detected_keywords=list(set(detected_keywords[:5]))  # Top 5 unique
        )


# Global classifier instance
classifier = IntentClassifier()
