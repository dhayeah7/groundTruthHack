"""Gemini LLM Client - Section 7 of Architecture."""
import google.generativeai as genai
from config import settings
from typing import Optional


class GeminiClient:
    """Client for Google Gemini LLM API."""
    
    def __init__(self):
        """Initialize Gemini client with API key."""
        genai.configure(api_key=settings.gemini_api_key)
        
        # Use Gemini 2.0 Flash (confirmed available)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        # Generation config
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=1024,
        )
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate response from Gemini using the provided prompt.
        
        Args:
            prompt: Complete structured prompt (from PromptBuilder)
        
        Returns:
            Generated response text
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text
            
        except Exception as e:
            print(f"Error generating response from Gemini: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."
    
    async def generate_response_async(self, prompt: str) -> str:
        """Async version of generate_response (for future streaming support)."""
        # For now, just call sync version
        # In production, implement proper async streaming
        return self.generate_response(prompt)


# Global client instance
gemini_client = None

def get_gemini_client() -> GeminiClient:
    """Get or create global Gemini client."""
    global gemini_client
    if gemini_client is None:
        gemini_client = GeminiClient()
    return gemini_client
