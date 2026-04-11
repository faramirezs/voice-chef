from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.tenant_models import Tenants
from app.user_models import Users
from app.recipe_models import Recipe, Recipes

class Additives(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='additives_pkey'),
        UniqueConstraint('code', name='additives_code_key')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    code: int = Field(sa_column=Column('code', Integer, nullable=False))
    name_de: str = Field(sa_column=Column('name_de', String(255), nullable=False))
    name_en: Optional[str] = Field(default=None, sa_column=Column('name_en', String(255)))

    ingredient: list['Ingredients'] = Relationship(back_populates='additive', sa_relationship_kwargs={'secondary': 'ingredient_additives'})


class Allergens(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='allergens_pkey'),
        UniqueConstraint('code', name='allergens_code_key')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    code: int = Field(sa_column=Column('code', Integer, nullable=False))
    name_de: str = Field(sa_column=Column('name_de', String(255), nullable=False))
    name_en: Optional[str] = Field(default=None, sa_column=Column('name_en', String(255)))
    parent_code: Optional[int] = Field(default=None, sa_column=Column('parent_code', Integer))

    ingredient: list['Ingredients'] = Relationship(back_populates='allergen', sa_relationship_kwargs={'secondary': 'ingredient_allergens'})


class AuditLogs(SQLModel, table=True):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='audit_logs_pkey'),
        Index('idx_audit_logs_entity', 'entity', 'entity_id'),
        Index('idx_audit_logs_tenant', 'tenant_id', text('created_at DESC'))
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    tenant_id: uuid.UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))
    actor_type: str = Field(sa_column=Column('actor_type', String(50), nullable=False))
    actor_id: uuid.UUID = Field(sa_column=Column('actor_id', Uuid, nullable=False))
    action: str = Field(sa_column=Column('action', String(50), nullable=False))
    entity: str = Field(sa_column=Column('entity', String(100), nullable=False))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    entity_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('entity_id', Uuid))
    old_data: Optional[dict] = Field(default=None, sa_column=Column('old_data', JSONB))
    new_data: Optional[dict] = Field(default=None, sa_column=Column('new_data', JSONB))


class Units(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("unit_type::text = ANY (ARRAY['weight'::character varying, 'volume'::character varying, 'piece'::character varying, 'custom'::character varying]::text[])", name='valid_unit_type'),
        PrimaryKeyConstraint('id', name='units_pkey'),
        UniqueConstraint('code', name='units_code_key')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    code: str = Field(sa_column=Column('code', String(20), nullable=False))
    name_de: str = Field(sa_column=Column('name_de', String(100), nullable=False))
    unit_type: str = Field(sa_column=Column('unit_type', String(20), nullable=False))
    is_base: bool = Field(sa_column=Column('is_base', Boolean, nullable=False, server_default=text('false')))
    name_en: Optional[str] = Field(default=None, sa_column=Column('name_en', String(100)))
    grams_per_unit: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('grams_per_unit', Numeric))


class Agents(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='agents_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='agents_pkey')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    tenant_id: uuid.UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))
    agent_type: str = Field(sa_column=Column('agent_type', String(50), nullable=False))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    capabilities: dict = Field(sa_column=Column('capabilities', JSONB, nullable=False, server_default=text("'[]'::jsonb")))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))

    tenant: 'Tenants' = Relationship(back_populates='agents')
    agent_interactions: list['AgentInteractions'] = Relationship(back_populates='agent')


