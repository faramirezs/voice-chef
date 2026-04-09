from app.models.recipe import Recipe
from app.models.recipe_ingredients import RecipeIngredient
from app.models.ingredient import Ingredient

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


def to_recipe_detail(recipe):
    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "status": recipe.status,
        "yield_mode": recipe.yield_mode,
        "portion_size_grams": recipe.portion_size_grams,
        "total_raw_weight_grams": recipe.total_raw_weight_grams,
        "total_cooked_weight_grams": recipe.total_cooked_weight_grams,
        "portions_count_resolved": recipe.portions_count_resolved,
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at,
        "ingredients": [
            to_recipe_ingredient_response(link)
            for link in sorted(recipe.recipe_ingredients, key=lambda x: x.sort_order)
        ],
    }