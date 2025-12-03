# Nike AI Assistant Backend

Backend API for the Nike AI Assistant with Adaptive RAG, PII Redaction, and
Gemini LLM.

## Architecture Components

This backend implements sections 2-9 of the architecture:

- **Section 2**: API Gateway (FastAPI)
- **Section 3**: Intent & Sentiment Classifier
- **Section 4**: RAG System (FAISS vector database)
- **Section 5**: PII Redaction Layer
- **Section 6**: Prompt Builder
- **Section 7**: Gemini LLM Integration
- **Section 8**: Local Personalization
- **Section 9**: Adaptive RAG Update System

## Setup

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Configure environment**:

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

3. **Run the server**:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### `POST /chat`

Main chat endpoint that processes user messages through the complete pipeline.

**Request**:

```json
{
    "message": "Do you have Pegasus size 10 at KLCC?",
    "location": {
        "latitude": 3.1576,
        "longitude": 101.7117
    },
    "user_id": "U001",
    "session_id": "optional-session-id"
}
```

**Response**:

```json
{
  "response": "Yes! Nike Air Zoom Pegasus 40 size 10 is in stock...",
  "intent": "product_availability",
  "sentiment": "neutral",
  "product_cards": [...],
  "store_info": [...],
  "show_map": true,
  "show_cta": true,
  "session_id": "uuid",
  "debug_info": {...}
}
```

### `GET /health`

Health check endpoint showing status of all components.

### `GET /session/{session_id}`

Retrieve conversation history for a session.

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `CORS_ORIGINS`: Allowed CORS origins (default: http://localhost:3000)
- `MOCK_DATA_PATH`: Path to mock RAG data (default: ../mock-rag-data)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

## Development

The backend uses:

- **FastAPI** for the API framework
- **sentence-transformers** for text embeddings
- **FAISS** for vector similarity search
- **Google Generative AI** SDK for Gemini LLM
- **Pydantic** for data validation

All components are modular and can be tested independently.
