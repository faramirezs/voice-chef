from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
import uuid
from uuid import UUID, uuid4

from sqlalchemy import PrimaryKeyConstraint, text, DateTime, Column
from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Index, Integer, LargeBinary, Numeric, String, Text, UniqueConstraint, Uuid
from sqlmodel import Field, SQLModel, Relationship


class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Core fields
    name: str = Field(max_length=255, index=True)
    status: str = Field(default="draft", max_length=50)

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Foreign keys
    tenant_id: UUID | None = Field(default=None, foreign_key="tenants.id")
    created_by: UUID | None = Field(default=None, foreign_key="users.id")

    # Text fields
    description: str | None = None
    description_short: str | None = None
    instructions: str | None = None
    notes: str | None = None
    notes_instructions: str | None = None
    serving_recommendation: str | None = None
    side_dishes: str | None = None
    storage_text: str | None = None
    origin_fish: str | None = None
    origin_location: str | None = None
    devices: str | None = None
    utensils: str | None = None
    packaging: str | None = None
    packaging_material: str | None = None
    ingredient_list_custom: str | None = None
    allergene_source: str | None = None
    preparation_time: str | None = None
    waiting_time: str | None = None
    cooking_time: str | None = None
    shelf_life: str | None = None
    yield_unit: str | None = Field(default=None, max_length=50)
    recipe_number: str | None = Field(default=None, max_length=100)
    batch_number: str | None = Field(default=None, max_length=100, index=True)
    storage_temperature: str | None = Field(default=None, max_length=50)
    labor_effort: str | None = Field(default=None, max_length=50)
    nutri_score_category: str | None = Field(default=None, max_length=10)
    unit_measure: str | None = Field(default=None, max_length=50)
    unit_serving: str | None = Field(default=None, max_length=50)
    yield_mode: str = Field(default="count", max_length=20, index=True)

    # Numeric fields
    yield_amount: Decimal | None = None
    reduction_factor: Decimal | None = Field(default=None, index=True)    
    eigene_menge: Decimal | None = None
    net_weight: Decimal | None = None
    fill_weight: Decimal | None = None
    fill_quantity: Decimal | None = None
    drained_weight: Decimal | None = None
    total_weight: Decimal | None = None
    portion_weight: Decimal | None = None
    margin: Decimal | None = None
    nutri_score_veg_fruits: Decimal | None = None
    preference_nutri_value: Decimal | None = None
    portion_size_grams: Decimal | None = None
    total_raw_weight_grams: Decimal | None = None
    total_cooked_weight_grams: Decimal | None = None
    portions_count_resolved: Decimal | None = None
    # NOTE: MK - DB schema defines their precision and scale. Therefore, no need enforce them here.
    # If enforcement of precision/scale in SQLModel wanted here, use the sa_column parameter
    # to specify a SQLAlchemy Column with the desired Numeric type.
    # For example:
    # # yield_amount: Optional[Decimal] = Field(sa_column=Column(Numeric(10, 2)))
    # # reduction_factor: Optional[Decimal] = Field(sa_column=Column(Numeric(10, 4)))
    # # nutri_score_veg_fruits: Optional[Decimal] = Field(sa_column=Column(Numeric(5, 2)))

    # Booleans
    portion_by_weight: bool = False
    mise_en_place_display: bool = True
    is_component: bool = Field(default=False, index=True)

    # Dates
    production_date: date | None = None 
    use_by_date: date | None = None
    expiry_date: date | None = None


class Ingredients(SQLModel, table=True):
    __tablename__ = "ingredients"

    id: UUID = Field(default_factory=uuid4, primary_key=True)     # Primary key
    name: str = Field(max_length=255, index=True)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    tenant_id: UUID | None = Field(default=None, foreign_key="tenants.id") 
    parent_id: UUID | None = Field(default=None, foreign_key="ingredients.id", index=True)
    default_unit: str | None = Field(default=None, max_length=50)
    ingredient_type: str | None = Field(default=None, max_length=50)
    bls_key: str | None = Field(default=None, max_length=100)
    nutrition_id: UUID | None = Field(default=None, foreign_key="nutrition_facts.id")
    initial_recipe_id: UUID | None = None
    usage_count: int | None = Field(default=0, index=True)
    recipe_count: int | None = 0
    is_custom: bool = False
    has_parent: bool = False
    # parent: Optional['Ingredients'] = Relationship(back_populates='children', sa_relationship_kwargs={"remote_side": "Ingredients.id"})
    # children: List['Ingredients'] = Relationship(back_populates='parent')
    # tenant: Optional['Tenants'] = Relationship(back_populates='ingredients')
    # ingredient_nutrition: Optional['IngredientNutrition'] = Relationship(sa_relationship_kwargs={'uselist': False}, back_populates='ingredient')
    # ingredient_prices: List['IngredientPrices'] = Relationship(back_populates='ingredient')
    # recipe_ingredients: List['RecipeIngredients'] = Relationship(back_populates='ingredient')


