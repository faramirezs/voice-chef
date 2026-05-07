from sqlmodel import Session, select
from uuid import UUID
from fastapi import HTTPException, status
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient


def validate_recipe_business_rules(recipe) -> None:
    """
    Validate recipe business rules before creation/update.
    
    Raises HTTPException(400) if any rule is violated.
    """
    # Rule 1: active + weight mode requires portion_size_grams > 0
    if recipe.status == "active" and recipe.yield_mode == "weight":
        if not recipe.portion_size_grams or recipe.portion_size_grams <= 0:
            raise HTTPException(
                status_code=400,
                detail="portion_size_grams is required and must be > 0 for active weight-mode recipes"
            )
    
    # Rule 2: Negative totals not allowed
    if recipe.total_raw_weight_grams and recipe.total_raw_weight_grams < 0:
        raise HTTPException(
            status_code=400,
            detail="total_raw_weight_grams must not be negative"
        )
    if recipe.total_cooked_weight_grams and recipe.total_cooked_weight_grams < 0:
        raise HTTPException(
            status_code=400,
            detail="total_cooked_weight_grams must not be negative"
        )
    if recipe.portions_count_resolved and recipe.portions_count_resolved <= 0:
        raise HTTPException(
            status_code=400,
            detail="portions_count_resolved must be greater than 0"
        )


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
        "unit": link.unit if link.unit else None,
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
        "instructions": recipe.instructions,
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

def validate_ingredient_sort_order(recipe) -> None:
    """
    Validate that sort_order values are sequential starting from 0 with no gaps.
    
    Expected sequence: 0, 1, 2, 3, ... (each value exactly +1 from previous)
    
    Raises:
        HTTPException(409): If sort_order values are not sequential or have duplicates
    """
    if not recipe.ingredients:
        return
    
    sort_orders = [ing.sort_order for ing in recipe.ingredients]
    
    # Check for duplicates
    unique_sort_orders = set(sort_orders)
    if len(sort_orders) != len(unique_sort_orders):
        seen = set()
        duplicates = set()
        for sort_order in sort_orders:
            if sort_order in seen:
                duplicates.add(sort_order)
            seen.add(sort_order)
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate sort_order values found: {duplicates}"
        )
    
    # Check for sequential order starting from 0
    expected_sequence = set(range(len(sort_orders)))
    actual_sequence = set(sort_orders)
    
    if actual_sequence != expected_sequence:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"sort_order must be sequential starting from 0. Expected: {sorted(expected_sequence)}, Got: {sorted(actual_sequence)}"
        )


def validate_all_ingredients_exist_no_duplicates(
        session: Session,
        recipe
) -> None:
    """
    Validate that all ingredients exist in the database.
    
    Raises:
        HTTPException(400): If any ingredient IDs don't exist in database
        HTTPException(409): If there are duplicate ingredient_ids in the recipe
    """
    if not recipe.ingredients:
        return
    
    # Check for duplicate ingredient_ids
    ingredient_ids = []
    for ing in recipe.ingredients:
        ingredient_ids.append(ing.ingredient_id)
    # Convert list to set: remove duplicates
    unique_ids = set(ingredient_ids)
    
    if len(ingredient_ids) != len(unique_ids):
        # Find duplicates
        seen = set()
        duplicates = set()
        for ing_id in ingredient_ids:
            if ing_id in seen:
                duplicates.add(ing_id)
            seen.add(ing_id)
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate ingredient IDs found: {duplicates}"
        )
    
    # Check that all ingredients exist in database
    existing_ingredients = session.exec(
        select(Ingredient).where(Ingredient.id.in_(unique_ids))
    ).all()
    
    if len(existing_ingredients) != len(unique_ids):
        # Check which id user sent that DB doesn't have
        existing_ids = {ing.id for ing in existing_ingredients}
        missing_ids = unique_ids - existing_ids
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid ingredient IDs: {missing_ids}"
        )
