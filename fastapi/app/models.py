from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import text, DateTime, Column
from sqlmodel import Field, SQLModel

from pydantic import BaseModel



# class Additives(SQLModel, table=True):
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='additives_pkey'),
#         UniqueConstraint('code', name='additives_code_key'),
#         Index('idx_additives_code', 'code')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     code: str = Field(sa_column=mapped_column('code', Text, nullable=False))
#     name: str = Field(sa_column=mapped_column('name', Text, nullable=False))

#     ingredient_additives: List['IngredientAdditives'] = Relationship(back_populates='additive')


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


# class Heroes(SQLModel, table=True):
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='heroes_pkey'),
#         UniqueConstraint('email', name='heroes_email_key'),
#         UniqueConstraint('username', name='heroes_username_key')
#     )

#     id: Optional[int] = Field(default=None, sa_column=mapped_column('id', Integer))
#     username: str = Field(sa_column=mapped_column('username', String, nullable=False))
#     email: str = Field(sa_column=mapped_column('email', String, nullable=False))
#     firstname: str = Field(sa_column=mapped_column('firstname', String, nullable=False))
#     lastname: str = Field(sa_column=mapped_column('lastname', String, nullable=False))


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


# class Tenants(SQLModel, table=True):
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='tenants_pkey'),
#         UniqueConstraint('slug', name='tenants_slug_key'),
#         Index('ix_tenants_name', 'name'),
#         Index('ix_tenants_slug', 'slug', unique=True)
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid))
#     created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
#     updated_at: datetime = Field(sa_column=mapped_column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
#     name: str = Field(sa_column=mapped_column('name', String(255), nullable=False))
#     slug: str = Field(sa_column=mapped_column('slug', String(100), nullable=False))
#     is_active: bool = Field(sa_column=mapped_column('is_active', Boolean, nullable=False, server_default=text('true')))
#     settings: Optional[str] = Field(default=None, sa_column=mapped_column('settings', String))

#     ingredients: List['Ingredients'] = Relationship(back_populates='tenant')
#     users: List['Users'] = Relationship(back_populates='tenant')
#     recipes: List['Recipes'] = Relationship(back_populates='tenant')


# class IngredientAdditives(SQLModel, table=True):
#     __tablename__ = 'ingredient_additives'
#     __table_args__ = (
#         ForeignKeyConstraint(['additive_id'], ['additives.id'], ondelete='CASCADE', name='ingredient_additives_additive_id_fkey'),
#         PrimaryKeyConstraint('ingredient_id', 'additive_id', name='ingredient_additives_pkey'),
#         Index('idx_ing_additives_additive', 'additive_id')
#     )

#     ingredient_id: UUID = Field(sa_column=mapped_column('ingredient_id', Uuid, nullable=False))
#     additive_id: UUID = Field(sa_column=mapped_column('additive_id', Uuid, nullable=False))

#     additive: Optional['Additives'] = Relationship(back_populates='ingredient_additives')


# class IngredientAllergens(SQLModel, table=True):
#     __tablename__ = 'ingredient_allergens'
#     __table_args__ = (
#         ForeignKeyConstraint(['allergen_id'], ['allergens.id'], ondelete='CASCADE', name='ingredient_allergens_allergen_id_fkey'),
#         PrimaryKeyConstraint('ingredient_id', 'allergen_id', name='ingredient_allergens_pkey'),
#         Index('idx_ing_allergens_allergen', 'allergen_id')
#     )

#     ingredient_id: UUID = Field(sa_column=mapped_column('ingredient_id', Uuid, nullable=False))
#     allergen_id: UUID = Field(sa_column=mapped_column('allergen_id', Uuid, nullable=False))

#     allergen: Optional['Allergens'] = Relationship(back_populates='ingredient_allergens')