class Categories(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='categories_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='categories_pkey')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    tenant_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('tenant_id', Uuid))

    tenant: Optional['Tenants'] = Relationship(back_populates='categories')
    recipe: list['Recipes'] = Relationship(back_populates='category', sa_relationship_kwargs={'secondary': 'recipe_categories'})


class Ingredients(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['parent_id'], ['ingredients.id'], name='ingredients_parent_id_fkey'),
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='ingredients_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredients_pkey'),
        Index('idx_ingredients_name', 'name'),
        Index('idx_ingredients_parent', 'parent_id'),
        Index('idx_ingredients_tenant', 'tenant_id')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    source: str = Field(sa_column=Column('source', String(50), nullable=False, server_default=text("'standard'::character varying")))
    is_custom: bool = Field(sa_column=Column('is_custom', Boolean, nullable=False, server_default=text('false')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    tenant_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('tenant_id', Uuid))
    name_english: Optional[str] = Field(default=None, sa_column=Column('name_english', String(255)))
    bls_key: Optional[str] = Field(default=None, sa_column=Column('bls_key', String(50)))
    default_unit: Optional[str] = Field(default=None, sa_column=Column('default_unit', String(50)))
    parent_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('parent_id', Uuid))

    additive: list['Additives'] = Relationship(back_populates='ingredient', sa_relationship_kwargs={'secondary': 'ingredient_additives'})
    allergen: list['Allergens'] = Relationship(back_populates='ingredient', sa_relationship_kwargs={'secondary': 'ingredient_allergens'})
    parent: Optional['Ingredients'] = Relationship(back_populates='parent_reverse', sa_relationship_kwargs={'remote_side': '[Ingredients.id]'})
    parent_reverse: list['Ingredients'] = Relationship(back_populates='parent', sa_relationship_kwargs={'remote_side': '[Ingredients.parent_id]'})
    tenant: Optional['Tenants'] = Relationship(back_populates='ingredients')
    ingredient_nutrition: 'IngredientNutrition' = Relationship(back_populates='ingredient', sa_relationship_kwargs={'uselist': False})
    ingredient_prices: list['IngredientPrices'] = Relationship(back_populates='ingredient')
    ingredient_units: list['IngredientUnits'] = Relationship(back_populates='ingredient')
    recipe_ingredients: list['RecipeIngredients'] = Relationship(back_populates='ingredient')


class ShoppingLists(SQLModel, table=True):
    __tablename__ = 'shopping_lists'
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='shopping_lists_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='shopping_lists_pkey')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    tenant_id: uuid.UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))
    name: str = Field(sa_column=Column('name', String(255), nullable=False, server_default=text("'Shopping List'::character varying")))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))

    tenant: 'Tenants' = Relationship(back_populates='shopping_lists')
    shopping_list_items: list['ShoppingListItems'] = Relationship(back_populates='list')


class Tags(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='tags_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='tags_pkey')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    tenant_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('tenant_id', Uuid))

    tenant: Optional['Tenants'] = Relationship(back_populates='tags')
    recipe: list['Recipes'] = Relationship(back_populates='tag', sa_relationship_kwargs={'secondary': 'recipe_tags'})


class TaskLists(SQLModel, table=True):
    __tablename__ = 'task_lists'
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='task_lists_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='task_lists_pkey')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    tenant_id: uuid.UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))
    name: str = Field(sa_column=Column('name', String(255), nullable=False, server_default=text("'Prep List'::character varying")))
    date: datetime.date = Field(sa_column=Column('date', Date, nullable=False, server_default=text('CURRENT_DATE')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))

    tenant: 'Tenants' = Relationship(back_populates='task_lists')
    task_items: list['TaskItems'] = Relationship(back_populates='list')


class AgentInteractions(SQLModel, table=True):
    __tablename__ = 'agent_interactions'
    __table_args__ = (
        ForeignKeyConstraint(['agent_id'], ['agents.id'], name='agent_interactions_agent_id_fkey'),
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='agent_interactions_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='agent_interactions_pkey'),
        Index('idx_agent_interactions_agent', 'agent_id', text('created_at DESC')),
        Index('idx_agent_interactions_tenant', 'tenant_id', text('created_at DESC'))
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    tenant_id: uuid.UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))
    agent_id: uuid.UUID = Field(sa_column=Column('agent_id', Uuid, nullable=False))
    source: str = Field(sa_column=Column('source', String(50), nullable=False))
    raw_input: str = Field(sa_column=Column('raw_input', Text, nullable=False))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    parsed_intent: Optional[str] = Field(default=None, sa_column=Column('parsed_intent', String(255)))
    confidence_score: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('confidence_score', Numeric(3, 2)))
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column('tool_calls', JSONB, server_default=text("'[]'::jsonb")))
    response_text: Optional[str] = Field(default=None, sa_column=Column('response_text', Text))
    latency_ms: Optional[int] = Field(default=None, sa_column=Column('latency_ms', Integer))
    error: Optional[str] = Field(default=None, sa_column=Column('error', Text))

    agent: 'Agents' = Relationship(back_populates='agent_interactions')
    tenant: 'Tenants' = Relationship(back_populates='agent_interactions')


