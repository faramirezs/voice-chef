from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_session
from app.models.recipe_photos import RecipePhoto
from app.services.file_service import save_jpeg

router = APIRouter(prefix="/recipe-photos", tags=["recipe-photos"])

@router.post("/")
def upload_recipe_photo(
    recipe_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
):
    # 1. Save file locally
    file_path, filename = save_jpeg(file)

    # 2. Store in DB
    photo = RecipePhoto(
        recipe_id=recipe_id,
        # photo_url=file_path,  # ← storing local path for now
        photo_url=f"/uploads/{filename}",  # URL to access via StaticFiles
        photo_type=file.content_type,
    )

    db.add(photo)
    db.commit()
    db.refresh(photo)

    return {
        "id": photo.id,
        "recipe_id": photo.recipe_id,
        "photo_url": photo.photo_url,
    }