from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Index, Numeric, PrimaryKeyConstraint, String, Text, Uuid, text
from sqlmodel import Field, Relationship, SQLModel


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

	id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True))
	tenant_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column('tenant_id', Uuid))
	name: str = Field(sa_column=Column('name', String(255), nullable=False))
	description: Optional[str] = Field(default=None, sa_column=Column('description', Text))
	yield_amount: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('yield_amount', Numeric(10, 2)))
	yield_unit: Optional[str] = Field(default=None, sa_column=Column('yield_unit', String(50)))
	instructions: Optional[str] = Field(default=None, sa_column=Column('instructions', Text))
	status: str = Field(sa_column=Column('status', String(50), nullable=False, server_default=text("'draft'::character varying")))
	created_by: Optional[uuid.UUID] = Field(default=None, sa_column=Column('created_by', Uuid))
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
	yield_mode: str = Field(sa_column=Column('yield_mode', String(20), nullable=False, server_default=text("'count'::character varying")))
	portion_size_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('portion_size_grams', Numeric))
	total_raw_weight_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('total_raw_weight_grams', Numeric))
	total_cooked_weight_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('total_cooked_weight_grams', Numeric))
	portions_count_resolved: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('portions_count_resolved', Numeric))
	created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
	updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))

	category: list['Categories'] = Relationship(back_populates='recipe', sa_relationship_kwargs={'secondary': 'recipe_categories'})
	users: Optional['Users'] = Relationship(back_populates='recipes')
	tenant: 'Tenants' = Relationship(back_populates='recipes')
	tag: list['Tags'] = Relationship(back_populates='recipe', sa_relationship_kwargs={'secondary': 'recipe_tags'})
	recipe_ingredients: list['RecipeIngredients'] = Relationship(back_populates='recipe')
	recipe_versions: list['RecipeVersions'] = Relationship(back_populates='recipe')


Recipe = Recipes
