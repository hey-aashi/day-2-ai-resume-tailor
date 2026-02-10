import json
from typing import Dict
from config.settings import settings


def _stub_response(resume_text: str, job_description: str) -> Dict:
    return {
        "summary_enhancement": "Tailored summary aligning experience with the job requirements.",
        "keyword_optimization": ["python", "fastapi", "ai", "nlp"],
        "skills_gap": ["vector databases", "mlops"],
        "recommendations": [
            "Add metrics demonstrating impact.",
            "Emphasize relevant projects and outcomes.",
        ],
    }


def tailor_resume(resume_text: str, job_description: str) -> Dict:
    if not settings.google_api_key:
        return _stub_response(resume_text, job_description)
    import google.generativeai as genai

    genai.configure(api_key=settings.google_api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = (
        "You are an expert resume coach. Given a resume and a job description, "
        "produce JSON with keys: summary_enhancement (string), keyword_optimization (array of strings), "
        "skills_gap (array of strings), recommendations (array of strings). "
        "Return only JSON. "
        f"Resume:\n{resume_text}\n\nJob Description:\n{job_description}\n"
    )
    response = model.generate_content(prompt)
    try:
        text = response.text or ""
        data = json.loads(text)
        return data
    except Exception:
        return _stub_response(resume_text, job_description)
