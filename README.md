# AI Resume Tailor (FastAPI)

A production-ready FastAPI backend for tailoring resumes to job descriptions using PyPDF2 for PDF extraction and Gemini 2.5 Flash for AI-driven analysis.

## Features
- Upload PDF resumes
- Submit job descriptions
- AI-powered tailoring: keywords, skills gap, summary enhancement, recommendations
- Robust PDF text extraction and preprocessing
- Structured info extraction (contact details, sections)
- Health check endpoint
- Environment-based configuration and logging

## Requirements
- Python 3.10+
- A Google Generative AI API key (Gemini)

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create an `.env` from `.env.example` and set values:
   - `GOOGLE_API_KEY`
   - `APP_HOST`, `APP_PORT`, `APP_DEBUG`
   - `UPLOAD_DIR`, `OUTPUT_DIR`, `MAX_UPLOAD_SIZE_MB`, `ALLOWED_EXTENSIONS`
4. Run the server:
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints
- `GET /health`  
  Health probe. Returns service status and configuration summary.

- `POST /upload-resume` (multipart/form-data)  
  Accepts a PDF file (`file`). Validates, stores, extracts text, and returns a `resume_id`.

- `POST /submit-job` (application/json)  
  Body: `{ "job_description": "..." }`. Stores description and returns a `job_id`.

- `POST /tailor` (application/json)  
  Body accepts:
  - `{ "resume_id": "...", "job_description": "..." }`, or
  - `{ "resume_id": "...", "job_id": "..." }`  
  Performs analysis with Gemini and returns structured suggestions.

## Testing
Run tests with:
```
pytest -q
```

## Notes
- If `GOOGLE_API_KEY` is not set, the AI service falls back to deterministic stubbed responses for local testing.
- Automatic docs are available at `/docs` (Swagger UI) and `/redoc`.

## Security & Limits
- Allowed extensions and upload size are enforced from `.env`.
- Filenames are sanitized; inputs are validated and normalized.