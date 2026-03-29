from typing import Optional
import datetime
import decimal
import uuid
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Index, Integer, LargeBinary, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field, Relationship, SQLModel

class Additives(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='additives_pkey'),
        UniqueConstraint('code', name='additives_code_key'),
        Index('idx_additives_code', 'code')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')))
    code: str = Field(sa_column=Column('code', Text, nullable=False))
    name: str = Field(sa_column=Column('name', Text, nullable=False))

    ingredient_additives: list['IngredientAdditives'] = Relationship(back_populates='additive')


class Allergens(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='allergens_pkey'),
        UniqueConstraint('code', name='allergens_code_key'),
        Index('idx_allergens_code', 'code')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')))
    code: str = Field(sa_column=Column('code', Text, nullable=False))
    name: str = Field(sa_column=Column('name', Text, nullable=False))

    ingredient_allergens: list['IngredientAllergens'] = Relationship(back_populates='allergen')


class AuditLogs(SQLModel, table=True):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='audit_logs_pkey'),
        Index('idx_audit_logs_created', 'created_at'),
        Index('idx_audit_logs_entity', 'entity', 'entity_id'),
        Index('idx_audit_logs_user', 'user_id')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')))
    action: str = Field(sa_column=Column('action', Text, nullable=False))
    entity: str = Field(sa_column=Column('entity', Text, nullable=False))
    user_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('user_id', UUID(as_uuid=True)))
    entity_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('entity_id', UUID(as_uuid=True)))
    created_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('created_at', DateTime(True), server_default=text('now()')))


class Categories(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='categories_pkey'),
        Index('idx_categories_name', 'name')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')))
    name: str = Field(sa_column=Column('name', Text, nullable=False))

    recipe_categories: list['RecipeCategories'] = Relationship(back_populates='category')


class Files(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='files_pkey'),
        Index('idx_files_recipe', 'recipe_id')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')))
    file_type: str = Field(sa_column=Column('file_type', Text, nullable=False))
    uri: str = Field(sa_column=Column('uri', Text, nullable=False))
    recipe_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('recipe_id', UUID(as_uuid=True)))
    created_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('created_at', DateTime(True), server_default=text('now()')))


class NutritionFacts(SQLModel, table=True):
    __tablename__ = 'nutrition_facts'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='nutrition_facts_pkey'),
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')))
    energy_kj: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('energy_kj', Numeric))
    energy_kcal: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('energy_kcal', Numeric))
    fat: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('fat', Numeric))
    saturates: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('saturates', Numeric))
    carbs: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('carbs', Numeric))
    sugars: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('sugars', Numeric))
    protein: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('protein', Numeric))
    salt: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('salt', Numeric))

    recipe_nutrition: list['RecipeNutrition'] = Relationship(back_populates='nutrition')


class RecipeVersions(SQLModel, table=True):
    __tablename__ = 'recipe_versions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='recipe_versions_pkey'),
        Index('idx_recipe_versions_data', 'data', postgresql_using='gin'),
        Index('idx_recipe_versions_recipe', 'recipe_id')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')))
    version: int = Field(sa_column=Column('version', Integer, nullable=False))
    data: dict = Field(sa_column=Column('data', JSONB, nullable=False))
    recipe_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('recipe_id', UUID(as_uuid=True)))
    created_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('created_at', DateTime(True), server_default=text('now()')))