t_ingredient_additives = Table(
    'ingredient_additives', SQLModel.metadata,
    Column('ingredient_id', Uuid, primary_key=True),
    Column('additive_id', Uuid, primary_key=True),
    ForeignKeyConstraint(['additive_id'], ['additives.id'], ondelete='CASCADE', name='ingredient_additives_additive_id_fkey'),
    ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_additives_ingredient_id_fkey'),
    PrimaryKeyConstraint('ingredient_id', 'additive_id', name='ingredient_additives_pkey'),
    Index('idx_ing_additives_additive', 'additive_id')
)


t_ingredient_allergens = Table(
    'ingredient_allergens', SQLModel.metadata,
    Column('ingredient_id', Uuid, primary_key=True),
    Column('allergen_id', Uuid, primary_key=True),
    ForeignKeyConstraint(['allergen_id'], ['allergens.id'], ondelete='CASCADE', name='ingredient_allergens_allergen_id_fkey'),
    ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_allergens_ingredient_id_fkey'),
    PrimaryKeyConstraint('ingredient_id', 'allergen_id', name='ingredient_allergens_pkey'),
    Index('idx_ing_allergens_allergen', 'allergen_id')
)


class IngredientNutrition(SQLModel, table=True):
    __tablename__ = 'ingredient_nutrition'
    __table_args__ = (
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_nutrition_ingredient_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredient_nutrition_pkey'),
        UniqueConstraint('ingredient_id', name='ingredient_nutrition_ingredient_id_key')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    ingredient_id: uuid.UUID = Field(sa_column=Column('ingredient_id', Uuid, nullable=False))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    energy_kj: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('energy_kj', Numeric))
    energy_kcal: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('energy_kcal', Numeric))
    fat: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('fat', Numeric))
    saturates: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('saturates', Numeric))
    carbs: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('carbs', Numeric))
    sugars: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('sugars', Numeric))
    protein: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('protein', Numeric))
    fiber: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('fiber', Numeric))
    salt: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('salt', Numeric))
    alcohol: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('alcohol', Numeric))
    water: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('water', Numeric))

    ingredient: 'Ingredients' = Relationship(back_populates='ingredient_nutrition')


class IngredientPrices(SQLModel, table=True):
    __tablename__ = 'ingredient_prices'
    __table_args__ = (
        CheckConstraint('price_per_gram IS NULL OR price_per_gram > 0::numeric', name='ingredient_prices_price_per_gram_positive'),
        CheckConstraint('price_per_unit > 0::numeric', name='positive_price'),
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_prices_ingredient_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredient_prices_pkey'),
        Index('idx_ingredient_prices_ing', 'ingredient_id'),
        Index('idx_ingredient_prices_latest_lookup', 'ingredient_id', 'unit', text('updated_at DESC'), text('created_at DESC'), text('id DESC')),
        Index('uq_ingredient_no_supplier', 'ingredient_id', postgresql_where='(supplier_id IS NULL)', unique=True),
        Index('uq_ingredient_supplier', 'ingredient_id', 'supplier_id', postgresql_where='(supplier_id IS NOT NULL)', unique=True)
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    ingredient_id: uuid.UUID = Field(sa_column=Column('ingredient_id', Uuid, nullable=False))
    currency: str = Field(sa_column=Column('currency', String(10), nullable=False, server_default=text("'EUR'::character varying")))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    price_per_unit: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('price_per_unit', Numeric(10, 4)))
    unit: Optional[str] = Field(default=None, sa_column=Column('unit', String(50)))
    supplier_name: Optional[str] = Field(default=None, sa_column=Column('supplier_name', String(255)))
    supplier_id: Optional[str] = Field(default=None, sa_column=Column('supplier_id', String(100)))
    article_number: Optional[str] = Field(default=None, sa_column=Column('article_number', String(100)))
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

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    ingredient_id: uuid.UUID = Field(sa_column=Column('ingredient_id', Uuid, nullable=False))
    unit_code: str = Field(sa_column=Column('unit_code', String(20), nullable=False))
    grams_per_unit: decimal.Decimal = Field(sa_column=Column('grams_per_unit', Numeric, nullable=False))
    label: Optional[str] = Field(default=None, sa_column=Column('label', String(100)))

    ingredient: 'Ingredients' = Relationship(back_populates='ingredient_units')


