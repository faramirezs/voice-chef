import os
import uuid
import shutil
from fastapi import UploadFile, HTTPException
from app.core.config import settings

UPLOAD_DIR = settings.UPLOAD_DIR
UPLOAD_URL_PREFIX = settings.UPLOAD_URL_PREFIX


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
    
    return f"{UPLOAD_URL_PREFIX}/{filename}"


def delete_file(path: str):
    if not path:
        return

    normalized_path = path.split("?", 1)[0].split("#", 1)[0]
    filename = os.path.basename(normalized_path)
    full_path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(full_path):
        os.remove(full_path)


# NOTE MK: This function is for seed images copying by saving them with uuids
def save_file_from_path(src_path: str) -> str:
    ext = os.path.splitext(src_path)[1].lower()

    if ext not in [".jpg", ".jpeg", ".png"]:
        raise ValueError("Only jpg/png allowed")

    filename = f"{uuid.uuid4()}{ext}"
    dst_path = os.path.join(UPLOAD_DIR, filename)
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    shutil.copyfile(src_path, dst_path)

    return f"{UPLOAD_URL_PREFIX}/{filename}"