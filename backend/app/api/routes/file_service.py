from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_session
from app.models.recipe import Recipe
# from app.models.recipe_photos import RecipePhoto
from app.services.file_service import save_file, delete_file

router = APIRouter(prefix="/recipe_photos", tags=["File Service"])

@router.post("/")
def upload_recipe_photo(
    recipe_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
):
    recipe = db.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    filename = save_file(file)  # Save file locally
    new_url = f"/uploads/{filename}"  # URL to access via StaticFiles

    if recipe.photo_url:
        delete_file(recipe.photo_url)  # Delete old file if exists

    recipe.photo_url = new_url  # Update the recipe's photo_url

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return {"photo_url": recipe.photo_url}


@router.get("/{recipe_id}")
def get_recipe_photo(recipe_id: UUID, db: Session = Depends(get_session)):
    recipe = db.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

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

    return {"message": "Photo deleted"}