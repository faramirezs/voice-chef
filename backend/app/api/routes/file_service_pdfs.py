from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from typing import Annotated, List
from pydantic import BaseModel
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.users import Users
import os

from app.utils.file_service_pdfs_utils import save_pdf, delete_pdf

router = APIRouter(prefix="/pdfs", tags=["File Service"])

UPLOAD_DIR = settings.UPLOAD_DIR


class PDFFile(BaseModel):
    filename: str
    size: int


@router.get("", response_model=List[PDFFile])
def retrieve_pdfs(
    current_user: Annotated[Users, Depends(get_current_user)],
):
    """
    List all available PDF files
    """
    if not os.path.exists(UPLOAD_DIR):
        return []

    pdfs = []
    try:
        for filename in os.listdir(UPLOAD_DIR):
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    pdfs.append(
                        PDFFile(
                            filename=filename,
                            size=size,
                        )
                    )
    except OSError as e:
        raise HTTPException(500, f"Error reading PDF directory: {str(e)}")

    return pdfs


@router.post("")
def upload_pdf(
    current_user: Annotated[Users, Depends(get_current_user)],
    file: UploadFile = File(...)
):
    file_url = save_pdf(file)

    return JSONResponse(
        status_code=201,
        content={"file_url": file_url},
    )


@router.get("/{filename}")
def retrieve_pdf(
    current_user: Annotated[Users, Depends(get_current_user)],
    filename: str
):
    """Get a PDF file through authenticated endpoint"""
    filename = os.path.basename(filename)
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=403, detail="Only PDF files are allowed")

    return FileResponse(
        file_path,
        media_type="application/pdf",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


@router.delete("/{filename}")
def delete_pdf_file(
    current_user: Annotated[Users, Depends(get_current_user)],
    filename: str
):
    delete_pdf(filename)
    return {"detail": "File deleted"}