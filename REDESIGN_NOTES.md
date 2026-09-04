# AI Architect Portfolio — Frontend Redesign

The frontend was rebuilt around an enterprise AI control-plane visual language.

## What changed
- Replaced the inconsistent light-card layout with a cohesive dark architecture-console UI.
- Added fixed desktop system navigation and responsive mobile navigation.
- Reworked Overview, Architecture, Experience, Security and Contact sections.
- Rebuilt the AI Architect Copilot UI.
- Added a compact RAG execution trace showing:
  - Query embedding
  - Semantic retrieval
  - Authorization
  - Reranking
  - Final context
  - LLM
- Added source metadata presentation to the assistant.
- Changed the frontend API URL to support `NEXT_PUBLIC_API_URL`, with localhost:8000 as the fallback.
- Updated page metadata.

## Backend
The existing FastAPI / FAISS / HuggingFace / Ollama implementation was preserved.

The ZIP intentionally excludes `backend/.env` for security. Keep your existing local `.env` file when running the backend.

## Run
Frontend:
```bash
npm install
npm run dev
```

Backend:
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

Optional frontend environment variable:
```text
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```
