"""Prompt Builder - Section 6 of Architecture."""
from typing import List, Dict


class PromptBuilder:
    """Build structured prompts for Gemini LLM."""
    
    SYSTEM_INSTRUCTION = """You are a helpful Nike customer support assistant. Your role is to help customers find products, locate stores, check availability, and provide information about promotions.

Guidelines:
- Be friendly, enthusiastic, and helpful
- Use the provided context to answer questions accurately
- If a product is in stock, mention the quantity and location
- Suggest related products when appropriate
- Always mention relevant promotions or loyalty benefits
- If you don't have information in the context, politely say so
- Keep responses concise but informative
- Use natural, conversational language

Remember: You represent the Nike brand - maintain a positive, athletic, and inspiring tone."""
    
    def _format_user_profile(self, user_profile: dict) -> str:
        """Formats user profile information into a string."""
        if not user_profile:
            return "Guest User"
        
        profile_parts = []
        if 'loyalty_tier' in user_profile:
            profile_parts.append(f"- Loyalty Tier: {user_profile['loyalty_tier']}")
        if 'preferred_size' in user_profile:
            profile_parts.append(f"- Preferred Size: {user_profile['preferred_size']}")
        if 'favorite_store' in user_profile:
            profile_parts.append(f"- Usual Store: {user_profile['favorite_store']}")
        
        return "\n".join(profile_parts) if profile_parts else "Guest User"

    def build_prompt(self, user_message: str, context_chunks: List[Dict], 
                    user_info: Dict = None, conversation_history: List[Dict] = None) -> str:
        """
        Build a structured prompt combining system instruction, context, and user message.
        """
        # Extract user name if available
        user_name = "there"
        if user_info and user_info.get('name'):
            full_name = user_info['name']
            user_name = full_name.split(' ')[0] if ' ' in full_name else full_name

        system_instruction = f"""You are a helpful, energetic Nike AI Assistant.
Your goal is to help customers find products, check store availability, and get recommendations.

CRITICAL INSTRUCTIONS:
1. BE BRIEF AND CONCISE. Do not ramble.
2. Use the customer's name: "Hey {user_name}!"
3. FORMATTING: Do NOT use asterisks (*) for bullet points or bold text. Use dashes (-) for lists. Keep it clean.
4. Do NOT redact store information like phone numbers.
5. SINGLE PRODUCT FOCUS: If the user asks about a specific product (e.g., "Show me Air Force 1"), ONLY return that single product ID (e.g., "P011") in the JSON `product_ids` list. Do NOT use the product name.
6. STORE RELEVANCE: Do NOT include `store_ids` in the JSON unless you explicitly mention the store in your text response.
7. RELEVANCE: Only recommend items/stores if there is a specific reason.
8. Always maintain the Nike brand voice.

CONTEXT FROM DATABASE:
"""
        prompt_parts = [system_instruction]
        
        # Context section
        if context_chunks:
            for i, chunk in enumerate(context_chunks, 1):
                prompt_parts.append(f"{i}. {chunk['text']}\n")
            prompt_parts.append("\n---\n")
        
        # User personalization (if available)
        if user_info:
            prompt_parts.append("USER PROFILE:\n")
            if 'loyalty_tier' in user_info:
                prompt_parts.append(f"- Loyalty Tier: {user_info['loyalty_tier']}\n")
            if 'preferred_size' in user_info:
                prompt_parts.append(f"- Preferred Size: {user_info['preferred_size']}\n")
            if 'favorite_store' in user_info:
                prompt_parts.append(f"- Usual Store: {user_info['favorite_store']}\n")
            
            # Add purchase history
            if 'purchase_history' in user_info and user_info['purchase_history']:
                history = user_info['purchase_history']
                prompt_parts.append("- Recent Purchases:\n")
                for p in history[:3]:  # Show last 3
                    prompt_parts.append(f"  * {p['product_name']} (${p['price']}) on {p['date']}\n")
            
            prompt_parts.append("\n---\n")
            
        # Add conversation history
        if conversation_history:
            prompt_parts.append("CONVERSATION HISTORY:\n")
            for turn in conversation_history[-5:]:  # Last 5 turns
                prompt_parts.append(f"User: {turn['user_message']}\n")
                if 'response' in turn:
                    # Handle both dict and object response formats
                    resp_text = turn['response'].get('response') if isinstance(turn['response'], dict) else turn['response']
                    prompt_parts.append(f"AI: {resp_text}\n")
            prompt_parts.append("\n---\n")
            
        # User query
        prompt_parts.append(f"USER QUERY: {user_message}\n")
        prompt_parts.append("RESPONSE:")
        
        return "".join(prompt_parts)
    
    def build_simple_prompt(self, user_message: str) -> str:
        """Build a simple prompt without context (for general queries)."""
        return f"{self.SYSTEM_INSTRUCTION}\n\n---\n\nUSER QUESTION: {user_message}\n\nASSISTANT RESPONSE:"


# Global builder instance
prompt_builder = PromptBuilder()
