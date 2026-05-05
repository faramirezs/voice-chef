import os
import uuid
import shutil
import io
from PIL import Image
from fastapi import UploadFile, HTTPException
from app.core.config import settings

UPLOAD_DIR = settings.UPLOAD_DIR
UPLOAD_URL_PREFIX = settings.UPLOAD_URL_PREFIX

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB
ALLOWED_FORMATS = {"JPEG", "PNG"}

def save_file(file: UploadFile) -> str:
    
    contents = file.file.read()
    
    # Format validation
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()  # ensures it's a valid image
        format = image.format  # 'JPEG', 'PNG'
    except Exception:
        raise HTTPException(400, "Invalid image file")
    
    # Image type validation
    if format not in ALLOWED_FORMATS:
        raise HTTPException(400, "Only JPEG and PNG images are allowed")

    # Size validation
    if len(contents) == 0:
        raise HTTPException(400, "File is empty")
    elif len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File size exceeds the limit of 1MB")

    # File name and path generation
    filename = f"{uuid.uuid4()}"
    if format == "JPEG":
        filename += ".jpg"
    elif format == "png":
        filename += ".png"
    new_url = os.path.join(UPLOAD_DIR, filename)

    # Save/write file
    with open(new_url, "wb") as buffer:
        buffer.write(contents)
    
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

