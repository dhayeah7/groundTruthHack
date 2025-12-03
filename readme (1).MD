# H-002 | Customer Experience Automation

Complete implementation of the Hyper-Personalized Nike AI Assistant with
Adaptive RAG, Single PII Redaction, and Gemini LLM integration.

# 🔄 Data Flow (Brief Overview)

## 1. User Query (Web UI)
- User enters a message in the chat interface.
- User's location is captured.
- Request is sent securely via **HTTPS** to the backend.

## 2. Backend Processing
- **Intent & Entity Detection** – Extracts product, size, location, action type.
- **RAG Engine** – Searches vector DB + structured JSON/DB sources for relevant context:
  - `products`, `stores`, `inventory`, `promotions`, `preferences`

## 3. PII Redaction Layer
Removes sensitive information before sending to LLM:
- emails, phone numbers, order IDs, full street addresses  
- internal database IDs / employee names  
Keeps product info, store name, mall location, promotions

## 4. Gemini LLM Response Generation
- Uses **redacted context + user query**
- Generates a natural, structured response

## 5. Local Personalization & UI Response
- Backend adds UI elements: **product cards, maps, CTAs, reservation options**
- Final formatted response returned to the frontend UI

## 6. Adaptive Learning
- User intent & preference summary converted into embeddings
- Stored back into **Vector DB** to improve future recommendations

## 🏗️ Architecture Overview

This system implements all 10 sections from the architecture diagram:

1. **Web Client / Front-End** - Next.js chat UI (`/nike-ai-chat`)
2. **Backend API Gateway** - FastAPI (`/backend/main.py`)
3. **Intent + Sentiment Classifier** - Keyword-based classification
   (`/backend/intent_classifier.py`)
4. **RAG System** - FAISS vector database (`/backend/rag_system.py`)
5. **Single PII Redaction** - RegEx-based sanitization
   (`/backend/pii_redaction.py`)
6. **Prompt Builder** - LLM prompt assembly (`/backend/prompt_builder.py`)
7. **Gemini LLM** - Google Gemini 1.5 Flash (`/backend/gemini_client.py`)
8. **Local Personalization** - User-specific enhancements
   (`/backend/personalization.py`)
9. **Adaptive RAG Update** - Continuous learning (`/backend/adaptive_rag.py`)
10. **Response Render** - UI display with product cards & CTAs (`/nike-ai-chat`)

Backend will run at **http://localhost:8000**
Frontend will run at **http://localhost:3000**


## 📁 Project Structure

```
/gtHack
├── mock-rag-data/              # Mock data for RAG system
│   ├── products.json           # 10 Nike products
│   ├── stores.json             # 5 KL area stores
│   ├── inventory.json          # Real-time stock data
│   ├── promotions.json         # 8 active promotions
│   ├── user_preferences.json   # 5 user profiles
│   └── README.md               # Data documentation
│
├── backend/                    # FastAPI backend (Python)
│   ├── main.py                 # Main API app (Section 2)
│   ├── intent_classifier.py   # Section 3
│   ├── rag_system.py           # Section 4
│   ├── pii_redaction.py        # Section 5
│   ├── prompt_builder.py       # Section 6
│   ├── gemini_client.py        # Section 7
│   ├── personalization.py      # Section 8
│   ├── adaptive_rag.py         # Section 9
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables
│
└── nike-ai-chat/               # Next.js frontend (TypeScript)
    ├── app/
    │   ├── page.tsx            # Main chat interface
    │   └── layout.tsx          # Root layout
    ├── components/
    │   ├── ChatBubble.tsx      # Message bubbles
    │   ├── ProductCard.tsx     # Product display
    │   └── StoreCard.tsx       # Store information
    ├── lib/
    │   ├── api.ts              # API client
    │   └── config.ts           # Frontend config
    └── package.json
```

### Backend

-  Intent classification (product/store/promo/general)
-  Sentiment detection (urgent/frustrated/excited/neutral)
-  Vector similarity search with FAISS
-  PII redaction (emails, phones, addresses removed)
-  Gemini LLM integration
-  User preference tracking
-  Adaptive learning from conversations
-  Modular architecture

### Frontend

-  Nike-branded chat UI
-  Real-time messaging
-  Dynamic product cards
-  Store location cards with directions
-  Geolocation support
-  Responsive design
-  Loading states & animations

## Privacy & Security

**PII Redaction (Section 5)**:

- Removes: emails, phone numbers, order IDs, exact addresses
- Keeps: mall names, product names, pricing, hours
- No PII reaches the Gemini LLM

## Data Flow Example

**Query**: "Do you have Pegasus size 10 at KLCC?"

1. **Intent Classification** → `product_availability`
2. **RAG Retrieval** → Products, Stores, Inventory
3. **PII Redaction** → Sanitize retrieved context
4. **Prompt Building** → Assemble LLM prompt
5. **Gemini Generation** → "Pegasus size 10 is in stock at Nike KLCC (7
   units)..."
6. **Personalization** → Add loyalty benefits
7. **Adaptive Update** → Store user preference: "likes Pegasus size 10"
8. **UI Response** → Display with product card + CTA buttons

## 🛠️ Tech Stack

**Backend**:

- FastAPI
- sentence-transformers
- FAISS
- Google Generative AI 
- Pydantic

**Frontend**:

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS

## Example Queries

Try these in the chat interface:

- **Product Availability**: "Do you have Air Max 90 size 9 at Pavilion?"
- **Store Locator**: "Where is the nearest Nike store?"
- **Recommendations**: "Show me running shoes for marathon training"
- **Promotions**: "What sales are available?"
- **General**: "Tell me about the Vaporfly"

## 🔄 Adaptive Learning

The system learns from each conversation:

- Tracks product preferences
- Remembers size preferences
- Identifies favorite stores
- Extracts purchase intent keywords
- Updates automatically for better recommendations
