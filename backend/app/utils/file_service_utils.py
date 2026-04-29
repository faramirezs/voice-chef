import os
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import settings

UPLOAD_DIR = settings.UPLOAD_DIR


def save_file(file: UploadFile) -> str:
    allowed_types = {"image/jpeg", "image/png"}
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Only JPEG and PNG files are allowed")

    filename = f"{uuid.uuid4()}"
    if file.content_type == "image/jpeg":
        filename += ".jpg"
    elif file.content_type == "image/png":
        filename += ".png"
    # elif file.content_type == "application/pdf":
    #     filename += ".pdf"

    new_url = os.path.join(UPLOAD_DIR, filename)

    with open(new_url, "wb") as buffer:
        buffer.write(file.file.read())
    
    return new_url


def delete_file(path: str):
    if not path:
        return

    normalized_path = path.split("?", 1)[0].split("#", 1)[0]
    filename = os.path.basename(normalized_path)
    full_path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(full_path):
        os.remove(full_path)