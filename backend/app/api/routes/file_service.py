from fastapi import APIRouter, UploadFile, File, Depends, Response, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_session
from app.models.recipe import Recipe
from app.utils.file_service_utils import save_file, delete_file

router = APIRouter(prefix="/recipe_photos", tags=["File Service"])


@router.put("/")
def upload_recipe_photo(
    recipe_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
):
    recipe = db.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

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
def get_recipe_photo(recipe_id: UUID, db: Session = Depends(get_session)):
    recipe = db.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if not recipe.photo_url:
        raise HTTPException(status_code=404, detail="Photo not found")

    return {"photo_url": recipe.photo_url}


@router.delete("/{recipe_id}/photo")
def delete_recipe_photo(
    recipe_id: UUID,
    db: Session = Depends(get_session),
):
    recipe = db.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if not recipe.photo_url:
        raise HTTPException(status_code=404, detail="Photo not found")

    delete_file(recipe.photo_url) #  Delete file from disk
    recipe.photo_url = None # Set value to NULL for db

    db.add(recipe)
    db.commit()

    return Response(status_code=204)