class ShoppingListItems(SQLModel, table=True):
    __tablename__ = 'shopping_list_items'
    __table_args__ = (
        CheckConstraint('quantity_grams IS NULL OR quantity_grams >= 0::numeric', name='shopping_list_items_quantity_grams_non_negative'),
        ForeignKeyConstraint(['list_id'], ['shopping_lists.id'], ondelete='CASCADE', name='shopping_list_items_list_id_fkey'),
        PrimaryKeyConstraint('id', name='shopping_list_items_pkey'),
        Index('idx_shopping_items_list', 'list_id')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    list_id: uuid.UUID = Field(sa_column=Column('list_id', Uuid, nullable=False))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    is_checked: bool = Field(sa_column=Column('is_checked', Boolean, nullable=False, server_default=text('false')))
    sort_order: int = Field(sa_column=Column('sort_order', Integer, nullable=False, server_default=text('0')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    quantity: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('quantity', Numeric))
    unit: Optional[str] = Field(default=None, sa_column=Column('unit', String(50)))
    quantity_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('quantity_grams', Numeric))

    list: 'ShoppingLists' = Relationship(back_populates='shopping_list_items')


class TaskItems(SQLModel, table=True):
    __tablename__ = 'task_items'
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['pending'::character varying, 'done'::character varying]::text[])", name='valid_task_status'),
        ForeignKeyConstraint(['list_id'], ['task_lists.id'], ondelete='CASCADE', name='task_items_list_id_fkey'),
        PrimaryKeyConstraint('id', name='task_items_pkey'),
        Index('idx_task_items_list', 'list_id')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    list_id: uuid.UUID = Field(sa_column=Column('list_id', Uuid, nullable=False))
    title: str = Field(sa_column=Column('title', String(500), nullable=False))
    status: str = Field(sa_column=Column('status', String(50), nullable=False, server_default=text("'pending'::character varying")))
    sort_order: int = Field(sa_column=Column('sort_order', Integer, nullable=False, server_default=text('0')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))

    list: 'TaskLists' = Relationship(back_populates='task_items')


t_recipe_categories = Table(
    'recipe_categories', SQLModel.metadata,
    Column('recipe_id', Uuid, primary_key=True),
    Column('category_id', Uuid, primary_key=True),
    ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', name='recipe_categories_category_id_fkey'),
    ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_categories_recipe_id_fkey'),
    PrimaryKeyConstraint('recipe_id', 'category_id', name='recipe_categories_pkey'),
    Index('idx_recipe_categories_cat', 'category_id')
)


