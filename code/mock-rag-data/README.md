# Nike AI Assistant - Mock RAG Data

This directory contains comprehensive mock data for the Nike AI Assistant's
Retrieval-Augmented Generation (RAG) system.

## 📁 Data Files Overview

### 1. **products.json** - Product Catalog

Contains 10 diverse Nike products across different categories:

- **Running Shoes**: Pegasus 40, Vaporfly Next% 3, Revolution 7
- **Lifestyle Shoes**: Air Max 90
- **Training Shoes**: Metcon 9
- **Apparel**: Dri-FIT Swift Top, Pro Shorts, Club Fleece Hoodie
- **Accessories**: Brasilia Duffel Bag, Everyday Cushion Socks

**Key Fields**:

- Product details (name, category, price, sizes, colors)
- Feature descriptions
- Keywords for search/matching
- `embedding_text`: Pre-formatted text optimized for vector embedding

### 2. **stores.json** - Store Locations

5 Nike retail locations in Kuala Lumpur area:

- Nike KLCC (Flagship)
- Nike Pavilion KL
- Nike Mid Valley
- Nike 1 Utama
- Nike Sunway Pyramid

**Key Fields**:

- Full address and GPS coordinates
- Operating hours (all stores: 10 AM - 10 PM daily)
- Contact information
- Services offered (customization, expert fitting, Nike App reservations)
- Amenities and accessibility features
- `embedding_text`: Optimized for location-based queries

### 3. **inventory.json** - Real-Time Stock Data

Live inventory across all stores showing:

- Stock levels by size (e.g., size 10 has 7 units)
- Stock levels by color variant
- Total units available
- Last updated timestamp
- Low stock thresholds
- Restock dates

**Example Use Cases**:

- "Do you have Pegasus size 10 at KLCC?" → Check S001 + P001
- "Which store has the most Air Max 90?" → Compare across stores

### 4. **promotions.json** - Active Offers

8 different promotion types:

- **Holiday Sale**: 20% off running shoes & apparel
- **Nike Members**: Early access to releases
- **Student Discount**: 10% year-round
- **Bundle Deals**: Buy 2 get 1 free on accessories
- **Loyalty Programs**: Gold (15% off) & Silver (10% off) tiers
- **Marathon Special**: 25% off select running shoes
- **Referral Program**: RM50 credit for both parties

**Key Fields**:

- Discount percentages or reward amounts
- Applicable products/categories
- Date ranges (or ongoing)
- Terms & conditions
- Promo codes where applicable

### 5. **user_preferences.json** - Adaptive Learning Data

5 user profiles representing different customer segments:

#### User Profiles:

1. **U001 - Advanced Marathon Runner**
   - Prefers: Pegasus, Vaporfly | Size 10 | Gold tier
   - Favorite store: Nike KLCC (8 visits)
   - Budget: $100-$300

2. **U002 - Streetwear Enthusiast**
   - Prefers: Air Max 90, Hoodies | Size 8.5 | Silver tier
   - Favorite store: Nike Pavilion KL
   - Budget: $50-$150

3. **U003 - Gym/CrossFit Athlete**
   - Prefers: Metcon, Training gear | Size 11 | Gold tier
   - Favorite store: Nike Mid Valley
   - Interests: Weightlifting, HIIT

4. **U004 - Beginner Runner**
   - Prefers: Revolution (affordable) | Size 7.5 | Basic member
   - Favorite store: Nike Sunway Pyramid
   - Budget: $50-$100

5. **U005 - Elite Competitive Runner**
   - Prefers: Vaporfly (carbon plate) | Size 9.5 | Gold tier
   - Recent race: KL Marathon 2025 (3:12:45)
   - Budget: $150-$400

**Key Fields**:

- Conversation history count
- Preferred categories, products, sizes, colors
- Favorite stores and visit frequency
- Purchase intent signals (keywords indicating what they need)
- Loyalty tier and points
- Activity level and interests
- `embedding_text`: Summary for similarity matching

---

## 🎯 How RAG Uses This Data

### Query Flow Example:

**User Query**: _"I'm at KLCC Nike, do you have Pegasus size 10?"_

1. **Intent Classification**: Product availability query
2. **RAG Retrieval**:
   - **products.json**: Find P001 (Pegasus 40)
   - **stores.json**: Get S001 (Nike KLCC) details
   - **inventory.json**: Check stock at S001 for P001 size 10 → **7 units
     available**
   - **user_preferences.json**: If user is U001, note they've asked about
     Pegasus 8 times before
3. **Context Assembly**: Combine retrieved data
4. **PII Redaction**: Remove any employee names, internal IDs from context
5. **LLM Generation**: Gemini creates response using safe context
6. **Adaptive Update**: Store insight → "U001 inquired about Pegasus size 10
   again"

---

## 🔄 Adaptive RAG Learning

The system learns from conversations and updates `user_preferences.json`:

**Insights Extracted**:

- Which products users ask about repeatedly
- Preferred sizes (high confidence when consistent)
- Favorite store locations based on visit patterns
- Purchase intent keywords (e.g., "marathon training", "gym workout")
- Budget range based on inquired products

**Future Personalization**:

- "Since you prefer running shoes in size 10..." (based on size_preferences)
- "Your usual store Nike KLCC has..." (based on favorite_store)
- "As a Gold member, you get 15% off..." (based on loyalty_tier)

---

## 📊 Data Statistics

| Data Type         | Count | Purpose                |
| ----------------- | ----- | ---------------------- |
| Products          | 10    | Product catalog search |
| Stores            | 5     | Location-based queries |
| Inventory Records | 11    | Real-time availability |
| Promotions        | 8     | Offer recommendations  |
| User Profiles     | 5     | Personalization        |

---

## 🛡️ Privacy & PII Redaction

**What Gets Redacted** (from RAG results only):

- ❌ Employee names
- ❌ Phone numbers (from retrieved context)
- ❌ Email addresses (from retrieved context)
- ❌ Order IDs
- ❌ Exact street addresses

**What Stays** (operational data needed for assistance):

- ✅ Mall names (KLCC, Pavilion KL)
- ✅ Product names and prices
- ✅ Store operating hours
- ✅ Promo codes
- ✅ Loyalty tier information

**User input is NEVER redacted** - only the retrieved RAG context is sanitized
before being sent to Gemini.

---

## 🚀 Usage in Vector Database

For production implementation:

```python
# Example: Creating embeddings
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Embed product data
for product in products:
    embedding = model.encode(product['embedding_text'])
    # Store in Pinecone/Chroma with metadata

# Embed user preferences
for user in user_preferences:
    embedding = model.encode(user['embedding_text'])
    # Store for similarity matching
```

**Vector DB Collections**:

- `products_collection`: Searchable product catalog
- `stores_collection`: Geo + text search for locations
- `inventory_collection`: Real-time availability (updated frequently)
- `promotions_collection`: Active offers and deals
- `user_insights_collection`: Adaptive learning (grows over time)

---

**Generated for**: Nike AI Assistant Architecture Demo\
**Date**: December 2025\
**Purpose**: Mock data for RAG system demonstration and testing