class Tenants(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tenants_pkey'),
        UniqueConstraint('slug', name='tenants_slug_key'),
        Index('ix_tenants_name', 'name'),
        Index('ix_tenants_slug', 'slug', unique=True)
    )

    id: UUID = Field(sa_column=Column('id', Uuid))
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    slug: str = Field(sa_column=Column('slug', String(100), nullable=False))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    settings: str | None = Field(default=None, sa_column=Column('settings', String))

    # ingredients: List['Ingredients'] = Relationship(back_populates='tenant')
    # users: List['Users'] = Relationship(back_populates='tenant')
    # recipes: List['Recipes'] = Relationship(back_populates='tenant')

class IngredientAllergens(SQLModel, table=True):
    __tablename__ = 'ingredient_allergens'
    __table_args__ = (
        ForeignKeyConstraint(['allergen_id'], ['allergens.id'], ondelete='CASCADE', name='ingredient_allergens_allergen_id_fkey'),
        PrimaryKeyConstraint('ingredient_id', 'allergen_id', name='ingredient_allergens_pkey'),
        Index('idx_ing_allergens_allergen', 'allergen_id')
    )

    ingredient_id: UUID = Field(sa_column=Column('ingredient_id', Uuid, nullable=False))
    allergen_id: UUID = Field(sa_column=Column('allergen_id', Uuid, nullable=False))

    # allergen: Optional['Allergens'] = Relationship(back_populates='ingredient_allergens')
    
class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='users_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        Index('ix_users_email', 'email', unique=True)
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
 
    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Text fields
    email: str
    password_hash: str
    role: str

    # Booleans
    is_active: bool

    # Foreign keys
    tenant_id: UUID | None = Field(default=None, foreign_key="tenants.id")


class Additives(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='additives_pkey'),
        UniqueConstraint('code', name='additives_code_key'),
        Index('idx_additives_code', 'code')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('uuid_generate_v4()')))
    code: str = Field(sa_column=Column('code', Text, nullable=False))
    name: str = Field(sa_column=Column('name', Text, nullable=False))

    ingredient_additives: list['IngredientAdditives'] = Relationship(back_populates='additive')


class IngredientAdditives(SQLModel, table=True):
    __tablename__ = 'ingredient_additives'
    __table_args__ = (
        ForeignKeyConstraint(['additive_id'], ['additives.id'], ondelete='CASCADE', name='ingredient_additives_additive_id_fkey'),
        PrimaryKeyConstraint('ingredient_id', 'additive_id', name='ingredient_additives_pkey'),
        Index('idx_ing_additives_additive', 'additive_id')
    )

    ingredient_id: uuid.UUID = Field(sa_column=Column('ingredient_id', Uuid, primary_key=True))
    additive_id: uuid.UUID = Field(sa_column=Column('additive_id', Uuid, primary_key=True))

    additive: 'Additives' = Relationship(back_populates='ingredient_additives')


# class RecipeIngredients(SQLModel, table=True):
#     __tablename__ = 'recipe_ingredients'
#     __table_args__ = (
#         ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='recipe_ingredients_ingredient_id_fkey'),
#         ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_ingredients_recipe_id_fkey'),
#         PrimaryKeyConstraint('id', name='recipe_ingredients_pkey'),
#         UniqueConstraint('recipe_id', 'ingredient_id', 'sort_order', name='uq_recipe_ingredient_order'),
#         Index('ix_recipe_ingredients_ingredient_id', 'ingredient_id'),
#         Index('ix_recipe_ingredients_recipe_id', 'recipe_id'),
#         Index('ix_recipe_ingredients_sort_order', 'sort_order')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid))
#     created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
#     updated_at: datetime = Field(sa_column=mapped_column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
#     recipe_id: UUID = Field(sa_column=mapped_column('recipe_id', Uuid, nullable=False))
#     ingredient_id: UUID = Field(sa_column=mapped_column('ingredient_id', Uuid, nullable=False))
#     sort_order: int = Field(sa_column=mapped_column('sort_order', Integer, nullable=False, server_default=text('0')))
#     quantity: Optional[Decimal] = Field(default=None, sa_column=mapped_column('quantity', Numeric(10, 4)))
#     unit: str | None = Field(default=None, sa_column=mapped_column('unit', String(50)))
#     preparation: str | None = Field(default=None, sa_column=mapped_column('preparation', String(255)))
#     quid: Optional[Decimal] = Field(default=None, sa_column=mapped_column('quid', Numeric(10, 4)))
#     item_type: str | None = Field(default=None, sa_column=mapped_column('item_type', String(50)))

