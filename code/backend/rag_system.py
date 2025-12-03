"""RAG System - Section 4 of Architecture.

Retrieval-Augmented Generation using FAISS vector database.
"""
import json
import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from config import settings


class RAGSystem:
    """Vector-based retrieval system for Nike products, stores, inventory, and promotions."""
    
    def __init__(self):
        """Initialize the RAG system with embedding model and vector indices."""
        print("Initializing RAG system...")
        
        # Load embedding model
        self.model = SentenceTransformer(settings.embedding_model)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Data storage
        self.products = []
        self.stores = []
        self.inventory = []
        self.promotions = []
        self.user_preferences = []
        
        # FAISS indices
        self.product_index = None
        self.store_index = None
        self.promotion_index = None
        self.user_pref_index = None
        
        # Load data
        self._load_mock_data()
        self._create_indices()
        
        print(f"RAG system initialized with {len(self.products)} products, "
              f"{len(self.stores)} stores, {len(self.promotions)} promotions")
    
    def _load_mock_data(self):
        """Load all mock data from JSON files."""
        data_path = settings.mock_data_path
        
        # Load products
        with open(os.path.join(data_path, 'products.json'), 'r') as f:
            data = json.load(f)
            self.products = data['products']
        
        # Load stores
        with open(os.path.join(data_path, 'stores.json'), 'r') as f:
            data = json.load(f)
            self.stores = data['stores']
        
        # Load inventory
        with open(os.path.join(data_path, 'inventory.json'), 'r') as f:
            data = json.load(f)
            self.inventory = data['inventory']
        
        # Load promotions
        with open(os.path.join(data_path, 'promotions.json'), 'r') as f:
            data = json.load(f)
            self.promotions = data['promotions']
        
        # Load user preferences
        with open(os.path.join(data_path, 'user_preferences.json'), 'r') as f:
            data = json.load(f)
            self.user_preferences = data['user_preferences']
    
    def _create_indices(self):
        """Create FAISS indices for all data types."""
        # Products index
        product_texts = [p['embedding_text'] for p in self.products]
        product_embeddings = self.model.encode(product_texts, convert_to_numpy=True)
        self.product_index = faiss.IndexFlatL2(self.embedding_dim)
        self.product_index.add(product_embeddings)
        
        # Stores index
        store_texts = [s['embedding_text'] for s in self.stores]
        store_embeddings = self.model.encode(store_texts, convert_to_numpy=True)
        self.store_index = faiss.IndexFlatL2(self.embedding_dim)
        self.store_index.add(store_embeddings)
        
        # Promotions index
        promo_texts = [p['embedding_text'] for p in self.promotions]
        promo_embeddings = self.model.encode(promo_texts, convert_to_numpy=True)
        self.promotion_index = faiss.IndexFlatL2(self.embedding_dim)
        self.promotion_index.add(promo_embeddings)
        
        # User preferences index
        if self.user_preferences:
            user_texts = [u['embedding_text'] for u in self.user_preferences]
            user_embeddings = self.model.encode(user_texts, convert_to_numpy=True)
            self.user_pref_index = faiss.IndexFlatL2(self.embedding_dim)
            self.user_pref_index.add(user_embeddings)
    
    def query(self, query_text: str, intent: str = "general", 
              user_id: Optional[str] = None, k: int = None) -> List[Dict]:
        """
        Query the RAG system for relevant context.
        
        Args:
            query_text: User's query
            intent: Detected intent category
            user_id: Optional user ID for personalization
            k: Number of results (default from settings)
        
        Returns:
            List of relevant context chunks
        """
        if k is None:
            k = settings.top_k_results
        
        # Encode query
        query_embedding = self.model.encode([query_text], convert_to_numpy=True)
        
        context_chunks = []
        
        # Search based on intent
        if intent in ["product_availability", "recommendations", "general_query"]:
            # Search products - Limit to 3 as requested
            distances, indices = self.product_index.search(query_embedding, min(k, 3))
            for idx, dist in zip(indices[0], distances[0]):
                product = self.products[idx]
                context_chunks.append({
                    "type": "product",
                    "text": f"Product: {product['name']} ({product['category']}) - ${product['price']}. "
                            f"{product['description']} Available sizes: {', '.join(map(str, product['sizes_available']))}. "
                            f"Colors: {', '.join(product['colors'])}.",
                    "metadata": product,
                    "relevance_score": float(1.0 / (1.0 + dist))
                })
        
        if intent in ["store_locator", "product_availability", "general_query"]:
            # Search stores - Limit to 2 as requested
            distances, indices = self.store_index.search(query_embedding, min(k, 2))
            for idx, dist in zip(indices[0], distances[0]):
                store = self.stores[idx]
                context_chunks.append({
                    "type": "store",
                    "text": f"Store: {store['name']} at {store['mall_name']}. "
                            f"Hours: {store['hours']['monday']}. "
                            f"Services: {', '.join(store['services'])}. "
                            f"Contact: {store['contact']['phone']}.",
                    "metadata": store,
                    "relevance_score": float(1.0 / (1.0 + dist))
                })
        
        if intent in ["promotions", "general_query"]:
            # Search promotions
            distances, indices = self.promotion_index.search(query_embedding, min(k, 3))
            for idx, dist in zip(indices[0], distances[0]):
                promo = self.promotions[idx]
                context_chunks.append({
                    "type": "promotion",
                    "text": f"Promotion: {promo['name']} - {promo['description']}. "
                            f"Type: {promo['type']}.",
                    "metadata": promo,
                    "relevance_score": float(1.0 / (1.0 + dist))
                })
        
        # Add inventory data if querying product availability
        if intent == "product_availability":
            context_chunks.extend(self._get_inventory_context(query_text))
        
        # Add user preference context if user_id provided
        if user_id:
            user_context = self._get_user_preference_context(user_id)
            if user_context:
                context_chunks.append(user_context)
        
        # Sort by relevance
        context_chunks.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return context_chunks[:k]
    
    def _get_inventory_context(self, query: str) -> List[Dict]:
        """Get inventory information from query."""
        inventory_chunks = []
        
        # Simple keyword matching for inventory
        for inv in self.inventory:
            product_name = inv['product_name'].lower()
            store_name = inv['store_name'].lower()
            
            if product_name in query.lower() or store_name in query.lower():
                stock_info = f"Inventory: {inv['product_name']} at {inv['store_name']}. "
                stock_info += f"Total stock: {inv['total_units']} units. "
                
                # Add size-specific info if query mentions sizes
                size_match = None
                for size in inv.get('stock_by_size', {}).keys():
                    if str(size) in query:
                        size_match = size
                        break
                
                if size_match:
                    stock_info += f"Size {size_match}: {inv['stock_by_size'][size_match]} units available."
                
                inventory_chunks.append({
                    "type": "inventory",
                    "text": stock_info,
                    "metadata": inv,
                    "relevance_score": 0.9
                })
        
        return inventory_chunks
    
    def _get_user_preference_context(self, user_id: str) -> Optional[Dict]:
        """Get user preference context."""
        for user in self.user_preferences:
            if user['user_id'] == user_id:
                text = f"User preferences: Prefers {user['size_preferences'].get('shoes', 'unknown')} in shoes. "
                text += f"Favorite store: {user['favorite_store']['store_name']}. "
                text += f"Loyalty tier: {user['loyalty_tier']}."
                
                return {
                    "type": "user_preference",
                    "text": text,
                    "metadata": user,
                    "relevance_score": 1.0
                }
        return None
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get product details by ID."""
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None
    
    def get_store_by_id(self, store_id: str) -> Optional[Dict]:
        """Get store details by ID."""
        for store in self.stores:
            if store['id'] == store_id:
                return store
        return None


# Global RAG instance (initialized on first import)
rag_system = None

def get_rag_system() -> RAGSystem:
    """Get or create global RAG system instance."""
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
    return rag_system
