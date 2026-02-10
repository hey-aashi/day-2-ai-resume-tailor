import io
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from fastapi import status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import settings, UPLOAD_PATH, OUTPUT_PATH
from models.schemas import (
    JobSubmission,
    UploadResponse,
    JobResponse,
    TailorRequest,
    TailoredResponse,
)
from services.pdf_service import extract_text, extract_structured_info
from services.ai_service import tailor_resume
from utils.security import sanitize_filename, is_allowed_extension, within_size_limit
from utils.text import normalize_whitespace


logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("ai-resume-tailor")

app = FastAPI(
    title="AI Resume Tailor",
    description="Tailor resumes to job descriptions using PDF extraction and Gemini AI.",
    version="1.0.0",
)

FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


if (FRONTEND_DIST / "assets").exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="assets",
    )


@app.get("/", include_in_schema=False)
def root():
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return {"message": "AI Resume Tailor API. See /docs"}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
        "<rect width='32' height='32' fill='#0a0a0a'/>"
        "<path d='M6 24L14 8l4 8 8-4-6 12z' fill='#3b82f6'/>"
        "<circle cx='20' cy='10' r='3' fill='#10b981'/>"
        "</svg>"
    )
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "debug": settings.app_debug,
        "rate_limit_enabled": settings.rate_limit_enabled,
    }


@app.post(
    "/upload-resume",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["resume"],
)
async def upload_resume(file: UploadFile = File(...)):
    filename = sanitize_filename(file.filename or "")
    if not filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    allowed = [e for e in settings.allowed_extensions.split(",") if e]
    if not is_allowed_extension(filename, allowed):
        raise HTTPException(status_code=415, detail="Unsupported file type")
    buffer = io.BytesIO(await file.read())
    size = len(buffer.getvalue())
    if not within_size_limit(size, settings.max_upload_size_mb):
        raise HTTPException(status_code=413, detail="File too large")
    resume_id = str(uuid.uuid4())
    destination = UPLOAD_PATH / f"{resume_id}{Path(filename).suffix}"
    with destination.open("wb") as f:
        f.write(buffer.getvalue())
    try:
        text = extract_text(destination)
        processed_path = OUTPUT_PATH / f"{resume_id}.txt"
        processed_path.write_text(text, encoding="utf-8")
    except Exception as e:
        logger.exception("PDF processing failed")
        raise HTTPException(status_code=422, detail="Failed to process PDF") from e
    return UploadResponse(resume_id=resume_id, filename=filename, size_bytes=size)


@app.post("/submit-job", response_model=JobResponse, tags=["job"])
async def submit_job(payload: JobSubmission):
    text = normalize_whitespace(payload.job_description)
    if len(text) < 10:
        raise HTTPException(status_code=400, detail="Job description too short")
    job_id = str(uuid.uuid4())
    job_path = OUTPUT_PATH / f"job_{job_id}.txt"
    job_path.write_text(text, encoding="utf-8")
    return JobResponse(job_id=job_id, size_bytes=len(text.encode("utf-8")))


@app.post("/tailor", response_model=TailoredResponse, tags=["analysis"])
async def tailor(payload: TailorRequest):
    if not payload.resume_id:
        raise HTTPException(status_code=400, detail="resume_id required")
    resume_txt_path = OUTPUT_PATH / f"{payload.resume_id}.txt"
    if not resume_txt_path.exists():
        raise HTTPException(status_code=404, detail="Processed resume not found")
    resume_text = resume_txt_path.read_text(encoding="utf-8")
    job_text: Optional[str] = None
    if payload.job_description:
        job_text = normalize_whitespace(payload.job_description)
    elif payload.job_id:
        job_path = OUTPUT_PATH / f"job_{payload.job_id}.txt"
        if not job_path.exists():
            raise HTTPException(status_code=404, detail="Job description not found")
        job_text = job_path.read_text(encoding="utf-8")
    else:
        raise HTTPException(status_code=400, detail="Provide job_description or job_id")
    try:
        _ = extract_structured_info(resume_text)
        result = tailor_resume(resume_text, job_text)
    except Exception as e:
        logger.exception("AI tailoring failed")
        raise HTTPException(status_code=500, detail="AI tailoring failed") from e
    return TailoredResponse(
        summary_enhancement=result.get("summary_enhancement", ""),
        keyword_optimization=result.get("keyword_optimization", []),
        skills_gap=result.get("skills_gap", []),
        recommendations=result.get("recommendations", []),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