#     ingredient: Optional['Ingredients'] = Relationship(back_populates='recipe_ingredients')
#     recipe: Optional['Recipes'] = Relationship(back_populates='recipe_ingredients')


# class Ingredients(SQLModel, table=True):
#     __table_args__ = (
#         ForeignKeyConstraint(['parent_id'], ['ingredients.id'], name='ingredients_parent_id_fkey'),
#         ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='ingredients_tenant_id_fkey'),
#         PrimaryKeyConstraint('id', name='ingredients_pkey'),
#         Index('idx_ingredients_parent_id', 'parent_id'),
#         Index('idx_ingredients_usage_count', 'usage_count'),
#         Index('ix_ingredients_name', 'name')
#     )

#     id: UUID = Field(sa_column=Column('id', Uuid))
#     created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
#     updated_at: datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
#     name: str = Field(sa_column=Column('name', String(255), nullable=False))
#     tenant_id: Optional[UUID] = Field(default=None, sa_column=Column('tenant_id', Uuid))
#     default_unit: str | None = Field(default=None, sa_column=Column('default_unit', String(50)))
#     nutrition_id: Optional[UUID] = Field(default=None, sa_column=Column('nutrition_id', Uuid))
#     usage_count: Optional[int] = Field(default=None, sa_column=Column('usage_count', Integer, server_default=text('0')))
#     recipe_count: Optional[int] = Field(default=None, sa_column=Column('recipe_count', Integer, server_default=text('0')))
#     ingredient_type: str | None = Field(default=None, sa_column=Column('ingredient_type', String(50)))
#     bls_key: str | None = Field(default=None, sa_column=Column('bls_key', String(100)))
#     is_custom: Optional[bool] = Field(default=None, sa_column=Column('is_custom', Boolean, server_default=text('false')))
#     has_parent: Optional[bool] = Field(default=None, sa_column=Column('has_parent', Boolean, server_default=text('false')))
#     parent_id: Optional[UUID] = Field(default=None, sa_column=Column('parent_id', Uuid))
#     initial_recipe_id: Optional[UUID] = Field(default=None, sa_column=Column('initial_recipe_id', Uuid))

#     parent: Optional['Ingredients'] = Relationship(back_populates='children', sa_relationship_kwargs={"remote_side": "Ingredients.id"})
#     children: List['Ingredients'] = Relationship(back_populates='parent')
#     tenant: Optional['Tenants'] = Relationship(back_populates='ingredients')
#     # ingredient_nutrition: Optional['IngredientNutrition'] = Relationship(sa_relationship_kwargs={'uselist': False}, back_populates='ingredient')
#     # ingredient_prices: List['IngredientPrices'] = Relationship(back_populates='ingredient')
#     # recipe_ingredients: List['RecipeIngredients'] = Relationship(back_populates='ingredient')



# class Allergens(SQLModel, table=True):
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='allergens_pkey'),
#         UniqueConstraint('code', name='allergens_code_key'),
#         Index('idx_allergens_code', 'code')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     code: str = Field(sa_column=mapped_column('code', Text, nullable=False))
#     name: str = Field(sa_column=mapped_column('name', Text, nullable=False))

#     ingredient_allergens: List['IngredientAllergens'] = Relationship(back_populates='allergen')


# class AuditLogs(SQLModel, table=True):
#     __tablename__ = 'audit_logs'
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='audit_logs_pkey'),
#         Index('idx_audit_logs_created', 'created_at'),
#         Index('idx_audit_logs_entity', 'entity', 'entity_id'),
#         Index('idx_audit_logs_user', 'user_id')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     action: str = Field(sa_column=mapped_column('action', Text, nullable=False))
#     entity: str = Field(sa_column=mapped_column('entity', Text, nullable=False))
#     user_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('user_id', Uuid))
#     entity_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('entity_id', Uuid))
#     created_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('created_at', DateTime(True), server_default=text('now()')))


# class Categories(SQLModel, table=True):
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='categories_pkey'),
#         Index('idx_categories_name', 'name')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     name: str = Field(sa_column=mapped_column('name', Text, nullable=False))

#     recipe_categories: List['RecipeCategories'] = Relationship(back_populates='category')