class Tags(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tags_pkey'),
        Index('idx_tags_name', 'name')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')))
    name: str = Field(sa_column=Column('name', Text, nullable=False))

    recipe_tags: list['RecipeTags'] = Relationship(back_populates='tag')


class Tenants(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tenants_pkey'),
        UniqueConstraint('slug', name='tenants_slug_key'),
        Index('ix_tenants_name', 'name'),
        Index('ix_tenants_slug', 'slug', unique=True)
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    slug: str = Field(sa_column=Column('slug', String(100), nullable=False))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    settings: Optional[str] = Field(default=None, sa_column=Column('settings', String))

    ingredients: list['Ingredients'] = Relationship(back_populates='tenant')
    users: list['Users'] = Relationship(back_populates='tenant')
    recipes: list['Recipes'] = Relationship(back_populates='tenant')


class Units(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("unit_type::text = ANY (ARRAY['weight'::character varying, 'volume'::character varying, 'piece'::character varying, 'custom'::character varying]::text[])", name='valid_unit_type'),
        PrimaryKeyConstraint('id', name='units_pkey'),
        UniqueConstraint('code', name='units_code_key')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    code: str = Field(sa_column=Column('code', String(20), nullable=False))
    name_de: str = Field(sa_column=Column('name_de', String(100), nullable=False))
    unit_type: str = Field(sa_column=Column('unit_type', String(20), nullable=False))
    is_base: bool = Field(sa_column=Column('is_base', Boolean, nullable=False, server_default=text('false')))
    name_en: Optional[str] = Field(default=None, sa_column=Column('name_en', String(100)))
    grams_per_unit: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('grams_per_unit', Numeric))


class IngredientAdditives(SQLModel, table=True):
    __tablename__ = 'ingredient_additives'
    __table_args__ = (
        ForeignKeyConstraint(['additive_id'], ['additives.id'], ondelete='CASCADE', name='ingredient_additives_additive_id_fkey'),
        PrimaryKeyConstraint('ingredient_id', 'additive_id', name='ingredient_additives_pkey'),
        Index('idx_ing_additives_additive', 'additive_id')
    )

    ingredient_id: uuid.UUID = Field(sa_column=Column('ingredient_id', UUID(as_uuid=True), primary_key=True))
    additive_id: uuid.UUID = Field(sa_column=Column('additive_id', UUID(as_uuid=True), primary_key=True))

    additive: 'Additives' = Relationship(back_populates='ingredient_additives')


class IngredientAllergens(SQLModel, table=True):
    __tablename__ = 'ingredient_allergens'
    __table_args__ = (
        ForeignKeyConstraint(['allergen_id'], ['allergens.id'], ondelete='CASCADE', name='ingredient_allergens_allergen_id_fkey'),
        PrimaryKeyConstraint('ingredient_id', 'allergen_id', name='ingredient_allergens_pkey'),
        Index('idx_ing_allergens_allergen', 'allergen_id')
    )

    ingredient_id: uuid.UUID = Field(sa_column=Column('ingredient_id', UUID(as_uuid=True), primary_key=True))
    allergen_id: uuid.UUID = Field(sa_column=Column('allergen_id', UUID(as_uuid=True), primary_key=True))

    allergen: 'Allergens' = Relationship(back_populates='ingredient_allergens')


class Ingredients(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['parent_id'], ['ingredients.id'], name='ingredients_parent_id_fkey'),
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='ingredients_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredients_pkey'),
        Index('idx_ingredients_parent_id', 'parent_id'),
        Index('idx_ingredients_usage_count', 'usage_count'),
        Index('ix_ingredients_name', 'name')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    tenant_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('tenant_id', UUID(as_uuid=True)))
    default_unit: Optional[str] = Field(default=None, sa_column=Column('default_unit', String(50)))
    nutrition_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('nutrition_id', UUID(as_uuid=True)))
    usage_count: Optional[int] = Field(default=None, sa_column=Column('usage_count', Integer, server_default=text('0')))
    recipe_count: Optional[int] = Field(default=None, sa_column=Column('recipe_count', Integer, server_default=text('0')))
    ingredient_type: Optional[str] = Field(default=None, sa_column=Column('ingredient_type', String(50)))
    bls_key: Optional[str] = Field(default=None, sa_column=Column('bls_key', String(100)))
    is_custom: Optional[bool] = Field(default=None, sa_column=Column('is_custom', Boolean, server_default=text('false')))
    has_parent: Optional[bool] = Field(default=None, sa_column=Column('has_parent', Boolean, server_default=text('false')))
    parent_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('parent_id', UUID(as_uuid=True)))
    initial_recipe_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('initial_recipe_id', UUID(as_uuid=True)))

    parent: Optional['Ingredients'] = Relationship(back_populates='parent_reverse', sa_relationship_kwargs={'remote_side': '[Ingredients.id]'})
    parent_reverse: list['Ingredients'] = Relationship(back_populates='parent', sa_relationship_kwargs={'remote_side': '[Ingredients.parent_id]'})
    tenant: Optional['Tenants'] = Relationship(back_populates='ingredients')
    ingredient_nutrition: 'IngredientNutrition' = Relationship(back_populates='ingredient', sa_relationship_kwargs={'uselist': False})
    ingredient_prices: list['IngredientPrices'] = Relationship(back_populates='ingredient')
    ingredient_units: list['IngredientUnits'] = Relationship(back_populates='ingredient')
    recipe_ingredients: list['RecipeIngredients'] = Relationship(back_populates='ingredient')


