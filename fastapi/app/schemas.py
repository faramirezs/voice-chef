from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List

class RecipeCreate(SQLModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None