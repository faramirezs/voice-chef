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
        "quantity": str(link.quantity) if link.quantity else None,
        "unit": link.unit,
        "quantity_grams": str(quantity_grams),
        "preparation": link.preparation.strip() if link.preparation else None,
        "sort_order": link.sort_order,
    }


def to_recipe_summary(recipe):
    """Convert Recipe ORM to RecipeSummaryResponse dict with Decimal to string conversion."""
    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "status": recipe.status,
        "yield_mode": recipe.yield_mode,
        "portion_size_grams": str(recipe.portion_size_grams) if recipe.portion_size_grams else None,
        "total_raw_weight_grams": str(recipe.total_raw_weight_grams) if recipe.total_raw_weight_grams else None,
        "total_cooked_weight_grams": str(recipe.total_cooked_weight_grams) if recipe.total_cooked_weight_grams else None,
        "portions_count_resolved": str(recipe.portions_count_resolved) if recipe.portions_count_resolved else None,
        "photo_url": recipe.photo_url,
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at,
    }


def to_recipe_detail(recipe):
    """Convert Recipe ORM to RecipeDetailResponse dict with Decimal→string conversion and ingredients."""
    summary = to_recipe_summary(recipe)
    summary.update({
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
    })
    return summary


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
