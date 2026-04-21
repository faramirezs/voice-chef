import os
import uuid
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = os.path.abspath("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_file(file: UploadFile) -> tuple[str, str]:
    if file.content_type != "image/jpeg":
        raise HTTPException(400, "Only JPEG files are allowed")

    filename = f"{uuid.uuid4()}.jpg"
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