class RecipeCategories(SQLModel, table=True):
    __tablename__ = 'recipe_categories'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', name='recipe_categories_category_id_fkey'),
        PrimaryKeyConstraint('recipe_id', 'category_id', name='recipe_categories_pkey'),
        Index('idx_recipe_cat_category', 'category_id')
    )

    recipe_id: uuid.UUID = Field(sa_column=Column('recipe_id', UUID(as_uuid=True), primary_key=True))
    category_id: uuid.UUID = Field(sa_column=Column('category_id', UUID(as_uuid=True), primary_key=True))

    category: 'Categories' = Relationship(back_populates='recipe_categories')


class RecipeNutrition(SQLModel, table=True):
    __tablename__ = 'recipe_nutrition'
    __table_args__ = (
        ForeignKeyConstraint(['nutrition_id'], ['nutrition_facts.id'], ondelete='CASCADE', name='recipe_nutrition_nutrition_id_fkey'),
        PrimaryKeyConstraint('recipe_id', name='recipe_nutrition_pkey'),
        Index('idx_recipe_nutrition_nutrition', 'nutrition_id')
    )

    recipe_id: uuid.UUID = Field(sa_column=Column('recipe_id', UUID(as_uuid=True), primary_key=True))
    nutrition_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('nutrition_id', UUID(as_uuid=True)))
    updated_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('updated_at', DateTime(True), server_default=text('now()')))

    nutrition: Optional['NutritionFacts'] = Relationship(back_populates='recipe_nutrition')


class RecipeTags(SQLModel, table=True):
    __tablename__ = 'recipe_tags'
    __table_args__ = (
        ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE', name='recipe_tags_tag_id_fkey'),
        PrimaryKeyConstraint('recipe_id', 'tag_id', name='recipe_tags_pkey'),
        Index('idx_recipe_tags_tag', 'tag_id')
    )

    recipe_id: uuid.UUID = Field(sa_column=Column('recipe_id', UUID(as_uuid=True), primary_key=True))
    tag_id: uuid.UUID = Field(sa_column=Column('tag_id', UUID(as_uuid=True), primary_key=True))

    tag: 'Tags' = Relationship(back_populates='recipe_tags')


class Users(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='users_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        Index('ix_users_email', 'email', unique=True)
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    email: str = Field(sa_column=Column('email', String(255), nullable=False))
    password_hash: str = Field(sa_column=Column('password_hash', String(255), nullable=False))
    role: str = Field(sa_column=Column('role', String(50), nullable=False, server_default=text("'editor'::character varying")))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    tenant_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('tenant_id', UUID(as_uuid=True)))

    tenant: Optional['Tenants'] = Relationship(back_populates='users')
    recipes: list['Recipes'] = Relationship(back_populates='users')


class IngredientNutrition(SQLModel, table=True):
    __tablename__ = 'ingredient_nutrition'
    __table_args__ = (
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_nutrition_ingredient_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredient_nutrition_pkey'),
        UniqueConstraint('ingredient_id', name='ingredient_nutrition_ingredient_id_key')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    ingredient_id: uuid.UUID = Field(sa_column=Column('ingredient_id', UUID(as_uuid=True), nullable=False))
    energy_kj: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('energy_kj', Numeric(10, 2)))
    energy_kcal: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('energy_kcal', Numeric(10, 2)))
    carbs: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('carbs', Numeric(10, 2)))
    protein: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('protein', Numeric(10, 2)))
    fat: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('fat', Numeric(10, 2)))
    sugars: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('sugars', Numeric(10, 2)))
    fiber: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('fiber', Numeric(10, 2)))
    saturates: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('saturates', Numeric(10, 2)))
    salt: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('salt', Numeric(10, 2)))
    created_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('created_at', DateTime(True), server_default=text('now()')))
    updated_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('updated_at', DateTime(True), server_default=text('now()')))
    alcohol: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('alcohol', Numeric(10, 3)))
    water: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('water', Numeric(10, 3)))

    ingredient: 'Ingredients' = Relationship(back_populates='ingredient_nutrition')