# class Ingredients(SQLModel, table=True):
#     __table_args__ = (
#         ForeignKeyConstraint(['parent_id'], ['ingredients.id'], name='ingredients_parent_id_fkey'),
#         ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='ingredients_tenant_id_fkey'),
#         PrimaryKeyConstraint('id', name='ingredients_pkey'),
#         Index('idx_ingredients_parent_id', 'parent_id'),
#         Index('idx_ingredients_usage_count', 'usage_count'),
#         Index('ix_ingredients_name', 'name')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid))
#     created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
#     updated_at: datetime = Field(sa_column=mapped_column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
#     name: str = Field(sa_column=mapped_column('name', String(255), nullable=False))
#     tenant_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('tenant_id', Uuid))
#     default_unit: Optional[str] = Field(default=None, sa_column=mapped_column('default_unit', String(50)))
#     nutrition_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('nutrition_id', Uuid))
#     usage_count: Optional[int] = Field(default=None, sa_column=mapped_column('usage_count', Integer, server_default=text('0')))
#     recipe_count: Optional[int] = Field(default=None, sa_column=mapped_column('recipe_count', Integer, server_default=text('0')))
#     ingredient_type: Optional[str] = Field(default=None, sa_column=mapped_column('ingredient_type', String(50)))
#     bls_key: Optional[str] = Field(default=None, sa_column=mapped_column('bls_key', String(100)))
#     is_custom: Optional[bool] = Field(default=None, sa_column=mapped_column('is_custom', Boolean, server_default=text('false')))
#     has_parent: Optional[bool] = Field(default=None, sa_column=mapped_column('has_parent', Boolean, server_default=text('false')))
#     parent_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('parent_id', Uuid))
#     initial_recipe_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('initial_recipe_id', Uuid))

#     parent: Optional['Ingredients'] = Relationship(back_populates='parent_reverse')
#     parent_reverse: List['Ingredients'] = Relationship(back_populates='parent')
#     tenant: Optional['Tenants'] = Relationship(back_populates='ingredients')
#     ingredient_nutrition: Optional['IngredientNutrition'] = Relationship(sa_relationship_kwargs={'uselist': False}, back_populates='ingredient')
#     ingredient_prices: List['IngredientPrices'] = Relationship(back_populates='ingredient')
#     recipe_ingredients: List['RecipeIngredients'] = Relationship(back_populates='ingredient')


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


# class Users(SQLModel, table=True):
#     __table_args__ = (
#         ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='users_tenant_id_fkey'),
#         PrimaryKeyConstraint('id', name='users_pkey'),
#         UniqueConstraint('email', name='users_email_key'),
#         Index('ix_users_email', 'email', unique=True)
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid))
#     created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
#     updated_at: datetime = Field(sa_column=mapped_column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
#     email: str = Field(sa_column=mapped_column('email', String(255), nullable=False))
#     password_hash: str = Field(sa_column=mapped_column('password_hash', String(255), nullable=False))
#     role: str = Field(sa_column=mapped_column('role', String(50), nullable=False, server_default=text("'editor'::character varying")))
#     is_active: bool = Field(sa_column=mapped_column('is_active', Boolean, nullable=False, server_default=text('true')))
#     tenant_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('tenant_id', Uuid))

#     tenant: Optional['Tenants'] = Relationship(back_populates='users')
#     recipes: List['Recipes'] = Relationship(back_populates='users')


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
#     currency: Optional[str] = Field(default=None, sa_column=mapped_column('currency', String(3), server_default=text("'EUR'::character varying")))
#     unit: Optional[str] = Field(default=None, sa_column=mapped_column('unit', String(50)))
#     supplier_id: Optional[str] = Field(default=None, sa_column=mapped_column('supplier_id', String(100)))
#     supplier_name: Optional[str] = Field(default=None, sa_column=mapped_column('supplier_name', String(255)))
#     article_number: Optional[str] = Field(default=None, sa_column=mapped_column('article_number', String(100)))
#     created_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('created_at', DateTime(True), server_default=text('now()')))
#     updated_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('updated_at', DateTime(True), server_default=text('now()')))

#     ingredient: Optional['Ingredients'] = Relationship(back_populates='ingredient_prices')


