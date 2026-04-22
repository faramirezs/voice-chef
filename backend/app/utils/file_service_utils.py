import os
import uuid
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = os.path.abspath("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_file(file: UploadFile) -> tuple[str, str]:
    allowed_types = {"image/jpeg", "image/png", "application/pdf"}
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Only JPEG, PNG and PDF files are allowed")

    filename = f"{uuid.uuid4()}"
    if file.content_type == "image/jpeg":
        filename += ".jpg"
    elif file.content_type == "image/png":
        filename += ".png"
    elif file.content_type == "application/pdf":
        filename += ".pdf"

    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path, filename



def delete_file(path: str):
    if not path:
        return

    filename = path.split("/")[-1]  # extract "abc.jpg"
    full_path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(full_path):
        os.remove(full_path)