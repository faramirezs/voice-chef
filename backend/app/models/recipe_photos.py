# from datetime import date, datetime
# from decimal import Decimal
# from uuid import UUID, uuid4
# from typing import Optional, TYPE_CHECKING

# from sqlmodel import SQLModel, Field, Relationship
# from sqlalchemy import Index, CheckConstraint, Column, Text, UniqueConstraint, text, Boolean, DateTime, LargeBinary

# if TYPE_CHECKING:
#     from app.models.recipe import Recipe


# class RecipePhoto(SQLModel, table=True):
#     __tablename__ = "recipe_photos"
#     __table_args__ = (
#         Index("idx_recipe_photos_recipe", "recipe_id"),
#     )

#     # Primary key, Timestamps
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     created_at: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
# )
#     # Core fields
#     photo_url: str | None = Field(default=None, sa_column=Column(Text))
#     photo_type: str | None = Field(default=None, max_length=50)
#     photo_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))

#     # Booleans
#     is_primary: bool = Field(default=False, sa_column=Column(Boolean, server_default=text("false")))

#     # Foreign keys
#     recipe_id: UUID = Field(foreign_key="recipes.id", ondelete="CASCADE", nullable=False)

#     # Relationship attributes
#     recipe: Optional["Recipe"] = Relationship(back_populates="recipe_photos")
