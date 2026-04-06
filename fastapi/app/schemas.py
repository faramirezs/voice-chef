from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List


class RecipeCreate(SQLModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None

class RecipeRead(SQLModel):
    id: UUID
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None

class RecipeUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    instructions: str | None = None

class IngredientCreate(SQLModel):
    name: str
    quantity: Optional[str] = None