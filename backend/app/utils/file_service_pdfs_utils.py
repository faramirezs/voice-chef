import os
import re
import shutil
import tempfile
from fastapi import UploadFile, HTTPException
from app.core.config import settings

UPLOAD_DIR = settings.UPLOAD_DIR
UPLOAD_URL_PREFIX = settings.UPLOAD_URL_PREFIX

MAX_FILE_SIZE = 100 * 1024 * 1024  # 10 MB
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

    filename = sanitize_filename(file.filename)

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only .pdf files are allowed")
    
    # File name and path generation
    filename = ensure_unique_filename(filename)
    file_path = os.path.join(UPLOAD_DIR, filename)

    temp_file = None
    temp_path = None

    try:
        # Stream the upload to a temporary file first so validation doesn't
        # require loading the entire file into memory.
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            dir=UPLOAD_DIR,
            suffix=".upload",
        )
        temp_path = temp_file.name
        temp_file.close()

        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        file_size = os.path.getsize(temp_path)

        # Size validation
        if file_size == 0:
            raise HTTPException(400, "File is empty")
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(400, "File too large (max 10MB)")

        # Format validation using the temp file header
        with open(temp_path, "rb") as f:
            header = f.read(5)
            if not is_pdf_file(header):
                raise HTTPException(400, "Invalid PDF file")

        shutil.move(temp_path, file_path)
        temp_path = None

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    return f"{UPLOAD_URL_PREFIX}/{filename}"


def delete_pdf(filename: str):
    filename = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(path):
        os.remove(path)
    else:
        raise HTTPException(404, "File not found")