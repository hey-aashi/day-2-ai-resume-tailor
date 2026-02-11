import re


def clean_text(text: str) -> str:
    text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", " ", text)
    return text


def normalize_whitespace(text: str) -> str:
    text = "".join(ch for ch in text if ch.isprintable() or ch in "\t\n\r")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\s{2,})", " ", text)
    return text.strip()


def extract_json_from_text(text: str) -> str:
    """Extract JSON from potential markdown code blocks or surrounding text."""
    text = text.strip()
    # Handle markdown code blocks
    if "```" in text:
        # Try to find content between ```json and ``` or just ``` and ```
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            return json_match.group(1).strip()
    
    # If no markdown blocks, try to find the first '{' and last '}'
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx:end_idx + 1].strip()
        
    return text
