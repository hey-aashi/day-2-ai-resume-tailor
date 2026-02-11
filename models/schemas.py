from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class JobSubmission(BaseModel):
    job_description: str = Field(min_length=10, max_length=20000)


class UploadResponse(BaseModel):
    resume_id: str
    filename: str
    size_bytes: int


class JobResponse(BaseModel):
    job_id: str
    size_bytes: int


class TailorRequest(BaseModel):
    resume_id: str
    job_description: Optional[str] = None
    job_id: Optional[str] = None


class TailoredResponse(BaseModel):
    summary_enhancement: str
    keyword_optimization: List[str]
    skills_gap: List[str]
    recommendations: List[str]


class CoverLetterRequest(BaseModel):
    resume_id: str
    job_description: str = Field(min_length=50, max_length=20000)


class CoverLetterResponse(BaseModel):
    cover_letter: str
    placeholders: Dict[str, str]
    word_count: int
    generation_time_ms: Optional[float] = None
