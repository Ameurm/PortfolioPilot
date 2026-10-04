from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from rag_service import answer_question
from resume_service import (
    get_session_upload_directory,
    process_resume,
)

app = FastAPI(
    title="AI Architect Portfolio API",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent

MAX_RESUME_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://portfolio-pilot-sigma.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str


@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.session_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Session ID is required.",
        )

    result = answer_question(
        request.message,
        session_id=request.session_id,
    )

    return result


@app.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    session_id: str = Form(...),
):
    if not session_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Session ID is required.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume filename is required.",
        )

    original_name = Path(file.filename).name
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported resume format. Please upload a PDF or DOCX file.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded resume is empty.",
        )

    if len(content) > MAX_RESUME_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Resume must be smaller than 10 MB.",
        )

    session_upload_dir = get_session_upload_directory(session_id)
    session_upload_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid4().hex}{extension}"
    stored_path = session_upload_dir / stored_name

    stored_path.write_bytes(content)

    try:
        result = process_resume(
            file_path=stored_path,
            resume_name=original_name,
            session_id=session_id,
        )
    except Exception as exc:
        if stored_path.exists():
            stored_path.unlink()

        raise HTTPException(
            status_code=422,
            detail=f"Unable to process resume: {exc}",
        )

    return {
        "success": True,
        "message": "Resume uploaded and indexed successfully.",
        "session_id": session_id,
        **result,
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ai-architect-portfolio-api",
    }
