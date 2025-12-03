# Nike AI Assistant

## How to Run

### 1. Start Backend

```bash
cd backend
# Create virtual env if needed: python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend

```bash
cd nike-ai-chat
npm install
npm run dev
```

### 3. Access App

Open [http://localhost:3000](http://localhost:3000)
