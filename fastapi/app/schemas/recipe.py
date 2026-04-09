from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List


class RecipeCreate(SQLModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None

class RecipeRead(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    # description: Optional[str] = None
    # instructions: Optional[str] = None

class RecipeUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