# class Recipes(SQLModel, table=True):
#     __table_args__ = (
#         ForeignKeyConstraint(['created_by'], ['users.id'], name='recipes_created_by_fkey'),
#         ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='recipes_tenant_id_fkey'),
#         PrimaryKeyConstraint('id', name='recipes_pkey'),
#         Index('idx_recipes_batch_number', 'batch_number'),
#         Index('idx_recipes_is_component', 'is_component'),
#         Index('idx_recipes_reduction_factor', 'reduction_factor'),
#         Index('ix_recipes_name', 'name')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid))
#     created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
#     updated_at: datetime = Field(sa_column=mapped_column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
#     name: str = Field(sa_column=mapped_column('name', String(255), nullable=False))
#     status: str = Field(sa_column=mapped_column('status', String(50), nullable=False, server_default=text("'draft'::character varying")))
#     tenant_id: Optional[UUID] = Field(default=None, sa_column=mapped_column('tenant_id', Uuid))
#     description: Optional[str] = Field(default=None, sa_column=mapped_column('description', Text))
#     yield_amount: Optional[Decimal] = Field(default=None, sa_column=mapped_column('yield_amount', Numeric(10, 2)))
#     yield_unit: Optional[str] = Field(default=None, sa_column=mapped_column('yield_unit', String(50)))
#     instructions: Optional[str] = Field(default=None, sa_column=mapped_column('instructions', Text))
#     created_by: Optional[UUID] = Field(default=None, sa_column=mapped_column('created_by', Uuid))
#     description_short: Optional[str] = Field(default=None, sa_column=mapped_column('description_short', Text))
#     serving_recommendation: Optional[str] = Field(default=None, sa_column=mapped_column('serving_recommendation', Text))
#     side_dishes: Optional[str] = Field(default=None, sa_column=mapped_column('side_dishes', Text))
#     notes: Optional[str] = Field(default=None, sa_column=mapped_column('notes', Text))
#     preparation_time: Optional[str] = Field(default=None, sa_column=mapped_column('preparation_time', Text))
#     waiting_time: Optional[str] = Field(default=None, sa_column=mapped_column('waiting_time', Text))
#     cooking_time: Optional[str] = Field(default=None, sa_column=mapped_column('cooking_time', Text))
#     shelf_life: Optional[str] = Field(default=None, sa_column=mapped_column('shelf_life', Text))
#     reduction_factor: Optional[Decimal] = Field(default=None, sa_column=mapped_column('reduction_factor', Numeric(10, 4)))
#     eigene_menge: Optional[Decimal] = Field(default=None, sa_column=mapped_column('eigene_menge', Numeric(10, 2)))
#     recipe_number: Optional[str] = Field(default=None, sa_column=mapped_column('recipe_number', String(100)))
#     packaging: Optional[str] = Field(default=None, sa_column=mapped_column('packaging', Text))
#     packaging_material: Optional[str] = Field(default=None, sa_column=mapped_column('packaging_material', Text))
#     net_weight: Optional[Decimal] = Field(default=None, sa_column=mapped_column('net_weight', Numeric(10, 2)))
#     fill_weight: Optional[Decimal] = Field(default=None, sa_column=mapped_column('fill_weight', Numeric(10, 2)))
#     fill_quantity: Optional[Decimal] = Field(default=None, sa_column=mapped_column('fill_quantity', Numeric(10, 2)))
#     drained_weight: Optional[Decimal] = Field(default=None, sa_column=mapped_column('drained_weight', Numeric(10, 2)))
#     total_weight: Optional[Decimal] = Field(default=None, sa_column=mapped_column('total_weight', Numeric(10, 2)))
#     portion_by_weight: Optional[bool] = Field(default=None, sa_column=mapped_column('portion_by_weight', Boolean, server_default=text('false')))
#     portion_weight: Optional[Decimal] = Field(default=None, sa_column=mapped_column('portion_weight', Numeric(10, 2)))
#     batch_number: Optional[str] = Field(default=None, sa_column=mapped_column('batch_number', String(100)))
#     production_date: Optional[date] = Field(default=None, sa_column=mapped_column('production_date', Date))
#     use_by_date: Optional[date] = Field(default=None, sa_column=mapped_column('use_by_date', Date))
#     expiry_date: Optional[date] = Field(default=None, sa_column=mapped_column('expiry_date', Date))
#     storage_text: Optional[str] = Field(default=None, sa_column=mapped_column('storage_text', Text))
#     storage_temperature: Optional[str] = Field(default=None, sa_column=mapped_column('storage_temperature', String(50)))
#     bio_label_eu: Optional[bool] = Field(default=None, sa_column=mapped_column('bio_label_eu', Boolean))
#     origin_fish: Optional[str] = Field(default=None, sa_column=mapped_column('origin_fish', Text))
#     origin_location: Optional[str] = Field(default=None, sa_column=mapped_column('origin_location', Text))
#     devices: Optional[str] = Field(default=None, sa_column=mapped_column('devices', Text))
#     utensils: Optional[str] = Field(default=None, sa_column=mapped_column('utensils', Text))
#     labor_effort: Optional[str] = Field(default=None, sa_column=mapped_column('labor_effort', String(50)))
#     margin: Optional[Decimal] = Field(default=None, sa_column=mapped_column('margin', Numeric(10, 2)))
#     sales_price_points: Optional[Decimal] = Field(default=None, sa_column=mapped_column('sales_price_points', Numeric(10, 2)))
#     vat_rate: Optional[Decimal] = Field(default=None, sa_column=mapped_column('vat_rate', Numeric(5, 2)))
#     nutri_score_category: Optional[str] = Field(default=None, sa_column=mapped_column('nutri_score_category', String(10)))
#     nutri_score_veg_fruits: Optional[Decimal] = Field(default=None, sa_column=mapped_column('nutri_score_veg_fruits', Numeric(5, 2)))
#     layout_id: Optional[str] = Field(default=None, sa_column=mapped_column('layout_id', String(50)))
#     row_height: Optional[int] = Field(default=None, sa_column=mapped_column('row_height', Integer))
#     rezeptblatt_image_width: Optional[int] = Field(default=None, sa_column=mapped_column('rezeptblatt_image_width', Integer))
#     mise_en_place_display: Optional[bool] = Field(default=None, sa_column=mapped_column('mise_en_place_display', Boolean, server_default=text('true')))
#     notes_instructions: Optional[str] = Field(default=None, sa_column=mapped_column('notes_instructions', Text))
#     is_component: Optional[bool] = Field(default=None, sa_column=mapped_column('is_component', Boolean, server_default=text('false')))
#     branch_ids: Optional[str] = Field(default=None, sa_column=mapped_column('branch_ids', Text))
#     ingredient_list_custom: Optional[str] = Field(default=None, sa_column=mapped_column('ingredient_list_custom', Text))
#     ingredient_list_product_pass: Optional[str] = Field(default=None, sa_column=mapped_column('ingredient_list_product_pass', Text))
#     allergene_source: Optional[str] = Field(default=None, sa_column=mapped_column('allergene_source', Text))
#     unit_measure: Optional[str] = Field(default=None, sa_column=mapped_column('unit_measure', String(50)))
#     unit_serving: Optional[str] = Field(default=None, sa_column=mapped_column('unit_serving', String(50)))
#     preference_allergens: Optional[str] = Field(default=None, sa_column=mapped_column('preference_allergens', Text))
#     preference_price: Optional[Decimal] = Field(default=None, sa_column=mapped_column('preference_price', Numeric(10, 2)))
#     preference_nutri_value: Optional[Decimal] = Field(default=None, sa_column=mapped_column('preference_nutri_value', Numeric(10, 2)))

    # users: Optional['Users'] = Relationship(back_populates='recipes')
    # tenant: Optional['Tenants'] = Relationship(back_populates='recipes')
    # recipe_ingredients: List['RecipeIngredients'] = Relationship(back_populates='recipe')
    # recipe_photos: List['RecipePhotos'] = Relationship(back_populates='recipe')

