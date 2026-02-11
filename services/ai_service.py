import json
import logging
from typing import Dict
from config.settings import settings
from utils.text import extract_json_from_text

logger = logging.getLogger("ai-resume-tailor")


def _stub_response(resume_text: str, job_description: str) -> Dict:
    logger.debug("Returning stub response for tailor_resume")
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
        logger.warning("No Google API key, using stub for tailor_resume")
        return _stub_response(resume_text, job_description)
    
    import google.generativeai as genai

    try:
        genai.configure(api_key=settings.google_api_key)
        # Using gemini-flash-latest which is usually 1.5 Flash and stable
        model = genai.GenerativeModel("gemini-flash-latest")
        prompt = (
            "You are an expert resume coach. Given a resume and a job description, "
            "produce JSON with keys: summary_enhancement (string), keyword_optimization (array of strings), "
            "skills_gap (array of strings), recommendations (array of strings). "
            "Return ONLY the raw JSON object. Do not include any explanations or markdown formatting unless required. "
            f"Resume:\n{resume_text}\n\nJob Description:\n{job_description}\n"
        )
        
        logger.info("Calling Gemini API for resume tailoring")
        response = model.generate_content(prompt)
        
        if not response.text:
            logger.error("Gemini API returned empty response")
            return _stub_response(resume_text, job_description)

        cleaned_text = extract_json_from_text(response.text)
        logger.debug(f"Cleaned AI response: {cleaned_text[:100]}...")
        
        data = json.loads(cleaned_text)
        return data
    except Exception as e:
        logger.exception(f"AI tailoring failed with error: {str(e)}")
        return _stub_response(resume_text, job_description)
