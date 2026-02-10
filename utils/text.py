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
