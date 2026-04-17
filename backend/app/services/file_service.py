import os
import uuid
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = os.path.abspath("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_jpeg(file: UploadFile) -> tuple[str, str]:
    # ✅ Validate type
    if file.content_type != "image/jpeg":
        raise HTTPException(400, "Only JPEG files are allowed")

    # ✅ Generate unique filename
    filename = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # ✅ Save file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path, filename