# class Files(SQLModel, table=True):
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='files_pkey'),
#         Index('idx_files_recipe', 'recipe_id')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     file_type: str = Field(sa_column=mapped_column('file_type', Text, nullable=False))
#     uri: str = Field(sa_column=mapped_column('uri', Text, nullable=False))
#     recipe_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('recipe_id', Uuid))
#     created_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('created_at', DateTime(True), server_default=text('now()')))


# class NutritionFacts(SQLModel, table=True):
#     __tablename__ = 'nutrition_facts'
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='nutrition_facts_pkey'),
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     energy_kj: Optional[Decimal] = Field(default=None, sa_column=mapped_column('energy_kj', Numeric))
#     energy_kcal: Optional[Decimal] = Field(default=None, sa_column=mapped_column('energy_kcal', Numeric))
#     fat: Optional[Decimal] = Field(default=None, sa_column=mapped_column('fat', Numeric))
#     saturates: Optional[Decimal] = Field(default=None, sa_column=mapped_column('saturates', Numeric))
#     carbs: Optional[Decimal] = Field(default=None, sa_column=mapped_column('carbs', Numeric))
#     sugars: Optional[Decimal] = Field(default=None, sa_column=mapped_column('sugars', Numeric))
#     protein: Optional[Decimal] = Field(default=None, sa_column=mapped_column('protein', Numeric))
#     salt: Optional[Decimal] = Field(default=None, sa_column=mapped_column('salt', Numeric))

#     recipe_nutrition: List['RecipeNutrition'] = Relationship(back_populates='nutrition')


# class RecipeVersions(SQLModel, table=True):
#     __tablename__ = 'recipe_versions'
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='recipe_versions_pkey'),
#         Index('idx_recipe_versions_data', 'data'),
#         Index('idx_recipe_versions_recipe', 'recipe_id')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     version: int = Field(sa_column=mapped_column('version', Integer, nullable=False))
#     data: dict = Field(sa_column=mapped_column('data', JSONB, nullable=False))
#     recipe_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('recipe_id', Uuid))
#     created_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('created_at', DateTime(True), server_default=text('now()')))


# class Tags(SQLModel, table=True):
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='tags_pkey'),
#         Index('idx_tags_name', 'name')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     name: str = Field(sa_column=mapped_column('name', Text, nullable=False))

#     recipe_tags: List['RecipeTags'] = Relationship(back_populates='tag')



# class RecipeCategories(SQLModel, table=True):
#     __tablename__ = 'recipe_categories'
#     __table_args__ = (
#         ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', name='recipe_categories_category_id_fkey'),
#         PrimaryKeyConstraint('recipe_id', 'category_id', name='recipe_categories_pkey'),
#         Index('idx_recipe_cat_category', 'category_id')
#     )

#     recipe_id: UUID = Field(sa_column=mapped_column('recipe_id', Uuid, nullable=False))
#     category_id: UUID = Field(sa_column=mapped_column('category_id', Uuid, nullable=False))

#     category: Optional['Categories'] = Relationship(back_populates='recipe_categories')


# class RecipeNutrition(SQLModel, table=True):
#     __tablename__ = 'recipe_nutrition'
#     __table_args__ = (
#         ForeignKeyConstraint(['nutrition_id'], ['nutrition_facts.id'], ondelete='CASCADE', name='recipe_nutrition_nutrition_id_fkey'),
#         PrimaryKeyConstraint('recipe_id', name='recipe_nutrition_pkey'),
#         Index('idx_recipe_nutrition_nutrition', 'nutrition_id')
#     )

#     recipe_id: UUID = Field(sa_column=mapped_column('recipe_id', Uuid))
#     nutrition_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('nutrition_id', Uuid))
#     updated_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('updated_at', DateTime(True), server_default=text('now()')))

#     nutrition: Optional['NutritionFacts'] = Relationship(back_populates='recipe_nutrition')


# class RecipeTags(SQLModel, table=True):
#     __tablename__ = 'recipe_tags'
#     __table_args__ = (
#         ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE', name='recipe_tags_tag_id_fkey'),
#         PrimaryKeyConstraint('recipe_id', 'tag_id', name='recipe_tags_pkey'),
#         Index('idx_recipe_tags_tag', 'tag_id')
#     )

#     recipe_id: UUID = Field(sa_column=mapped_column('recipe_id', Uuid, nullable=False))
#     tag_id: UUID = Field(sa_column=mapped_column('tag_id', Uuid, nullable=False))

#     tag: Optional['Tags'] = Relationship(back_populates='recipe_tags')