## MP: converted table (by LLM)

class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Core fields
    name: str = Field(max_length=255, index=True)
    status: str = Field(default="draft", max_length=50)

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
            onupdate=text("now()"),
        )
    )

    # Foreign keys
    tenant_id: Optional[UUID] = Field(default=None, foreign_key="tenants.id")
    created_by: Optional[UUID] = Field(default=None, foreign_key="users.id")

    # Text fields
    description: Optional[str] = None
    description_short: Optional[str] = None
    instructions: Optional[str] = None
    notes: Optional[str] = None
    notes_instructions: Optional[str] = None
    serving_recommendation: Optional[str] = None
    side_dishes: Optional[str] = None
    storage_text: Optional[str] = None
    origin_fish: Optional[str] = None
    origin_location: Optional[str] = None
    devices: Optional[str] = None
    utensils: Optional[str] = None
    packaging: Optional[str] = None
    packaging_material: Optional[str] = None
    branch_ids: Optional[str] = None
    ingredient_list_custom: Optional[str] = None
    ingredient_list_product_pass: Optional[str] = None
    allergene_source: Optional[str] = None

    # Numeric fields
    yield_amount: Optional[Decimal] = None
    reduction_factor: Optional[Decimal] = Field(default=None, index=True)
    eigene_menge: Optional[Decimal] = None
    net_weight: Optional[Decimal] = None
    fill_weight: Optional[Decimal] = None
    fill_quantity: Optional[Decimal] = None
    drained_weight: Optional[Decimal] = None
    total_weight: Optional[Decimal] = None
    portion_weight: Optional[Decimal] = None
    margin: Optional[Decimal] = None
    sales_price_points: Optional[Decimal] = None
    vat_rate: Optional[Decimal] = None
    nutri_score_veg_fruits: Optional[Decimal] = None
    preference_price: Optional[Decimal] = None
    preference_nutri_value: Optional[Decimal] = None

    # Strings
    yield_unit: Optional[str] = Field(default=None, max_length=50)
    recipe_number: Optional[str] = Field(default=None, max_length=100)
    batch_number: Optional[str] = Field(default=None, max_length=100, index=True)
    storage_temperature: Optional[str] = Field(default=None, max_length=50)
    labor_effort: Optional[str] = Field(default=None, max_length=50)
    nutri_score_category: Optional[str] = Field(default=None, max_length=10)
    layout_id: Optional[str] = Field(default=None, max_length=50)
    unit_measure: Optional[str] = Field(default=None, max_length=50)
    unit_serving: Optional[str] = Field(default=None, max_length=50)

    # Booleans
    portion_by_weight: bool = Field(default=False)
    bio_label_eu: Optional[bool] = None
    mise_en_place_display: bool = Field(default=True)
    is_component: bool = Field(default=False)

    # Integers
    row_height: Optional[int] = None
    rezeptblatt_image_width: Optional[int] = None

    # Dates
    production_date: Optional[date] = None
    use_by_date: Optional[date] = None
    expiry_date: Optional[date] = None

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
#     unit: Optional[str] = Field(default=None, sa_column=mapped_column('unit', String(50)))
#     preparation: Optional[str] = Field(default=None, sa_column=mapped_column('preparation', String(255)))
#     quid: Optional[Decimal] = Field(default=None, sa_column=mapped_column('quid', Numeric(10, 4)))
#     item_type: Optional[str] = Field(default=None, sa_column=mapped_column('item_type', String(50)))

