import os
import re
from fastapi import UploadFile, HTTPException
from app.core.config import settings

UPLOAD_DIR = settings.UPLOAD_DIR
UPLOAD_URL_PREFIX = settings.UPLOAD_URL_PREFIX

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = {"application/pdf"}


# Format validation function
def is_pdf_file(contents: bytes) -> bool:
    return contents.startswith(b"%PDF-")


def sanitize_filename(filename: str) -> str:
    filename = os.path.basename(filename)  # prevent path traversal
    filename = filename.strip()

    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    return filename


def ensure_unique_filename(filename: str) -> str:
    base, ext = os.path.splitext(filename)
    counter = 1
    candidate = filename

    while os.path.exists(os.path.join(UPLOAD_DIR, candidate)):
        candidate = f"{base}_{counter}{ext}"
        counter += 1

    return candidate


def save_pdf(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, "Only PDF files are allowed")

    contents = file.file.read()
    
    # Size validation
    if len(contents) == 0:
        raise HTTPException(400, "File is empty")
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")
  
    # Format validation
    if not is_pdf_file(contents):
        raise HTTPException(400, "Invalid PDF file")

    filename = sanitize_filename(file.filename)

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only .pdf files are allowed")
    
    # File name and path generation
    filename = ensure_unique_filename(filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
  
    # Save/write file
    with open(file_path, "wb") as f:
        f.write(contents)

    return f"{UPLOAD_URL_PREFIX}/{filename}"


def delete_pdf(filename: str):
    filename = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(path):
        os.remove(path)
    else:
        raise HTTPException(404, "File not found")