# class IngredientNutrition(SQLModel, table=True):
#     __tablename__ = 'ingredient_nutrition'
#     __table_args__ = (
#         ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_nutrition_ingredient_id_fkey'),
#         PrimaryKeyConstraint('id', name='ingredient_nutrition_pkey'),
#         UniqueConstraint('ingredient_id', name='ingredient_nutrition_ingredient_id_key')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('gen_random_uuid()')))
#     ingredient_id: UUID = Field(sa_column=mapped_column('ingredient_id', Uuid, nullable=False))
#     energy_kj: Optional[Decimal] = Field(default=None, sa_column=mapped_column('energy_kj', Numeric(10, 2)))
#     energy_kcal: Optional[Decimal] = Field(default=None, sa_column=mapped_column('energy_kcal', Numeric(10, 2)))
#     carbs: Optional[Decimal] = Field(default=None, sa_column=mapped_column('carbs', Numeric(10, 2)))
#     protein: Optional[Decimal] = Field(default=None, sa_column=mapped_column('protein', Numeric(10, 2)))
#     fat: Optional[Decimal] = Field(default=None, sa_column=mapped_column('fat', Numeric(10, 2)))
#     sugars: Optional[Decimal] = Field(default=None, sa_column=mapped_column('sugars', Numeric(10, 2)))
#     fiber: Optional[Decimal] = Field(default=None, sa_column=mapped_column('fiber', Numeric(10, 2)))
#     saturates: Optional[Decimal] = Field(default=None, sa_column=mapped_column('saturates', Numeric(10, 2)))
#     salt: Optional[Decimal] = Field(default=None, sa_column=mapped_column('salt', Numeric(10, 2)))
#     created_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('created_at', DateTime(True), server_default=text('now()')))
#     updated_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('updated_at', DateTime(True), server_default=text('now()')))
#     alcohol: Optional[Decimal] = Field(default=None, sa_column=mapped_column('alcohol', Numeric(10, 3)))
#     water: Optional[Decimal] = Field(default=None, sa_column=mapped_column('water', Numeric(10, 3)))

#     ingredient: Optional['Ingredients'] = Relationship(back_populates='ingredient_nutrition')


# class IngredientPrices(SQLModel, table=True):
#     __tablename__ = 'ingredient_prices'
#     __table_args__ = (
#         ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_prices_ingredient_id_fkey'),
#         PrimaryKeyConstraint('id', name='ingredient_prices_pkey'),
#         UniqueConstraint('ingredient_id', 'supplier_id', name='ingredient_prices_ingredient_id_supplier_id_key'),
#         Index('idx_ingredient_prices_ingredient', 'ingredient_id')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     ingredient_id: UUID = Field(sa_column=mapped_column('ingredient_id', Uuid, nullable=False))
#     price_per_unit: Optional[Decimal] = Field(default=None, sa_column=mapped_column('price_per_unit', Numeric(10, 2)))
#     currency: str | None = Field(default=None, sa_column=mapped_column('currency', String(3), server_default=text("'EUR'::character varying")))
#     unit: str | None = Field(default=None, sa_column=mapped_column('unit', String(50)))
#     supplier_id: str | None = Field(default=None, sa_column=mapped_column('supplier_id', String(100)))
#     supplier_name: str | None = Field(default=None, sa_column=mapped_column('supplier_name', String(255)))
#     article_number: str | None = Field(default=None, sa_column=mapped_column('article_number', String(100)))
#     created_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('created_at', DateTime(True), server_default=text('now()')))
#     updated_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('updated_at', DateTime(True), server_default=text('now()')))

#     ingredient: Optional['Ingredients'] = Relationship(back_populates='ingredient_prices')


# class RecipePhotos(SQLModel, table=True):
#     __tablename__ = 'recipe_photos'
#     __table_args__ = (
#         ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_photos_recipe_id_fkey'),
#         PrimaryKeyConstraint('id', name='recipe_photos_pkey'),
#         Index('idx_recipe_photos_recipe', 'recipe_id')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     recipe_id: UUID = Field(sa_column=mapped_column('recipe_id', Uuid, nullable=False))
#     photo_url: str | None = Field(default=None, sa_column=mapped_column('photo_url', Text))
#     photo_data: Optional[bytes] = Field(default=None, sa_column=mapped_column('photo_data', LargeBinary))
#     photo_type: str | None = Field(default=None, sa_column=mapped_column('photo_type', String(50)))
#     is_primary: Optional[bool] = Field(default=None, sa_column=mapped_column('is_primary', Boolean, server_default=text('false')))
#     created_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('created_at', DateTime(True), server_default=text('now()')))

#     recipe: Optional['Recipes'] = Relationship(back_populates='recipe_photos')
