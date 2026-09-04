from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_service import answer_question


app = FastAPI(
    title="AI Architect Portfolio API",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Request Model
# =========================================================

class ChatRequest(BaseModel):
    message: str


# =========================================================
# Chat Endpoint
# =========================================================

@app.post("/chat")
async def chat(request: ChatRequest):

    result = answer_question(
        request.message
    )

    return result


# =========================================================
# Health Check
# =========================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "ai-architect-portfolio-api",
    }