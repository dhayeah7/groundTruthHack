"""Main FastAPI Application - Section 2 of Architecture (API Gateway)."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid

from config import settings
from intent_classifier import classifier
from rag_system import get_rag_system
from pii_redaction import redactor
from prompt_builder import prompt_builder
from gemini_client import get_gemini_client
from personalization import personalization_engine
from adaptive_rag import adaptive_updater

# Initialize FastAPI app
app = FastAPI(
    title="Nike AI Assistant API",
    description="Hyper-Personalized Nike AI Assistant with Adaptive RAG + PII Redaction + Gemini LLM",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class LocationData(BaseModel):
    """User location data."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ChatRequest(BaseModel):
    """Chat request from frontend."""
    message: str
    location: Optional[LocationData] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response to frontend."""
    response: str
    intent: str
    sentiment: str
    product_cards: List[Dict] = []
    store_info: List[Dict] = []
    show_map: bool = False
    show_cta: bool = False
    session_id: str
    debug_info: Optional[Dict] = None


# Session storage (in-memory for demo)
sessions = {}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Nike AI Assistant API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    try:
        rag = get_rag_system()
        gemini = get_gemini_client()
        
        return {
            "status": "healthy",
            "components": {
                "rag_system": "initialized",
                "gemini_client": "initialized",
                "intent_classifier": "ready",
                "pii_redactor": "ready"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - orchestrates the entire pipeline.
    
    Pipeline:
    1. Intent & Sentiment Classification (Section 3)
    2. RAG Retrieval (Section 4)
    3. PII Redaction (Section 5)
    4. Prompt Building (Section 6)
    5. Gemini LLM Generation (Section 7)
    6. Local Personalization (Section 8)
    7. Adaptive RAG Update (Section 9)
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        user_id = request.user_id or "anonymous"
        
        # SECTION 3: Intent & Sentiment Classification
        classification = classifier.classify(
            request.message,
            location=request.location.dict() if request.location else None
        )
        
        # SECTION 4: RAG Retrieval
        rag = get_rag_system()
        context_chunks = rag.query(
            query_text=request.message,
            intent=classification.intent.value,
            user_id=user_id if user_id != "anonymous" else None
        )
        
        # SECTION 5: PII Redaction (ONLY on RAG results)
        sanitized_chunks = redactor.redact_context(context_chunks)
        redaction_summary = redactor.get_redaction_summary()
        
        # Extract user info for personalization
        user_info = None
        for chunk in sanitized_chunks:
            if chunk.get('type') == 'user_preference':
                metadata = chunk.get('metadata', {})
                user_info = {
                    "name": metadata.get('name'),
                    "loyalty_tier": metadata.get('loyalty_tier'),
                    "preferred_size": metadata.get('size_preferences', {}).get('shoes'),
                    "favorite_store": metadata.get('favorite_store', {}).get('store_name'),
                    "purchase_history": metadata.get('purchase_history', [])
                }
                break
        
        # SECTION 6: Prompt Building
        prompt = prompt_builder.build_prompt(
            user_message=request.message,
            context_chunks=sanitized_chunks,
            user_info=user_info,
            conversation_history=sessions.get(session_id, [])
        )
        
        # SECTION 7: Gemini LLM Generation
        gemini = get_gemini_client()
        llm_response = await gemini.generate_response_async(prompt)
        
        # SECTION 8: Local Personalization
        enhanced_response = personalization_engine.enhance_response(
            response=llm_response,
            user_info=user_info,
            context_metadata=context_chunks
        )
        
        # SECTION 9: Adaptive RAG Update
        if user_id != "anonymous":
            insights = adaptive_updater.extract_insights(
                user_id=user_id,
                query=request.message,
                context_used=context_chunks,
                response=llm_response
            )
            adaptive_updater.update_user_preferences(insights)
        
        # Extract product and store data for UI
        product_cards = []
        store_info = []
        
        for product_id in enhanced_response["ui_hints"]["product_ids"]:
            product = rag.get_product_by_id(product_id)
            if product:
                product_cards.append({
                    "id": product["id"],
                    "name": product["name"],
                    "price": product["price"],
                    "category": product["category"],
                    "image_url": product.get("image_url", f"/api/product-images/{product['id']}.jpg"),
                    "colors": product["colors"][:2]  # First 2 colors
                })
        
        for store_id in enhanced_response["ui_hints"]["store_ids"]:
            store = rag.get_store_by_id(store_id)
            if store:
                store_info.append({
                    "id": store["id"],
                    "name": store["name"],
                    "address": f"{store['mall_name']}, {store['address']['city']}",
                    "hours": store["hours"]["monday"],
                    "coordinates": store["coordinates"]
                })
        
        # Build response
        response = ChatResponse(
            response=enhanced_response["text"],
            intent=classification.intent.value,
            sentiment=classification.sentiment.value,
            product_cards=product_cards,
            store_info=store_info,
            show_map=enhanced_response["ui_hints"]["show_map"],
            show_cta=enhanced_response["ui_hints"]["show_cta"],
            session_id=session_id,
            debug_info={
                "classification": {
                    "intent": classification.intent.value,
                    "sentiment": classification.sentiment.value,
                    "confidence": classification.confidence,
                    "keywords": classification.detected_keywords
                },
                "rag": {
                    "chunks_retrieved": len(context_chunks),
                    "chunks_redacted": redaction_summary["chunks_redacted"]
                },
                "personalization": enhanced_response["personalization"]
            }
        )
        
        # Store in session
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append({
            "user_message": request.message,
            "response": response.dict()
        })
        
        return response
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get conversation history for a session."""
    if session_id in sessions:
        return {"session_id": session_id, "messages": sessions[session_id]}
    return {"session_id": session_id, "messages": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
