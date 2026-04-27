from sqlmodel import Session, select
from uuid import UUID
from fastapi import HTTPException, status
from app.models.recipe import Recipe


def to_recipe_ingredient_response(link):
    ingredient = link.ingredient

    return {
        "id": link.id,
        "ingredient_id": ingredient.id,
        "ingredient_name": ingredient.name,
        "ingredient_default_unit": ingredient.default_unit,
        "quantity": link.quantity,
        "unit": link.unit,
        "quantity_grams": (
            link.quantity * 1000 if link.unit == "kg" else link.quantity
        ),
        "preparation": link.preparation,
        "sort_order": link.sort_order,
    }


# NOTE: mpeshko - link is RecipeIngredient, link.ingredient is an Ingredient
def to_recipe_detail(recipe):
    result = recipe.model_dump()

    ingredients_list = []
    for link in sorted(recipe.recipe_ingredients, key=lambda x: x.sort_order or 0):
        if link.ingredient:
            ingredients_list.append({
                "id": link.id,
                "ingredient_id": link.ingredient.id,
                "ingredient_name": link.ingredient.name,
                "ingredient_default_unit": link.ingredient.default_unit,
                
                "quantity": link.quantity,
                "unit": link.unit,
                "quantity_grams": link.quantity_grams,
                
                "preparation": link.preparation.strip() if link.preparation else None,
                "sort_order": link.sort_order
            })
    
    result["ingredients"] = ingredients_list
    return result

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
