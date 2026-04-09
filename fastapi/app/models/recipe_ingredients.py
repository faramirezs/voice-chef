from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional, List, TYPE_CHECKING
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.users import Users, Tenants 
    from app.models.ingredient import Ingredient

class RecipeIngredient(SQLModel, table=True):
    __tablename__ = "recipe_ingredients"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    recipe_id: UUID = Field(foreign_key="recipes.id")
    ingredient_id: UUID = Field(foreign_key="ingredients.id")

    quantity: Decimal
    unit: str

    preparation: Optional[str] = None
    sort_order: int = 0

    # Relationships
    recipe: "Recipe" = Relationship(back_populates="recipe_ingredients")
    ingredient: "Ingredient" = Relationship(back_populates="recipe_ingredients")