class RecipeIngredients(SQLModel, table=True):
    __tablename__ = 'recipe_ingredients'
    __table_args__ = (
        CheckConstraint('quantity_grams IS NULL OR quantity_grams >= 0::numeric', name='recipe_ingredients_quantity_grams_non_negative'),
        CheckConstraint('num_nonnulls(ingredient_id, sub_recipe_id) = 1', name='recipe_ingredients_exactly_one_item'),
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='recipe_ingredients_ingredient_id_fkey'),
        ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_ingredients_recipe_id_fkey'),
        ForeignKeyConstraint(['sub_recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_ingredients_sub_recipe_id_fkey'),
        PrimaryKeyConstraint('id', name='recipe_ingredients_pkey'),
        UniqueConstraint('recipe_id', 'ingredient_id', 'sort_order', name='uq_recipe_ingredient_order'),
        Index('idx_recipe_ingredients_ingredient', 'ingredient_id'),
        Index('idx_recipe_ingredients_recipe', 'recipe_id'),
        Index('idx_recipe_ingredients_sub_recipe', 'sub_recipe_id'),
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    recipe_id: uuid.UUID = Field(sa_column=Column('recipe_id', Uuid, nullable=False))
    ingredient_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('ingredient_id', Uuid, nullable=True))
    sub_recipe_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('sub_recipe_id', Uuid, nullable=True))
    sort_order: int = Field(sa_column=Column('sort_order', Integer, nullable=False, server_default=text('0')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    quantity: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('quantity', Numeric))
    unit: Optional[str] = Field(default=None, sa_column=Column('unit', String(50)))
    preparation: Optional[str] = Field(default=None, sa_column=Column('preparation', String(255)))
    quid_percent: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('quid_percent', Numeric))
    is_organic: Optional[bool] = Field(default=None, sa_column=Column('is_organic', Boolean, server_default=text('false')))
    item_type: Optional[str] = Field(default=None, sa_column=Column('item_type', String(50)))
    quantity_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('quantity_grams', Numeric))

    ingredient: Optional['Ingredients'] = Relationship(back_populates='recipe_ingredients')
    recipe: 'Recipes' = Relationship(back_populates='recipe_ingredients', sa_relationship_kwargs={'foreign_keys': '[RecipeIngredients.recipe_id]'})
    sub_recipe: Optional['Recipes'] = Relationship(sa_relationship_kwargs={'foreign_keys': '[RecipeIngredients.sub_recipe_id]'})


class RecipeNutritionCache(SQLModel, table=True):
    __tablename__ = 'recipe_nutrition_cache'
    __table_args__ = (
        ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_nutrition_cache_recipe_id_fkey'),
        PrimaryKeyConstraint('recipe_id', name='recipe_nutrition_cache_pkey')
    )

    recipe_id: uuid.UUID = Field(sa_column=Column('recipe_id', Uuid, primary_key=True))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    energy_kj: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('energy_kj', Numeric))
    energy_kcal: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('energy_kcal', Numeric))
    fat: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('fat', Numeric))
    saturates: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('saturates', Numeric))
    carbs: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('carbs', Numeric))
    sugars: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('sugars', Numeric))
    protein: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('protein', Numeric))
    salt: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('salt', Numeric))
    fiber: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('fiber', Numeric))


t_recipe_tags = Table(
    'recipe_tags', SQLModel.metadata,
    Column('recipe_id', Uuid, primary_key=True),
    Column('tag_id', Uuid, primary_key=True),
    ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_tags_recipe_id_fkey'),
    ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE', name='recipe_tags_tag_id_fkey'),
    PrimaryKeyConstraint('recipe_id', 'tag_id', name='recipe_tags_pkey'),
    Index('idx_recipe_tags_tag', 'tag_id')
)


class RecipeVersions(SQLModel, table=True):
    __tablename__ = 'recipe_versions'
    __table_args__ = (
        ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_versions_recipe_id_fkey'),
        PrimaryKeyConstraint('id', name='recipe_versions_pkey'),
        Index('idx_recipe_versions_recipe', 'recipe_id')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    recipe_id: uuid.UUID = Field(sa_column=Column('recipe_id', Uuid, nullable=False))
    version: int = Field(sa_column=Column('version', Integer, nullable=False))
    data: dict = Field(sa_column=Column('data', JSONB, nullable=False))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))

    recipe: 'Recipes' = Relationship(back_populates='recipe_versions')

