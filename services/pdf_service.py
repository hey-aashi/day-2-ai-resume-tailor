from pathlib import Path
import re
from typing import Dict, List
from PyPDF2 import PdfReader

from utils.text import clean_text, normalize_whitespace


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    text = "\n".join(pages)
    text = clean_text(text)
    text = normalize_whitespace(text)
    return text


def extract_structured_info(text: str) -> Dict[str, str | List[str]]:
    email = None
    phone = None
    name = None
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if email_match:
        email = email_match.group(0)
    phone_match = re.search(r"(\+?\d[\d\s\-]{7,}\d)", text)
    if phone_match:
        phone = phone_match.group(0)
    name_candidates = re.findall(r"^[A-Z][A-Za-z\-\s]{2,}$", text, re.MULTILINE)
    if name_candidates:
        name = name_candidates[0].strip()
    sections = []
    headings = re.findall(
        r"(?im)^(experience|work experience|education|skills|projects|summary|profile|certifications|achievements)\b.*$",
        text,
    )
    for h in headings:
        sections.append(h.strip().title())
    return {
        "name": name or "",
        "email": email or "",
        "phone": phone or "",
        "sections": sections,
    }
