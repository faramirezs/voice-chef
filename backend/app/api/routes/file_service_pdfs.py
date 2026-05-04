from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings
import os

from app.utils.file_service_pdfs_utils import save_pdf, delete_pdf

router = APIRouter(prefix="/pdf", tags=["File Service"])

UPLOAD_DIR = settings.UPLOAD_DIR
UPLOAD_URL_PREFIX = settings.UPLOAD_URL_PREFIX


@router.post("/")
def upload_pdf(file: UploadFile = File(...)):
    file_url = save_pdf(file)

    return JSONResponse(
        status_code=201,
        content={"file_url": file_url},
    )


@router.get("/{filename}")
def get_pdf(filename: str):
    filename = os.path.basename(filename)
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")

    return {
        "file_url": f"{UPLOAD_URL_PREFIX}/{filename}"
    }


@router.delete("/{filename}")
def delete_pdf_file(filename: str):
    delete_pdf(filename)
    return {"detail": "File deleted"}