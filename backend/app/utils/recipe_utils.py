from sqlmodel import Session, select
from uuid import UUID
from fastapi import HTTPException, status
from app.models.recipe import Recipe


def to_recipe_ingredient_response(link):

    ingredient = link.ingredient
    if not ingredient:
        return None

    quantity_grams = getattr(link, "quantity_grams", None)
    if quantity_grams is None:
        quantity = link.quantity or 0
        unit = (getattr(link, "unit", "") or "").strip().lower()
        quantity_grams = quantity * 1000 if unit == "kg" else quantity

    return {
        "id": link.id,
        "ingredient_id": ingredient.id,
        "ingredient_name": ingredient.name,
        "ingredient_default_unit": ingredient.default_unit,
        "quantity": link.quantity,
        "unit": link.unit,
        "quantity_grams": quantity_grams,
        "preparation": link.preparation.strip() if link.preparation else None,
        "sort_order": link.sort_order,
    }


def to_recipe_detail(recipe):
    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "status": recipe.status,
        "yield_mode": recipe.yield_mode,
        "portions_count_resolved": recipe.portions_count_resolved,
        "portion_size_grams": recipe.portion_size_grams,
        "total_raw_weight_grams": recipe.total_raw_weight_grams,
        "total_cooked_weight_grams": recipe.total_cooked_weight_grams,
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at,
        "photo_url": recipe.photo_url,
        "preparation_time_minutes": recipe.preparation_time_minutes,
        "cooking_time_minutes": recipe.cooking_time_minutes,
        "is_component": recipe.is_component,
        "ingredients": [
            r for r in (
                to_recipe_ingredient_response(link)
                for link in sorted(
                    recipe.recipe_ingredients, 
                    key=lambda x: x.sort_order or 0
                )
            ) if r is not None
        ],
    }


def ensure_unique_recipe_name(
        session: Session, 
        name: str, 
        tenant_id: UUID, 
        exclude_id: UUID | None = None
) -> None:

    if not name:
        return
    q = select(Recipe).where(
        Recipe.name == name.strip(), 
        Recipe.tenant_id == tenant_id
    )
    if exclude_id:
        q = q.where(Recipe.id != exclude_id)
    if session.exec(q).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Recipe name already exists"
        )