#     ingredient: Optional['Ingredients'] = Relationship(back_populates='recipe_ingredients')
#     recipe: Optional['Recipes'] = Relationship(back_populates='recipe_ingredients')


# class RecipePhotos(SQLModel, table=True):
#     __tablename__ = 'recipe_photos'
#     __table_args__ = (
#         ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_photos_recipe_id_fkey'),
#         PrimaryKeyConstraint('id', name='recipe_photos_pkey'),
#         Index('idx_recipe_photos_recipe', 'recipe_id')
#     )

#     id: UUID = Field(sa_column=mapped_column('id', Uuid, server_default=text('uuid_generate_v4()')))
#     recipe_id: UUID = Field(sa_column=mapped_column('recipe_id', Uuid, nullable=False))
#     photo_url: Optional[str] = Field(default=None, sa_column=mapped_column('photo_url', Text))
#     photo_data: Optional[bytes] = Field(default=None, sa_column=mapped_column('photo_data', LargeBinary))
#     photo_type: Optional[str] = Field(default=None, sa_column=mapped_column('photo_type', String(50)))
#     is_primary: Optional[bool] = Field(default=None, sa_column=mapped_column('is_primary', Boolean, server_default=text('false')))
#     created_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('created_at', DateTime(True), server_default=text('now()')))

#     recipe: Optional['Recipes'] = Relationship(back_populates='recipe_photos')