class IngredientPrices(SQLModel, table=True):
    __tablename__ = 'ingredient_prices'
    __table_args__ = (
        CheckConstraint('price_per_gram IS NULL OR price_per_gram > 0::numeric', name='ingredient_prices_price_per_gram_positive'),
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_prices_ingredient_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredient_prices_pkey'),
        UniqueConstraint('ingredient_id', 'supplier_id', name='ingredient_prices_ingredient_id_supplier_id_key'),
        Index('idx_ingredient_prices_ingredient', 'ingredient_id'),
        Index('idx_ingredient_prices_latest_lookup', 'ingredient_id', 'unit', 'updated_at', 'created_at', 'id')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')))
    ingredient_id: uuid.UUID = Field(sa_column=Column('ingredient_id', UUID(as_uuid=True), nullable=False))
    price_per_unit: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('price_per_unit', Numeric(10, 2)))
    currency: Optional[str] = Field(default=None, sa_column=Column('currency', String(3), server_default=text("'EUR'::character varying")))
    unit: Optional[str] = Field(default=None, sa_column=Column('unit', String(50)))
    supplier_id: Optional[str] = Field(default=None, sa_column=Column('supplier_id', String(100)))
    supplier_name: Optional[str] = Field(default=None, sa_column=Column('supplier_name', String(255)))
    article_number: Optional[str] = Field(default=None, sa_column=Column('article_number', String(100)))
    created_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('created_at', DateTime(True), server_default=text('now()')))
    updated_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('updated_at', DateTime(True), server_default=text('now()')))
    price_per_gram: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('price_per_gram', Numeric(14, 8)))

    ingredient: 'Ingredients' = Relationship(back_populates='ingredient_prices')


