from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import (
    Column, DateTime, ForeignKeyConstraint, PrimaryKeyConstraint, text,
    Index
)
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from app.models.recipe import Recipe


# ─── ORM SQLMOdel model for recipe_versions ─────────────────────────────────────────────────

class RecipeVersions(SQLModel, table=True):
    __tablename__ = 'recipe_versions'
    __table_args__ = (
        ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_versions_recipe_id_fkey'),
        PrimaryKeyConstraint('id', name='recipe_versions_pkey'),
        Index('idx_recipe_versions_recipe', 'recipe_id')
    )
    # Primary key, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    version: int = Field(nullable=False)
    data: dict = Field(sa_column=Column('data', JSONB, nullable=False))
    created_at: datetime = Field(sa_column=Column(
        'created_at', DateTime(True), nullable=False, server_default=text('now()')))
    # Foreign keys
    recipe_id: UUID = Field(nullable=False)
    # Relationship attributes
    recipe: 'Recipe' = Relationship(back_populates='recipe_versions')
