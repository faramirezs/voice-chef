from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import (
    ForeignKeyConstraint, PrimaryKeyConstraint,
    Column, String, text
)
from uuid import UUID

if TYPE_CHECKING:
    from app.models.users import Tenants
    from app.models.recipe import Recipe


# ─── ORM SQLMOdel model for categories ─────────────────────────────────────────────────

# Categories are typically a strict hierarchy (for example: Soups, Desserts, 
# Beverages). A recipe usually belongs to only one category.

#                   id                  |   name   | tenant_id
# --------------------------------------+----------+-----------
#  ad707d77-d0d1-50c3-a439-2ff69c384fe5 | Buffet   |
#  4153ecd0-06a4-5deb-92a5-b082735ba9c8 | Dessert  |
#  adac8118-7a91-52a8-91a7-d593e5b5bdc1 | Kantine  |
#  d24ab8c5-85de-5842-955e-65e174b390e7 | Kuchen   |
#  f242e6ee-53ca-5836-912f-0cd195b68d3f | Sandwich |
#  f1885a49-c43d-5256-b423-fdd078dd7e97 | Zutat    |
#  c6df4441-3866-5ba7-bbf2-4f1222e4d869 | buffet   |

class Categories(SQLModel, table=True):
    __tablename__ = "categories"
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='categories_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='categories_pkey')
    )
    # Primary key
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    # Core fields
    name: str = Field(max_length=255, nullable=False)
    # Foreign keys
    tenant_id: UUID | None = Field(default=None)
    # Relationship attributes
    tenant: Optional['Tenants'] = Relationship(back_populates='categories')
    recipe: list['Recipe'] = Relationship(
        back_populates='category', 
        sa_relationship_kwargs={'secondary': 'recipe_categories'})


# ─── ORM SQLMOdel model for tags ─────────────────────────────────────────────────

# Tags are flexible labels (for example: "Spicy", "Lactose-free"). 
# A single recipe can have multiple tags at the same time.

#  id | name | tenant_id
# ----+------+-----------
# (0 rows)

class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='tags_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='tags_pkey')
    )

    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    name: str = Field(max_length=255, nullable=False)
    # Foreign keys
    tenant_id: UUID | None = Field(default=None)
    # Relationship attributes
    tenant: Optional['Tenants'] = Relationship(back_populates='tags')
    recipe: list['Recipe'] = Relationship(
        back_populates='tag', sa_relationship_kwargs={'secondary': 'recipe_tags'})
