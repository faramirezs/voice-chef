from sqlmodel import SQLModel
from sqlalchemy import (
    Table, Index, PrimaryKeyConstraint,
    ForeignKeyConstraint, Column, Uuid,
)


# ─── ORM object for ingredient_allergens (Many-to-Many) ─────────────────────────────────────────────────

# NOTE: mpeshko. SQLModel uses this Table object simply to determine how to 
# link Ingredients and Additives without creating an unnecessary Python class 
# that you would never need on its own.

t_ingredient_allergens = Table(
    'ingredient_allergens', 
    SQLModel.metadata,
    Column('ingredient_id', Uuid, primary_key=True),
    Column('allergen_id', Uuid, primary_key=True),
    ForeignKeyConstraint(['allergen_id'], ['allergens.id'], ondelete='CASCADE', name='ingredient_allergens_allergen_id_fkey'),
    ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_allergens_ingredient_id_fkey'),
    PrimaryKeyConstraint('ingredient_id', 'allergen_id', name='ingredient_allergens_pkey'),
    Index('idx_ing_allergens_allergen', 'allergen_id')
)


t_ingredient_additives = Table(
    'ingredient_additives', 
    SQLModel.metadata,
    Column('ingredient_id', Uuid, primary_key=True),
    Column('additive_id', Uuid, primary_key=True),
    ForeignKeyConstraint(['additive_id'], ['additives.id'], ondelete='CASCADE', name='ingredient_additives_additive_id_fkey'),
    ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_additives_ingredient_id_fkey'),
    PrimaryKeyConstraint('ingredient_id', 'additive_id', name='ingredient_additives_pkey'),
    Index('idx_ing_additives_additive', 'additive_id')
)

t_recipe_categories = Table(
    'recipe_categories', SQLModel.metadata,
    Column('recipe_id', Uuid, primary_key=True),
    Column('category_id', Uuid, primary_key=True),
    ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', name='recipe_categories_category_id_fkey'),
    ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_categories_recipe_id_fkey'),
    PrimaryKeyConstraint('recipe_id', 'category_id', name='recipe_categories_pkey'),
    Index('idx_recipe_categories_cat', 'category_id')
)

t_recipe_tags = Table(
    'recipe_tags', SQLModel.metadata,
    Column('recipe_id', Uuid, primary_key=True),
    Column('tag_id', Uuid, primary_key=True),
    ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_tags_recipe_id_fkey'),
    ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE', name='recipe_tags_tag_id_fkey'),
    PrimaryKeyConstraint('recipe_id', 'tag_id', name='recipe_tags_pkey'),
    Index('idx_recipe_tags_tag', 'tag_id')
)
