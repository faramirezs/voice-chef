from fastapi import APIRouter, UploadFile, File, Depends, Response, status, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import Annotated
from uuid import UUID
import os

from app.core.database import get_session
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.recipe import Recipe
from app.models.users import Users
from app.utils.file_service_image_utils import save_file, delete_file

router = APIRouter(prefix="/recipe_images", tags=["File Service"])


@router.put("/")
def upload_recipe_photo(
    current_user: Annotated[Users, Depends(get_current_user)],
    recipe_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
):
    recipe = db.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if recipe.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this recipe")

    old_url = recipe.photo_url
    new_url = save_file(file)

    try:
        recipe.photo_url = new_url

        db.add(recipe)
        db.commit()
        db.refresh(recipe)

    except Exception:
        db.rollback()
        delete_file(new_url)
        raise

    if old_url:
        delete_file(old_url)

    return JSONResponse(
        status_code=status.HTTP_200_OK if old_url else status.HTTP_201_CREATED,
        content={"photo_url": recipe.photo_url},
    )


@router.get("/{recipe_id}")
def get_recipe_photo(
    current_user: Annotated[Users, Depends(get_current_user)],
    recipe_id: UUID,
    db: Session = Depends(get_session)
):
    recipe = db.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if recipe.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this recipe")
    
    if not recipe.photo_url:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Extract filename from photo_url and serve the file
    file_path = recipe.photo_url.lstrip("/")
    full_path = os.path.join(settings.UPLOAD_DIR, os.path.basename(file_path))
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Photo file not found on disk")
    
    return FileResponse(full_path, media_type="image/jpeg")


@router.delete("/{recipe_id}")
def delete_recipe_photo(
    current_user: Annotated[Users, Depends(get_current_user)],
    recipe_id: UUID,
    db: Session = Depends(get_session),
):
    recipe = db.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if recipe.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this recipe")

    if not recipe.photo_url:
        raise HTTPException(status_code=404, detail="Photo not found")

    delete_file(recipe.photo_url) #  Delete file from disk
    recipe.photo_url = None # Set value to NULL for db

    db.add(recipe)
    db.commit()

    return Response(status_code=204)