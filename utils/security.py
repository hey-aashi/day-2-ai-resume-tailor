import os
import re
from pathlib import Path
from typing import Iterable


def sanitize_filename(name: str) -> str:
    name = os.path.basename(name)
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name


def is_allowed_extension(name: str, allowed: Iterable[str]) -> bool:
    ext = Path(name).suffix.lower()
    allowed_exts = {e.strip().lower() for e in allowed}
    return ext in allowed_exts


def within_size_limit(size_bytes: int, max_mb: int) -> bool:
    return size_bytes <= max_mb * 1024 * 1024
