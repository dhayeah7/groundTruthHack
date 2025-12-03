"""Personalization Layer - Section 8 of Architecture."""
from typing import Dict, Optional, List


class PersonalizationEngine:
    """Add personalized touches to LLM responses."""
    
    def enhance_response(self, response: str, user_info: Optional[Dict],
                        context_metadata: List[Dict]) -> Dict:
        """
        Enhance response with personalization and structured data.
        
        Args:
            response: Raw LLM response text
            user_info: User preference data
            context_metadata: Metadata from RAG context chunks
        
        Returns:
            Enhanced response with personalization and UI hints
        """
        enhanced = {
            "text": response,
            "personalization": {},
            "ui_hints": {
                "show_product_cards": False,
                "show_map": False,
                "show_cta": False,
                "product_ids": [],
                "store_ids": []
            }
        }
        
        # Add personalization context
        if user_info:
            enhanced["personalization"] = {
                "loyalty_tier": user_info.get("loyalty_tier"),
                "preferred_size": user_info.get("preferred_size"),
                "favorite_store": user_info.get("favorite_store")
            }
            
        # Extract UI hints from LLM response (JSON block)
        import re
        import json
        
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        hints_found = False
        
        if json_match:
            try:
                llm_hints = json.loads(json_match.group(1))
                if "product_ids" in llm_hints:
                    enhanced["ui_hints"]["show_product_cards"] = True
                    enhanced["ui_hints"]["product_ids"] = llm_hints["product_ids"]
                    hints_found = True
                if "store_ids" in llm_hints:
                    enhanced["ui_hints"]["show_map"] = True
                    enhanced["ui_hints"]["store_ids"] = llm_hints["store_ids"]
                    hints_found = True
                
                # Remove the JSON block from the text response
                enhanced["text"] = response.replace(json_match.group(0), "").strip()
                
            except json.JSONDecodeError:
                pass
        
        # Fallback: Extract UI hints from context metadata if no LLM hints
        if not hints_found:
            for chunk in context_metadata:
                chunk_type = chunk.get("type")
                
                if chunk_type == "product":
                    enhanced["ui_hints"]["show_product_cards"] = True
                    product_id = chunk.get("metadata", {}).get("id")
                    if product_id:
                        enhanced["ui_hints"]["product_ids"].append(product_id)
                
                elif chunk_type == "store":
                    enhanced["ui_hints"]["show_map"] = True
                    store_id = chunk.get("metadata", {}).get("id")
                    if store_id:
                        enhanced["ui_hints"]["store_ids"].append(store_id)
                
                elif chunk_type == "inventory":
                    enhanced["ui_hints"]["show_cta"] = True

        # Add loyalty benefits to response if applicable AND products are shown
        if user_info and user_info.get("loyalty_tier") in ["Gold", "Silver"]:
            if enhanced["ui_hints"]["show_product_cards"]:
                tier = user_info["loyalty_tier"]
                discount = "15%" if tier == "Gold" else "10%"
                loyalty_note = f"\n\nAs a {tier} member, you get {discount} off this purchase!"
                if loyalty_note.strip() not in response:
                    enhanced["text"] += loyalty_note
        
        return enhanced


# Global personalization engine
personalization_engine = PersonalizationEngine()