class IngredientUnits(SQLModel, table=True):
    __tablename__ = 'ingredient_units'
    __table_args__ = (
        CheckConstraint('grams_per_unit > 0::numeric', name='ingredient_units_grams_per_unit_positive'),
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_units_ingredient_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredient_units_pkey'),
        UniqueConstraint('ingredient_id', 'unit_code', name='uq_ingredient_unit'),
        Index('idx_ingredient_units_ingredient', 'ingredient_id')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    ingredient_id: uuid.UUID = Field(sa_column=Column('ingredient_id', UUID(as_uuid=True), nullable=False))
    unit_code: str = Field(sa_column=Column('unit_code', String(20), nullable=False))
    grams_per_unit: decimal.Decimal = Field(sa_column=Column('grams_per_unit', Numeric, nullable=False))
    label: Optional[str] = Field(default=None, sa_column=Column('label', String(100)))

    ingredient: 'Ingredients' = Relationship(back_populates='ingredient_units')


class Recipes(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint('portion_size_grams IS NULL OR portion_size_grams > 0::numeric', name='positive_portion_size_grams'),
        CheckConstraint('portions_count_resolved IS NULL OR portions_count_resolved > 0::numeric', name='positive_portions_count_resolved'),
        CheckConstraint("status::text <> 'active'::text OR yield_mode::text <> 'weight'::text OR portion_size_grams IS NOT NULL AND portion_size_grams > 0::numeric", name='weight_mode_requires_portion_size_when_active'),
        CheckConstraint('total_cooked_weight_grams IS NULL OR total_cooked_weight_grams >= 0::numeric', name='positive_total_cooked_weight_grams'),
        CheckConstraint('total_raw_weight_grams IS NULL OR total_raw_weight_grams >= 0::numeric', name='positive_total_raw_weight_grams'),
        CheckConstraint("yield_mode::text = ANY (ARRAY['count'::character varying, 'weight'::character varying]::text[])", name='valid_yield_mode'),
        ForeignKeyConstraint(['created_by'], ['users.id'], name='recipes_created_by_fkey'),
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='recipes_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='recipes_pkey'),
        Index('idx_recipes_batch_number', 'batch_number'),
        Index('idx_recipes_is_component', 'is_component'),
        Index('idx_recipes_reduction_factor', 'reduction_factor'),
        Index('idx_recipes_yield_mode', 'yield_mode'),
        Index('ix_recipes_name', 'name')
    )
    id: uuid.UUID = Field(default_factory=uuid4, primary_key=True)

    # id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    status: str = Field(sa_column=Column('status', String(50), nullable=False, server_default=text("'draft'::character varying")))
    yield_mode: str = Field(sa_column=Column('yield_mode', String(20), nullable=False, server_default=text("'count'::character varying")))
    tenant_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('tenant_id', UUID(as_uuid=True)))
    description: Optional[str] = Field(default=None, sa_column=Column('description', Text))
    yield_amount: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('yield_amount', Numeric(10, 2)))
    yield_unit: Optional[str] = Field(default=None, sa_column=Column('yield_unit', String(50)))
    instructions: Optional[str] = Field(default=None, sa_column=Column('instructions', Text))
    created_by: Optional[uuid.UUID] = Field(default=None, sa_column=Column('created_by', UUID(as_uuid=True)))
    description_short: Optional[str] = Field(default=None, sa_column=Column('description_short', Text))
    serving_recommendation: Optional[str] = Field(default=None, sa_column=Column('serving_recommendation', Text))
    side_dishes: Optional[str] = Field(default=None, sa_column=Column('side_dishes', Text))
    notes: Optional[str] = Field(default=None, sa_column=Column('notes', Text))
    preparation_time: Optional[str] = Field(default=None, sa_column=Column('preparation_time', Text))
    waiting_time: Optional[str] = Field(default=None, sa_column=Column('waiting_time', Text))
    cooking_time: Optional[str] = Field(default=None, sa_column=Column('cooking_time', Text))
    shelf_life: Optional[str] = Field(default=None, sa_column=Column('shelf_life', Text))
    reduction_factor: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('reduction_factor', Numeric(10, 4)))
    eigene_menge: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('eigene_menge', Numeric(10, 2)))
    recipe_number: Optional[str] = Field(default=None, sa_column=Column('recipe_number', String(100)))
    packaging: Optional[str] = Field(default=None, sa_column=Column('packaging', Text))
    packaging_material: Optional[str] = Field(default=None, sa_column=Column('packaging_material', Text))
    net_weight: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('net_weight', Numeric(10, 2)))
    fill_weight: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('fill_weight', Numeric(10, 2)))
    fill_quantity: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('fill_quantity', Numeric(10, 2)))
    drained_weight: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('drained_weight', Numeric(10, 2)))
    total_weight: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('total_weight', Numeric(10, 2)))
    portion_by_weight: Optional[bool] = Field(default=None, sa_column=Column('portion_by_weight', Boolean, server_default=text('false')))
    portion_weight: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('portion_weight', Numeric(10, 2)))
    batch_number: Optional[str] = Field(default=None, sa_column=Column('batch_number', String(100)))
    production_date: Optional[datetime.date] = Field(default=None, sa_column=Column('production_date', Date))
    use_by_date: Optional[datetime.date] = Field(default=None, sa_column=Column('use_by_date', Date))
    expiry_date: Optional[datetime.date] = Field(default=None, sa_column=Column('expiry_date', Date))
    storage_text: Optional[str] = Field(default=None, sa_column=Column('storage_text', Text))
    storage_temperature: Optional[str] = Field(default=None, sa_column=Column('storage_temperature', String(50)))
    origin_fish: Optional[str] = Field(default=None, sa_column=Column('origin_fish', Text))
    origin_location: Optional[str] = Field(default=None, sa_column=Column('origin_location', Text))
    devices: Optional[str] = Field(default=None, sa_column=Column('devices', Text))
    utensils: Optional[str] = Field(default=None, sa_column=Column('utensils', Text))
    labor_effort: Optional[str] = Field(default=None, sa_column=Column('labor_effort', String(50)))
    margin: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('margin', Numeric(10, 2)))
    nutri_score_category: Optional[str] = Field(default=None, sa_column=Column('nutri_score_category', String(10)))
    nutri_score_veg_fruits: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('nutri_score_veg_fruits', Numeric(5, 2)))
    mise_en_place_display: Optional[bool] = Field(default=None, sa_column=Column('mise_en_place_display', Boolean, server_default=text('true')))
    notes_instructions: Optional[str] = Field(default=None, sa_column=Column('notes_instructions', Text))
    is_component: Optional[bool] = Field(default=None, sa_column=Column('is_component', Boolean, server_default=text('false')))
    ingredient_list_custom: Optional[str] = Field(default=None, sa_column=Column('ingredient_list_custom', Text))
    allergene_source: Optional[str] = Field(default=None, sa_column=Column('allergene_source', Text))
    unit_measure: Optional[str] = Field(default=None, sa_column=Column('unit_measure', String(50)))
    unit_serving: Optional[str] = Field(default=None, sa_column=Column('unit_serving', String(50)))
    preference_nutri_value: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('preference_nutri_value', Numeric(10, 2)))
    portion_size_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('portion_size_grams', Numeric))
    total_raw_weight_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('total_raw_weight_grams', Numeric))
    total_cooked_weight_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('total_cooked_weight_grams', Numeric))
    portions_count_resolved: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('portions_count_resolved', Numeric))

    users: Optional['Users'] = Relationship(back_populates='recipes')
    tenant: Optional['Tenants'] = Relationship(back_populates='recipes')
    recipe_ingredients: list['RecipeIngredients'] = Relationship(back_populates='recipe')
    recipe_photos: list['RecipePhotos'] = Relationship(back_populates='recipe')


