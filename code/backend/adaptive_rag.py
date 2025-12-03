"""Adaptive RAG Update System - Section 9 of Architecture."""
import json
import os
from typing import Dict, List
from datetime import datetime
from config import settings


class AdaptiveRAGUpdater:
    """Learn from conversations and update user preferences."""
    
    def __init__(self):
        """Initialize the adaptive updater."""
        self.user_prefs_path = os.path.join(settings.mock_data_path, 'user_preferences.json')
    
    def extract_insights(self, user_id: str, query: str, 
                        context_used: List[Dict], response: str) -> Dict:
        """
        Extract insights from a conversation.
        
        Args:
            user_id: User identifier
            query: User's query
            context_used: Context chunks that were used
            response: Generated response
        
        Returns:
            Extracted insights dictionary
        """
        insights = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "query_keywords": self._extract_keywords(query),
            "products_mentioned": [],
            "stores_mentioned": [],
            "sizes_mentioned": [],
            "intent_signals": []
        }
        
        # Extract products
        for chunk in context_used:
            if chunk.get("type") == "product":
                product = chunk.get("metadata", {})
                if product.get("id"):
                    insights["products_mentioned"].append({
                        "id": product["id"],
                        "name": product.get("name"),
                        "category": product.get("category")
                    })
            
            elif chunk.get("type") == "store":
                store = chunk.get("metadata", {})
                if store.get("id"):
                    insights["stores_mentioned"].append({
                        "id": store["id"],
                        "name": store.get("name")
                    })
        
        # Extract size mentions
        sizes = self._extract_sizes(query)
        insights["sizes_mentioned"] = sizes
        
        # Extract intent signals
        intent_keywords = [
            "marathon", "running", "training", "gym", "workout",
            "casual", "lifestyle", "racing", "beginner", "professional"
        ]
        for keyword in intent_keywords:
            if keyword in query.lower():
                insights["intent_signals"].append(keyword)
        
        return insights
    
    def update_user_preferences(self, insights: Dict) -> bool:
        """
        Update user preference file with new insights.
        
        Args:
            insights: Extracted insights from conversation
        
        Returns:
            True if update successful
        """
        try:
            # Load current preferences
            with open(self.user_prefs_path, 'r') as f:
                data = json.load(f)
                user_prefs = data.get('user_preferences', [])
            
            # Find or create user
            user = None
            for u in user_prefs:
                if u['user_id'] == insights['user_id']:
                    user = u
                    break
            
            if not user:
                # Create new user profile
                user = {
                    "user_id": insights['user_id'],
                    "conversation_history_count": 0,
                    "preferred_categories": [],
                    "preferred_products": [],
                    "size_preferences": {},
                    "favorite_store": {},
                    "purchase_intent_signals": [],
                    "loyalty_tier": "Member",
                    "embedding_text": ""
                }
                user_prefs.append(user)
            
            # Update conversation count
            user['conversation_history_count'] += 1
            
            # Update product preferences
            for product in insights.get('products_mentioned', []):
                existing = next((p for p in user['preferred_products'] 
                               if p.get('product_id') == product['id']), None)
                if existing:
                    existing['mentions'] += 1
                    existing['last_inquired'] = datetime.utcnow().strftime('%Y-%m-%d')
                else:
                    user['preferred_products'].append({
                        "product_id": product['id'],
                        "product_name": product['name'],
                        "mentions": 1,
                        "last_inquired": datetime.utcnow().strftime('%Y-%m-%d')
                    })
            
            # Update size preferences
            if insights.get('sizes_mentioned'):
                size = insights['sizes_mentioned'][0]  # Use first mentioned
                current_size = user['size_preferences'].get('shoes')
                if current_size == size:
                    # Increase confidence
                    user['size_preferences']['confidence'] = min(
                        user['size_preferences'].get('confidence', 0.5) + 0.1, 
                        1.0
                    )
                else:
                    user['size_preferences']['shoes'] = size
                    user['size_preferences']['confidence'] = 0.6
            
            # Update store preferences
            if insights.get('stores_mentioned'):
                store = insights['stores_mentioned'][0]
                if user.get('favorite_store', {}).get('store_id') == store['id']:
                    user['favorite_store']['visit_frequency'] += 1
                else:
                    user['favorite_store'] = {
                        "store_id": store['id'],
                        "store_name": store['name'],
                        "visit_frequency": 1,
                        "last_visit": datetime.utcnow().strftime('%Y-%m-%d')
                    }
            
            # Update intent signals
            for signal in insights.get('intent_signals', []):
                if signal not in user['purchase_intent_signals']:
                    user['purchase_intent_signals'].append(signal)
            
            # Update embedding text for better future matching
            user['embedding_text'] = self._build_embedding_text(user)
            
            # Save back to file
            with open(self.user_prefs_path, 'w') as f:
                json.dump({'user_preferences': user_prefs}, f, indent=2)
            
            print(f"Updated preferences for user {insights['user_id']}")
            return True
            
        except Exception as e:
            print(f"Error updating user preferences: {e}")
            return False
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Simple keyword extraction
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 4][:5]
        return keywords
    
    def _extract_sizes(self, text: str) -> List[str]:
        """Extract size mentions from text."""
        import re
        # Match shoe sizes (numeric) and apparel sizes (S, M, L, XL, etc)
        size_pattern = r'\b(size\s+)?(\d+\.?\d*|XS|S|M|L|XL|XXL)\b'
        matches = re.findall(size_pattern, text, re.IGNORECASE)
        return [m[1] for m in matches if m[1]]
    
    def _build_embedding_text(self, user: Dict) -> str:
        """Build embedding text from user profile."""
        parts = []
        
        # Products
        if user.get('preferred_products'):
            products = [p['product_name'] for p in user['preferred_products'][:3]]
            parts.append(f"prefers {' '.join(products)}")
        
        # Size
        if user.get('size_preferences', {}).get('shoes'):
            parts.append(f"size {user['size_preferences']['shoes']}")
        
        # Store
        if user.get('favorite_store', {}).get('store_name'):
            parts.append(f"{user['favorite_store']['store_name']}")
        
        # Loyalty
        parts.append(f"{user.get('loyalty_tier', 'member')}")
        
        # Intent signals
        if user.get('purchase_intent_signals'):
            parts.extend(user['purchase_intent_signals'][:3])
        
        return ' '.join(parts)


# Global updater instance
adaptive_updater = AdaptiveRAGUpdater()
