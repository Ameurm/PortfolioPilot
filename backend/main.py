from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.rag_service import answer_question
from backend.resume_service import process_resume


app = FastAPI(
    title="AI Architect Portfolio API",
    version="1.0.0",
)


# ============================================================
# Paths and Upload Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

RESUME_UPLOAD_DIR = (
    BASE_DIR
    / "resume_data"
    / "uploads"
)

MAX_RESUME_SIZE = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
}


# ============================================================
# CORS
# ============================================================

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


# ============================================================
# Request Models
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# Chat Endpoint
# ============================================================

@app.post("/chat")
async def chat(request: ChatRequest):

    result = answer_question(
        request.message
    )

    return result


# ============================================================
# Resume Upload Endpoint
# ============================================================

@app.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Resume filename is required.",
        )

    original_name = Path(
        file.filename
    ).name

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    extension = Path(
        original_name
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported resume format. "
                "Please upload a PDF or DOCX file."
            ),
        )

    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    content = await file.read()

    if not content:

        raise HTTPException(
            status_code=400,
            detail="The uploaded resume is empty.",
        )

    # --------------------------------------------------------
    # Validate file size
    # --------------------------------------------------------

    if len(content) > MAX_RESUME_SIZE:

        raise HTTPException(
            status_code=413,
            detail=(
                "Resume must be smaller than 10 MB."
            ),
        )

    # --------------------------------------------------------
    # Create upload directory
    # --------------------------------------------------------

    RESUME_UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Generate safe stored filename
    # --------------------------------------------------------

    stored_name = (
        f"{uuid4().hex}{extension}"
    )

    stored_path = (
        RESUME_UPLOAD_DIR
        / stored_name
    )

    stored_path.write_bytes(
        content
    )

    # --------------------------------------------------------
    # Extract, chunk, embed and index resume
    # --------------------------------------------------------

    try:

        result = process_resume(
            file_path=stored_path,
            resume_name=original_name,
        )

    except Exception as exc:

        if stored_path.exists():
            stored_path.unlink()

        raise HTTPException(
            status_code=422,
            detail=(
                "Unable to process resume: "
                f"{exc}"
            ),
        )

    # --------------------------------------------------------
    # Return indexing result
    # --------------------------------------------------------

    return {
        "success": True,
        "message": (
            "Resume uploaded and indexed successfully."
        ),
        **result,
    }


# ============================================================
# Health Endpoint
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "ai-architect-portfolio-api",
    }