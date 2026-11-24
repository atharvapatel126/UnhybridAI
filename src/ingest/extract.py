"""Validated extraction; document contents never act as application instructions."""
from pathlib import Path
import re

from config import settings


def validate_filename(name):
    return (isinstance(name, str) and 0 < len(name) <= 180
            and re.fullmatch(r"[\w .()-]+\.(pdf|txt|md)", name, re.I) is not None
            and name not in (".", "..") and not name.startswith(".")
            and "/" not in name and "\\" not in name)


def extract_document(path):
    result = {"pages": [], "errors": []}
    try:
        path = Path(path)
        if not validate_filename(path.name):
            raise ValueError("Use a safe PDF, TXT, or MD filename without path separators.")
        if path.stat().st_size > settings.upload_limit_mb * 1024 * 1024:
            raise ValueError("File exceeds the 20 MB upload limit.")
        if path.suffix.lower() == ".pdf":
            import pymupdf
            with pymupdf.open(path) as document:
                if document.needs_pass:
                    raise ValueError("Encrypted PDFs are not supported. Upload an unencrypted copy.")
                if not document.is_pdf:
                    raise ValueError("The file is not a valid PDF.")
                for number, page in enumerate(document, 1):
                    text = page.get_text().strip()
                    if text:
                        result["pages"].append({"text": text, "page": number, "source_file": path.name})
        else:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                result["pages"].append({"text": text, "page": 1, "source_file": path.name})
        if not result["pages"]:
            raise ValueError("No extractable text. Scanned PDFs need OCR before upload.")
    except ValueError as exc:
        result = {"pages": [], "errors": [str(exc)]}
    except Exception:
        result = {"pages": [], "errors": ["Cannot read document. Check the file is accessible, valid, and UTF-8 for text files."]}
    return result