class RecipeIngredients(SQLModel, table=True):
    __tablename__ = 'recipe_ingredients'
    __table_args__ = (
        CheckConstraint('quantity_grams IS NULL OR quantity_grams >= 0::numeric', name='recipe_ingredients_quantity_grams_non_negative'),
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='recipe_ingredients_ingredient_id_fkey'),
        ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_ingredients_recipe_id_fkey'),
        PrimaryKeyConstraint('id', name='recipe_ingredients_pkey'),
        UniqueConstraint('recipe_id', 'ingredient_id', 'sort_order', name='uq_recipe_ingredient_order'),
        Index('ix_recipe_ingredients_ingredient_id', 'ingredient_id'),
        Index('ix_recipe_ingredients_recipe_id', 'recipe_id'),
        Index('ix_recipe_ingredients_sort_order', 'sort_order')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    recipe_id: uuid.UUID = Field(sa_column=Column('recipe_id', UUID(as_uuid=True), nullable=False))
    ingredient_id: uuid.UUID = Field(sa_column=Column('ingredient_id', UUID(as_uuid=True), nullable=False))
    sort_order: int = Field(sa_column=Column('sort_order', Integer, nullable=False, server_default=text('0')))
    quantity: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('quantity', Numeric(10, 4)))
    unit: Optional[str] = Field(default=None, sa_column=Column('unit', String(50)))
    preparation: Optional[str] = Field(default=None, sa_column=Column('preparation', String(255)))
    quid: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('quid', Numeric(10, 4)))
    item_type: Optional[str] = Field(default=None, sa_column=Column('item_type', String(50)))
    quantity_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('quantity_grams', Numeric))

    ingredient: 'Ingredients' = Relationship(back_populates='recipe_ingredients')
    recipe: 'Recipes' = Relationship(back_populates='recipe_ingredients')


class RecipePhotos(SQLModel, table=True):
    __tablename__ = 'recipe_photos'
    __table_args__ = (
        ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_photos_recipe_id_fkey'),
        PrimaryKeyConstraint('id', name='recipe_photos_pkey'),
        Index('idx_recipe_photos_recipe', 'recipe_id')
    )

    id: uuid.UUID = Field(sa_column=Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')))
    recipe_id: uuid.UUID = Field(sa_column=Column('recipe_id', UUID(as_uuid=True), nullable=False))
    photo_url: Optional[str] = Field(default=None, sa_column=Column('photo_url', Text))
    photo_data: Optional[bytes] = Field(default=None, sa_column=Column('photo_data', LargeBinary))
    photo_type: Optional[str] = Field(default=None, sa_column=Column('photo_type', String(50)))
    is_primary: Optional[bool] = Field(default=None, sa_column=Column('is_primary', Boolean, server_default=text('false')))
    created_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('created_at', DateTime(True), server_default=text('now()')))

    recipe: 'Recipes' = Relationship(back_populates='recipe_photos')