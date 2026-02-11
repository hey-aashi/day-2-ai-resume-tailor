import json
import logging
from typing import Dict, Optional
from config.settings import settings
from utils.text import extract_json_from_text

logger = logging.getLogger("ai-resume-tailor")


def _stub_cover_letter_response(resume_text: str, job_text: str) -> Dict:
    """Stub response for testing when API key is not available."""
    return {
        "cover_letter": """[Date]

[Hiring Manager's Name]
[Company Name]
[Company Address]

Dear Hiring Manager,

I am writing to express my strong interest in the position at your company. With my background in software development and proven track record of delivering high-quality solutions, I am confident that I would be a valuable addition to your team.

Throughout my career, I have demonstrated expertise in Python, FastAPI, and modern web technologies. My experience includes building scalable applications, implementing AI-powered features, and collaborating effectively with cross-functional teams. I am particularly excited about the opportunity to contribute to your organization's innovative projects.

I would welcome the opportunity to discuss how my skills and experience align with your needs. Thank you for considering my application. I look forward to speaking with you soon.

Sincerely,
[Your Name]""",
        "placeholders": {
            "date": "[Date]",
            "company_name": "[Company Name]",
            "hiring_manager": "[Hiring Manager's Name]",
            "company_address": "[Company Address]",
            "your_name": "[Your Name]"
        }
    }


def generate_cover_letter(resume_text: str, job_text: str) -> Dict:
    """
    Generate a professional cover letter using Gemini AI.
    
    Args:
        resume_text: The extracted text from the user's resume
        job_text: The job description text
        
    Returns:
        Dict containing:
        - cover_letter: The generated cover letter text
        - placeholders: Dictionary of placeholder values that can be replaced
        
    Raises:
        ValueError: If input parameters are invalid
        RuntimeError: If AI generation fails
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty")
    
    if not job_text or not job_text.strip():
        raise ValueError("Job description cannot be empty")
    
    if len(job_text.strip()) < 50:
        raise ValueError("Job description must be at least 50 characters")
    
    logger.info("Starting cover letter generation")
    
    if not settings.google_api_key:
        logger.warning("No Google API key configured, returning stub response")
        return _stub_cover_letter_response(resume_text, job_text)
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=settings.google_api_key)
        # Using gemini-flash-latest which is usually 1.5 Flash and stable
        model = genai.GenerativeModel("gemini-flash-latest")
        
        prompt = f"""
        You are an expert career coach and professional writer. 
        
        Given the following resume and job description, generate a compelling, professional cover letter that:
        
        1. Is approximately 250-350 words in length
        2. Effectively bridges the candidate's experience with the specific job requirements
        3. Uses professional, confident, and engaging language
        4. Includes appropriate placeholders for personalization:
           - [Date] for the current date
           - [Company Name] for the hiring company
           - [Hiring Manager's Name] for the hiring manager
           - [Company Address] for the company address
           - [Your Name] for the candidate's name
        
        5. Follows a standard business letter format with proper salutation and closing
        6. Highlights relevant skills and experiences that match the job requirements
        7. Demonstrates genuine interest in the position and company
        8. Includes a clear call to action for next steps
        
        Resume Text:
        {resume_text}
        
        Job Description:
        {job_text}
        
        Return the response in this JSON format:
        {{
            "cover_letter": "The complete cover letter text with placeholders",
            "placeholders": {{
                "date": "[Date]",
                "company_name": "[Company Name]",
                "hiring_manager": "[Hiring Manager's Name]",
                "company_address": "[Company Address]",
                "your_name": "[Your Name]"
            }}
        }}
        
        Ensure the cover letter is professional, concise, and tailored specifically to this job opportunity.
        """
        
        logger.info("Sending request to Gemini AI for cover letter generation")
        response = model.generate_content(prompt)
        
        if not response.text:
            raise RuntimeError("Empty response from Gemini AI")
        
        logger.info("Received response from Gemini AI, parsing JSON")
        
        # Parse the JSON response
        try:
            cleaned_text = extract_json_from_text(response.text)
            data = json.loads(cleaned_text)
            
            # Validate the response structure
            if not isinstance(data, dict):
                raise ValueError("Response is not a dictionary")
            
            if "cover_letter" not in data:
                raise ValueError("Missing 'cover_letter' in response")
            
            if "placeholders" not in data:
                raise ValueError("Missing 'placeholders' in response")
            
            if not isinstance(data["placeholders"], dict):
                raise ValueError("'placeholders' must be a dictionary")
            
            # Validate cover letter content
            cover_letter = data["cover_letter"].strip()
            if not cover_letter:
                raise ValueError("Cover letter is empty")
            
            if len(cover_letter) < 100:
                raise ValueError("Cover letter is too short")
            
            if len(cover_letter) > 4000:
                raise ValueError("Cover letter is too long")
            
            logger.info(f"Successfully generated cover letter with {len(cover_letter)} characters")
            
            return {
                "cover_letter": cover_letter,
                "placeholders": data["placeholders"]
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response.text}")
            logger.error(f"Cleaned text tried to parse: {cleaned_text}")
            raise RuntimeError("Invalid JSON response from Gemini AI") from e
            
    except ImportError as e:
        logger.error(f"Failed to import google.generativeai: {e}")
        raise RuntimeError("Google AI library not available") from e
        
    except Exception as e:
        logger.exception("Cover letter generation failed")
        raise RuntimeError(f"Failed to generate cover letter: {str(e)}") from e